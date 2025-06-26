from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room
import sqlite3
from datetime import datetime
import os
import bcrypt
from werkzeug.utils import secure_filename

# App setup
app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app, async_mode='threading')

# Folder setup
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
app.config['CUSTOM_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CUSTOM_FOLDER'], exist_ok=True)

# Initialize DB
def init_db():
    with sqlite3.connect('chatbox.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password BLOB,
            profile_pic TEXT DEFAULT 'default.png'
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            recipient TEXT,
            content TEXT,
            timestamp TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS customization (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            background_image TEXT,
            background_url TEXT,
            blur_level TEXT,
            theme_color TEXT
        )''')

init_db()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        with sqlite3.connect('chatbox.db') as conn:
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = c.fetchone()
            if row and bcrypt.checkpw(password, row[0]):
                session['username'] = username
                return redirect(url_for('group_chat'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        profile_pic_file = request.files.get('profile_pic')
        profile_pic_url = request.form.get('profile_pic_url').strip()

        profile_pic = 'default.png'
        if profile_pic_file and profile_pic_file.filename != '':
            filename = secure_filename(profile_pic_file.filename)
            profile_pic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_pic = 'profile_pics/' + filename
        elif profile_pic_url != '':
            profile_pic = profile_pic_url

        with sqlite3.connect('chatbox.db') as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password, profile_pic) VALUES (?, ?, ?)", (username, password, profile_pic))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return 'Username already exists'
    return render_template('signup.html')

@app.route('/group_chat')
def group_chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    with sqlite3.connect('chatbox.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username != ?", (username,))
        users = c.fetchall()

        c.execute("SELECT sender, content, timestamp FROM messages WHERE recipient = 'GROUP' ORDER BY timestamp ASC")
        messages = c.fetchall()

        c.execute("SELECT background_image, background_url, blur_level, theme_color FROM customization WHERE username = ?", (username,))
        row = c.fetchone()
        customization = {
            'bg_image': row[0] if row else '',
            'bg_url': row[1] if row else '',
            'blur_level': row[2] if row else '0',
            'theme_color': row[3] if row else '#00f2ff'
        }

    return render_template('group_chat.html', username=username, messages=messages, customization=customization)

@socketio.on('group_message')
def handle_group_message(data):
    sender = session.get('username')
    message = data['message']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sqlite3.connect('chatbox.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO messages (sender, recipient, content, timestamp) VALUES (?, ?, ?, ?)", (sender, 'GROUP', message, timestamp))
        conn.commit()

    emit('new_group_message', {'sender': sender, 'message': message, 'timestamp': timestamp}, broadcast=True)

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    with sqlite3.connect('chatbox.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username != ?", (username,))
        users = [u[0] for u in c.fetchall()]

    return render_template('select_partner.html', users=users)

@app.route('/chat/<partner>')
def private_chat(partner):
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('private_chat.html', partner=partner)

@app.route('/messages/<partner>')
def get_messages(partner):
    if 'username' not in session:
        return jsonify([])

    username = session['username']
    with sqlite3.connect('chatbox.db') as conn:
        c = conn.cursor()
        c.execute('''SELECT sender, content, timestamp FROM messages
                     WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)
                     ORDER BY timestamp ASC''', (username, partner, partner, username))
        rows = c.fetchall()

    messages = [{'sender': row[0], 'message': row[1], 'timestamp': row[2]} for row in rows]
    return jsonify(messages)

@socketio.on('join_room')
def join(data):
    join_room(data['partner'])

@socketio.on('private_message')
def handle_private_message(data):
    sender = session.get('username')
    receiver = data['receiver']
    message = data['message']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sqlite3.connect('chatbox.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO messages (sender, recipient, content, timestamp) VALUES (?, ?, ?, ?)", (sender, receiver, message, timestamp))
        conn.commit()

    emit('new_message', {'sender': sender, 'message': message, 'timestamp': timestamp}, room=receiver)
    emit('new_message', {'sender': sender, 'message': message, 'timestamp': timestamp}, room=sender)

@app.route('/customization', methods=['GET', 'POST'])
def customization():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    if request.method == 'POST':
        bg_file = request.files.get('background_image')
        bg_url = request.form.get('background_url', '').strip()
        blur_level = request.form.get('blur_level', '0px')
        theme_color = request.form.get('theme_color', '#00f2ff')

        bg_filename = ''
        if bg_file and bg_file.filename != '':
            bg_filename = secure_filename(bg_file.filename)
            bg_file.save(os.path.join(app.config['CUSTOM_FOLDER'], bg_filename))

        with sqlite3.connect('chatbox.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM customization WHERE username = ?", (username,))
            c.execute('''INSERT INTO customization (username, background_image, background_url, blur_level, theme_color)
                         VALUES (?, ?, ?, ?, ?)''', (username, bg_filename, bg_url, blur_level, theme_color))
            conn.commit()

        return redirect(url_for('group_chat'))

    return render_template('customization.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
