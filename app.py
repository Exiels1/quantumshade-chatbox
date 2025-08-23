from flask import Flask, render_template
from flask_socketio import SocketIO
import os

# Explicitly set the template and static folders
app = Flask(
    __name__,
    template_folder='app/templates',  # path to your templates
    static_folder='app/static'       # path to your static files
)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
