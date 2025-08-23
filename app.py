from flask import Flask
from flask_socketio import SocketIO

# tell Flask to look for templates/static inside the app folder
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

socketio = SocketIO(app)

# routes
@app.route('/')
def index():
    return render_template('index.html')
