from app import create_app, socketio
import eventlet
eventlet.monkey_patch()

# create the Flask app
app = create_app()

# For Render/production
# Gunicorn will look for "application" by default
application = app  # Flask app only; socketio.run() used for local dev

# Local development
if __name__ == "__main__":
    # Use SocketIO server locally
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
