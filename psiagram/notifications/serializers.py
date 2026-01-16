from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    post_image = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 
            'sender', 
            'sender_username', 
            'sender_avatar',
            'notification_type', 
            'post', 
            'post_image',
            'is_read', 
            'created_at'
        ]

    def get_sender_avatar(self, obj):
        if hasattr(obj.sender, 'profile') and obj.sender.profile.avatar:
            # Assuming you have the logic to build full URL or standard ImageField behavior
            return obj.sender.profile.avatar.url
        return None

    def get_post_image(self, obj):
        if obj.post and obj.post.image:
            return obj.post.image.url
        return None