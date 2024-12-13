from django.urls import path
from . import views
from .views import event_list, join_event, leave_event, EventUpdateView, EventDeleteView, event_create

urlpatterns = [
    path('', event_list, name='event_list'),
    path('events/create/', event_create, name='event_create'),
    path('event/<int:pk>/update/', EventUpdateView.as_view(), name='event_update'),
    path('event/<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('event/<int:event_id>/join/', join_event, name='join_event'),
    path('event/<int:event_id>/leave/', leave_event, name='leave_event'),
    path('event/<int:event_id>/chat/', views.event_group_chat, name='event_group_chat'),
    path('my-events/', views.my_events, name='my_events'),
    path('<int:event_id>/participants/', views.event_participants, name='event_participants'),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
]
