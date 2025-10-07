from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, UserProfileForm

# Create your views here.

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'تم إنشاء حسابك بنجاح!')
        return redirect('home')

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # إحصائيات المنتجات
        context['total_products'] = user.products.count()
        context['sold_products'] = user.products.filter(is_sold=True).count()
        context['active_products'] = user.products.filter(status='active').count()
        context['pending_products'] = user.products.filter(status='pending_approval').count()
        
        # إحصائيات الرسائل (إذا كان هناك نموذج رسائل)
        try:
            context['sent_messages'] = user.sent_messages.count()
            context['received_messages'] = user.received_messages.count()
        except:
            context['sent_messages'] = 0
            context['received_messages'] = 0
        
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث ملفك الشخصي بنجاح!')
        return super().form_valid(form)
