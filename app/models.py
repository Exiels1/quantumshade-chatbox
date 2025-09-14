from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(120), default="Available")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    backup_codes = db.Column(db.Text, nullable=True)  # JSON list of hashed codes

    sent_messages = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_backup_codes(self, raw_codes):
        # raw_codes: list of plaintext codes; store hashed JSON
        self.backup_codes = json.dumps([generate_password_hash(c) for c in raw_codes])

    def get_backup_hashes(self):
        if not self.backup_codes:
            return []
        try:
            return json.loads(self.backup_codes)
        except:
            return []

    def consume_backup_code(self, plaintext_code):
        # return True if matched and removed
        hashes = self.get_backup_hashes()
        for i, h in enumerate(hashes):
            if check_password_hash(h, plaintext_code):
                # remove used
                del hashes[i]
                self.backup_codes = json.dumps(hashes)
                return True
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room = db.Column(db.String(64), default="global")
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DirectThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    a_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    b_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DirectMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('direct_thread.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
