import os
from flask import Flask, render_template
from flask_socketio import SocketIO

port = int(os.environ.get("PORT", 10000))

# Explicitly tell Flask where templates & static files are
app = Flask(
    __name__,
    template_folder=os.path.join('app', 'templates'),
    static_folder=os.path.join('app', 'static')
)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
    