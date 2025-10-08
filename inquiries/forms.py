# inquiries/forms.py
from django import forms
from .models import ContactInquiry


class ContactInquiryForm(forms.ModelForm):
    """
    نموذج استفسار العملاء
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
                'placeholder': 'الاسم الكامل / Full Name',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف / Phone Number',
                'required': True,
                'type': 'tel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني / Email (optional)',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'العنوان / Address (optional)',
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
                'placeholder': 'كيف يمكننا مساعدتك؟ / How can we help you?',
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
        self.fields['address'].required = False
        
        # Add empty option to dropdowns
        self.fields['service_needed'].empty_label = "اختر خدمة (اختياري) / Select Service (optional)"
        self.fields['product_interest'].empty_label = "اختر منتج (اختياري) / Select Product (optional)"
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        # Remove spaces and dashes
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Basic validation - at least 10 digits
        if len(phone) < 10:
            raise forms.ValidationError("رقم الهاتف غير صحيح / Invalid phone number")
        
        return phone
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        inquiry_type = cleaned_data.get('inquiry_type')
        service_needed = cleaned_data.get('service_needed')
        product_interest = cleaned_data.get('product_interest')
        
        # If inquiry type is service_request, service should be selected
        if inquiry_type == 'service_request' and not service_needed:
            self.add_error('service_needed', 'يرجى اختيار الخدمة المطلوبة / Please select a service')
        
        # If inquiry type is product_info, product should be selected
        if inquiry_type == 'product_info' and not product_interest:
            self.add_error('product_interest', 'يرجى اختيار المنتج / Please select a product')
        
        return cleaned_data


class QuickContactForm(forms.Form):
    """
    نموذج تواصل سريع (للصفحة الرئيسية)
    Quick contact form (for homepage)
    """
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الاسم / Name *',
            'required': True
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الهاتف / Phone *',
            'required': True,
            'type': 'tel'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'البريد الإلكتروني / Email',
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'العنوان / Address',
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'كيف يمكننا مساعدتك؟ / How can we help? *',
            'rows': 3,
            'required': True
        })
    )
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if len(phone) < 10:
            raise forms.ValidationError("رقم الهاتف غير صحيح / Invalid phone number")
        
        return phone

