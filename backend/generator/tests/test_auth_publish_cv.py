"""
Tests for auth endpoints, publish toggle, CV match, model behaviour,
and serializer validation — areas not covered in test_endpoints.py.

All OpenAI / service calls are mocked — no real API calls are made.
"""
import io
import uuid
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from generator.models import InterviewKit

User = get_user_model()

SAMPLE_KIT = {
    "job_description": {
        "role_title": "Senior Python Developer",
        "summary": "Build scalable backend systems.",
        "responsibilities": ["Design APIs"],
        "required_qualifications": ["5+ years Python"],
        "preferred_qualifications": ["Django"],
        "what_we_offer": ["Remote work"],
    },
    "scorecard": {"dimensions": [{"name": "Python", "weight": "40%", "criteria": ["Writes clean code"]}]},
    "interview_questions": {
        "behavioral": [{"question": "Tell me about a conflict.", "what_to_listen_for": "Empathy."}],
        "technical": [{"question": "Explain the GIL.", "what_to_listen_for": "Depth."}],
    },
    "skills_assessment_rubric": {
        "skills": [
            {
                "skill": "Python",
                "levels": {
                    "below_expectations": "Struggles.",
                    "meets_expectations": "Solid.",
                    "exceeds_expectations": "Expert.",
                },
            }
        ]
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db):
    return User.objects.create_user(username="manager", password="pass1234")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", password="pass1234")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def token_client(user):
    """Client authenticated via token header (used for logout tests)."""
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def draft_kit(db, user):
    return InterviewKit.objects.create(
        role_title="Senior Python Developer",
        role_description="We need a senior Python developer for our platform team.",
        role_level="Senior",
        industry="Tech",
        company_size="Startup",
        remote_policy="Remote",
        generated_kit=SAMPLE_KIT,
        status="draft",
        created_by=user,
    )


@pytest.fixture
def published_kit(db, user):
    return InterviewKit.objects.create(
        role_title="Junior Designer",
        role_description="Looking for a junior UI/UX designer to join our creative team.",
        role_level="Junior",
        industry="Tech",
        company_size="Mid-size",
        remote_policy="Hybrid",
        generated_kit=SAMPLE_KIT,
        status="published",
        created_by=user,
    )


# ---------------------------------------------------------------------------
# Auth: Login
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLogin:
    def test_valid_credentials_return_token(self, user):
        client = APIClient()
        response = client.post("/api/auth/login/", {"username": "manager", "password": "pass1234"})
        assert response.status_code == 200
        assert "token" in response.data
        assert response.data["username"] == "manager"

    def test_wrong_password_returns_400(self, user):
        client = APIClient()
        response = client.post("/api/auth/login/", {"username": "manager", "password": "wrong"})
        assert response.status_code == 400
        assert "detail" in response.data

    def test_missing_fields_returns_400(self):
        client = APIClient()
        response = client.post("/api/auth/login/", {})
        assert response.status_code == 400

    def test_nonexistent_user_returns_400(self):
        client = APIClient()
        response = client.post("/api/auth/login/", {"username": "ghost", "password": "x"})
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Auth: Logout
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLogout:
    def test_authenticated_user_can_logout(self, token_client):
        response = token_client.post("/api/auth/logout/")
        assert response.status_code == 204

    def test_token_is_deleted_after_logout(self, user, token_client):
        token_client.post("/api/auth/logout/")
        assert not Token.objects.filter(user=user).exists()

    def test_unauthenticated_user_cannot_logout(self):
        client = APIClient()
        response = client.post("/api/auth/logout/")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Kit detail: PATCH
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestKitPatch:
    def test_owner_can_update_role_title(self, auth_client, draft_kit):
        response = auth_client.patch(f"/api/kits/{draft_kit.id}/", {"role_title": "Updated Title"})
        assert response.status_code == 200
        draft_kit.refresh_from_db()
        assert draft_kit.role_title == "Updated Title"

    def test_owner_can_update_role_description(self, auth_client, draft_kit):
        response = auth_client.patch(
            f"/api/kits/{draft_kit.id}/", {"role_description": "A fully updated role description here."}
        )
        assert response.status_code == 200
        draft_kit.refresh_from_db()
        assert draft_kit.role_description == "A fully updated role description here."

    def test_unauthenticated_cannot_patch(self, draft_kit):
        client = APIClient()
        response = client.patch(f"/api/kits/{draft_kit.id}/", {"role_title": "Hacked"})
        assert response.status_code == 401

    def test_non_owner_cannot_patch(self, other_user, draft_kit):
        client = APIClient()
        client.force_authenticate(user=other_user)
        response = client.patch(f"/api/kits/{draft_kit.id}/", {"role_title": "Hacked"})
        assert response.status_code == 404

    def test_patch_nonexistent_kit_returns_404(self, auth_client):
        response = auth_client.patch(f"/api/kits/{uuid.uuid4()}/", {"role_title": "X"})
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Publish toggle
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPublishToggle:
    def test_owner_can_publish_draft(self, auth_client, draft_kit):
        response = auth_client.patch(f"/api/kits/{draft_kit.id}/publish/", {"status": "published"})
        assert response.status_code == 200
        draft_kit.refresh_from_db()
        assert draft_kit.status == "published"

    def test_owner_can_unpublish(self, auth_client, published_kit):
        response = auth_client.patch(f"/api/kits/{published_kit.id}/publish/", {"status": "draft"})
        assert response.status_code == 200
        published_kit.refresh_from_db()
        assert published_kit.status == "draft"

    def test_invalid_status_value_returns_400(self, auth_client, draft_kit):
        response = auth_client.patch(f"/api/kits/{draft_kit.id}/publish/", {"status": "archived"})
        assert response.status_code == 400

    def test_missing_status_returns_400(self, auth_client, draft_kit):
        response = auth_client.patch(f"/api/kits/{draft_kit.id}/publish/", {})
        assert response.status_code == 400

    def test_unauthenticated_cannot_toggle(self, draft_kit):
        client = APIClient()
        response = client.patch(f"/api/kits/{draft_kit.id}/publish/", {"status": "published"})
        assert response.status_code == 401

    def test_non_owner_cannot_toggle(self, other_user, draft_kit):
        client = APIClient()
        client.force_authenticate(user=other_user)
        response = client.patch(f"/api/kits/{draft_kit.id}/publish/", {"status": "published"})
        assert response.status_code == 404

    def test_response_contains_updated_status(self, auth_client, draft_kit):
        response = auth_client.patch(f"/api/kits/{draft_kit.id}/publish/", {"status": "published"})
        assert response.data["status"] == "published"


# ---------------------------------------------------------------------------
# CV match
# ---------------------------------------------------------------------------


def _make_fake_pdf():
    buf = io.BytesIO(b"%PDF-1.4 fake pdf content")
    buf.name = "cv.pdf"
    return buf


@pytest.mark.django_db
class TestCVMatch:
    @patch("generator.views.match_cv_to_role", return_value={"score": 82, "summary": "Strong match"})
    @patch("generator.views.extract_text_from_pdf", return_value="Experienced Python developer.")
    def test_valid_cv_against_published_kit_returns_200(self, mock_extract, mock_match, published_kit):
        client = APIClient()
        response = client.post(
            f"/api/kits/{published_kit.id}/match-cv/",
            {"cv_file": _make_fake_pdf()},
            format="multipart",
        )
        assert response.status_code == 200
        assert response.data["score"] == 82

    def test_cv_match_against_draft_kit_returns_404(self, draft_kit):
        client = APIClient()
        response = client.post(
            f"/api/kits/{draft_kit.id}/match-cv/",
            {"cv_file": _make_fake_pdf()},
            format="multipart",
        )
        assert response.status_code == 404

    def test_missing_cv_file_returns_400(self, published_kit):
        client = APIClient()
        response = client.post(f"/api/kits/{published_kit.id}/match-cv/", {})
        assert response.status_code == 400
        assert "cv_file" in response.data["detail"]

    @patch("generator.views.extract_text_from_pdf", side_effect=ValueError("Cannot parse PDF"))
    def test_unparseable_pdf_returns_400(self, mock_extract, published_kit):
        client = APIClient()
        response = client.post(
            f"/api/kits/{published_kit.id}/match-cv/",
            {"cv_file": _make_fake_pdf()},
            format="multipart",
        )
        assert response.status_code == 400
        assert "Cannot parse PDF" in response.data["detail"]

    @patch("generator.views.match_cv_to_role", side_effect=ValueError("Service failure"))
    @patch("generator.views.extract_text_from_pdf", return_value="CV text here.")
    def test_service_error_returns_400(self, mock_extract, mock_match, published_kit):
        client = APIClient()
        response = client.post(
            f"/api/kits/{published_kit.id}/match-cv/",
            {"cv_file": _make_fake_pdf()},
            format="multipart",
        )
        assert response.status_code == 400

    def test_cv_match_on_nonexistent_kit_returns_404(self):
        client = APIClient()
        response = client.post(
            f"/api/kits/{uuid.uuid4()}/match-cv/",
            {"cv_file": _make_fake_pdf()},
            format="multipart",
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestInterviewKitModel:
    def test_str_contains_title_and_id(self, draft_kit):
        assert "Senior Python Developer" in str(draft_kit)
        assert str(draft_kit.id) in str(draft_kit)

    def test_default_status_is_draft(self, user):
        kit = InterviewKit.objects.create(
            role_title="Test Role",
            role_description="A minimal test role description.",
            generated_kit=SAMPLE_KIT,
            created_by=user,
        )
        assert kit.status == "draft"

    def test_id_is_uuid(self, draft_kit):
        assert isinstance(draft_kit.id, uuid.UUID)

    def test_kits_ordered_newest_first(self, user):
        kit1 = InterviewKit.objects.create(
            role_title="First",
            role_description="First role description text.",
            generated_kit=SAMPLE_KIT,
            created_by=user,
        )
        kit2 = InterviewKit.objects.create(
            role_title="Second",
            role_description="Second role description text.",
            generated_kit=SAMPLE_KIT,
            created_by=user,
        )
        kits = list(InterviewKit.objects.all())
        assert kits[0].id == kit2.id
        assert kits[1].id == kit1.id

    def test_kit_deleted_when_user_is_deleted(self, user, draft_kit):
        user.delete()
        assert not InterviewKit.objects.filter(pk=draft_kit.id).exists()


# ---------------------------------------------------------------------------
# Serializer validation (tested via the API)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCreateSerializerValidation:
    def test_description_at_exact_min_length_passes(self, auth_client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            response = auth_client.post(
                "/api/generate/full-kit/",
                {"role_description": "x" * 20},
                format="json",
            )
        assert response.status_code == 201

    def test_description_one_under_min_fails(self, auth_client):
        response = auth_client.post(
            "/api/generate/full-kit/",
            {"role_description": "x" * 19},
            format="json",
        )
        assert response.status_code == 400

    def test_description_at_exact_max_length_passes(self, auth_client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            response = auth_client.post(
                "/api/generate/full-kit/",
                {"role_description": "x" * 5000},
                format="json",
            )
        assert response.status_code == 201

    def test_description_one_over_max_fails(self, auth_client):
        response = auth_client.post(
            "/api/generate/full-kit/",
            {"role_description": "x" * 5001},
            format="json",
        )
        assert response.status_code == 400

    def test_all_valid_role_levels_accepted(self, auth_client):
        for level in ["Junior", "Mid-level", "Senior", "Lead"]:
            with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
                response = auth_client.post(
                    "/api/generate/full-kit/",
                    {"role_description": "x" * 20, "role_level": level},
                    format="json",
                )
            assert response.status_code == 201, f"Failed for role_level: {level}"

    def test_all_valid_industries_accepted(self, auth_client):
        for industry in ["Tech", "Finance", "Healthcare", "Marketing", "Operations", "Other"]:
            with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
                response = auth_client.post(
                    "/api/generate/full-kit/",
                    {"role_description": "x" * 20, "industry": industry},
                    format="json",
                )
            assert response.status_code == 201, f"Failed for industry: {industry}"

    def test_invalid_company_size_fails(self, auth_client):
        response = auth_client.post(
            "/api/generate/full-kit/",
            {"role_description": "x" * 20, "company_size": "Huge Corp"},
            format="json",
        )
        assert response.status_code == 400

    def test_invalid_remote_policy_fails(self, auth_client):
        response = auth_client.post(
            "/api/generate/full-kit/",
            {"role_description": "x" * 20, "remote_policy": "Occasionally"},
            format="json",
        )
        assert response.status_code == 400
