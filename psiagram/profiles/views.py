from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from django.shortcuts import get_object_or_404
from .models import UserProfile
from .serializers import ProfileListSerializer, UserProfileSerializer

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or Update a user profile by the User ID (pk).
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['pk']
        return get_object_or_404(UserProfile, user__id=user_id)


class FollowToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        target_profile = get_object_or_404(UserProfile, user__id=pk)
        my_profile = request.user.profile

        if my_profile == target_profile:
            return Response({"error": "You cannot follow yourself."}, status=400)

        if my_profile.follows.filter(pk=target_profile.pk).exists():
            my_profile.follows.remove(target_profile)
            return Response({"status": "unfollowed"})
        else:
            my_profile.follows.add(target_profile)
            return Response({"status": "followed"})


class ProfileSearchView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__first_name', 'user__last_name']


class FollowersListView(generics.ListAPIView):
    serializer_class = ProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['pk']
        profile = get_object_or_404(UserProfile, user__id=user_id)
        return profile.followed_by.all()


class FollowingListView(generics.ListAPIView):
    serializer_class = ProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['pk']
        profile = get_object_or_404(UserProfile, user__id=user_id)
        return profile.follows.all()