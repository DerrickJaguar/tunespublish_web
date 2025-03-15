# recommendation/engine/base.py

from abc import ABC, abstractmethod

class BaseRecommendationEngine(ABC):

    @abstractmethod
    def recommend(self, user, num_recommendations=10):
        pass

    @abstractmethod
    def update_preferences(self, user):
        pass
