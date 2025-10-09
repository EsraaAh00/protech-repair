# inquiries/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse_lazy
from .models import ContactInquiry
from .forms import ContactInquiryForm, QuickContactForm
from .utils import get_client_ip, get_user_agent
import logging

logger = logging.getLogger(__name__)


class ContactInquiryCreateView(CreateView):
    """
    View for creating new inquiry
    """
    model = ContactInquiry
    form_class = ContactInquiryForm
    template_name = 'inquiries/contact_form.html'
    success_url = reverse_lazy('inquiries:thank_you')
    
    def form_valid(self, form):
        # Add IP and User Agent
        form.instance.ip_address = get_client_ip(self.request)
        form.instance.user_agent = get_user_agent(self.request)
        
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            'Your inquiry has been sent successfully! We will contact you soon.'
        )
        
        logger.info(f"New inquiry created: {self.object.id}")
        
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'An error occurred. Please check the entered data.'
        )
        return super().form_invalid(form)


def contact_form_view(request):
    """
    Contact form view (function-based)
    """
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.ip_address = get_client_ip(request)
            inquiry.user_agent = get_user_agent(request)
            inquiry.save()
            
            messages.success(
                request,
                'Your inquiry has been sent successfully!'
            )
            
            return redirect('inquiries:thank_you')
        else:
            messages.error(
                request,
                'Please check the form for errors.'
            )
    else:
        form = ContactInquiryForm()
    
    return render(request, 'inquiries/contact_form.html', {'form': form})


def quick_contact_view(request):
    """
    Quick contact form (for AJAX requests)
    """
    if request.method == 'POST':
        form = QuickContactForm(request.POST)
        if form.is_valid():
            # Create inquiry from quick form
            inquiry = ContactInquiry.objects.create(
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data.get('email', ''),
                address=form.cleaned_data['address'],
                message=form.cleaned_data['message'],
                inquiry_type=form.cleaned_data.get('inquiry_type', 'free_estimate'),
                service_needed=form.cleaned_data.get('service_needed'),
                product_interest=form.cleaned_data.get('product_interest'),
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # AJAX request
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'message': 'Your request has been sent successfully!'
                })
            else:
                messages.success(request, 'Your request has been sent successfully!')
                return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            else:
                messages.error(request, 'An error occurred. Please check your input.')
                return redirect('home')
    
    return redirect('home')


def thank_you_view(request):
    """
    Thank you page after inquiry submission
    """
    return render(request, 'inquiries/thank_you.html')


def inquiry_detail_view(request, pk):
    """
    Inquiry detail view (admin only)
    """
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('home')
    
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    return render(request, 'inquiries/inquiry_detail.html', {'inquiry': inquiry})
