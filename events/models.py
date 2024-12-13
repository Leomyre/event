from django.contrib.auth.models import AbstractUser
from django.db import models

from src import settings


class CustomUser(AbstractUser):
    ROLE_PARTICIPANT = 'participant'
    ROLE_ORGANIZER = 'organizer'
    ROLE_CHOICES = [
        (ROLE_PARTICIPANT, 'Participant'),
        (ROLE_ORGANIZER, 'Organisateur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PARTICIPANT)

    def is_organizer(self):
        return self.role == 'organizer'
    
    def is_participant(self):
        return self.role == self.ROLE_PARTICIPANT

from django.core.exceptions import ValidationError

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')

    def number_of_participants(self):
        return self.participants.count()
    
    def __str__(self):
        return self.title
    
    def is_participant(self, user):
        return self.participants.filter(participant=user).exists()

    def clean(self):
        if self.date < now():
            raise ValidationError("La date de l'événement ne peut pas être dans le passé.")

class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'participant')


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        self.is_read = True
        self.save()


from django.utils.timezone import now

class EventMessage(models.Model):
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='event_sent_messages'
    )

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'EventMessage from {self.sender.username}'
