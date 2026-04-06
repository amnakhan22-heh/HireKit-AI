import json
import uuid
import pytest
from unittest.mock import patch
from django.urls import reverse
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


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def saved_kit(db):
    return InterviewKit.objects.create(
        role_title="Senior Software Engineer",
        role_description="We need a senior engineer to build APIs.",
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
