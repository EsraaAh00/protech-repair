# inquiries/forms.py
from django import forms
from .models import ContactInquiry


class ContactInquiryForm(forms.ModelForm):
    """
    Customer inquiry form
    """
    
    class Meta:
        model = ContactInquiry
        fields = [
            'name', 'phone', 'email', 'address',
            'inquiry_type', 'service_needed', 'product_interest',
            'message'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'required': True,
                'type': 'tel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email (optional)',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Service Address *',
                'required': True
            }),
            'inquiry_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'service_needed': forms.Select(attrs={
                'class': 'form-control',
            }),
            'product_interest': forms.Select(attrs={
                'class': 'form-control',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'How can we help you?',
                'rows': 4,
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make service_needed and product_interest optional
        self.fields['service_needed'].required = False
        self.fields['product_interest'].required = False
        self.fields['email'].required = False
        
        # Add empty option to dropdowns
        self.fields['service_needed'].empty_label = "Select Service (optional)"
        self.fields['product_interest'].empty_label = "Select Product (optional)"
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        # Remove spaces and dashes
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Basic validation - at least 10 digits
        if len(phone) < 10:
            raise forms.ValidationError("Invalid phone number")
        
        return phone
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        inquiry_type = cleaned_data.get('inquiry_type')
        service_needed = cleaned_data.get('service_needed')
        product_interest = cleaned_data.get('product_interest')
        
        # If inquiry type is service_request, service should be selected
        if inquiry_type == 'service_request' and not service_needed:
            self.add_error('service_needed', 'Please select a service')
        
        # If inquiry type is product_info, product should be selected
        if inquiry_type == 'product_info' and not product_interest:
            self.add_error('product_interest', 'Please select a product')
        
        return cleaned_data


class QuickContactForm(forms.Form):
    """
    Quick contact form (for homepage)
    """
    INQUIRY_TYPE_CHOICES = [
        ('free_estimate', 'Free Estimate'),
        ('service_request', 'Service Request'),
        ('product_info', 'Product Info'),
        ('general', 'General Inquiry'),
        ('emergency', 'Emergency'),
    ]
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name *',
            'required': True
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number *',
            'required': True,
            'type': 'tel'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        })
    )
    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Service Address *',
            'required': True
        })
    )
    inquiry_type = forms.ChoiceField(
        choices=INQUIRY_TYPE_CHOICES,
        initial='free_estimate',
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    service_needed = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    product_interest = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'How can we help you? *',
            'rows': 3,
            'required': True
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from services.models import Service
        from products.models import Product
        
        # Set querysets
        self.fields['service_needed'].queryset = Service.objects.filter(is_active=True)
        self.fields['service_needed'].empty_label = "Select Service (optional)"
        
        self.fields['product_interest'].queryset = Product.objects.filter(is_active=True)
        self.fields['product_interest'].empty_label = "Select Product (optional)"
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if len(phone) < 10:
            raise forms.ValidationError("Invalid phone number")
        
        return phone

