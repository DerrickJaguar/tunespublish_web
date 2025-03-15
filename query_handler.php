<?php 
// query_handler.php

header('Content-Type: application/json');

// Sample responses for TunesPublish
$responses = array(
    "artist profile" => "To view or edit your artist profile, log in and navigate to the 'Artist Dashboard'.",
    "upload music" => "To upload new music, go to the 'Upload' section after logging into your artist account.",
    "album details" => "To view or edit album details, head over to the 'Albums' section in your artist dashboard.",
    "analytics" => "To view your music analytics, visit the 'Analytics' section under your artist profile.",
    "royalties" => "To view your earnings and royalties, log in and check the 'Royalties' section.",
    "promote music" => "To promote your music, visit the 'Promotions' page. You can set up campaigns to increase visibility.",
    "listener profile" => "Log in to access your listener profile and manage your playlists.",
    "create playlist" => "To create a new playlist, log in and navigate to 'My Playlists'.",
    "recommendations" => "Check out the 'Recommended for You' section to find music based on your preferences and listening history.",
    "top charts" => "Visit the 'Top Charts' page to see the most popular tracks and albums on TunesPublish.",
    "discover new music" => "To discover new music, head over to the 'Explore' section and check out trending artists and songs.",
    "withdraw earnings" => "To withdraw your earnings as an artist, log in and go to the 'Royalties' section under your artist account.",
    "song insights" => "To get insights on your songs' performance, navigate to the 'Song Insights' section in your dashboard.",
    "contact support" => "For assistance, please email support@tunespublish.com or visit the 'Help Center' on our website.",
    "login" => "Log in to your account to manage your music or explore new tracks.",
    "logout" => "To log out, click on the 'Logout' button in the account settings.",
    "update profile" => "To update your personal details or artist profile, visit the 'Profile Settings' page.",
    "view royalties" => "Check your royalties by going to the 'Royalties' section on your dashboard.",
    "track analytics" => "Access detailed analytics on your music's performance by visiting the 'Track Analytics' section.",
    "general inquiry" => "For general inquiries, please visit our FAQ section or contact our support team.",
    "edit playlist" => "To edit your playlist, visit 'My Playlists' and choose the playlist you want to modify.",
    "delete playlist" => "To delete a playlist, log in, navigate to 'My Playlists', and select the playlist you want to remove.",
    "add collaborators" => "To add collaborators to a track, go to the 'Upload' or 'Track Details' section and invite other artists to collaborate.",
    "remove track" => "To remove a track from your account, visit the 'Track Management' section in your dashboard and select the track to delete.",
    "reset password" => "To reset your password, click 'Forgot Password' on the login page and follow the instructions.",
    "change email" => "To change your account email, go to 'Account Settings' and update your email address.",
    "subscription details" => "To view your subscription details or manage your plan, visit the 'Subscription' section.",
    "listener history" => "To view your listening history, log in and visit the 'History' section under your listener profile.",
    "support ticket" => "To open a support ticket, log in and go to the 'Help Center', then describe your issue and submit it for assistance.",
    "artist biography" => "To update your artist biography, visit the 'Artist Dashboard' and click on the 'Biography' section.",
    "monetization options" => "To explore monetization options, visit the 'Monetization' page in your artist dashboard and see available features.",
    "artist collaborations" => "To collaborate with other artists, visit the 'Collaborations' section in your dashboard and send a collaboration request.",
    "submit to playlists" => "To submit your track to curated playlists, visit the 'Submit to Playlists' section in the artist dashboard.",
    "license music" => "To license your music for commercial use, visit the 'Licensing' section and submit your request.",
    "fan engagement" => "To engage with your fans, visit the 'Fan Engagement' section where you can respond to messages and see fan activity.",
);

// Capture and process user message
$message = strtolower(trim($_POST['message']));

// Default response if no match is found
$response = "I'm not sure about that. Could you please provide more details or contact our support team?";

// Convert the responses array keys into a single string
$keys = array_keys($responses);
$keysString = implode(' ', $keys);

// Check if the message contains any of the keywords
foreach ($keys as $key) {
    if (strpos($message, $key) !== false) {
        $response = $responses[$key];
        break; // Exit loop after finding the first match
    }
}

// Return the response in JSON format
echo json_encode(array("response" => $response));
?>
