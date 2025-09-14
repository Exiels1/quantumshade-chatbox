const socket = io(); // Connect to the Socket.IO server

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const threadId = chatMessages.dataset.threadId;

// These should be injected from Flask into your template
// Example in Jinja: <script>window.CURRENT_USER_ID={{ current_user.id }};</script>
const currentUserId = window.CURRENT_USER_ID;

// Helper to append message
function appendMessage(data) {
  const isMe = data.sender_id === currentUserId;

  const wrapper = document.createElement('div');
  wrapper.classList.add('message', isMe ? 'sent' : 'received');

  wrapper.innerHTML = `
    <img src="${data.sender_avatar}" class="msg-avatar">
    <div class="bubble">
      <div class="message-content">${data.content}</div>
      <div class="message-meta">
        <span class="message-time">
          ${new Date(data.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  `;

  chatMessages.appendChild(wrapper);
  chatMessages.scrollTop = chatMessages.scrollHeight; // Auto scroll
}

// Send message
sendBtn.addEventListener('click', () => {
  const text = messageInput.value.trim();
  if (text) {
    socket.emit('send_dm', { thread_id: threadId, text });
    messageInput.value = ''; // Clear input
  }
});

// Press Enter to send
messageInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    sendBtn.click();
  }
});

// Receive new message
socket.on('new_dm', (data) => {
  if (data.thread_id === parseInt(threadId)) {
    appendMessage(data);
  }
});
