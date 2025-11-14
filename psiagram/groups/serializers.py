from rest_framework import serializers
from.models import Group, GroupJoinRequest
from users.serializers import UserSerializer

class GroupJoinRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the GroupJoinRequest model. It shows details about the user requesting to join and the group.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = GroupJoinRequest
        fields = ['id', 'user', 'user_username', 'group', 'group_name', 'status', 'requested_at']
        extra_kwargs = {
            'user': {'read_only': True},
            'group': {'read_only': True}
        }


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the Group model. It includes details about the admin and members.
    """
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    
    members_details = UserSerializer(many=True, read_only=True, source='members')

    join_requests = GroupJoinRequestSerializer(many=True, read_only=True, source='join_requests')
    
    members_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = [
            'id', 
            'name', 
            'description', 
            'group_picture',
            'admin', 
            'admin_username',
            'members',
            'members_details',
            'members_count',
            'join_requests',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'admin': {'read_only': True},
            'members': {'write_only': True, 'required': False}
        }

    def get_members_count(self, obj):
        return obj.members.count()