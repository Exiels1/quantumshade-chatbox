// dm.js - client Socket.IO for DM page
const socket = io();

// Utilities
function appendMessage(sender, content, ts, isMe=false){
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message ' + (isMe ? 'sent' : 'received');
    div.innerHTML = `<div class="message-content"></div><div class="message-meta"><span class="message-time"></span></div>`;
    div.querySelector('.message-content').textContent = content;
    div.querySelector('.message-time').textContent = ts || '';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Join DM room on load
document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const threadId = chatMessages && chatMessages.dataset.threadId;
    if(!threadId) return;
    socket.emit('join_dm', { thread_id: threadId });

    // Listen for new messages
    socket.on('new_dm', (data) => {
        const isMe = data.sender === window.CURRENT_USERNAME;
        appendMessage(data.sender, data.content, data.created_at ? new Date(data.created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) : '', isMe);
    });

    // Send message
    const sendBtn = document.getElementById('sendBtn');
    const input = document.getElementById('messageInput');
    sendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if(!text) return;
        socket.emit('send_dm', { thread_id: threadId, text });
        input.value = '';
    });

    input.addEventListener('keydown', (e) => {
        if(e.key === 'Enter'){
            e.preventDefault();
            sendBtn.click();
        }
    });
});
