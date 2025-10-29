from django.urls import path
from .views import InitiateUploadView, UploadCompleteView

urlpatterns = [
    path('initiate-upload/', InitiateUploadView.as_view(), name='initiate-upload'),
    path('upload-complete/', UploadCompleteView.as_view(), name='upload-complete'),
]