document.addEventListener("DOMContentLoaded", function() {
            fetchInitialUserList();
            setupWebSocket();
});

function fetchInitialUserList() {
            fetch('/cgi-bin/user_list.cgi')
                .then(response => response.json())
                .then(data => {
                                    if (data.error) {
                                                            console.error(data.error);
                                                        } else {
                                                                                updateUserList(data);
                                                                            }
                                })
                .catch(error => console.error('Error fetching user list:', error));
}

function updateUserList(users) {
            const userListContainer = document.getElementById('user-list');
            userListContainer.innerHTML = '';

            users.forEach(user => {
                            const userElement = document.createElement('div');
                            userElement.textContent = user;
                            userElement.addEventListener('click', () => fetchAndDisplayChatHistory(user));
                            userListContainer.appendChild(userElement);
                        });
}

function fetchAndDisplayChatHistory(user) {

            fetch(`/cgi-bin/chat_history.cgi?user=${user}`)
                .then(response => response.json())
                .then(data => {
                                    if (data.error) {
                                                            console.error(data.error);
                                                        } else {
                                                                                updateChatHistory(data, user);
                                                                            }
                                })
                .catch(error => console.error('Error fetching chat history:', error));
}

function updateChatHistory(messages, user) {
            const chatHistoryContainer = document.getElementById('chat-history');
            chatHistoryContainer.innerHTML = '';
            document.getElementById('user-name').textContent = user;

            messages.forEach(message => {
                            const messageElement = document.createElement('div');
                            messageElement.textContent = `${message.sender}: ${message.message}`;
                            chatHistoryContainer.appendChild(messageElement);
                        });
}

function setupWebSocket() {
            const ws = new WebSocket('ws://localhost:3000');

            ws.onopen = function() {
                            console.log('WebSocket connection opened');
                        };

            ws.onmessage = function(event) {
                            console.log('Message from server: ', event.data);

                        };

            ws.onclose = function() {
                            console.log('WebSocket connection closed');
                        };

            document.getElementById('message-input').addEventListener('keypress', function(event) {
                            if (event.key === 'Enter') {
                                                sendMessage(ws);
                                            }
                        });
}

function sendMessage(ws) {
            const messageInput = document.getElementById('message-input');
            const message = messageInput.value;
            messageInput.value = '';

            if (ws.readyState === WebSocket.OPEN) {
                            ws.send(message);
                        }
}