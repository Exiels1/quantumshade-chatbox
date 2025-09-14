from flask import render_template, request
from flask_login import current_user
from flask_socketio import emit, join_room
from . import db
from .models import DirectMessage
from datetime import datetime

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

@app.route('/chat/<int:conversation_id>')
def chat(conversation_id):
    # Fetch the current user (assuming you have a way to get the logged-in user)
    current_user = get_current_user()

    # Fetch the conversation's messages
    messages = DirectMessage.query.filter_by(conversation_id=conversation_id).all()

    # Count unread messages for this conversation
    unread_count = DirectMessage.query.filter_by(
        recipient_id=current_user.id,
        sender_id=conversation_id,  # Assuming sender_id is the conversation partner's ID
        is_read=False
    ).count()

    # Mark unread messages as read
    DirectMessage.query.filter_by(
        recipient_id=current_user.id,
        sender_id=conversation_id,
        is_read=False
    ).update({"is_read": True})

    # Commit the changes to the database
    db.session.commit()

    # Render the chat template
    return render_template(
        'chat.html',
        messages=messages,
        unread_count=unread_count,
        current_user=current_user
    )
