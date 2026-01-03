from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'followers_count', 'following_count')
    search_fields = ('user__username', 'user__email', 'bio')
    # Use filter_horizontal for easier management of the ManyToMany 'follows' field
    filter_horizontal = ('follows',)

    def followers_count(self, obj):
        return obj.followed_by.count()
    followers_count.short_description = 'Followers'

    def following_count(self, obj):
        return obj.follows.count()
    following_count.short_description = 'Following'