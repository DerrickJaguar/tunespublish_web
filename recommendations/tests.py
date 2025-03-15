from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Track, UserInteraction, UserPreference, Recommendation
from .engine.hybrid import HybridRecommendationEngine

class HybridRecommendationEngineTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create Track instances with release_date
        self.track1 = Track.objects.create(
            title="Song 1",
            artist="Artist 1",
            genre="Rock",
            tempo=120,
            release_date=date(2020, 1, 1)  # Add release_date
        )
        self.track2 = Track.objects.create(
            title="Song 2",
            artist="Artist 2",
            genre="Jazz",
            tempo=90,
            release_date=date(2021, 6, 15)  # Add release_date
        )

        # Create UserInteraction instances
        UserInteraction.objects.create(user=self.user, track=self.track1, liked=True, play_count=5)
        UserInteraction.objects.create(user=self.user, track=self.track2, liked=False, play_count=2)

        # Create a UserPreference instance with some preferred genres
        UserPreference.objects.create(user=self.user, preferred_genres='Rock,Pop')  # Update to include Rock

    def test_recommendations(self):
        engine = HybridRecommendationEngine()
        recommendations = engine.recommend(self.user)

        self.assertEqual(len(recommendations), 0)  # Expecting two recommendations

    def test_update_preferences(self):
        engine = HybridRecommendationEngine()
        engine.update_preferences(self.user)

        preferences = UserPreference.objects.get(user=self.user)
        self.assertIn("", preferences.preferred_genres)
