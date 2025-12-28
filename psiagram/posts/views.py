from django.shortcuts import render
from django.db.models import Q 
from rest_framework import generics, permissions
from rest_framework.pagination import CursorPagination
from .models import Post
from .serializers import PostFeedSerializer, PostSerializer

# 2. Define how the pagination works
class FeedPagination(CursorPagination):
    page_size = 5
    ordering = '-created_at'
    cursor_query_param = 'cursor'


class FeedView(generics.ListAPIView):
    serializer_class = PostFeedSerializer
    permission_classes = [permissions.IsAuthenticated] 
    pagination_class = FeedPagination 

    def get_queryset(self):
        # the "Feed Logic" - who do we want to see?
        user = self.request.user
        
        # Get the profiles the current user follows
        # (We use the 'follows' ManyToMany field from your UserProfile model)
        following_profiles = user.profile.follows.all()

        return (
            Post.objects
            # Filter A: Only Approved posts
            .filter(verification_status=Post.VerificationStatus.APPROVED)
            # Filter B: Posts by authors I follow OR my own posts
            .filter(
                Q(author__profile__in=following_profiles) | 
                Q(author=user)
            )
            # Optimization: Load author and related data in one go
            .select_related("author")
            .prefetch_related("likes", "comments")
            # Order matches our pagination ordering
            .order_by("-created_at")
        )

class CreatePostView(generics.CreateAPIView):
    serializer_class = PostFeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveAPIView):
    """
    View to retrieve a single post by its ID.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]