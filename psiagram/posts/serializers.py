from rest_framework import serializers
from.models import Post, Comment, Like
from pets.serializers import PetProfileSerializer
from users.serializers import UserSerializer

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
            'post': {'write_only': True}
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
    Serializer for the Post model. Includes details about the author, comments, tagged pets, and likes.
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    comments = CommentSerializer(many=True, read_only=True)
    
    tagged_pets_details = PetProfileSerializer(many=True, read_only=True, source='tagged_pets')
    
    likes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 
            'author', 
            'author_username', 
            'image', 
            'caption', 
            'created_at', 
            'updated_at',
            'tagged_pets',
            'tagged_pets_details',
            'comments',
            'likes_count',
            'verification_status',
            'rekognition_labels'
        ]
        extra_kwargs = {
            'author': {'read_only': True}, 
            'tagged_pets': {'write_only': True, 'required': False}, 
            'verification_status': {'read_only': True},
            'rekognition_labels': {'read_only': True}
        }

    def get_likes_count(self, obj):
        return obj.likes.count()