const socket = io(); // Connect to the Socket.IO server

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const threadId = chatMessages.dataset.threadId;

// Send a message
sendBtn.addEventListener('click', () => {
  const message = messageInput.value.trim();
  if (message) {
    socket.emit('send_dm', { thread_id: threadId, text: message });
    messageInput.value = ''; // Clear the input
  }
});

// Receive a new message
socket.on('new_dm', (data) => {
  if (data.thread_id === threadId) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', data.sender === currentUser ? 'sent' : 'received');
    messageDiv.innerHTML = `
      <div class="message-content">${data.content}</div>
      <div class="message-meta">
        <span class="message-time">${new Date(data.created_at).toLocaleTimeString()}</span>
      </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
  }
});