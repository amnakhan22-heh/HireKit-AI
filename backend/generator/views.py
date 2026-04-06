from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView

from .models import InterviewKit
from .serializers import InterviewKitCreateSerializer, InterviewKitSerializer
from .services import generate_full_kit


class GenerateFullKitView(APIView):
    def post(self, request):
        serializer = InterviewKitCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        role_description = serializer.validated_data["role_description"]
        generated_kit = generate_full_kit(role_description)

        role_title = (
            generated_kit.get("job_description", {}).get("role_title", "Untitled Role")
        )
        interview_kit = InterviewKit.objects.create(
            role_title=role_title,
            role_description=role_description,
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
