// dm.js — QuantumShade client messaging UX (Socket.IO)
const socket = io();

// small helpers
function qs(sel, base=document) { return base.querySelector(sel); }
function qsa(sel, base=document) { return Array.from(base.querySelectorAll(sel)); }

function formatTime(iso){
  try {
    const d = iso ? new Date(iso) : new Date();
    return d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
  } catch(e){ return ''; }
}

function createMessageElement({id, content, ts, isMe=false, status=''}) {
  const wrapper = document.createElement('div');
  wrapper.className = 'qs-message ' + (isMe ? 'sent' : 'received');
  if(id) wrapper.dataset.messageId = id;

  const bubble = document.createElement('div');
  bubble.className = 'qs-bubble';

  const contentEl = document.createElement('div');
  contentEl.className = 'qs-msg-content';
  contentEl.textContent = content || '';

  const meta = document.createElement('div');
  meta.className = 'qs-msg-meta';

  const time = document.createElement('span');
  time.className = 'qs-time';
  time.textContent = formatTime(ts);

  meta.appendChild(time);
  if(isMe){
    const statusEl = document.createElement('span');
    statusEl.className = 'qs-status';
    statusEl.textContent = status || '●';
    meta.appendChild(statusEl);
  }

  bubble.appendChild(contentEl);
  bubble.appendChild(meta);
  wrapper.appendChild(bubble);

  return wrapper;
}

function scrollToBottom(container, smooth=true){
  if(smooth) container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
  else container.scrollTop = container.scrollHeight;
}

function flashAvatarGlow(){
  const avatar = qs('.qs-profile .qs-avatar-glow');
  if(!avatar) return;
  avatar.animate([{boxShadow: '0 0 24px rgba(57,255,20,0.14)'}, {boxShadow: '0 0 6px rgba(57,255,20,0.05)'}], {duration:700, easing:'ease-out'});
}

// DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const messagesEl = document.getElementById('chatMessages');
  const sendBtn = document.getElementById('sendBtn');
  const input = document.getElementById('messageInput');
  const typingIndicator = document.getElementById('typingIndicator');

  if(!messagesEl) return;
  const threadId = messagesEl.dataset.threadId;

  // Join room
  if(threadId){
    socket.emit('join_dm', { thread_id: threadId });
  }

  // incoming message (server should emit 'new_dm' JSON with thread_id, sender, content, created_at)
  socket.on('new_dm', (data) => {
    if(String(data.thread_id) !== String(threadId)) return; // ignore other threads
    const isMe = data.sender === window.CURRENT_USERNAME;
    const el = createMessageElement({ id: data.id || '', content: data.content, ts: data.created_at, isMe, status: data.status || '' });
    messagesEl.appendChild(el);
    scrollToBottom(messagesEl, true);
    flashAvatarGlow();
  });

  // typing indicator handling (server should emit 'typing' and 'stop_typing' events)
  socket.on('typing', (d) => {
    if(String(d.thread_id) !== String(threadId)) return;
    typingIndicator.style.display = 'flex';
  });
  socket.on('stop_typing', (d) => {
    if(String(d.thread_id) !== String(threadId)) return;
    typingIndicator.style.display = 'none';
  });

  // send message
  function sendMessage(){
    const text = input.value.trim();
    if(!text) return;
    socket.emit('send_dm', { thread_id: threadId, text: text });

    // optimistic UI
    const el = createMessageElement({ id:'', content: text, ts: new Date().toISOString(), isMe: true, status: '●' });
    messagesEl.appendChild(el);
    scrollToBottom(messagesEl, true);
    input.value = '';
    socket.emit('stop_typing', { thread_id: threadId }); // ensure typing stops
  }

  sendBtn.addEventListener('click', (e) => {
    e.preventDefault();
    sendMessage();
  });
  input.addEventListener('keydown', (e) => {
    if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); return; }
    // emit typing events with debounce
    socket.emit('typing', { thread_id: threadId });
    if(window._qsTypingTimer) clearTimeout(window._qsTypingTimer);
    window._qsTypingTimer = setTimeout(()=> socket.emit('stop_typing', { thread_id: threadId }), 900);
  });

  // gentle auto-scroll on load
  setTimeout(()=> scrollToBottom(messagesEl, false), 50);
});
document.addEventListener('DOMContentLoaded', () => {
  const threadId = chatMessages.dataset.threadId;

  // Join DM room
  socket.emit('join_dm', { thread_id: threadId });

  // Send
  sendBtn.addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message) {
      socket.emit('send_dm', { thread_id: threadId, text: message });
      messageInput.value = '';
    }
  });

  // Receive
  socket.on('new_dm', (data) => {
    if (data.thread_id === threadId) {
      const msgDiv = document.createElement('div');
      msgDiv.classList.add('message', data.sender === window.CURRENT_USER ? 'sent' : 'received');
      msgDiv.innerHTML = `
        <div class="bubble">
          <div class="message-content">${data.content}</div>
          <div class="message-meta">${new Date(data.created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</div>
        </div>
      `;
      chatMessages.appendChild(msgDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  });
});
