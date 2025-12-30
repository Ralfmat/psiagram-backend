from django.urls import path
from .views import FeedView, CreatePostView, PostDetailView, UserPostsView

urlpatterns = [
    path("feed/", FeedView.as_view(), name="posts-feed"),
    path("create/", CreatePostView.as_view(), name="post-create"),
    path("<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("user/<int:pk>/", UserPostsView.as_view(), name="user-posts")
]