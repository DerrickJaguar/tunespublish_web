# recommendation/serializers.py

from rest_framework import serializers
from .models import Track, UserPreference, Recommendation

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'title', 'artist', 'genre', 'tempo', 'release_date']

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'track', 'score']

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['preferred_genres', 'disliked_genres']
