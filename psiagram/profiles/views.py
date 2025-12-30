from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import UserProfile
from .serializers import UserProfileSerializer

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or Update a user profile by the User ID (pk).
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['pk']
        return get_object_or_404(UserProfile, user__id=user_id)