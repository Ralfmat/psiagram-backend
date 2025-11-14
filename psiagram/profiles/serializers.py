from rest_framework import serializers
from.models import UserProfile
from users.serializers import UserSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    """
    # Nested serializer to include user details
    user = UserSerializer(read_only=True)
    
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'avatar', 'follows_count', 'followed_by_count']
        extra_kwargs = {
            # Field 'follows' is read-only because
            # because we will manage it through a separate endpoint (e.g., /profiles/1/follow/)
            'follows': {'read_only': True}
        }

    def get_followers_count(self, obj):
        return obj.followed_by.count()

    def get_following_count(self, obj):
        return obj.follows.count()