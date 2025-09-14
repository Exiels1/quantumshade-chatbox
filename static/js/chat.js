// Initialize Socket.IO
const socket = io();

// Join the current conversation room
const currentRoomId = "{{ current_conversation.id }}";
socket.emit("join", currentRoomId);

// DOM Elements
const messageBox = document.getElementById("message-box");
const sendButton = document.getElementById("send-button");
const messagesContainer = document.querySelector(".messages");

// Function to append a new message to the DOM
function appendMessage(content, isOutgoing, timestamp) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", isOutgoing ? "outgoing" : "incoming");

    const bubbleDiv = document.createElement("div");
    bubbleDiv.classList.add("bubble");
    bubbleDiv.textContent = content;

    const timestampDiv = document.createElement("div");
    timestampDiv.classList.add("timestamp");
    timestampDiv.textContent = timestamp;

    bubbleDiv.appendChild(timestampDiv);
    messageDiv.appendChild(bubbleDiv);
    messagesContainer.appendChild(messageDiv);

    // Auto-scroll to the bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Send message event
sendButton.addEventListener("click", () => {
    const content = messageBox.value.trim();
    if (content === "") return;

    // Emit the message to the server
    socket.emit("send_message", {
        room_id: currentRoomId,
        content: content
    });

    // Append the message to the DOM as outgoing
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    appendMessage(content, true, timestamp);

    // Clear the input box
    messageBox.value = "";
});

// Listen for "new_message" event from the server
socket.on("new_message", (data) => {
    const { content, timestamp } = data;

    // Append the message to the DOM as incoming
    appendMessage(content, false, timestamp);
});