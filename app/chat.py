from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from app.models import User, DirectMessage, db
from flask_socketio import emit, join_room
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

def make_dm_room(thread_id):
    return f"dm_{thread_id}"

def register_socketio_handlers(sio):
    @sio.on('join_dm')
    def handle_join_dm(data):
        if not current_user.is_authenticated:
            return False
        thread_id = data.get('thread_id')
        if not thread_id:
            return
        room = make_dm_room(thread_id)
        join_room(room)
        # optionally emit existing messages? frontend can fetch via HTTP

    @sio.on('leave_dm')
    def handle_leave_dm(data):
        # no-op for now; SocketIO will handle disconnect
        return

    @sio.on('send_dm')
    def handle_send_dm(data):
        if not current_user.is_authenticated:
            return False
        thread_id = data.get('thread_id')
        text = (data or {}).get('text','').strip()
        if not (thread_id and text):
            return
        # Persist DirectMessage
        dm = DirectMessage(thread_id=thread_id, sender_id=current_user.id, content=text)
        db.session.add(dm)
        db.session.commit()
        msg_payload = {
            'sender': current_user.username,
            'content': dm.content,
            'created_at': dm.created_at.isoformat(),
            'thread_id': thread_id
        }
        emit('new_dm', msg_payload, to=make_dm_room(thread_id))

@chat_bp.route('/chat/<int:conversation_id>')
@login_required
def chat(conversation_id):
    # Fetch the active user (current logged-in user)
    active_user = current_user

    # Fetch the other user or conversation details
    other = User.query.get(conversation_id)
    if not other:
        return "Conversation not found", 404

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
