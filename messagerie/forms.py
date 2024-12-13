from django import forms
from .models import PrivateMessage

class PrivateMessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Écrivez votre message...', 'rows': 3}),
        }
