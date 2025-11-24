from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model (used for User Details endpoint).
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['email']