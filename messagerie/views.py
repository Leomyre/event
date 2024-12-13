from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from .models import Message, CustomUser, UserProfile

@login_required
def inbox(request):
    # Récupérer toutes les conversations de l'utilisateur connecté
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').order_by('-timestamp')

    # Créer un dictionnaire pour associer un utilisateur à une conversation
    user_conversations = {}
    for msg in conversations:
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        if other_user != request.user:
            if other_user not in user_conversations:
                user_conversations[other_user] = []
            user_conversations[other_user].append(msg)

    return render(request, 'messages/inbox.html', {'user_conversations': user_conversations})


@login_required
def conversation(request, user_id):
    receiver = get_object_or_404(CustomUser, id=user_id)

    # Vérifier si l'utilisateur connecté a le droit d'accéder à la conversation
    if request.user.role == CustomUser.ROLE_PARTICIPANT and receiver.role == CustomUser.ROLE_ORGANIZER:
        messages.error(request, "Vous n'avez pas le droit de contacter cet utilisateur.")
        return redirect('inbox')

    # Récupérer les messages entre les deux utilisateurs
    messages_list = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')

    if request.method == 'POST':
        plain_text_message = request.POST.get('message', '').strip()
        if plain_text_message:
            # Sauvegarde du message
            Message.objects.create(sender=request.user, receiver=receiver, content=plain_text_message)
            messages.success(request, 'Message envoyé avec succès!')
            return redirect('conversation', user_id=user_id)

        messages.error(request, "Le message ne peut pas être vide.")

    return render(request, 'messages/conversation.html', {'messages': messages_list, 'receiver': receiver})

from django.contrib.auth import get_user_model

@login_required
def send_message(request):
    User = get_user_model()
    users = User.objects.exclude(id=request.user.id)  # Exclure l'utilisateur connecté

    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        message_content = request.POST.get('message', '').strip()

        # Vérifier les données envoyées
        if not receiver_id or not message_content:
            messages.error(request, 'Veuillez sélectionner un destinataire et écrire un message.')
            return render(request, 'messages/send_message.html', {'users': users})

        # Vérifier que le destinataire existe
        receiver = get_object_or_404(User, id=receiver_id)

        # Créer le message
        Message.objects.create(sender=request.user, receiver=receiver, content=message_content)
        messages.success(request, f'Message envoyé à {receiver.username}!')
        return redirect('inbox')  # Redirige vers la boîte de réception

    return render(request, 'messages/send_message.html', {'users': users})


@login_required
def send_message_with_receiver(request,receiver_id):
    User = get_user_model()
    users = User.objects.exclude(id=request.user.id)  # Exclure l'utilisateur connecté

    if request.method == 'POST':
        message_content = request.POST.get('message', '').strip()

        # Vérifier les données envoyées
        if not receiver_id or not message_content:
            messages.error(request, 'Veuillez sélectionner un destinataire et écrire un message.')
            return render(request, 'messages/send_message.html', {'users': users})

        # Vérifier que le destinataire existe
        receiver = get_object_or_404(User, id=receiver_id)

        # Créer le message
        Message.objects.create(sender=request.user, receiver=receiver, content=message_content)
        messages.success(request, f'Message envoyé à {receiver.username}!')
        return redirect('conversation', user_id=receiver_id)

    return render(request, 'messages/conversation.html', {'users': users})


@login_required
def delete_conversation(request, user_id):
    receiver = get_object_or_404(CustomUser, id=user_id)

    # Supprimer tous les messages de la conversation
    Message.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
    ).delete()

    messages.success(request, 'Conversation supprimée avec succès.')
    return redirect('inbox')


@login_required
def manage_account(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        photo = request.FILES.get('photo')

        if password and password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('manage_account')

        user = request.user
        if username:
            user.username = username

        if password:
            user.password = make_password(password)
            update_session_auth_hash(request, user)

        if photo:
            profile, created = UserProfile.objects.get_or_create(user=user)
            fs = FileSystemStorage(location='media/profile_photos')
            filename = fs.save(photo.name, photo)
            profile.photo = f"profile_photos/{filename}"
            profile.save()

        user.save()
        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('manage_account')

    return render(request, 'messages/manage_account.html', {'user': request.user})
