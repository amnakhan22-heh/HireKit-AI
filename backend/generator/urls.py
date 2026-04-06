from django.urls import path
from .views import GenerateFullKitView, InterviewKitListView, InterviewKitDetailView

urlpatterns = [
    path("generate/full-kit/", GenerateFullKitView.as_view(), name="generate-full-kit"),
    path("kits/", InterviewKitListView.as_view(), name="kit-list"),
    path("kits/<uuid:pk>/", InterviewKitDetailView.as_view(), name="kit-detail"),
]
