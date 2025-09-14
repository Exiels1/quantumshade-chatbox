from flask_login import current_user
from flask_socketio import emit, join_room
from . import db
from .models import Message, DirectMessage

def register_socketio_handlers(sio):
    @sio.on('connect')
    def handle_connect():
        if not current_user.is_authenticated:
            return False
        join_room('global')
        emit('system', {'msg': f'{current_user.username} connected'}, to='global')

    @sio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            emit('system', {'msg': f'{current_user.username} disconnected'}, to='global')

    @sio.on('send_message')
    def handle_send_message(data):
        if not current_user.is_authenticated:
            return
        text = (data or {}).get('text','').strip()
        if not text:
            return
        m = Message(user_id=current_user.id, room='global', content=text)
        db.session.add(m)
        db.session.commit()
        emit('new_message', {
            'username': current_user.username,
            'content': m.content,
            'created_at': m.created_at.isoformat()
        }, to='global')

    @sio.on('send_dm')
    def handle_send_dm(data):
        if not current_user.is_authenticated:
            return
        thread_id = (data or {}).get('thread_id')
        text = (data or {}).get('text','').strip()
        if not (thread_id and text):
            return
        dm = DirectMessage(thread_id=thread_id, sender_id=current_user.id, content=text)
        db.session.add(dm)
        db.session.commit()
        emit('new_dm', {
            'sender': current_user.username,
            'content': dm.content,
            'created_at': dm.created_at.isoformat(),
            'thread_id': thread_id
        }, to=f"dm_{thread_id}")
