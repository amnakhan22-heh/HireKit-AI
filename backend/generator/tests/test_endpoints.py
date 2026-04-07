import uuid
import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from generator.models import InterviewKit


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
def saved_kit(db):
    return InterviewKit.objects.create(
        role_title="Senior Software Engineer",
        role_description="We need a senior engineer to build APIs.",
        role_level="Senior",
        industry="Tech",
        company_size="Startup",
        remote_policy="Remote",
        generated_kit=SAMPLE_KIT,
    )


@pytest.mark.django_db
class TestGenerateFullKit:
    def test_returns_201_with_valid_description(self, client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            response = client.post(
                "/api/generate/full-kit/",
                data={"role_description": "We need a senior engineer to build scalable APIs."},
                format="json",
            )
        assert response.status_code == 201
        data = response.json()
        assert data["role_title"] == "Senior Software Engineer"
        assert "generated_kit" in data

    def test_returns_201_with_all_context_fields(self, client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            response = client.post(
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

    def test_context_fields_saved_to_database(self, client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            client.post(
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

    def test_returns_400_when_description_too_short(self, client):
        response = client.post(
            "/api/generate/full-kit/",
            data={"role_description": "Too short"},
            format="json",
        )
        assert response.status_code == 400

    def test_returns_400_when_description_missing(self, client):
        response = client.post("/api/generate/full-kit/", data={}, format="json")
        assert response.status_code == 400

    def test_returns_400_for_invalid_role_level(self, client):
        response = client.post(
            "/api/generate/full-kit/",
            data={
                "role_description": "We need a senior engineer to build scalable APIs.",
                "role_level": "Intern",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_kit_is_persisted_to_database(self, client):
        with patch("generator.views.generate_full_kit", return_value=SAMPLE_KIT):
            client.post(
                "/api/generate/full-kit/",
                data={"role_description": "We need a senior engineer to build scalable APIs."},
                format="json",
            )
        assert InterviewKit.objects.count() == 1


@pytest.mark.django_db
class TestKitList:
    def test_returns_200_and_empty_list(self, client):
        response = client.get("/api/kits/")
        assert response.status_code == 200
        assert response.json()["results"] == []

    def test_returns_saved_kits(self, client, saved_kit):
        response = client.get("/api/kits/")
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_returns_context_fields_in_list(self, client, saved_kit):
        response = client.get("/api/kits/")
        result = response.json()["results"][0]
        assert result["role_level"] == "Senior"
        assert result["industry"] == "Tech"


@pytest.mark.django_db
class TestKitDetail:
    def test_returns_200_for_existing_kit(self, client, saved_kit):
        response = client.get(f"/api/kits/{saved_kit.id}/")
        assert response.status_code == 200
        assert response.json()["id"] == str(saved_kit.id)

    def test_returns_404_for_nonexistent_kit(self, client):
        response = client.get(f"/api/kits/{uuid.uuid4()}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestKitDelete:
    def test_returns_204_on_delete(self, client, saved_kit):
        response = client.delete(f"/api/kits/{saved_kit.id}/")
        assert response.status_code == 204
        assert InterviewKit.objects.count() == 0

    def test_returns_404_when_deleting_nonexistent_kit(self, client):
        response = client.delete(f"/api/kits/{uuid.uuid4()}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestRegenerateSection:
    def test_returns_200_and_updates_section(self, client, saved_kit):
        with patch("generator.views.generate_section", return_value=SAMPLE_SCORECARD):
            response = client.post(
                f"/api/kits/{saved_kit.id}/regenerate-section/",
                data={"section_name": "scorecard"},
                format="json",
            )
        assert response.status_code == 200
        data = response.json()
        assert data["section_name"] == "scorecard"
        assert data["data"] == SAMPLE_SCORECARD

    def test_section_is_persisted_to_database(self, client, saved_kit):
        with patch("generator.views.generate_section", return_value=SAMPLE_SCORECARD):
            client.post(
                f"/api/kits/{saved_kit.id}/regenerate-section/",
                data={"section_name": "scorecard"},
                format="json",
            )
        saved_kit.refresh_from_db()
        assert saved_kit.generated_kit["scorecard"] == SAMPLE_SCORECARD

    def test_returns_400_for_invalid_section_name(self, client, saved_kit):
        response = client.post(
            f"/api/kits/{saved_kit.id}/regenerate-section/",
            data={"section_name": "invalid_section"},
            format="json",
        )
        assert response.status_code == 400

    def test_returns_404_for_nonexistent_kit(self, client):
        response = client.post(
            f"/api/kits/{uuid.uuid4()}/regenerate-section/",
            data={"section_name": "scorecard"},
            format="json",
        )
        assert response.status_code == 404
