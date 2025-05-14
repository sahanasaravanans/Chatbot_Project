// Chatbot functionality

document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'chat-message user-message' : 'chat-message bot-message';

        if (message.includes('\n')) {
            message.split('\n').forEach((line, index) => {
                if (index > 0) {
                    messageDiv.appendChild(document.createElement('br'));
                }
                messageDiv.appendChild(document.createTextNode(line));
            });
        } else {
            messageDiv.textContent = message;
        }

        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function addImage(imageUrl) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot-message';

        const image = document.createElement('img');
        image.src = imageUrl;
        image.alt = 'Bot response image';
        image.className = 'bot-image';

        messageDiv.appendChild(image);
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot-message typing-indicator';
        typingDiv.innerHTML = '<span>.</span><span>.</span><span>.</span>';
        typingDiv.id = 'typing-indicator';
        chatContainer.appendChild(typingDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async function sendMessage(message) {
        try {
            showTypingIndicator();

            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: message })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            removeTypingIndicator();

            if (data.text) addMessage(data.text);
            if (data.image_url) addImage(data.image_url);

        } catch (error) {
            removeTypingIndicator();
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request.', false);
        }
    }

    function handleSend() {
        const message = messageInput.value.trim();
        if (message) {
            addMessage(message, true);
            messageInput.value = '';
            sendMessage(message);
        }
    }

    sendButton.addEventListener('click', handleSend);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSend();
        }
    });

    scrollToBottom();
});
