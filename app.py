from flask import Flask, render_template, request
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow connections from anywhere

@app.route('/')
def index():
    return render_template('index.html')  # Your chatbox page

# Example of a Socket.IO event
@socketio.on('message')
def handle_message(msg):
    print(f"Received message: {msg}")
    socketio.send(msg)  # Broadcast back to all clients

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
