from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, decorators, exceptions
from rest_framework.response import Response
from .models import Group, GroupJoinRequest
from .serializers import GroupSerializer, GroupJoinRequestSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing groups.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned groups to a search query.
        """
        queryset = Group.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def perform_create(self, serializer):
        """
        Set the creator as an admin and member.
        """
        group = serializer.save()
        group.admins.add(self.request.user)
        group.members.add(self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Delete the group. Only allow if the user is an admin.
        """
        group = self.get_object()
        if not group.admins.filter(id=request.user.id).exists():
             return Response(
                 {'detail': 'Only admins can delete the group.'}, 
                 status=status.HTTP_403_FORBIDDEN
             )
        return super().destroy(request, *args, **kwargs)

    @decorators.action(detail=False, methods=['get'])
    def my_groups(self, request):
        """
        Return groups the current user is a member of.
        """
        groups = request.user.joined_groups.all()
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """
        Send a join request.
        """
        group = self.get_object()
        if group.members.filter(id=request.user.id).exists():
            return Response({'detail': 'Already a member.'}, status=status.HTTP_400_BAD_REQUEST)
        
        join_request, created = GroupJoinRequest.objects.get_or_create(
            user=request.user,
            group=group,
            defaults={'status': GroupJoinRequest.Status.PENDING}
        )
        
        if not created and join_request.status != GroupJoinRequest.Status.PENDING:
             join_request.status = GroupJoinRequest.Status.PENDING
             join_request.save()
             
        return Response({'detail': 'Join request sent.'}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """
        Leave the group.
        """
        group = self.get_object()
        if not group.members.filter(id=request.user.id).exists():
            return Response({'detail': 'Not a member.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent leaving if you are the last admin? (Optional logic, not requested but good practice)
        # For now, just remove them.
        group.members.remove(request.user)
        if group.admins.filter(id=request.user.id).exists():
            group.admins.remove(request.user)
            
        return Response({'detail': 'Left the group.'}, status=status.HTTP_200_OK)

    # --- Admin Actions ---

    @decorators.action(detail=True, methods=['get'])
    def requests(self, request, pk=None):
        """
        List pending join requests (Admin only).
        """
        group = self.get_object()
        if not group.admins.filter(id=request.user.id).exists():
             raise exceptions.PermissionDenied("Only admins can view requests.")
        
        requests = group.join_requests.filter(status=GroupJoinRequest.Status.PENDING)
        serializer = GroupJoinRequestSerializer(requests, many=True)
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'], url_path='handle-request')
    def handle_request(self, request, pk=None):
        """
        Approve or Reject a join request (Admin only).
        Body: { "request_id": <int>, "action": "approve" | "reject" }
        """
        group = self.get_object()
        if not group.admins.filter(id=request.user.id).exists():
             raise exceptions.PermissionDenied("Only admins can manage requests.")

        request_id = request.data.get('request_id')
        action = request.data.get('action')
        
        join_req = get_object_or_404(GroupJoinRequest, id=request_id, group=group)
        
        if action == 'approve':
            join_req.status = GroupJoinRequest.Status.APPROVED
            join_req.save()
            group.members.add(join_req.user)
            return Response({'detail': 'User approved.'})
        elif action == 'reject':
            join_req.status = GroupJoinRequest.Status.REJECTED
            join_req.save()
            return Response({'detail': 'User rejected.'})
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['post'], url_path='manage-member')
    def manage_member(self, request, pk=None):
        """
        Kick, Promote, or Demote a member (Admin only).
        Body: { "user_id": <int>, "action": "kick" | "promote" | "demote" }
        """
        group = self.get_object()
        if not group.admins.filter(id=request.user.id).exists():
             raise exceptions.PermissionDenied("Only admins can manage members.")

        target_user_id = request.data.get('user_id')
        action = request.data.get('action')
        target_user = get_object_or_404(User, id=target_user_id)
        
        # --- NEW SAFETY CHECKS ---
        if target_user.id == request.user.id:
            if action == 'kick':
                 return Response({'detail': 'You cannot kick yourself from the group.'}, status=status.HTTP_400_BAD_REQUEST)
            if action == 'demote':
                 return Response({'detail': 'You cannot demote yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        # -------------------------

        if not group.members.filter(id=target_user.id).exists():
             return Response({'detail': 'User is not in this group.'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'kick':
            group.members.remove(target_user)
            group.admins.remove(target_user)
            return Response({'detail': 'User kicked.'})
        
        elif action == 'promote':
            group.admins.add(target_user)
            return Response({'detail': 'User promoted to admin.'})
            
        elif action == 'demote':
            group.admins.remove(target_user)
            return Response({'detail': 'User demoted from admin.'})
            
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)