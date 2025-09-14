from app import create_app, socketio
from app.models import get_conversations, get_current_conversation, get_messages, get_current_user

app = create_app()

@app.route('/chat')
def chat():
    conversations = get_conversations()
    current_conversation = get_current_conversation()
    messages = get_messages(current_conversation.id)
    current_user = get_current_user()
    return render_template(
        'chat.html',
        conversations=conversations,
        current_conversation=current_conversation,
        messages=messages,
        current_user=current_user
    )

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
