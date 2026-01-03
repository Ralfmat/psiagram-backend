from django.conf import settings
from rest_framework import serializers
import boto3
from .models import UserProfile
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)
    s3_key = serializers.CharField(write_only=True, required=False)
    is_following = serializers.SerializerMethodField()
    username = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'avatar', 'followers_count', 'following_count', 's3_key', 'is_following', 'username']
        extra_kwargs = {
            'follows': {'read_only': True},
            'avatar': {'read_only': True}
        }
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followed_by.filter(id=request.user.profile.id).exists()
        return False

    def get_followers_count(self, obj):
        return obj.followed_by.count()

    def get_following_count(self, obj):
        return obj.follows.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.avatar:
            representation['avatar'] = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{instance.avatar}"
        return representation

    def update(self, instance, validated_data):
        s3_key = validated_data.pop('s3_key', None)
        new_username = validated_data.pop('username', None)

        if new_username and instance.user.username != new_username:
            if User.objects.filter(username=new_username).exclude(id=instance.user.id).exists():
                raise serializers.ValidationError({"username": "This username is already taken."})
            
            instance.user.username = new_username
            instance.user.save()

        if s3_key:
            # Logic to move the file from 'uploads/' to 'avatars/' on S3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION_NAME,
            )
            bucket_name = settings.AWS_S3_BUCKET_NAME

            # 1. Define new path
            filename = s3_key.split('/')[-1]
            new_key = f"avatars/{filename}"

            try:
                # 2. Copy object
                s3_client.copy_object(
                    Bucket=bucket_name,
                    CopySource={'Bucket': bucket_name, 'Key': s3_key},
                    Key=new_key
                )
                # 3. Delete original from 'uploads/'
                s3_client.delete_object(Bucket=bucket_name, Key=s3_key)

                # 4. Set the avatar field to the new path
                instance.avatar = new_key
                
            except Exception as e:
                raise serializers.ValidationError(f"Failed to process S3 file: {str(e)}")

        return super().update(instance, validated_data)


class ProfileListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users in Followers/Following lists.
    """
    username = serializers.CharField(source='user.username')
    user_id = serializers.IntegerField(source='user.id')
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'username', 'avatar', 'is_following']
        read_only_fields = fields

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if the requesting user follows the user in the list
            # 'obj' is the profile of the person in the list.
            # We check if request.user.profile.follows contains 'obj'
            try:
                return request.user.profile.follows.filter(id=obj.id).exists()
            except UserProfile.DoesNotExist:
                return False
        return False
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.avatar:
            representation['avatar'] = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{instance.avatar}"
        return representation
