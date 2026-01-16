from django.contrib import admin
from .models import Post, Comment, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'verification_status', 'created_at')
    list_filter = ('verification_status', 'created_at')
    search_fields = ('caption', 'author__username')

admin.site.register(Comment)
admin.site.register(Like)