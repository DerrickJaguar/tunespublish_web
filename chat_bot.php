<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TunesPublish Live Chat</title>
    <style>
        /* Floating Button Styles */
        .chat-button {
            position: fixed;
            bottom: 20px;
            right: 5px;
            background-color: darkblue;
            color: white;
            border: none;
            border-radius: 50%;
            width: 70px;
            height: 70px;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            z-index: 1000;
            background-image: url("img/live.jpeg");
            background-repeat: no-repeat;
            background-size: cover;
            animation: shake 2s ease-in-out infinite;
        }
        .chat-button:hover {
            background-color: #006bbd;
        }
        .chat-button img {
            width: 55px;
            height: 55px;
        }

        /* Chat Form Styles */
        .chat-form-container {
            position: fixed;
            bottom: 0;
            right: 0;
            width: 25%;
            height: 75%;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            border-radius: 10px 10px 0 0;
            overflow: hidden;
            transform: translateY(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
            display: flex;
            flex-direction: column;
        }
        .chat-form-header {
            background-color: darkblue;
            color: white;
            padding: 1px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .chat-form-header h4 {
            margin: 0;
            flex: 1;
        }
        .chat-form-header img {
            width: 50px; /* Adjust size of the logo */
            height: auto;
            margin-left: 10px;
        }
        .chat-form-header .close-btn {
            cursor: pointer;
            font-size: 1.8em;
        }
        .chat-form-body {
            padding: 10px;
            flex: 1;
            overflow-y: auto;
        }
        .chat-form-body textarea {
            width: 100%;
            height: 60px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            resize: none;
        }
        .chat-form-msg {
            padding: 10px;
            text-align: right;
            display: flex;
            gap: 10px;
        }
        .chat-form-msg textarea {
            flex: 1;
            border-radius: 10px;
            border: 1px solid black;
        }
        .chat-form-msg button {
            background-color: #003344;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-form-msg button:hover {
            background-color: #006bbd;
        }
        /* Chat messages */
        .chat-message {
            margin-bottom: 10px;
        }
        .chat-message.bot {
            text-align: left;
        }
        .chat-message.user {
            text-align: right;
        }
        .chat-message p {
            display: inline-block;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
        .chat-message.bot p {
            background-color: #f1f1f1;
        }
        .chat-message.user p {
            background-color: #003344;
            color: white;
        }
        /* Expanded Form */
        .chat-form-container.expanded {
            transform: translateY(0);
        }
        
        /* Shaking Animation */
        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            50% { transform: translateX(0); }
            75% { transform: translateX(10px); }
            100% { transform: translateX(0); }
        }
    </style>
</head>
<body>

<div class="chat-button" onclick="toggleChatForm()">
</div>

<div class="chat-form-container" id="chatForm">
    <div class="chat-form-header">
    <img src="img/chase.jpg" alt="Logo"> 

        <h4>Live Chat Support</h4>
        <span class="close-btn" onclick="toggleChatForm()">&times;</span>
    </div>
    <div class="chat-form-body">
        <div class="chat-message bot">
            <p>Welcome to TunesPublish! How can we assist you today?</p>
        </div>
    </div>
    <div class="chat-form-msg">
        <textarea id="chatInput" placeholder="Describe your issue..."></textarea>
        <button onclick="sendChat()">Send</button>
    </div>
</div>

<script>
    function toggleChatForm() {
        var chatForm = document.getElementById('chatForm');
        chatForm.classList.toggle('expanded');
    }

    async function sendChat() {
        var chatInput = document.getElementById('chatInput');
        var message = chatInput.value.trim();
        if (message !== '') {
            var chatBody = document.querySelector('.chat-form-body');

            // Append user message
            var userMessage = document.createElement('div');
            userMessage.className = 'chat-message user';
            userMessage.innerHTML = '<p>' + message + '</p>';
            chatBody.appendChild(userMessage);

            // Scroll to the bottom
            chatBody.scrollTop = chatBody.scrollHeight;

            // Clear input
            chatInput.value = '';

            // Get response from query_handler.php
            var response = await getResponse(message);

            var botMessage = document.createElement('div');
            botMessage.className = 'chat-message bot';
            botMessage.innerHTML = '<p>' + response + '</p>';
            chatBody.appendChild(botMessage);

            // Scroll to the bottom
            chatBody.scrollTop = chatBody.scrollHeight;
        } else {
            alert('Please enter a message.');
        }
    }

    async function getResponse(message) {
        let response = '';
        await fetch('query_handler.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'message=' + encodeURIComponent(message)
        })
        .then(response => response.json())
        .then(data => {
            response = data.response;
        });
        return response;
    }
</script>

</body>
</html>
