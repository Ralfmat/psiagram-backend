from django.contrib import admin
from .models import Event, EventAttendance

class EventAttendanceInline(admin.TabularInline):
    model = EventAttendance
    extra = 1
    autocomplete_fields = ['user']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizer', 'group', 'start_time', 'end_time', 'created_at')
    list_filter = ('start_time', 'created_at', 'group')
    search_fields = ('name', 'description', 'location', 'organizer__username', 'group__name')
    autocomplete_fields = ['organizer', 'group']
    inlines = [EventAttendanceInline]

@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'event')
    list_filter = ('event__start_time',)
    search_fields = ('user__username', 'event__name')
    autocomplete_fields = ['user', 'event']
