from rest_framework import serializers
from .models import Group, GroupJoinRequest
from users.serializers import UserSerializer

class GroupMemberSerializer(UserSerializer):
    """
    Serializer for group members with extra context status.
    """
    is_following = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = list(UserSerializer.Meta.fields) + ['is_following', 'is_admin']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        try:
            if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'following'):
                return request.user.profile.following.filter(id=obj.id).exists()
        except Exception:
            pass
        return False

    def get_is_admin(self, obj):
        group = self.context.get('group')
        if group:
            return group.admins.filter(id=obj.id).exists()
        return False

class GroupJoinRequestSerializer(serializers.ModelSerializer):
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
    admins_details = UserSerializer(many=True, read_only=True, source='admins')
    members_details = serializers.SerializerMethodField()
    
    # FIXED: Removed redundant source='join_requests'
    join_requests = GroupJoinRequestSerializer(many=True, read_only=True)
    
    members_count = serializers.SerializerMethodField(read_only=True)
    is_member = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)
    has_pending_request = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = [
            'id', 
            'name', 
            'description', 
            'group_picture',
            'admins',
            'admins_details',
            'members_details',
            'members_count',
            'join_requests',
            'is_member',
            'is_admin',
            'has_pending_request',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'admins': {'read_only': True},
        }

    def get_members_details(self, obj):
        context = self.context.copy()
        context['group'] = obj
        return GroupMemberSerializer(obj.members.all(), many=True, context=context).data

    def get_members_count(self, obj):
        return obj.members.count()

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False

    def get_is_admin(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.admins.filter(id=request.user.id).exists()
        return False
    
    def get_has_pending_request(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.join_requests.filter(
                user=request.user, 
                status=GroupJoinRequest.Status.PENDING
            ).exists()
        return False