from django.urls import path
from .views import FollowersListView, FollowingListView, ProfileDetailView, FollowToggleView, ProfileSearchView

urlpatterns = [
    path('search/', ProfileSearchView.as_view(), name='profile-search'),
    path('<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('<int:pk>/follow/', FollowToggleView.as_view(), name='follow-toggle'),
    path('<int:pk>/followers/', FollowersListView.as_view(), name='profile-followers'),
    path('<int:pk>/following/', FollowingListView.as_view(), name='profile-following'),
]