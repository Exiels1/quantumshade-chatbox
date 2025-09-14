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
    # Redirect to the user's direct messages or another page
    return redirect(url_for('main.index'))

@main_bp.route('/dm/<int:id>')
@login_required
def dm(id):
    # Fetch the active user (current logged-in user)
    active_user = current_user

    # Fetch the other user by ID
    other = User.query.get(id)
    if not other:
        return "User not found", 404

    # Fetch the thread or messages
    thread = DirectMessage.query.filter(
        (DirectMessage.sender_id == active_user.id) & (DirectMessage.recipient_id == other.id) |
        (DirectMessage.sender_id == other.id) & (DirectMessage.recipient_id == active_user.id)
    ).order_by(DirectMessage.timestamp.asc()).all()

    # Mark unread messages as read
    DirectMessage.query.filter_by(
        recipient_id=active_user.id,
        sender_id=other.id,
        is_read=False
    ).update({"is_read": True})
    db.session.commit()

    # Pass all required variables to the template
    return render_template(
        'dm.html',
        active_user=active_user,
        other=other,
        thread_id=f"{active_user.id}-{other.id}",
        dms=thread
    )

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

