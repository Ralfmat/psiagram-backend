from django.conf import settings
from rest_framework import serializers
from .models import UserProfile
from users.serializers import UserSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'avatar', 'followers_count', 'following_count']
        extra_kwargs = {
            'follows': {'read_only': True}
        }

    def get_followers_count(self, obj):
        return obj.followed_by.count()

    def get_following_count(self, obj):
        return obj.follows.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert relative avatar path to full S3 URL
        if instance.avatar:
            # Reusing logic: https://{BUCKET}.s3.{REGION}.amazonaws.com/{KEY}
            representation['avatar'] = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{instance.avatar}"
        return representation