from django.urls import path
from .views import GoogleLogin

urlpatterns = [
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
]