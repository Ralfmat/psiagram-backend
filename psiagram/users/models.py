from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom user model extending AbstractUser.
    Authentication uses 'email' instead of 'username'.
    """
    email = models.EmailField(_('email address'), unique=True)
    
    # These fields are already in AbstractUser, but we make them explicit if needed
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    birth_date = models.DateField(_('birth date'), null=True, blank=True)

    # Set email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    
    # Fields required when creating a superuser (besides email and password)
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email