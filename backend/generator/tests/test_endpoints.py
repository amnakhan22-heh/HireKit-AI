import uuid
import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from generator.models import InterviewKit

User = get_user_model()


SAMPLE_KIT = {
    "job_description": {
        "role_title": "Senior Software Engineer",
        "role_level": "Senior",
        "summary": "Build and maintain scalable systems.",
        "responsibilities": ["Design APIs", "Review code"],
        "required_qualifications": ["5+ years Python"],
        "preferred_qualifications": ["Experience with Django"],
        "what_we_offer": ["Remote work", "Competitive salary"],
    },
    "scorecard": {
        "dimensions": [
            {
                "name": "Technical Skills",
                "weight": "40%",
                "criteria": ["Solves problems independently"],
            }
        ]
    },
    "interview_questions": {
        "behavioral": [
            {
                "question": "Tell me about a time you led a project.",
                "what_to_listen_for": "Leadership, ownership, outcome.",
            }
        ],
        "technical": [
            {
                "question": "Explain database indexing.",
                "what_to_listen_for": "Depth of understanding, trade-offs.",
            }
        ],
    },
    "skills_assessment_rubric": {
        "skills": [
            {
                "skill": "Python",
                "levels": {
                    "below_expectations": "Struggles with basics.",
                    "meets_expectations": "Writes clean, working code.",
                    "exceeds_expectations": "Optimises and mentors others.",
                },
            }
        ]
    },
}

SAMPLE_SCORECARD = {
    "dimensions": [
        {
            "name": "Problem Solving",
            "weight": "50%",
            "criteria": ["Breaks down complex problems"],
        }
    ]
}


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def auth_client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def saved_kit(db, user):
    return InterviewKit.objects.create(
        role_title="Senior Software Engineer",
        role_description="We need a senior engineer to build APIs.",
        role_level="Senior",
        industry="Tech",
        company_size="Startup",
        remote_policy="Remote",
        generated_kit=SAMPLE_KIT,
        created_by=user,
    )


@pytest.mark.django_db
class TestGenerateFullKit:
    def test_returns_201_with_valid_description(self, auth_client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            response = auth_client.post(
                "/api/generate/full-kit/",
                data={"role_description": "We need a senior engineer to build scalable APIs."},
                format="json",
            )
        assert response.status_code == 201
        data = response.json()
        assert data["role_title"] == "Senior Software Engineer"
        assert "generated_kit" in data

    def test_returns_201_with_all_context_fields(self, auth_client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            response = auth_client.post(
                "/api/generate/full-kit/",
                data={
                    "role_description": "We need a senior engineer to build scalable APIs.",
                    "role_level": "Senior",
                    "industry": "Tech",
                    "company_size": "Startup",
                    "remote_policy": "Remote",
                },
                format="json",
            )
        assert response.status_code == 201
        data = response.json()
        assert data["role_level"] == "Senior"
        assert data["industry"] == "Tech"
        assert data["company_size"] == "Startup"
        assert data["remote_policy"] == "Remote"

    def test_context_fields_saved_to_database(self, auth_client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            auth_client.post(
                "/api/generate/full-kit/",
                data={
                    "role_description": "We need a senior engineer to build scalable APIs.",
                    "role_level": "Senior",
                    "industry": "Tech",
                    "company_size": "Enterprise",
                    "remote_policy": "Hybrid",
                },
                format="json",
            )
        kit = InterviewKit.objects.first()
        assert kit.role_level == "Senior"
        assert kit.industry == "Tech"
        assert kit.company_size == "Enterprise"
        assert kit.remote_policy == "Hybrid"

    def test_returns_401_when_unauthenticated(self, client):
        response = client.post(
            "/api/generate/full-kit/",
            data={"role_description": "We need a senior engineer to build scalable APIs."},
            format="json",
        )
        assert response.status_code == 401

    def test_returns_400_when_description_too_short(self, auth_client):
        response = auth_client.post(
            "/api/generate/full-kit/",
            data={"role_description": "Too short"},
            format="json",
        )
        assert response.status_code == 400

    def test_returns_400_when_description_missing(self, auth_client):
        response = auth_client.post("/api/generate/full-kit/", data={}, format="json")
        assert response.status_code == 400

    def test_returns_400_for_invalid_role_level(self, auth_client):
        response = auth_client.post(
            "/api/generate/full-kit/",
            data={
                "role_description": "We need a senior engineer to build scalable APIs.",
                "role_level": "Intern",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_kit_is_persisted_to_database(self, auth_client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            auth_client.post(
                "/api/generate/full-kit/",
                data={"role_description": "We need a senior engineer to build scalable APIs."},
                format="json",
            )
        assert InterviewKit.objects.count() == 1


@pytest.mark.django_db
class TestKitList:
    def test_returns_200_and_empty_list_for_unauthenticated(self, client):
        response = client.get("/api/kits/")
        assert response.status_code == 200
        assert response.json()["results"] == []

    def test_returns_200_and_empty_list_for_authenticated_user_with_no_kits(self, auth_client):
        response = auth_client.get("/api/kits/")
        assert response.status_code == 200
        assert response.json()["results"] == []

    def test_returns_saved_kits_for_owning_user(self, auth_client, saved_kit):
        response = auth_client.get("/api/kits/")
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_does_not_return_other_users_kits(self, client, db, saved_kit):
        other_user = User.objects.create_user(username="other", password="pass")
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        response = other_client.get("/api/kits/")
        assert response.json()["count"] == 0

    def test_returns_context_fields_in_list(self, auth_client, saved_kit):
        response = auth_client.get("/api/kits/")
        result = response.json()["results"][0]
        assert result["role_level"] == "Senior"
        assert result["industry"] == "Tech"


@pytest.mark.django_db
class TestKitDetail:
    def test_returns_200_for_owner(self, auth_client, saved_kit):
        response = auth_client.get(f"/api/kits/{saved_kit.id}/")
        assert response.status_code == 200
        assert response.json()["id"] == str(saved_kit.id)

    def test_returns_404_for_unauthenticated_user_on_draft_kit(self, client, saved_kit):
        # draft kits are not visible to unauthenticated users
        response = client.get(f"/api/kits/{saved_kit.id}/")
        assert response.status_code == 404

    def test_returns_404_for_nonexistent_kit(self, client):
        response = client.get(f"/api/kits/{uuid.uuid4()}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestKitDelete:
    def test_returns_204_on_delete(self, auth_client, saved_kit):
        response = auth_client.delete(f"/api/kits/{saved_kit.id}/")
        assert response.status_code == 204
        assert InterviewKit.objects.count() == 0

    def test_returns_401_when_unauthenticated(self, client, saved_kit):
        response = client.delete(f"/api/kits/{saved_kit.id}/")
        assert response.status_code == 401

    def test_returns_404_when_deleting_nonexistent_kit(self, auth_client):
        response = auth_client.delete(f"/api/kits/{uuid.uuid4()}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestRegenerateSection:
    def test_returns_200_and_updates_section(self, auth_client, saved_kit):
        with patch("generator.views.generate_section", return_value=SAMPLE_SCORECARD):
            response = auth_client.post(
                f"/api/kits/{saved_kit.id}/regenerate-section/",
                data={"section_name": "scorecard"},
                format="json",
            )
        assert response.status_code == 200
        data = response.json()
        assert data["section_name"] == "scorecard"
        assert data["data"] == SAMPLE_SCORECARD

    def test_section_is_persisted_to_database(self, auth_client, saved_kit):
        with patch("generator.views.generate_section", return_value=SAMPLE_SCORECARD):
            auth_client.post(
                f"/api/kits/{saved_kit.id}/regenerate-section/",
                data={"section_name": "scorecard"},
                format="json",
            )
        saved_kit.refresh_from_db()
        assert saved_kit.generated_kit["scorecard"] == SAMPLE_SCORECARD

    def test_returns_401_when_unauthenticated(self, client, saved_kit):
        response = client.post(
            f"/api/kits/{saved_kit.id}/regenerate-section/",
            data={"section_name": "scorecard"},
            format="json",
        )
        assert response.status_code == 401

    def test_returns_400_for_invalid_section_name(self, auth_client, saved_kit):
        response = auth_client.post(
            f"/api/kits/{saved_kit.id}/regenerate-section/",
            data={"section_name": "invalid_section"},
            format="json",
        )
        assert response.status_code == 400

    def test_returns_404_for_nonexistent_kit(self, auth_client):
        response = auth_client.post(
            f"/api/kits/{uuid.uuid4()}/regenerate-section/",
            data={"section_name": "scorecard"},
            format="json",
        )
        assert response.status_code == 404
