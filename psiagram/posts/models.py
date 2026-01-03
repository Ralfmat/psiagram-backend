from django.db import models
from django.conf import settings

class Post(models.Model):
    """
    Model representing a user post in the application.
    """

    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Author'
    )
    image = models.ImageField(
        upload_to='posts/%Y/%m/%d/',
        verbose_name='Post Image'
    )
    tagged_pets = models.ManyToManyField(
        'pets.PetProfile',
        blank=True,
        related_name='tagged_in_posts',
        verbose_name='Tagged Pets'
    )
    caption = models.TextField(
        blank=True,
        null=True,
        verbose_name='Caption'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.APPROVED,
        verbose_name='Verification Status'
    )
    # Field to store raw AWS Rekognition labels as JSON
    rekognition_labels = models.JSONField(
        blank=True,
        null=True,
        verbose_name='AWS Rekognition Labels'
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"
    
class Comment(models.Model):
    """
    Model representing a comment on a post.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Post'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Author'
    )
    content = models.TextField(
        verbose_name='Content'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"


class Like(models.Model):
    """
    Model representing a like on a post.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Post'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='User'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'user'],
                name='unique_like'
            )
        ]
    
    def __str__(self):
        return f"Like by {self.user.username} on {self.post.id}"
