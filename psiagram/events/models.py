from django.db import models
from django.conf import settings

class Event(models.Model):
    """
    Model representing an event in the application.
    """
    name = models.CharField(max_length=200, verbose_name="Event Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    location = models.CharField(max_length=300, blank=True, null=True, verbose_name="Location")
    start_time = models.DateTimeField(verbose_name="Start Time")
    end_time = models.DateTimeField(verbose_name="End Time")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='Organizer'
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='EventAttendance',
        related_name='joined_events',
        blank=True,
        verbose_name='Attendees'
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['start_time']

    
    def __str__(self):
        return self.name
    

class EventAttendance(models.Model):
    """
    Model representing attendance of a user to an event.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Attending User'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='Event'
    )
    pets = models.ManyToManyField(
        'pets.PetProfile',
        blank=True,
        verbose_name='Attending Pets'
    )

    class Meta:
        verbose_name = "Event Attendance"
        verbose_name_plural = "Event Attendances"
        ordering = ['event', 'user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_event_attendance'
            )
        ]
    

    def __str__(self):
        pet_count = self.pets.count()
        pet_info = f" with {pet_count} pets" if pet_count > 0 else " (without pets)"
        return f"{self.user.username} - {self.event.name}{pet_info}"
