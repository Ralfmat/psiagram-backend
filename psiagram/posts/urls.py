from django.urls import path
from .views import FeedView, CreatePostView, PostDetailView

urlpatterns = [
    path("feed/", FeedView.as_view(), name="posts-feed"),
    path("create/", CreatePostView.as_view(), name="post-create"),
    path("<int:pk>/", PostDetailView.as_view(), name="post-detail"),
]