from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from core.mixins import AuthRequiredMixin
from .forms import CustomUserCreationForm

User = get_user_model()

class RegisterView(CreateView):
    """User registration using Django's built-in CreateView"""
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        
        # Send verification email
        send_mail(
            'Verify your email',
            f'Please click this link to verify your email: http://localhost:8000/verify/{user.id}/',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        messages.success(
            self.request,
            'Account created successfully! Please check your email to verify your account.'
        )
        return response

class HomeView(TemplateView):
    """Home page view"""
    template_name = 'emails/home.html'

class DashboardView(AuthRequiredMixin, TemplateView):
    """User dashboard view"""
    template_name = 'emails/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class ProfileView(AuthRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'emails/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
