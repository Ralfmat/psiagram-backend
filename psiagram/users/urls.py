from django.urls import path, include
from .views import GoogleLogin
from . import views


urlpatterns = [
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('auth/', include('dj_rest_auth.urls')),  
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    # Test purposes
    path("ping/", views.ping, name="users-ping"),

    path("me/", views.me, name="users-me"),
]