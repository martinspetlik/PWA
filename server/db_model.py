from server.models.user import User
from server.models.chat import Chat as Chat_db
from server.models.message import Message


def save_message(data):
    Message(author=data['author'], text=data['text'], chat=data['chat']).save()
