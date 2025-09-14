from flask_socketio import emit, join_room
from flask_login import current_user
from . import db
from .models import DirectMessage

def make_dm_room(thread_id):
    return f"dm_{thread_id}"

def register_socketio_handlers(sio):
    @sio.on('join_dm')
    def handle_join_dm(data):
        if not current_user.is_authenticated:
            return False
        thread_id = data.get('thread_id')
        if thread_id:
            join_room(make_dm_room(thread_id))

    @sio.on('send_dm')
    def handle_send_dm(data):
        if not current_user.is_authenticated:
            return False
        thread_id = data.get('thread_id')
        text = data.get('text', '').strip()
        if thread_id and text:
            dm = DirectMessage(thread_id=thread_id, sender_id=current_user.id, content=text)
            db.session.add(dm)
            db.session.commit()
            emit('new_dm', {
                'thread_id': thread_id,
                'sender': current_user.username,
                'content': dm.content,
                'created_at': dm.created_at.isoformat()
            }, to=make_dm_room(thread_id))
