from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from posts.models import Like, Comment
from profiles.models import UserProfile
from .models import Notification

@receiver(post_save, sender=Like)
def notify_on_like(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        user = instance.user

        if post.author != user:
            Notification.objects.create(
                recipient=post.author,
                sender=user,
                notification_type=Notification.NotificationType.LIKE,
                post=post
            )

@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        user = instance.author

        if post.author != user:
            Notification.objects.create(
                recipient=post.author,
                sender=user,
                notification_type=Notification.NotificationType.COMMENT,
                post=post
            )

@receiver(m2m_changed, sender=UserProfile.follows.through)
def notify_on_follow(sender, instance, action, reverse, pk_set, **kwargs):
    if action == "post_add":
        follower_user = instance.user

        for followed_profile_id in pk_set:
            followed_profile = UserProfile.objects.get(pk=followed_profile_id)
            followed_user = followed_profile.user

            if follower_user != followed_user:
                Notification.objects.create(
                    recipient=followed_user,
                    sender=follower_user,
                    notification_type=Notification.NotificationType.FOLLOW
                )