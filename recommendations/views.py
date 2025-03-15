from django.shortcuts import render

# Create your views here.
# recommendation/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .engine.hybrid import HybridRecommendationEngine
from .serializers import TrackSerializer, RecommendationSerializer

class TrackRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        engine = HybridRecommendationEngine()
        recommended_tracks = engine.recommend(request.user)
        serializer = TrackSerializer(recommended_tracks, many=True)
        return Response(serializer.data)

class UserPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        engine = HybridRecommendationEngine()
        preferences = engine.get_user_preferences(request.user)
        serializer = RecommendationSerializer(preferences)
        return Response(serializer.data)
#def show_recommendations(request):
    # Assuming the user is logged in
    #recommendations = Recommendation.objects.filter(user=request.user)
    #return render(request, 'musicapp/recommended.html', {'recommendations': recommendations})