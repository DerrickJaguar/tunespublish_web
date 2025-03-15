# recommendation/urls.py

from django.urls import path
from .views import TrackRecommendationsView, UserPreferencesView

urlpatterns = [
    path('recommendations/', TrackRecommendationsView.as_view(), name='track-recommendations'),
    path('preferences/', UserPreferencesView.as_view(), name='user-preferences'),
]