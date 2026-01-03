from django.shortcuts import render, get_object_or_404
from django.db.models import Q 
from profiles.models import UserProfile
from profiles.serializers import ProfileListSerializer
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from .models import Post, Like
from .serializers import PostFeedSerializer, PostSerializer, CommentSerializer

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


class UserPostsView(generics.ListAPIView):
    serializer_class = PostFeedSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FeedPagination

    def get_queryset(self):
        # Fetch posts for a specific user ID passed in the URL
        user_id = self.kwargs['pk']
        return Post.objects.filter(
            author__id=user_id,
            verification_status=Post.VerificationStatus.APPROVED
        ).order_by('-created_at')


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


class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            # User already liked this post, so we remove the like
            like.delete()
            return Response({'status': 'unliked', 'likes_count': post.likes.count()}, status=status.HTTP_200_OK)
        
        # User hasn't liked it yet, created new like
        return Response({'status': 'liked', 'likes_count': post.likes.count()}, status=status.HTTP_201_CREATED)


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)


class PostLikesListView(generics.ListAPIView):
    serializer_class = ProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return UserProfile.objects.filter(user__likes__post_id=post_id)