from django.db import models
from django.contrib.auth.admin import User


class Chat(models.Model):
    is_private = models.BooleanField()
    participants = models.ManyToManyField(User)


class Message(models.Model):
    text = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    is_edited = models.BooleanField(default=False)
