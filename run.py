import eventlet
eventlet.monkey_patch()  # Must be called before any other imports

from app import create_app, socketio  # Import after monkey_patch

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Use eventlet's WSGI server to run the app
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
