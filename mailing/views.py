from linecache import cache

from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Case, When, IntegerField
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Client, Message, Mailing, MailingLog
from .forms import ClientForm, MessageForm, MailingForm
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.views.decorators.cache import cache_page
import logging


logger = logging.getLogger(__name__)

def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status=Mailing.STARTED).count()
    unique_clients = Client.objects.values('email').distinct().count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
    }
    return render(request, 'mailing/home.html', context)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        logger.info(f"User {self.request.user} created a new client: {form.instance.email}")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MailingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_queryset(self):
        queryset = Mailing.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingLogListView(LoginRequiredMixin, ListView):
    model = MailingLog
    template_name = 'mailing/mailing_logs.html'

    def get_queryset(self):
        return MailingLog.objects.filter(mailing__owner=self.request.user, mailing_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing'] = get_object_or_404(Mailing, pk=self.kwargs['pk'], owner=self.request.user)
        return context


class ManagerMailingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/manager_mailing_list.html'
    permission_required = 'mailing.view_all_mailings'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.all()


def toggle_mailing_status(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    if mailing.status == Mailing.CREATED:
        mailing.status = Mailing.STARTED
    elif mailing.status == Mailing.STARTED:
        mailing.status = Mailing.COMPLETED

    mailing.save()
    return redirect('mailing:mailing_list')


@permission_required('mailing.disable_mailings')
def disable_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.status = Mailing.COMPLETED
    mailing.save()
    messages.success(request, f'Рассылка {mailing.id} была отключена')
    return redirect('mailing:manager_mailing_list')


@login_required
def statistics(request):
    # Общая статистика
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status=Mailing.STARTED).count()
    unique_clients = Client.objects.values('email').distinct().count()

    # Статистика по пользователю
    user_mailings = Mailing.objects.filter(owner=request.user).count()

    # Статистика по логам
    mailing_logs = MailingLog.objects.filter(mailing__owner=request.user)
    success_logs = mailing_logs.filter(status=MailingLog.SUCCESS).count()
    failure_logs = mailing_logs.filter(status=MailingLog.FAILURE).count()

    # Популярные сообщения
    popular_messages = Message.objects.filter(owner=request.user).annotate(
        mailing_count=Count('mailing')
    ).order_by('-mailing_count')[:5]

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
        'user_mailings': user_mailings,
        'success_logs': success_logs,
        'failure_logs': failure_logs,
        'popular_messages': popular_messages,
    }

    return render(request, 'mailing/statistics.html', context)


@cache_page(60 * 15)  # Кешируем на 15 минут
def home(request):
    total_mailings = cache.get('total_mailings')
    if not total_mailings:
        total_mailings = Mailing.objects.count()
        cache.set('total_mailings', total_mailings, 60 * 15)

    active_mailings = cache.get('active_mailings')
    if not active_mailings:
        active_mailings = Mailing.objects.filter(status=Mailing.STARTED).count()
        cache.set('active_mailings', active_mailings, 60 * 5)  # 5 минут для активных

    unique_clients = cache.get('unique_clients')
    if not unique_clients:
        unique_clients = Client.objects.values('email').distinct().count()
        cache.set('unique_clients', unique_clients, 60 * 60)  # 1 час для клиентов

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
    }
    return render(request, 'mailing/home.html', context)


# Для класс-базированных представлений
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'

    @method_decorator(cache_page(60 * 5))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = cache.get(f'mailings_{self.request.user.id}')
        if not queryset:
            queryset = Mailing.objects.filter(owner=self.request.user)
            cache.set(f'mailings_{self.request.user.id}', queryset, 60 * 5)
        return queryset
