from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static
from .views import show_recommendations
from .views import fetch_songs_by_language

# Add URLConf
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:song_id>/', views.detail, name='detail'),
    path('mymusic/', views.mymusic, name='mymusic'),
    path('playlist/', views.playlist, name='playlist'),
    path('playlist/<str:playlist_name>/', views.playlist_songs, name='playlist_songs'),
    path('favourite/', views.favourite, name='favourite'),
    path('all_songs/', views.all_songs, name='all_songs'),
    path('recent/', views.recent, name='recent'),
    path('local_songs/', views.local_songs, name='local_songs'),
    path('english_songs/', views.english_songs, name='english_songs'),
    path('play/<int:song_id>/', views.play_song, name='play_song'),
    path('play_song/<int:song_id>/', views.play_song_index, name='play_song_index'),
    path('play_recent_song/<int:song_id>/', views.play_recent_song, name='play_recent_song'),
    path('settings/', views.settings, name='settings'), 
    path('upload/', views.upload, name='upload'),
    path('delete/<int:pk>/', views.delete_file, name='delete_file'),
    path('chat_query_handler/', views.chat_query_handler, name='chat_query_handler'),
    path('my-recommendations/', show_recommendations, name='my_recommendations'),
    path('fetch-songs/<str:language>/', fetch_songs_by_language, name='fetch_songs_by_language'),
    path('recommended/', views.recommended, name='recommended'), 
    
    
    
    
    
  
     

]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)