document.addEventListener('DOMContentLoaded', function () {
    var currentUser = null; // To keep track of the current logged-in user
    var selectedUser = null; // To keep track of the selected user for 1-1 messaging

    var searchUserInput = document.getElementById('searchUser');
    var userList = document.getElementById('userList');
    var chatPanel = document.getElementById('chatPanel');
    var chatUserImage = document.getElementById('chatUserImage');
    var chatMessages = document.getElementById('chatMessages');
    var messageInput = document.getElementById('messageInput');
    var sendMessageBtn = document.getElementById('sendMessageBtn');

    var ws = new WebSocket('ws://localhost:3000/chat');

    // WebSocket onmessage event handler
    ws.onmessage = function (event) {
        var message = JSON.parse(event.data);
        if (message.sender_id === selectedUser.id || message.receiver_id === selectedUser.id) {
            renderMessage(message);
        }
    };

    // Function to fetch users from the server
    function fetchUsers() {
        fetch('/cgi-bin/chat_users.cgi')
            .then(response => response.json())
            .then(users => {
                renderUsers(users);
            })
            .catch(error => console.error('Error fetching users:', error));
    }

    // Function to render the list of users
    function renderUsers(users) {
        userList.innerHTML = ''; // Clear previous users
        users.forEach(user => {
            var userCard = document.createElement('div');
            userCard.classList.add('user-card');
            userCard.setAttribute('data-user-id', user.id);
            userCard.addEventListener('click', () => selectUser(user));

            var userInfo = document.createElement('div');
            userInfo.classList.add('user-info');

            var initial = document.createElement('div');
            initial.classList.add('initial');
            initial.textContent = user.name.charAt(0).toUpperCase();
            userInfo.appendChild(initial);

            var username = document.createElement('div');
            username.classList.add('username');
            username.textContent = user.name;
            userInfo.appendChild(username);

            userCard.appendChild(userInfo);
            userList.appendChild(userCard);

            user.element = userCard; // Store the DOM element reference in user object
        });
    }

    // Function to select a user and display chat panel
    function selectUser(user) {
        if (currentUser && selectedUser && selectedUser.id === user.id) {
            return; // If already selected, do nothing
        }

        selectedUser = user;

        if (currentUser && selectedUser) {
            chatPanel.style.display = 'block';

            var username = chatPanel.querySelector('.username');
            username.textContent = selectedUser.name;

            // Display chat messages
            chatMessages.innerHTML = ''; // Clear previous messages

            // Fetch chat history
            fetchChatHistory(currentUser.id, selectedUser.id);
        }
    }

    // Function to fetch chat history with selected user
    function fetchChatHistory(senderId, receiverId) {
        fetch(`/cgi-bin/chat_messages.cgi?sender_id=${senderId}&receiver_id=${receiverId}`)
            .then(response => response.json())
            .then(messages => {
                messages.forEach(message => renderMessage(message));
            })
            .catch(error => console.error('Error fetching chat history:', error));
    }

    // Function to render a message in the chat panel
    function renderMessage(message) {
        var messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        if (message.sender_id === currentUser.id) {
            messageDiv.classList.add('me');
        }

        var messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.textContent = message.content;

        var messageInfo = document.createElement('div');
        messageInfo.classList.add('message-info');
        if (message.sender_id === currentUser.id) {
            messageInfo.classList.add('me');
        }

        var usernameSpan = document.createElement('span');
        usernameSpan.classList.add('username');
        usernameSpan.textContent = message.sender_name;

        var timeSpan = document.createElement('span');
        timeSpan.classList.add('time');
        timeSpan.textContent = message.time;

        messageInfo.appendChild(usernameSpan);
        messageInfo.appendChild(timeSpan);
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageInfo);
        chatMessages.appendChild(messageDiv);

        // Scroll to the bottom of the chat messages
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to send a message to the server
    function sendToServer(senderId, receiverId, message) {
        var formData = new FormData();
        formData.append('sender_id', senderId);
        formData.append('receiver_id', receiverId);
        formData.append('message', message);

        fetch('/cgi-bin/chat_messages.cgi', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(message => {
            // Message is rendered by WebSocket callback
        })
        .catch(error => console.error('Error sending message:', error));
    }

    // Function to handle sending a message
    function sendMessage() {
        var message = messageInput.value.trim();
        if (!message) {
            return;
        }

        sendToServer(currentUser.id, selectedUser.id, message);

        // Clear the message input
        messageInput.value = '';

        // Scroll to the bottom of the chat messages
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Enable send button when message input is not empty
    messageInput.addEventListener('input', () => {
        sendMessageBtn.disabled = !messageInput.value.trim();
    });

    // Event listener for sending a message
    sendMessageBtn.addEventListener('click', sendMessage);

    // Initial fetch and render of users
    fetchUsers();
});