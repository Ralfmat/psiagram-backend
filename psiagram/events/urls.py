from django.urls import path
from .views import PublicEventsView, GroupEventsView, CreateEventView, EventDetailView

urlpatterns = [
    path('', PublicEventsView.as_view(), name='public-events'),
    path('create/', CreateEventView.as_view(), name='create-event'),
    path('group/<int:pk>/', GroupEventsView.as_view(), name='group-events'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
]