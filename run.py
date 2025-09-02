from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    # Threading mode (no eventlet). Good for easy installs.
    socketio.run(app, host="0.0.0.0", port=5000)
