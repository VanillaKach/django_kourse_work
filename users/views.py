from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from .forms import UserRegisterForm, UserProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import User
from mailing.models import Mailing, MailingLog


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    pass


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('mailing:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Статистика по рассылкам пользователя
        mailings = Mailing.objects.filter(owner=user)
        attempts = MailingLog.objects.filter(mailing__in=mailings)

        context['user_mailing_stats'] = {
            'total_mailings': mailings.count(),
            'active_mailings': mailings.filter(status='Запущена').count(),
            'successful_attempts': attempts.filter(status='Успешно').count(),
            'failed_attempts': attempts.filter(status='Не успешно').count(),
        }
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    fields = ['first_name', 'last_name', 'email']
    template_name = 'users/profile_update.html'  # ← явно укажи, чтобы не гадать
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user
