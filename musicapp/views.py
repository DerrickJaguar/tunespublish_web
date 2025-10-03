from audioop import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from authentication.forms import UserProfileForm
from authentication.models import UserProfile
from recommendations.models import Recommendation
from .forms import  SettingsForm, UploadForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import *
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Song, UserActivity



# Create your views here.
from django.db.models import Q
from recommendations.engine.hybrid import HybridRecommendationEngine

#def landing(request):
    #return render(request, 'musicapp/landing.html')
def index(request):
    user = request.user
    
    # Fetch recommended songs
    recommended_songs = generate_recommendations(user.id)
    
    # Recent songs
    recent_songs = None
    if not request.user.is_anonymous:
        recent_ids = Recent.objects.filter(user=request.user).order_by('-id')[:5].values_list('song_id', flat=True)
        recent_songs = Song.objects.filter(id__in=recent_ids)

    # Last played song
    first_time = False
    last_played_song = None
    if not request.user.is_anonymous:
        last_played_id = Recent.objects.filter(user=request.user).order_by('-id').first()
        if last_played_id:
            last_played_song = None
        else:
            first_time = True
            last_played_song = None  # Default song ID if no last played song

    # Fetch all songs
    songs = Song.objects.all()

    # Filter songs based on language
    indexpage_songs = songs.order_by('?')[:5]
    indexpage_local_songs = songs.filter(language='Local')[:5]
    indexpage_english_songs = songs.filter(language='English')[:5]

    # Handle search functionality
    query_search = False
    filtered_songs = songs
    search_query = request.GET.get('q')
    if search_query:
        filtered_songs = songs.filter(Q(name__icontains=search_query))
        query_search = True

    context = {
        'all_songs': indexpage_songs,        
        'recent_songs': recent_songs,
        'local_songs': indexpage_local_songs,
        'english_songs': indexpage_english_songs,
        'last_played': last_played_song,
        'first_time': first_time,
        'query_search': query_search,
    }
    return render(request, 'musicapp/index.html', context=context)


def local_songs(request):

    local_songs = Song.objects.filter(language='Local')

    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)

    query = request.GET.get('q')

    if query:
        local_songs = Song.objects.filter(Q(name__icontains=query)).distinct()
        context = {'local_songs': local_songs}
        return render(request, 'musicapp/local_songs.html', context)

    context = {'local_songs':local_songs,'last_played':last_played_song}
    return render(request, 'musicapp/local_songs.html',context=context)

@login_required(login_url='login')
def show_recommendations(request):
    # Assuming the user is logged in
    recommendations = Recommendation.objects.filter(user=request.user)
    return render(request, 'musicapp/recommended.html', {'recommendations': recommendations}) 

def english_songs(request):

    english_songs = Song.objects.filter(language='English')

    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)

    query = request.GET.get('q')

    if query:
        english_songs = Song.objects.filter(Q(name__icontains=query)).distinct()
        context = {'english_songs': english_songs}
        return render(request, 'musicapp/english_songs.html', context)

    context = {'english_songs':english_songs,'last_played':last_played_song}
    return render(request, 'musicapp/english_songs.html',context=context)

@login_required(login_url='login')
def play_song(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs, user=request.user).values()):
        data = Recent.objects.filter(song=songs, user=request.user)
        data.delete()
    data = Recent(song=songs, user=request.user)
    data.save()

    # Set a timer to trigger the popup after 30 seconds
    script = """
      setTimeout(function() {
        document.dispatchEvent(new CustomEvent('songPlaying'));
      }, 20000); // 30 seconds
    """
    return HttpResponse(script)

    # Redirect to the all_songs page
    return redirect('all_songs')

@login_required(login_url='login')
def play_song_index(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()
    return redirect('index')


@login_required(login_url='login')
def play_recent_song(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()
    return redirect('recent')

def fetch_songs_by_language(request, language):
    # Validate the language to ensure it's either 'Local' or 'English'
    if language not in ['Local', 'English']:
        return JsonResponse({'error': 'Invalid language'}, status=400)

    # Fetch songs that belong to the specified language
    songs = Song.objects.filter(language=language).values('id', 'name', 'album', 'language', 'song_img', 'year', 'singer', 'song_file')  # Adjust fields as necessary
    return JsonResponse(list(songs), safe=False)


def all_songs(request):
    songs = Song.objects.all()

    first_time = False
    #Last played song
    if not request.user.is_anonymous:
        last_played_list = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
        if last_played_list:
            last_played_id = last_played_list[0]['song_id']
            last_played_song = Song.objects.get(id=last_played_id)
    else:
        first_time = True
        last_played_song = Song.objects.get(id=7)

    
    # apply search filters
    qs_singers = Song.objects.values_list('singer').all()
    s_list = [s.split(',') for singer in qs_singers for s in singer]
    all_singers = sorted(list(set([s.strip() for singer in s_list for s in singer])))
    qs_languages = Song.objects.values_list('language').all()
    all_languages = sorted(list(set([l.strip() for lang in qs_languages for l in lang])))
    
    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        search_singer = request.GET.get('singers') or ''
        search_language = request.GET.get('languages') or ''
        filtered_songs = songs.filter(Q(name__icontains=search_query)).filter(Q(language__icontains=search_language)).filter(Q(singer__icontains=search_singer)).distinct()
        context = {
        'songs': filtered_songs,
        'last_played':last_played_song,
        'all_singers': all_singers,
        'all_languages': all_languages,
        'query_search': True,
        }
        return render(request, 'musicapp/all_songs.html', context)

    context = {
        'songs': songs,
        'last_played':last_played_song,
        'first_time':first_time,
        'all_singers': all_singers,
        'all_languages': all_languages,
        'query_search' : False,
        }
    return render(request, 'musicapp/all_songs.html', context=context)



def recent(request):
    
    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)

    #Display recent songs
    recent = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
    if recent and not request.user.is_anonymous :
        recent_id = [each['song_id'] for each in recent]
        recent_songs_unsorted = Song.objects.filter(id__in=recent_id,recent__user=request.user)
        recent_songs = list()
        for id in recent_id:
            recent_songs.append(recent_songs_unsorted.get(id=id))
    else:
        recent_songs = None

    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        filtered_songs = recent_songs_unsorted.filter(Q(name__icontains=search_query)).distinct()
        context = {'recent_songs': filtered_songs,'last_played':last_played_song,'query_search':True}
        return render(request, 'musicapp/recent.html', context)

    context = {'recent_songs':recent_songs,'last_played':last_played_song,'query_search':False}
    return render(request, 'musicapp/recent.html', context=context)


@login_required(login_url='login')
def detail(request, song_id):
    songs = Song.objects.filter(id=song_id).first()

    # Add data to recent database
    if list(Recent.objects.filter(song=songs, user=request.user).values()):
        data = Recent.objects.filter(song=songs, user=request.user)
        data.delete()
    data = Recent(song=songs, user=request.user)
    data.save()

    # Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)

    # Fetch playlists and favourite status
    playlists = Playlist.objects.filter(user=request.user).values('playlist_name').distinct()
    is_favourite = Favourite.objects.filter(user=request.user).filter(song=song_id).values('is_fav')

    # ✅ Fetch the next song (e.g., from the same album)
    next_song = Song.objects.filter(album=songs.album).exclude(id=songs.id).first()

    # Handle form submissions
    if request.method == "POST":
        if 'playlist' in request.POST:
            playlist_name = request.POST["playlist"]
            q = Playlist(user=request.user, song=songs, playlist_name=playlist_name)
            q.save()
            messages.success(request, "Song added to playlist!")
        elif 'add-fav' in request.POST:
            is_fav = True
            query = Favourite(user=request.user, song=songs, is_fav=is_fav)
            query.save()
            messages.success(request, "Added to favorite!")
            return redirect('detail', song_id=song_id)
        elif 'rm-fav' in request.POST:
            is_fav = True
            query = Favourite.objects.filter(user=request.user, song=songs, is_fav=is_fav)
            query.delete()
            messages.success(request, "Removed from favorite!")
            return redirect('detail', song_id=song_id)

    context = {
        'songs': songs,
        'playlists': playlists,
        'is_favourite': is_favourite,
        'last_played': last_played_song,
        'next_song': next_song,  # Pass the recommended song
    }

    return render(request, 'musicapp/detail.html', context=context)



def mymusic(request):
    return render(request, 'musicapp/mymusic.html')


def playlist(request):
    playlists = Playlist.objects.filter(user=request.user).values('playlist_name').distinct
    context = {'playlists': playlists}
    return render(request, 'musicapp/playlist.html', context=context)


def playlist_songs(request, playlist_name):
    songs = Song.objects.filter(playlist__playlist_name=playlist_name, playlist__user=request.user).distinct()

    if request.method == "POST":
        song_id = list(request.POST.keys())[1]
        playlist_song = Playlist.objects.filter(playlist_name=playlist_name, song__id=song_id, user=request.user)
        playlist_song.delete()
        messages.success(request, "Song removed from playlist!")

    context = {'playlist_name': playlist_name, 'songs': songs}

    return render(request, 'musicapp/playlist_songs.html', context=context)


def favourite(request):
    songs = Song.objects.filter(favourite__user=request.user, favourite__is_fav=True).distinct()
    print(f'songs: {songs}')
    
    if request.method == "POST":
        song_id = list(request.POST.keys())[1]
        favourite_song = Favourite.objects.filter(user=request.user, song__id=song_id, is_fav=True)
        favourite_song.delete()
        messages.success(request, "Removed from favourite!")
    context = {'songs': songs}
    return render(request, 'musicapp/favourite.html', context=context)

def generate_recommendations(user_id):
    # Example: Fetching last played or most liked songs by the user to recommend similar ones
    user_history = UserActivity.objects.filter(user_id=user_id).order_by('-timestamp')[:10]
    
    # Simplified recommendation logic: Get random songs for now, later integrate your ML model or logic
    recommendations = Song.objects.exclude(id__in=[activity.song.id for activity in user_history]).order_by('?')[:10]
    
    return recommendations



#def recommended_songs(request):
    user = request.user

    # Assuming you have some logic for recommending songs based on user's listening history, preferences, etc.
    recommended_songs = Song.objects.filter(genre__in=user.profile.favorite_genres.all())[:10]  # Example filter

    # If you have a more complex recommendation engine, call the logic here
    # recommended_songs = get_recommended_songs(user)

    return render(request, 'musicapp/recommended.html', {'recommended_songs': recommended_songs})
@login_required
def recommended(request):
    user = request.user
    recommended_songs = generate_recommendations(user)
    return render(request, 'recommended.html', {'recommended_songs': recommended_songs})

@login_required
def settings(request):
    user_profile = request.user.userprofile  # Assuming you have a OneToOneField between User and UserProfile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('index') # Redirect to a success page
        messages.success(request, "Profile successfully updated")  
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'musicapp/settings.html', {'form': form})


def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index') # Redirect to a success page
        messages.success(request, 'Song uploaded successfully!')
    else:
        form = UploadForm()
    return render(request, 'musicapp/upload.html', {'form': form})
    

def delete_file(request, pk):
    # Using get_object_or_404 to handle cases where the mp3 does not exist
    mp3 = get_object_or_404(UploadedFile, pk=pk)
    mp3.delete()
    return redirect(reverse('upload'))

responses = {
    "hello": "Hi there! How can I assist you today?",
    "hi": "Hello! What can I do for you?",
    "how are you": "I'm just a bot, but I'm here to help! How can I assist you?",
    "what is tunespublish": "TunesPublish is a music streaming platform where you can listen to your favorite tunes and discover new music.",
    "how do I sign up": "You can sign up by clicking the 'Sign Up' button on our homepage and filling out the registration form.",
    "how do I log in": "Click the 'Log In' button on the homepage and enter your credentials to access your account.",
    "forgot password": "If you've forgotten your password, click on 'Forgot Password' on the login page to reset it.",
    "change password": "To change your password, go to your account settings and select 'Change Password'.",
    "update profile": "You can update your profile information in the account settings section.",
    "contact support": "You can contact support by clicking on the 'Contact Us' page or sending an email to support@tunespublish.com.",
    "report a problem": "Please describe the problem you're facing, and we'll do our best to assist you.",
    "app not working": "Sorry to hear that. Please try restarting the app or contact support for further assistance.",
    "music not playing": "Check your internet connection and try restarting the app. If the issue persists, contact support.",
    "how to create playlist": "Go to 'Playlists' in your account, click 'Create New Playlist', and add your favorite songs.",
    "how to add songs to playlist": "Open the playlist you want to add songs to, then click 'Add Songs' and select your desired tracks.",
    "how to delete playlist": "Go to your playlist, click on the settings icon, and select 'Delete Playlist'.",
    "how to share playlist": "You can share your playlist by clicking the 'Share' button and choosing your preferred method.",
    "what is premium subscription": "Premium subscription offers ad-free listening, offline playback, and higher sound quality.",
    "how to upgrade to premium": "Visit the 'Upgrade' section in your account settings to choose a premium plan.",
    "subscription cancel": "You can cancel your subscription from the 'Subscription' section in your account settings.",
    "refund policy": "For information on refunds, please refer to our 'Refund Policy' page or contact support.",
    "music recommendations": "Based on your listening history, I can recommend some tracks or artists you might like.",
    "find a song": "Tell me the name of the song or artist you're looking for, and I'll help you find it.",
    "find an artist": "Let me know the name of the artist, and I'll find their music for you.",
    "genre recommendations": "Tell me your favorite genre, and I'll recommend some songs in that style.",
    "what is trending": "Check our 'Trending' section to see the latest popular tracks and albums.",
    "new releases": "Visit the 'New Releases' section to find the latest albums and singles.",
    "how to delete account": "To delete your account, go to account settings and select 'Delete Account'. Note that this action is irreversible.",
    "why is my account suspended": "If your account is suspended, please contact support for more details and assistance.",
    "what is a playlist": "A playlist is a collection of songs or albums that you can create and organize according to your preferences.",
    "how to listen offline": "Download your favorite songs or playlists for offline listening by clicking the 'Download' button.",
    "update app": "Make sure you have the latest version of the app installed for the best experience. Check your app store for updates.",
    "app support": "For app-related issues, please refer to our help center or contact support.",
    "how to use equalizer": "You can adjust the equalizer settings in the app's settings menu to enhance your listening experience.",
    "how to set up account": "Follow the instructions on the 'Sign Up' page to create and set up your account.",
    "how to change email": "To change your email address, go to your account settings and update your email information.",
    "what is the free trial": "Our free trial gives you access to premium features for a limited time. Sign up to start your trial.",
    "how to cancel free trial": "You can cancel your free trial from the 'Subscription' section in your account settings.",
    "how to manage subscription": "Manage your subscription from the 'Subscription' section in your account settings.",
    "how to get recommendations": "We use your listening history to provide personalized recommendations based on your taste.",
    "how to enable notifications": "Enable notifications in the app settings to stay updated on new releases and important updates.",
    "how to disable notifications": "Go to the app settings and turn off notifications if you prefer not to receive them.",
    "how to adjust settings": "Adjust your app settings by accessing the settings menu, where you can customize your preferences.",
    "how to clear cache": "To clear the cache, go to your app settings and find the 'Clear Cache' option.",
    "how to use dark mode": "Enable dark mode in the app settings to switch to a darker interface for easier viewing at night.",
    "how to contact us": "Visit our 'Contact Us' page for various ways to get in touch with our support team.",
    "how to report abuse": "If you encounter any abusive content, report it through the app's reporting feature or contact support.",
    "how to link accounts": "You can link your social media accounts through the account settings to share your activity.",
    "how to unlink accounts": "Unlink your social media accounts from the account settings if you no longer wish to connect them.",
    "how to change language": "Change the app's language from the settings menu to suit your preferred language.",
    "how to check usage": "View your app usage statistics in the 'Account' section to monitor your activity.",
    "how to update billing info": "Update your billing information in the 'Billing' section of your account settings.",
    "how to apply promo code": "Enter your promo code during checkout to apply any discounts to your subscription.",
    "how to get support": "For support, visit our 'Help Center' or contact us via the support email or phone number provided.",
    "how to edit playlist": "Edit your playlist by selecting it and making changes to the song list or playlist name.",
    "how to add friends": "Add friends by searching for their usernames and sending them a friend request.",
    "how to remove friends": "Remove friends by accessing your friends list and selecting the 'Remove' option next to their name.",
    "how to join community": "Join our community by participating in forums and following us on social media.",
    "how to follow artists": "Follow your favorite artists to get updates on their new releases and activities.",
    "how to unfollow artists": "Unfollow artists from your profile or the artist's page if you no longer wish to receive updates.",
    "how to find playlists": "Search for playlists using keywords or browse through our curated playlists.",
    "how to share music": "Share music by using the 'Share' feature to post songs or playlists on social media or via direct links.",
    "how to report issue": "Report any issues through the 'Report Issue' feature in the app or contact support directly.",
    "how to view history": "View your listening history by accessing the 'History' section in your profile.",
    "how to edit profile": "Edit your profile information through the account settings page.",
    "how to log out": "Log out from the app by selecting 'Log Out' from the account menu.",
    "how to reconnect account": "Reconnect your account by logging in again or following the account recovery steps.",
    "how to fix playback issues": "Try restarting the app or checking your internet connection. Contact support if the issue persists.",
    "how to set up family plan": "Set up a family plan from the 'Subscription' section by adding family members to your account.",
    "how to change plan": "Change your subscription plan from the 'Subscription' section in your account settings.",
    "how to get help": "Get help by visiting our help center or contacting our support team.",
    "how to use app features": "Explore our app features through the 'Help' section or user guide.",
    "how to provide feedback": "Provide feedback through the 'Feedback' feature in the app or email us directly.",
    "how to adjust volume": "Adjust the volume using the in-app controls or your device's volume settings.",
    "how to sync devices": "Sync your devices by logging into the same account on each device.",
    "how to transfer account": "Transfer your account by contacting support and following their instructions.",
    "how to upgrade app": "Upgrade the app by downloading the latest version from your app store.",
    "how to contact customer service": "Contact customer service through the 'Contact Us' page or support email.",
    "how to access premium features": "Access premium features by upgrading to a premium subscription.",
    "how to use voice commands": "Use voice commands by enabling voice control in the app settings.",
    "how to manage family account": "Manage your family account by adding or removing family members from the 'Family Plan' section.",
    "how to redeem gift card": "Redeem a gift card by entering the code in the 'Redeem Gift Card' section of your account settings.",
    "how to check remaining credits": "Check your remaining credits in the 'Account' section of the app.",
    "how to add to queue": "Add songs to your queue by selecting them and choosing 'Add to Queue'.",
    "how to view playlists": "View your playlists by accessing the 'Playlists' section in your profile.",
    "how to listen to albums": "Listen to albums by navigating to the 'Albums' section and selecting your desired album.",
    "how to manage notifications": "Manage notifications through the app settings to customize what you receive.",
    "how to enable dark mode": "Enable dark mode from the app settings for a darker interface.",
    "how to adjust playback speed": "Adjust playback speed in the app settings or playback controls.",
    "how to create a new account": "Create a new account by following the 'Sign Up' process on the homepage.",
    "how to find friends": "Find friends by searching their usernames or email addresses.",
    "how to invite friends": "Invite friends by sending them an invite link through the app.",
    "how to connect social media": "Connect your social media accounts through the account settings.",
    "how to manage connected accounts": "Manage your connected accounts from the 'Social Media' section in your profile settings.",
    "how to verify email": "Verify your email address by following the verification link sent to your inbox.",
    "how to troubleshoot issues": "Troubleshoot issues by checking our help center or contacting support.",
    "how to update app settings": "Update app settings by navigating to the settings menu within the app.",
    "how to access help center": "Access the help center by clicking on the 'Help' link in the app or website.",
    "how to get account information": "Get account information from the 'Account' section of your profile.",
    "how to set preferences": "Set your preferences through the app settings to customize your experience.",
    "how to use app offline": "Use the app offline by downloading content for offline access.",
    "how to check for updates": "Check for updates by visiting the app store and looking for the latest version.",
    "how to find new music": "Find new music by browsing the 'Discover' or 'New Releases' sections.",
    "how to follow playlists": "Follow playlists to get updates on any changes or new additions.",
    "how to unfollow playlists": "Unfollow playlists by selecting 'Unfollow' from the playlist options.",
    "how to manage account settings": "Manage your account settings from the 'Settings' menu in your profile.",
    "how to get music recommendations": "Get music recommendations based on your listening history and preferences.",
    "how to explore genres": "Explore different genres by browsing the 'Genres' section in the app.",
    "how to use search feature": "Use the search feature to find songs, albums, artists, or playlists.",
    "how to create a playlist": "Create a playlist by navigating to the 'Playlists' section and selecting 'Create New Playlist'.",
    "how to delete a song": "Delete a song from your library by selecting it and choosing 'Delete'.",
    "how to restore deleted songs": "Restore deleted songs by accessing the 'Deleted Songs' section if available.",
    "how to use the radio feature": "Use the radio feature to listen to curated stations or genres.",
    "how to access VIP features": "Access VIP features by subscribing to our premium or VIP plans.",
    "how to report technical issues": "Report technical issues through the 'Report Issue' feature or contact support.",
    "how to update billing details": "Update your billing details in the 'Billing' section of your account settings.",
    "how to get notifications about new releases": "Enable notifications for new releases in the app settings to stay updated.",
    "how to use app shortcuts": "Use app shortcuts for quick access to your favorite features or content.",
    "how to adjust equalizer settings": "Adjust the equalizer settings through the app's audio settings menu.",
    "how to customize interface": "Customize the app interface by selecting different themes or layouts in the settings.",
    "how to manage subscription plans": "Manage your subscription plans from the 'Subscription' section in your profile settings.",
    "how to find concert tickets": "Find concert tickets by checking the 'Events' or 'Concerts' section in the app.",
    "how to get artist updates": "Get updates on your favorite artists by following them and enabling notifications.",
    "how to contact account support": "Contact account support through the 'Help Center' or support email for account-related issues.",
    "how to view recent activity": "View your recent activity in the 'Activity' section of your profile.",
    "how to enable parental controls": "Enable parental controls by setting restrictions in the app's settings menu.",
    "how to access exclusive content": "Access exclusive content by subscribing to premium or special plans.",
    "how to set up family sharing": "Set up family sharing by adding family members to your plan from the 'Family Plan' section.",
    "how to redeem special offers": "Redeem special offers or discounts through the 'Offers' section in the app.",
    "how to find collaborators": "Find collaborators for music projects through the 'Collaborations' feature or community.",
    "how to create custom playlists": "Create custom playlists by selecting 'Create Playlist' and adding your preferred songs.",
    "how to add music to library": "Add music to your library by selecting 'Add to Library' from the song or album options.",
    "how to manage audio settings": "Manage your audio settings, including equalizer and volume, through the app settings menu.",
    "how to set up auto-renewal": "Set up auto-renewal for your subscription to avoid interruptions in service.",
    "how to use the search function": "Use the search function to find songs, albums, artists, or playlists by entering keywords.",
    "how to check subscription status": "Check your subscription status in the 'Subscription' section of your account settings.",
    "how to access offline music": "Access offline music by navigating to the 'Downloads' or 'Offline Music' section in the app.",
    "how to update personal information": "Update your personal information, such as name or contact details, in your profile settings.",
    "how to view account activity": "View your account activity and recent actions in the 'Activity' section.",
    "how to use music discovery features": "Use music discovery features like recommendations and curated playlists to find new music.",
    "how to manage notifications settings": "Manage your notification settings to choose what updates and alerts you receive.",
    "how to use the favorites feature": "Use the favorites feature to mark and access your favorite songs, albums, or artists quickly.",
    "how to subscribe to newsletters": "Subscribe to newsletters by entering your email address in the 'Newsletter' section of your account.",
    "how to use the playlist editor": "Use the playlist editor to reorder, add, or remove songs from your playlists.",
    "how to find specific tracks": "Find specific tracks by searching for them using the search bar or browsing through your library.",
    "how to use the radio function": "Use the radio function to listen to stations based on genres, moods, or artists.",
    "how to manage family accounts": "Manage family accounts by adding or removing members from your family plan.",
    "how to use the lyric feature": "Use the lyric feature to view song lyrics while listening to your favorite tracks.",
    "how to access customer service": "Access customer service through the 'Contact Us' page or support email.",
    "how to get music recommendations": "Get music recommendations based on your listening habits and preferences.",
    "how to change playback quality": "Change playback quality settings to adjust streaming or download quality.",
    "how to set up parental controls": "Set up parental controls to restrict content based on age or preferences.",
    "how to connect with artists": "Connect with artists through their profiles or social media links provided in the app.",
    "how to share music with friends": "Share music with friends by using the 'Share' feature or sending direct links.",
    "how to use voice search": "Use voice search to find music by speaking into the app's search bar.",
    "how to view top charts": "View top charts to see the most popular and trending songs and albums.",
    "how to redeem promotional codes": "Redeem promotional codes by entering them in the 'Promotions' section of your account.",
    "how to find similar artists": "Find similar artists by exploring recommendations based on your favorite musicians.",
    "how to check account balance": "Check your account balance or credits in the 'Account' section of the app.",
    "how to set up multi-device access": "Set up multi-device access by logging into your account on different devices.",
    "how to get exclusive discounts": "Get exclusive discounts by subscribing to special offers or promotional plans.",
    "how to use the music library": "Use the music library to browse, search, and organize your songs and albums.",
    "how to access your purchase history": "Access your purchase history in the 'Account' section to view past transactions.",
    "how to set up a new profile": "Set up a new profile by creating a new account or adding a new user to your existing account.",
    "how to use the shuffle feature": "Use the shuffle feature to play songs in random order from your playlists or library.",
    "how to create a collaborative playlist": "Create a collaborative playlist by inviting friends to add songs to it.",
    "how to download music": "Download music for offline listening by selecting 'Download' from the song or album options.",
    "how to access VIP support": "Access VIP support by contacting us through the dedicated VIP support channels.",
    "how to manage content restrictions": "Manage content restrictions by setting preferences in the parental controls section.",
    "how to get the latest updates": "Get the latest updates by subscribing to our newsletter or following us on social media.",
    "how to find album reviews": "Find album reviews by searching for them or browsing through our curated reviews section.",
    "how to connect with other users": "Connect with other users by participating in community forums or social media groups.",
    "how to use the app on different devices": "Use the app on different devices by logging in with the same account credentials.",
    "how to get help with billing": "Get help with billing issues by contacting support or checking the billing section in your account.",
    "how to view artist profiles": "View artist profiles to learn more about your favorite musicians and their discographies.",
    "how to use the music search feature": "Use the music search feature to find specific tracks, albums, or artists.",
    "how to manage music recommendations": "Manage music recommendations by updating your preferences or listening history.",
    "how to get updates on new features": "Get updates on new features by following our announcements or subscribing to our newsletter.",
    "how to find concert schedules": "Find concert schedules by checking the 'Events' or 'Concerts' section in the app.",
    "how to manage your playlist settings": "Manage your playlist settings by accessing the playlist options and adjusting preferences.",
    "how to use the sleep timer": "Use the sleep timer feature to set a time limit for playback before the app stops automatically.",
    "how to access user guides": "Access user guides through the help center or app documentation for detailed instructions.",
    "how to find community events": "Find community events by browsing the 'Events' section or joining our social media groups.",
    "how to use the crossfade feature": "Use the crossfade feature to smoothly transition between songs in your playlists.",
    "how to redeem special offers": "Redeem special offers by entering promo codes or following the offer instructions in the app.",
    "how to find music by mood": "Find music by mood by exploring curated playlists or mood-based stations.",
    "how to check for app updates": "Check for app updates by visiting your app store and downloading the latest version.",
    "how to manage offline downloads": "Manage offline downloads by accessing the 'Downloads' section and adjusting your saved content.",
    "how to create a personal playlist": "Create a personal playlist by selecting 'Create Playlist' and adding your favorite songs."
}

@login_required
@csrf_exempt
def chat_query_handler(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '').lower()

        response = "Sorry, I didn’t understand that. Can you rephrase the prompt?"
        for key in responses:
            if key in message:
                response = responses[key]
                break

        return JsonResponse({"response": response})
    return JsonResponse({"response": "Invalid request"})