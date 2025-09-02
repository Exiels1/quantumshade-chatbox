from app import create_app, socketio

# create the Flask app
app = create_app()

# for Render/production (Gunicorn or equivalent will call this "app")
if __name__ != "__main__":
    application = app  # sometimes Render expects "application"

# for local dev
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
