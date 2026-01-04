from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, exceptions
from .models import Event
from .serializers import EventSerializer
from groups.models import Group

class PublicEventsView(generics.ListAPIView):
    """
    Returns events that are NOT associated with any group.
    Accessible to everyone (authenticated).
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(group__isnull=True).order_by('start_time')


class GroupEventsView(generics.ListAPIView):
    """
    Returns events for a specific group.
    Only accessible if the user is a member of the group.
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['pk']
        group = get_object_or_404(Group, id=group_id)
        
        # Check membership
        if not group.members.filter(id=self.request.user.id).exists():
             raise exceptions.PermissionDenied("You must be a member to view these events.")

        return Event.objects.filter(group=group).order_by('start_time')


class CreateEventView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        group_input = serializer.validated_data.get('group')
        
        # If trying to post to a group, verify membership
        if group_input:
            if not group_input.members.filter(id=self.request.user.id).exists():
                 raise exceptions.PermissionDenied("You must be a member of this group to create an event.")
        
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveDestroyAPIView):
    """
    View to retrieve a single event or delete it.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        # Allow deletion if user is organizer OR group admin
        is_organizer = instance.organizer == self.request.user
        is_group_admin = instance.group and instance.group.admins.filter(id=self.request.user.id).exists()
        
        if not (is_organizer or is_group_admin):
             raise exceptions.PermissionDenied("You do not have permission to delete this event.")
             
        instance.delete()