from django.contrib.auth.forms import UserCreationForm

from src import settings
from .models import CustomUser, Event
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'role']

    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

from django import forms
from .models import EventMessage

class EventMessageForm(forms.ModelForm):
    class Meta:
        model = EventMessage
        fields = ['content']  # Pas besoin du champ 'receiver'

    def save(self, commit=True):
        # Assurez-vous que le champ 'receiver' est défini sur None pour les messages de groupe
        instance = super().save(commit=False)
        instance.receiver = None  # Pas de receiver pour les messages de groupe
        if commit:
            instance.save()
        return instance

from django.contrib.auth import get_user_model
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location']  # Ajoutez les champs de votre événement

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Récupérez l'utilisateur passé
        super().__init__(*args, **kwargs)

        # Si l'utilisateur est fourni, définissez-le comme organisateur de l'événement
        if user:
            self.instance.organizer = user