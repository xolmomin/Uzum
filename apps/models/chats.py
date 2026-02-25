from django.conf import settings
from django.db.models import Model, ForeignKey, CASCADE, DateTimeField, TextField, URLField, PositiveIntegerField, \
    BooleanField, Index
from django.utils import timezone


class ChatRoom(Model):

    buyer = ForeignKey(settings.AUTH_USER_MODEL,CASCADE,related_name="customer_chats",limit_choices_to={'type': 'user'},db_index=True)
    store = ForeignKey('apps.Store',CASCADE,related_name="store_chats",db_index=True)

    last_message_at = DateTimeField(default=timezone.now, db_index=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'store')
        ordering = ['-last_message_at']

    def __str__(self):
        return f"Chat: {self.buyer.phone} <-> {self.store.name}"


class Message(Model):
    chat = ForeignKey(ChatRoom, CASCADE, related_name="messages")
    sender = ForeignKey(settings.AUTH_USER_MODEL, CASCADE, related_name="sent_messages")
    text = TextField(null=True, blank=True)
    image_url = URLField(null=True, blank=True)

    image_width = PositiveIntegerField(null=True, blank=True)
    image_height = PositiveIntegerField(null=True, blank=True)

    is_read = BooleanField(default=False, db_index=True)
    read_at = DateTimeField(null=True, blank=True)
    timestamp = DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['timestamp']

        indexes = [
            Index(fields=['chat', 'is_read', 'timestamp']),
        ]

    def __str__(self):
        return f"Msg from {self.sender.phone} in Room {self.chat_id}"
