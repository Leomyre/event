# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),  # Conversation avec un utilisateur
    path('send-message/', views.send_message, name='send_message'),
    path('send-message/<int:receiver_id>/', views.send_message_with_receiver, name='send_message'),  # Envoyer un nouveau message
    path('conversation/delete/<int:user_id>/', views.delete_conversation, name='delete_conversation'),
    path('manage-account/', views.manage_account, name='manage_account'),  # Gérer le compte utilisateur
]
