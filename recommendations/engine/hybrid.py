# recommendation/engine/hybrid.py

from .collaborative_filtering import CollaborativeFilteringEngine
from .content_based import ContentBasedFilteringEngine
from ..models import Recommendation, Track


class HybridRecommendationEngine:

    def __init__(self):
        self.collaborative_engine = CollaborativeFilteringEngine()
        self.content_based_engine = ContentBasedFilteringEngine()

    def recommend(self, user, num_recommendations=10):
        collaborative_recommendations = self.collaborative_engine.recommend(user, num_recommendations)
        content_based_recommendations = self.content_based_engine.recommend(user, num_recommendations)

        if collaborative_recommendations is None:
            collaborative_recommendations = Track.objects.none()
        if content_based_recommendations is None:
            content_based_recommendations = Track.objects.none()

        return collaborative_recommendations | content_based_recommendations

    def update_preferences(self, user):
        self.collaborative_engine.update_preferences(user)
        self.content_based_engine.update_preferences(user)

