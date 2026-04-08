from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from .models import InterviewKit
from .serializers import (
    InterviewKitCreateSerializer,
    InterviewKitSerializer,
    PublishToggleSerializer,
    RegenerateSectionSerializer,
)
from .services import generate_full_kit, generate_section, match_cv_to_role
from .utils import extract_text_from_pdf


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateFullKitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InterviewKitCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        role_description = data["role_description"]
        role_level = data.get("role_level", "")
        industry = data.get("industry", "")
        company_size = data.get("company_size", "")
        remote_policy = data.get("remote_policy", "")

        generated_kit = generate_full_kit(
            role_description=role_description,
            role_level=role_level,
            industry=industry,
            company_size=company_size,
            remote_policy=remote_policy,
        )

        role_title = generated_kit.get("job_description", {}).get("role_title", "Untitled Role")
        interview_kit = InterviewKit.objects.create(
            role_title=role_title,
            role_description=role_description,
            role_level=role_level,
            industry=industry,
            company_size=company_size,
            remote_policy=remote_policy,
            generated_kit=generated_kit,
            created_by=request.user,
        )

        return Response(
            InterviewKitSerializer(interview_kit).data,
            status=status.HTTP_201_CREATED,
        )


class InterviewKitListView(ListAPIView):
    serializer_class = InterviewKitSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return InterviewKit.objects.filter(created_by=self.request.user)
        return InterviewKit.objects.filter(status='published')


class InterviewKitDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ('DELETE', 'PATCH'):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, pk):
        kit = get_object_or_404(InterviewKit, pk=pk)
        if kit.status != 'published' and kit.created_by != request.user:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(InterviewKitSerializer(kit).data)

    def patch(self, request, pk):
        kit = get_object_or_404(InterviewKit, pk=pk, created_by=request.user)
        update_fields = []
        if 'role_description' in request.data:
            kit.role_description = request.data['role_description']
            update_fields.append('role_description')
        if 'role_title' in request.data:
            kit.role_title = request.data['role_title']
            update_fields.append('role_title')
        if update_fields:
            kit.save(update_fields=update_fields)
        return Response(InterviewKitSerializer(kit).data)

    def delete(self, request, pk):
        kit = get_object_or_404(InterviewKit, pk=pk, created_by=request.user)
        kit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublishToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        kit = get_object_or_404(InterviewKit, pk=pk, created_by=request.user)
        serializer = PublishToggleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        kit.status = serializer.validated_data['status']
        kit.save(update_fields=['status'])
        return Response(InterviewKitSerializer(kit).data)


class RegenerateSectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = RegenerateSectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        section_name = serializer.validated_data["section_name"]
        kit = get_object_or_404(InterviewKit, pk=pk, created_by=request.user)

        regenerated = generate_section(
            section_name=section_name,
            role_description=kit.role_description,
            role_level=kit.role_level,
            industry=kit.industry,
            company_size=kit.company_size,
            remote_policy=kit.remote_policy,
        )

        kit.generated_kit[section_name] = regenerated
        kit.save(update_fields=["generated_kit"])

        return Response(
            {"section_name": section_name, "data": regenerated},
            status=status.HTTP_200_OK,
        )


class CVMatchView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        kit = get_object_or_404(InterviewKit, pk=pk, status='published')

        cv_file = request.FILES.get('cv_file')
        if cv_file is None:
            return Response({'detail': 'cv_file is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if cv_file.content_type != 'application/pdf':
            return Response({'detail': 'File must be a PDF.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cv_text = extract_text_from_pdf(cv_file)
        except ValueError as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        role_data = {
            'role_title': kit.role_title,
            'role_description': kit.role_description,
            'role_level': kit.role_level,
            'job_description': kit.generated_kit.get('job_description', {}),
        }

        try:
            match_result = match_cv_to_role(cv_text, role_data)
        except ValueError as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(match_result)
