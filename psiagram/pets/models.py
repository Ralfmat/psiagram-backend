from django.db import models
from django.conf import settings

class PetProfile(models.Model):
    """
    Model representing a pet profile associated with a user."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='pet_profiles',
        verbose_name='Owner'
    )
    name = models.CharField(max_length=100, verbose_name='Pet Name')
    breed = models.CharField(max_length=100, verbose_name='Breed')
    age = models.PositiveIntegerField(verbose_name='Age')
    profile_picture = models.ImageField(
        upload_to='pet_profiles/',
        null=True,
        blank=True,
        verbose_name='Profile Picture'
    )
    birthdate = models.DateField(null=True, blank=True, verbose_name='Birthdate')
    bio = models.TextField(blank=True, null=True, verbose_name='Biography')

    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username})"

    class Meta:
        verbose_name = "Pet Profile"
        verbose_name_plural = "Pet Profiles"
        ordering = ['name']