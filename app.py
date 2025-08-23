from flask import Flask, render_template
from flask_socketio import SocketIO
import os

# get port from Render environment
port = int(os.environ.get("PORT", 10000))

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
