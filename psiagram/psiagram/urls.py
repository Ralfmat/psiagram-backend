from django.contrib import admin
from django.urls import path, include
from .views import testView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    path('api/v1/rekognition/', include('aws_rekognition.urls')),
    path('test/', testView.as_view(), name='test_view'),

    path("users/", include("users.urls")),
    path("api/posts/", include("posts.urls")),
]