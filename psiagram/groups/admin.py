from django.contrib import admin
from .models import Group, GroupJoinRequest

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('admins', 'members')
    list_filter = ('created_at',)

@admin.register(GroupJoinRequest)
class GroupJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('user__username', 'group__name')
    list_editable = ('status',)