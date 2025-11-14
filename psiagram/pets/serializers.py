from rest_framework import serializers
from.models import PetProfile

class PetProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the PetProfile model.
    """
    # Instead of just owner ID, include owner's username
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = PetProfile
        fields = [
            'id', 
            'owner', 
            'owner_username', 
            'name', 
            'breed', 
            'age', 
            'profile_picture', 
            'birthdate', 
            'bio'
        ]
        extra_kwargs = {
            # 'owner' is write-only to allow setting it during creation
            'owner': {'write_only': True} 
        }