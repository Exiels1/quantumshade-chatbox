# Apply Eventlet monkey patching
import eventlet
eventlet.monkey_patch()

# Import the app and socketio after monkey patching
from app import create_app, socketio

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Run the app with Socket.IO and Eventlet
    socketio.run(app, host='0.0.0.0', port=5000)
