from django.conf import settings
from rest_framework import serializers
import boto3
from .models import UserProfile
from users.serializers import UserSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)
    s3_key = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'avatar', 'followers_count', 'following_count', 's3_key']
        extra_kwargs = {
            'follows': {'read_only': True},
            'avatar': {'read_only': True}
        }

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