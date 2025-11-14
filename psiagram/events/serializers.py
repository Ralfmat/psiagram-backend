from rest_framework import serializers
from.models import Event, EventAttendance
from users.serializers import UserSerializer
from pets.serializers import PetProfileSerializer

class EventAttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the EventAttendance model. It shows details about the user attending the event
    and the pets they are bringing along.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    pets_details = PetProfileSerializer(many=True, read_only=True, source='pets')
    
    class Meta:
        model = EventAttendance
        fields = ['id', 'user', 'user_username', 'event', 'pets', 'pets_details']
        extra_kwargs = {
            'user': {'read_only': True},  # Ustawiane w widoku
            'event': {'read_only': True}, # Ustawiane w widoku
            'pets': {'write_only': True, 'required': False}
        }


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model. It includes details about the organizer and attendees.
    """
    organizer_username = serializers.CharField(source='organizer.username', read_only=True)
    
    attendees_details = EventAttendanceSerializer(many=True, read_only=True, source='eventattendance_set')
    
    attendees_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 
            'name', 
            'description', 
            'location', 
            'start_time', 
            'end_time', 
            'organizer', 
            'organizer_username', 
            'attendees', 
            'attendees_details', 
            'attendees_count', 
            'created_at', 
            'updated_at'
        ]
        extra_kwargs = {
            'organizer': {'read_only': True},
            'attendees': {'read_only': True}
        }

    def get_attendees_count(self, obj):
        return obj.attendees.count()