from django.conf import settings
from rest_framework import serializers
from .models import Event, EventAttendance
from users.serializers import UserSerializer

def get_s3_url(file_path):
    if not file_path:
        return None
    # Check if it's already a full URL
    if str(file_path).startswith('http'):
        return str(file_path)
        
    return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{file_path}"

class EventAttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the EventAttendance model. It shows details about the user attending the event.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    
    class Meta:
        model = EventAttendance
        fields = ['id', 'user', 'user_username', 'event',]
        extra_kwargs = {
            'user': {'read_only': True},
            'event': {'read_only': True},
        }


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model. It includes details about the organizer and attendees.
    """
    organizer_username = serializers.CharField(source='organizer.username', read_only=True)
    organizer_avatar = serializers.SerializerMethodField(read_only=True)
    
    attendees_details = EventAttendanceSerializer(many=True, read_only=True, source='eventattendance_set')
    
    attendees_count = serializers.SerializerMethodField(read_only=True)
    is_attending = serializers.SerializerMethodField(read_only=True)

    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 
            'name', 
            'description', 
            'location', 
            'start_time', 
            'end_time',
            'group',
            'group_name',
            'organizer', 
            'organizer_username', 
            'organizer_avatar',
            'attendees', 
            'attendees_details', 
            'attendees_count', 
            'is_attending',
            'created_at', 
            'updated_at'
        ]
        extra_kwargs = {
            'organizer': {'read_only': True},
            'attendees': {'read_only': True}
        }

    def get_organizer_avatar(self, obj):
        if hasattr(obj.organizer, 'profile') and obj.organizer.profile.avatar:
            return get_s3_url(obj.organizer.profile.avatar)
        return None

    def get_attendees_count(self, obj):
        return obj.attendees.count()

    def get_is_attending(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attendees.filter(id=request.user.id).exists()
        return False