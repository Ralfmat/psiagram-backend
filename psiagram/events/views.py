from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, permissions, exceptions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from .models import Event, EventAttendance
from .serializers import EventSerializer
from groups.models import Group

# --- Pagination Classes ---

class EventFeedPagination(CursorPagination):
    page_size = 10
    ordering = '-created_at'
    cursor_query_param = 'cursor'

class EventListPagination(CursorPagination):
    page_size = 10
    ordering = 'start_time'
    cursor_query_param = 'cursor'


# --- Views ---

class PublicEventsView(generics.ListAPIView):
    """
    Returns events that are NOT associated with any group.
    Accessible to everyone (authenticated).
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EventListPagination

    def get_queryset(self):
        return Event.objects.filter(group__isnull=True).order_by('start_time')


class EventFeedView(generics.ListAPIView):
    """
    Returns a feed of events visible to the user:
    1. Public events (no group)
    2. Events from groups the user is a member of
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EventFeedPagination

    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(
            Q(group__isnull=True) | 
            Q(group__members=user)
        ).distinct().order_by('-created_at')


class GroupEventsView(generics.ListAPIView):
    """
    Returns events for a specific group.
    Only accessible if the user is a member of the group.
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EventListPagination

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


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a single event.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        
        # For write methods (DELETE, PUT, PATCH), check custom permissions
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            is_organizer = obj.organizer == request.user
            # Group admins can also manage events
            is_group_admin = obj.group and obj.group.admins.filter(id=request.user.id).exists()
            
            if not (is_organizer or is_group_admin):
                raise exceptions.PermissionDenied("You do not have permission to modify this event.")

    def perform_destroy(self, instance):
        # Actual deletion logic
        instance.delete()


class JoinEventView(APIView):
    """
    Toggle attendance for an event.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        
        # Check if user is already attending
        attendance, created = EventAttendance.objects.get_or_create(
            user=request.user,
            event=event
        )
        
        if not created:
            # User exists in attendance -> Remove (Leave)
            attendance.delete()
            return Response({'status': 'left', 'is_attending': False}, status=status.HTTP_200_OK)
        
        # Created -> Join
        return Response({'status': 'joined', 'is_attending': True}, status=status.HTTP_201_CREATED)