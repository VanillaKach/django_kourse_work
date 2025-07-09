from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from .models import User
from .forms import UserRegisterForm, UserProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


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


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user
