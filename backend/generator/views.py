from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from django.shortcuts import get_object_or_404

from .models import InterviewKit
from .serializers import (
    InterviewKitCreateSerializer,
    InterviewKitSerializer,
    RegenerateSectionSerializer,
)
from .services import generate_full_kit, generate_section


class GenerateFullKitView(APIView):
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
        )

        return Response(
            InterviewKitSerializer(interview_kit).data,
            status=status.HTTP_201_CREATED,
        )


class InterviewKitListView(ListAPIView):
    queryset = InterviewKit.objects.all()
    serializer_class = InterviewKitSerializer


class InterviewKitDetailView(RetrieveDestroyAPIView):
    queryset = InterviewKit.objects.all()
    serializer_class = InterviewKitSerializer


class RegenerateSectionView(APIView):
    def post(self, request, pk):
        serializer = RegenerateSectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        section_name = serializer.validated_data["section_name"]
        kit = get_object_or_404(InterviewKit, pk=pk)

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
