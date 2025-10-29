from django.db import models

class UploadedImage(models.Model):
    image_file = models.ImageField(upload_to='uploads/')
    s3_key = models.CharField(max_length=255, blank=True)
    analysis_result = models.JSONField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
