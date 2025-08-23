from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .models import User, Message, DirectThread, DirectMessage
from . import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.chat'))

@main_bp.route('/chat')
@login_required
def chat():
    messages = Message.query.filter_by(room='global').order_by(Message.created_at.asc()).limit(200).all()
    users = User.query.order_by(User.username.asc()).all()
    return render_template('chat.html', messages=messages, users=users)

@main_bp.route('/dm/<username>')
@login_required
def dm(username):
    other = User.query.filter_by(username=username).first_or_404()
    a, b = sorted([current_user.id, other.id])
    thread = DirectThread.query.filter_by(a_id=a, b_id=b).first()
    if not thread:
        thread = DirectThread(a_id=a, b_id=b)
        db.session.add(thread)
        db.session.commit()
    dms = DirectMessage.query.filter_by(thread_id=thread.id).order_by(DirectMessage.created_at.asc()).limit(200).all()
    return render_template('dm.html', other=other, thread_id=thread.id, dms=dms)

@main_bp.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        status = request.form.get('status','').strip()[:120]
        file = request.files.get('avatar')
        current_user.status = status
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.',1)[-1].lower()
            if ext not in current_app.config["ALLOWED_IMAGE_EXT"]:
                flash("Invalid image type", "error")
            else:
                path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"user_{current_user.id}.{ext}")
                file.save(path)
                rel = os.path.relpath(path, os.path.join(current_app.root_path, 'static'))
                current_user.avatar = rel.replace('..'+os.sep, '').replace('\\','/').replace('\\','/')
        db.session.commit()
        flash("Profile updated", "success")
        return redirect(url_for('main.profile'))
    return render_template('profile.html')
