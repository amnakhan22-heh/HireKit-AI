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
    """
    Handle user authentication and token issuance.

    Accepts username and password, authenticates against Django's auth backend,
    and returns a DRF token on success.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate a user and return their auth token.

        Args:
            request: DRF Request with ``username`` and ``password`` in the body.

        Returns:
            Response: JSON with ``token`` and ``username`` on success (200),
                or ``detail`` error message on failure (400).
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})


class LogoutView(APIView):
    """
    Handle user logout by deleting the authenticated user's token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Delete the requesting user's auth token, ending their session.

        Args:
            request: Authenticated DRF Request.

        Returns:
            Response: 204 No Content on success.
        """
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateFullKitView(APIView):
    """
    Handle full interview kit generation from a plain-language role description.

    Validates input, delegates generation to the service layer, persists the
    resulting kit, and returns it serialized. Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Validate input, generate a full interview kit, persist it, and return it.

        Args:
            request: Authenticated DRF Request containing ``role_description``
                and optional ``role_level``, ``industry``, ``company_size``,
                ``remote_policy`` fields.

        Returns:
            Response: Serialized ``InterviewKit`` on success (201), or validation
                errors (400).
        """
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
    """
    Return a paginated list of interview kits.

    Authenticated users see all kits they created. Unauthenticated users
    see only kits with ``status='published'``.
    """

    serializer_class = InterviewKitSerializer

    def get_queryset(self):
        """
        Filter kits by ownership (authenticated) or published status (anonymous).

        Returns:
            QuerySet: Filtered and ordered ``InterviewKit`` queryset.
        """
        if self.request.user.is_authenticated:
            return InterviewKit.objects.filter(created_by=self.request.user)
        return InterviewKit.objects.filter(status='published')


class InterviewKitDetailView(APIView):
    """
    Retrieve, update, or delete a single interview kit.

    GET is public for published kits; PATCH and DELETE require the requesting
    user to be the kit's owner.
    """

    def get_permissions(self):
        """
        Return ``IsAuthenticated`` for DELETE and PATCH; ``AllowAny`` for GET.

        Returns:
            list: A list containing one permission instance.
        """
        if self.request.method in ('DELETE', 'PATCH'):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, pk):
        """
        Retrieve a kit. Draft kits are only visible to their owner.

        Args:
            request: DRF Request (authenticated or anonymous).
            pk (UUID): Primary key of the kit.

        Returns:
            Response: Serialized kit (200), or 404 if not found or not accessible.
        """
        kit = get_object_or_404(InterviewKit, pk=pk)
        if kit.status != 'published' and kit.created_by != request.user:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(InterviewKitSerializer(kit).data)

    def patch(self, request, pk):
        """
        Update ``role_title`` and/or ``role_description`` on the owner's kit.

        Args:
            request: Authenticated DRF Request with optional ``role_title``
                and/or ``role_description`` in the body.
            pk (UUID): Primary key of the kit.

        Returns:
            Response: Serialized updated kit (200), or 404 if not found.
        """
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
        """
        Permanently delete the owner's kit.

        Args:
            request: Authenticated DRF Request.
            pk (UUID): Primary key of the kit.

        Returns:
            Response: 204 No Content on success, or 404 if not found.
        """
        kit = get_object_or_404(InterviewKit, pk=pk, created_by=request.user)
        kit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublishToggleView(APIView):
    """
    Toggle a kit's status between ``draft`` and ``published``.

    Requires authentication. Only the kit's owner can change its status.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        """
        Set the kit's status to the provided value.

        Args:
            request: Authenticated DRF Request with ``status`` in the body.
                Must be one of ``draft`` or ``published``.
            pk (UUID): Primary key of the kit.

        Returns:
            Response: Serialized updated kit (200), validation errors (400),
                or 404 if not found.
        """
        kit = get_object_or_404(InterviewKit, pk=pk, created_by=request.user)
        serializer = PublishToggleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        kit.status = serializer.validated_data['status']
        kit.save(update_fields=['status'])
        return Response(InterviewKitSerializer(kit).data)


class RegenerateSectionView(APIView):
    """
    Regenerate a single section of an existing kit without touching the rest.

    Requires authentication. Only the kit's owner can regenerate sections.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """
        Regenerate and persist one section of the specified kit.

        Args:
            request: Authenticated DRF Request with ``section_name`` in the body.
                Must be one of ``job_description``, ``scorecard``,
                ``interview_questions``, ``skills_assessment_rubric``.
            pk (UUID): Primary key of the kit.

        Returns:
            Response: JSON with ``section_name`` and regenerated ``data`` (200),
                validation errors (400), or 404 if not found.
        """
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
    """
    Match a candidate's uploaded CV PDF against a published interview kit.

    No authentication is required. The kit must be in ``published`` status.
    Uses the LangGraph two-stage pipeline: extract candidate profile, then score.
    """

    permission_classes = [AllowAny]

    def post(self, request, pk):
        """
        Extract CV text, run the CV match pipeline, and return the scored result.

        Args:
            request: DRF Request with a ``cv_file`` PDF in ``request.FILES``.
            pk (UUID): Primary key of a published interview kit.

        Returns:
            Response: CV match result dict (200), or an error detail (400/404).

        Raises:
            No exceptions are raised to the caller — errors are returned as
            400 responses with a ``detail`` field.
        """
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
        except (ValueError, Exception) as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(match_result)
