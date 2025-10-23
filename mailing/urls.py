from django.urls import path
from . import views
from .views import MailingListView

app_name = 'mailing'

urlpatterns = [
    path('', views.home, name='home'),
    # Клиенты
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    # Сообщения
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', views.MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
    # Рассылки
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/update/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/logs/', views.MailingLogListView.as_view(), name='mailing_logs'),
    path('mailings/<int:pk>/toggle/', views.toggle_mailing_status, name='toggle_mailing_status'),
    path('manager/mailings/', views.ManagerMailingListView.as_view(), name='manager_mailing_list'),
    path('manager/mailings/<int:pk>/disable/', views.disable_mailing, name='disable_mailing'),
    path('statistics/', views.statistics, name='statistics'),
    path('logs/<int:pk>/', views.MailingLogView.as_view(), name='mailing_logs'),
]

