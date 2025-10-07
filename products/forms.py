from django import forms
from .models import Product, ProductImage, Car, RealEstate, HotelBooking
from categories.models import Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'location_latitude', 'location_longitude']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان المنتج'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'وصف تفصيلي للمنتج'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'السعر بالريال السعودي'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location_latitude': forms.HiddenInput(),
            'location_longitude': forms.HiddenInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "اختر الفئة"

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_main': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'mileage', 'transmission_type', 'fuel_type', 'color', 'is_new']
        widgets = {
            'make': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الشركة المصنعة (مثل: تويوتا، فورد)'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموديل (مثل: كامري، F-150)'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'سنة الصنع',
                'min': 1990,
                'max': 2025
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'المسافة المقطوعة (كم)'
            }),
            'transmission_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fuel_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'لون السيارة'
            }),
            'is_new': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class RealEstateForm(forms.ModelForm):
    class Meta:
        model = RealEstate
        fields = ['property_type', 'area_sqm', 'num_bedrooms', 'num_bathrooms', 'is_furnished', 'for_rent']
        widgets = {
            'property_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'area_sqm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'المساحة بالمتر المربع'
            }),
            'num_bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد غرف النوم'
            }),
            'num_bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد الحمامات'
            }),
            'is_furnished': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'for_rent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class HotelBookingForm(forms.ModelForm):
    class Meta:
        model = HotelBooking
        fields = ['hotel_name', 'room_type', 'num_guests', 'check_in_date', 'check_out_date']
        widgets = {
            'hotel_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الفندق'
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'num_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد الضيوف'
            }),
            'check_in_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        } 