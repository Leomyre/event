from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import UpdateView
import json
from .models import Event
from .forms import EventForm
from django.utils.safestring import mark_safe

@login_required
def event_create(request):
    if request.method == 'POST':
        # Passez l'utilisateur connecté au formulaire
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            # Redirigez vers une page appropriée après la création (par exemple, liste d'événements)
            return redirect('event_list')  # Remplacez 'event-list' par le nom de votre URL cible
    else:
        # Initialisez le formulaire en mode GET
        form = EventForm(user=request.user)
    
    return render(request, 'events/organisateur/event_form.html', {'form': form})


def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/participant/event_list.html', {'events': events})

@login_required
def my_events(request):
    events = Event.objects.filter(organizer=request.user)
    event_titles = [event.title for event in events]
    participant_counts = [event.number_of_participants() for event in events]

    return render(request, 'events/organisateur/my_events.html', {
        'events': events,
        'event_titles_json': mark_safe(json.dumps(event_titles)),
        'participant_counts_json': mark_safe(json.dumps(participant_counts)),
    })

from django.contrib.auth import get_user_model

@login_required
def event_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Vérifiez si l'utilisateur est bien l'organisateur
    if not request.user.is_organizer():
        messages.error(request, "Vous devez être un organisateur pour gérer les participants.")
        return redirect('event_list')

    participants = event.participants.all()  # Utilisez une relation ManyToMany ou similaire

    if request.method == 'POST':
        participant_id = request.POST.get('participant_id')
        if not participant_id:
            messages.error(request, "Aucun ID de participant fourni.")
            return redirect('event_participants', event_id=event.id)

        User = get_user_model()
        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            messages.error(request, "Le participant spécifié n'existe pas.")
            return redirect('event_participants', event_id=event.id)

        if participant.is_organizer():
            messages.error(request, "Vous ne pouvez pas supprimer un organisateur.")
            return redirect('event_participants', event_id=event.id)

        # Supprimez le participant de l'événement
        EventParticipant.objects.filter(event=event, participant=participant).delete()
        messages.success(request, f"{participant.username} a été retiré de l'événement.")
        return redirect('event_participants', event_id=event.id)

    return render(request, 'events/organisateur/event_participants.html', {
        'event': event,
        'participants': participants,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Event, EventParticipant

@login_required
def join_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.is_participant(request.user):  # Utilise la méthode is_participant
        messages.info(request, "Vous êtes déjà inscrit à cet événement.")
    else:
        EventParticipant.objects.create(event=event, participant=request.user)
        messages.success(request, f"Vous pouvez communiquer dans le groupe de discussion de '{event.title}' maintenant.")
    return redirect('event_group_chat', event_id=event.id)



@login_required
def leave_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    EventParticipant.objects.filter(event=event, participant=request.user).delete()
    # Ajouter une notification
    event.organizer.notifications.create(message=f"{request.user.username} a quitté l'événement {event.title}.")
    return redirect('event_list')


from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import CustomUserCreationForm, EventForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Event


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    success_url = '/my-events/'
    fields = ['title', 'description', 'date', 'location']
    template_name = 'events/organisateur/event_form.html'

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    success_url = '/'
    template_name = 'events/event_confirm_delete.html'

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

from .forms import EventMessageForm

@login_required
def event_group_chat(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Vérifier si l'utilisateur est un participant de l'événement
    if not event.is_participant(request.user):
        messages.error(request, "Vous devez participer à cet événement pour accéder au chat.")
        return redirect('event_list')  # Rediriger vers la liste des événements si l'utilisateur n'est pas participant

    # Récupérer les messages du groupe, triés par timestamp
    messages_list = event.messages.all().order_by('timestamp')

    # Gérer l'envoi des messages
    if request.method == 'POST':
        form = EventMessageForm(request.POST)
        if form.is_valid():
            # Créer un nouveau message
            new_message = form.save(commit=False)
            new_message.event = event
            new_message.sender = request.user
            new_message.save()

            messages.success(request, "Votre message a été envoyé avec succès.")
            return redirect('event_group_chat', event_id=event.id)  # Rediriger vers le chat avec l'ID de l'événement
    else:
        form = EventMessageForm()

    return render(request, 'events/participant/event_chat.html', {
        'event': event,
        'messages': messages_list,
        'form': form,
    })


#@login_required
#def event_detail(request, event_id):
#    event = get_object_or_404(Event, id=event_id)

#    # Récupérer les participants de l'événement
 #   participants = event.participants.all()

#    # Vérifier si l'utilisateur connecté est un participant
#    is_participant = EventParticipant.objects.filter(event=event, participant=request.user).exists()

#    # Optionnellement, récupérer les messages associés à l'événement (si vous avez une fonctionnalité de chat)
#    messages = event.messages.all().order_by('timestamp')

#    return render(request, 'events/event_detail.html', {
#        'event': event,
#        'participants': participants,
#        'messages': messages,
#        'is_participant': is_participant,
#    })