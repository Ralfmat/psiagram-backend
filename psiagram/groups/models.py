from django.db import models
from django.conf import settings

class Group(models.Model):
    """
    Model representing a user group in the application.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Group Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    # Changed from single ForeignKey to ManyToMany to support multiple admins
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='administered_groups',
        verbose_name='Group Admins'
    )
    
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='joined_groups',
        blank=True,
        verbose_name='Group Members'
    )
    group_picture = models.ImageField(
        upload_to='group_pictures/',
        null=True,
        blank=True,
        verbose_name='Group Picture'
    )

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        ordering = ['name']
    

    def __str__(self):
        return self.name


class GroupJoinRequest(models.Model):
    """
    Model representing a request to join a group.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
    

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_join_requests',
        verbose_name='Requesting User'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='join_requests',
        verbose_name='Target Group'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Request Status'
    )
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='Requested At')

    class Meta:
        verbose_name = "Group Join Request"
        verbose_name_plural = "Group Join Requests"
        ordering = ['-requested_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'],
                name='unique_join_request'
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.group.name} ({self.status})"