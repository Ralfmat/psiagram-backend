from django.urls import path
from .views import FeedView, CreatePostView

urlpatterns = [
    path("feed/", FeedView.as_view(), name="posts-feed"),
    path("create/", CreatePostView.as_view(), name="posts-create"),
]