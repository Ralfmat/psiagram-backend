from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Post
from .serializers import PostFeedSerializer

class FeedView(generics.ListAPIView):
    serializer_class = PostFeedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Post.objects
            .filter(verification_status=Post.VerificationStatus.APPROVED)
            .select_related("author")
            .prefetch_related("likes", "comments")
            .order_by("-created_at")
        )

class CreatePostView(generics.CreateAPIView):
    serializer_class = PostFeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)