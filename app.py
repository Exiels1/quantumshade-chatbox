import os
from flask import Flask, render_template
from flask_socketio import SocketIO

# Initialize Flask with defaults—since templates/ and static/ are in root
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')  # Flask will look in ./templates

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=True,
        allow_unsafe_werkzeug=True
    )