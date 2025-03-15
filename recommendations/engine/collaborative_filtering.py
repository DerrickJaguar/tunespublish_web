# recommendation/engine/collaborative_filtering.py

from .base import BaseRecommendationEngine
from ..models import UserInteraction, Track, Recommendation
from django.db.models import Count

class CollaborativeFilteringEngine(BaseRecommendationEngine):

    def recommend(self, user, num_recommendations=10):
        # Find users who have interacted with the same tracks as the current user
        similar_users = UserInteraction.objects.filter(
            track__userinteraction__user=user  # Tracks interacted by the current user
        ).exclude(
            user=user  # Exclude the current user
        ).values(
            'user'  # Group by users
        ).annotate(
            similarity=Count('track')  # Calculate similarity based on common tracks
        ).order_by('-similarity')  # Order by most similar users first

        # Extract similar user IDs
        similar_user_ids = [u['user'] for u in similar_users]

        if not similar_user_ids:
            # If no similar users, return an empty queryset
            return Track.objects.none()

    # Recommend tracks that similar users have interacted with, excluding tracks the current user has already interacted with
        recommended_tracks = Track.objects.filter(
            userinteraction__user__in=similar_user_ids  # Tracks by similar users
        ).exclude(
            userinteraction__user=user  # Exclude tracks already seen by the current user
        ).distinct()[:num_recommendations]  # Limit the results

        # Prepare recommendations to save in bulk
        recommendations = []
        for track in recommended_tracks:
            recommendations.append(Recommendation(user=user, track=track, score=1.0))
        Recommendation.objects.bulk_create(recommendations)

        return recommended_tracks

    def update_preferences(self, user):
        # Placeholder method, not implemented for collaborative filtering
        pass
