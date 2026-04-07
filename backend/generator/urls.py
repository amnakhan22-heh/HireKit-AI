from django.urls import path
from .views import GenerateFullKitView, InterviewKitListView, InterviewKitDetailView, RegenerateSectionView

urlpatterns = [
    path("generate/full-kit/", GenerateFullKitView.as_view(), name="generate-full-kit"),
    path("kits/", InterviewKitListView.as_view(), name="kit-list"),
    path("kits/<uuid:pk>/", InterviewKitDetailView.as_view(), name="kit-detail"),
    path("kits/<uuid:pk>/regenerate-section/", RegenerateSectionView.as_view(), name="regenerate-section"),
]
