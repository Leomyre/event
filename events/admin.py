from django.contrib import admin
from .models import Event, EventParticipant, Notification

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'organizer', 'participant_count')
    list_filter = ('date', 'organizer')
    search_fields = ('title', 'description', 'organizer__username')
    ordering = ('-date',)

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Nombre de participants'


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'participant', 'joined_at')
    list_filter = ('event', 'joined_at')
    search_fields = ('event__title', 'participant__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'recipient')
    search_fields = ('recipient__username', 'message')
    ordering = ('-created_at',)
