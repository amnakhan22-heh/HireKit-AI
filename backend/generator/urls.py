from django.urls import path
from .views import (
    GenerateFullKitView,
    InterviewKitListView,
    InterviewKitDetailView,
    PublishToggleView,
    RegenerateSectionView,
    LoginView,
    LogoutView,
    CVMatchView,
)

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("generate/full-kit/", GenerateFullKitView.as_view(), name="generate-full-kit"),
    path("kits/", InterviewKitListView.as_view(), name="kit-list"),
    path("kits/<uuid:pk>/", InterviewKitDetailView.as_view(), name="kit-detail"),
    path("kits/<uuid:pk>/publish/", PublishToggleView.as_view(), name="kit-publish"),
    path("kits/<uuid:pk>/regenerate-section/", RegenerateSectionView.as_view(), name="regenerate-section"),
    path("kits/<uuid:pk>/match-cv/", CVMatchView.as_view(), name="cv-match"),
]
