from django.utils import timezone
import boto3
from django.conf import settings
from rest_framework import serializers
from .models import Post, Comment, Like
from users.serializers import UserSerializer
from groups.models import Group


def get_s3_url(file_path):
    if not file_path:
        return None
    # Check if it's already a full URL (in case we change logic later)
    if str(file_path).startswith('http'):
        return str(file_path)
        
    return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{file_path}"


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username', 'content', 'created_at']
        extra_kwargs = {
            'author': {'read_only': True},
            'post': {'read_only': True}
        }


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Like model.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'user_username', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True},
            'post': {'write_only': True}
        }


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model. Includes details about the author, comments, and likes.
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 
            'author', 
            'author_username',
            'group',
            'group_name',
            'image', 
            'caption', 
            'created_at', 
            'updated_at',
            'comments',
            'likes_count',
            'is_liked',
            'verification_status',
            'rekognition_labels',
            'author_avatar',
        ]
        extra_kwargs = {
            'author': {'read_only': True}, 
            'verification_status': {'read_only': True},
            'rekognition_labels': {'read_only': True}
        }

    def get_author_avatar(self, obj):
        if hasattr(obj.author, 'profile') and obj.author.profile.avatar:
            return get_s3_url(obj.author.profile.avatar)
        return None

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert relative image path to full S3 URL
        if instance.image:
            representation['image'] = get_s3_url(instance.image)
        return representation


class PostFeedSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    s3_key = serializers.CharField(write_only=True, required=False)
    is_liked = serializers.SerializerMethodField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_username",
            'author_avatar',
            "group",
            "group_name",
            "image",
            "caption",
            "created_at",
            "likes_count",
            "comments_count",
            "s3_key",
            "is_liked",
        ]
        extra_kwargs = {
            'image': {'required': False}
        }

    def get_author_avatar(self, obj):
        if hasattr(obj.author, 'profile') and obj.author.profile.avatar:
            return get_s3_url(obj.author.profile.avatar)
        return None

    def validate(self, attrs):
        if not attrs.get('image') and not attrs.get('s3_key'):
            raise serializers.ValidationError("Must provide either an image file or an s3_key.")
        return attrs

    def create(self, validated_data):
        s3_key = validated_data.pop('s3_key', None)

        if s3_key:
            # Logic to move the file from 'uploads/' to 'posts/' on S3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION_NAME,
            )
            bucket_name = settings.AWS_S3_BUCKET_NAME

            # 1. Define new path (mimicking upload_to='posts/%Y/%m/%d/')
            filename = s3_key.split('/')[-1]
            date_path = timezone.now().strftime('posts/%Y/%m/%d')
            new_key = f"{date_path}/{filename}"

            try:
                # 2. Copy object
                s3_client.copy_object(
                    Bucket=bucket_name,
                    CopySource={'Bucket': bucket_name, 'Key': s3_key},
                    Key=new_key
                )
                # 3. Delete original from 'uploads/'
                s3_client.delete_object(Bucket=bucket_name, Key=s3_key)

                # 4. Set the image field to the new path
                validated_data['image'] = new_key
                
            except Exception as e:
                raise serializers.ValidationError(f"Failed to process S3 file: {str(e)}")

        return super().create(validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert relative image path to full S3 URL
        if instance.image:
             representation['image'] = get_s3_url(instance.image)
        return representation
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
