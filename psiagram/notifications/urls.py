from django.urls import path
from .views import NotificationListView, UnreadNotificationCountView, MarkNotificationsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications-list'),
    path('unread-count/', UnreadNotificationCountView.as_view(), name='notifications-unread-count'),
    path('mark-read/', MarkNotificationsReadView.as_view(), name='notifications-mark-read'),
]