# recommendation/engine/content_based.py

from .base import BaseRecommendationEngine
from ..models import UserInteraction, Track, UserPreference, Recommendation
from django.db.models import Q, Count


class ContentBasedFilteringEngine(BaseRecommendationEngine):

    def recommend(self, user, num_recommendations=10):
        # Fetch or create user preferences
        preferences = self.get_user_preferences(user)

        # Handle the case where preferred genres might be missing or empty
        preferred_genres = preferences.preferred_genres.split(',') if preferences.preferred_genres else []

        if not preferred_genres:
            # If no preferred genres exist, return an empty queryset
            return Track.objects.none()

        # Filter tracks based on the preferred genres, ensuring no interaction has occurred
        recommended_tracks = Track.objects.filter(
            Q(genre__in=preferred_genres) & ~Q(userinteraction__user=user)
        ).distinct()[:num_recommendations]

        # Create recommendation objects
        recommendations = []
        for track in recommended_tracks:
            recommendations.append(Recommendation(user=user, track=track, score=1.0))
        Recommendation.objects.bulk_create(recommendations)

        return recommended_tracks

    def get_user_preferences(self, user):
        # Try to get user preferences; if none exist, create a default one
        try:
            return UserPreference.objects.get(user=user)
        except UserPreference.DoesNotExist:
            # Create a new preference object with empty or default values
            return UserPreference.objects.create(user=user, preferred_genres='')

    def update_preferences(self, user):
        # Get user interactions where the user liked the track
        interactions = UserInteraction.objects.filter(user=user, liked=True)

        # Count the number of likes per genre
        genre_count = interactions.values('track__genre').annotate(count=Count('track__genre')).order_by('-count')

        # Fetch or create user preferences
        preferences = self.get_user_preferences(user)

        # Update preferred genres based on interactions (only include genres with more than one like)
        preferred_genres = [item['track__genre'] for item in genre_count if item['count'] > 1]
        preferences.preferred_genres = ','.join(preferred_genres) if preferred_genres else ''
        preferences.save()
