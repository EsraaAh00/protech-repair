from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Product, Car, RealEstate, HotelBooking, ProductImage
from categories.models import Category
from .forms import ProductForm, CarForm, RealEstateForm, HotelBookingForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.db import models

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        return Product.objects.filter(status='active', is_approved=True).select_related('seller', 'category')

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    
    def get_object(self):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        # زيادة عدد المشاهدات
        product.views_count += 1
        product.save()
        return product
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # تحديد نوع المنتج
        context['product_type'] = self.get_product_type(product)
        
        # إضافة تفاصيل المنتج حسب النوع
        context['car_details'] = getattr(product, 'car_details', None)
        context['realestate_details'] = getattr(product, 'realestate_details', None)
        context['hotel_details'] = getattr(product, 'hotel_details', None)
        
        # إضافة منتجات مشابهة
        similar_products = Product.objects.filter(
            category=product.category,
            status='active',
            is_approved=True
        ).exclude(id=product.id)[:6]
        context['similar_products'] = similar_products
        
        return context
    
    def get_product_type(self, product):
        """تحديد نوع المنتج بناءً على الفئة"""
        category_name = product.category.name.lower()
        
        if 'سيارات' in category_name or 'سيارة' in category_name:
            return 'car'
        elif 'عقارات' in category_name or 'عقار' in category_name:
            return 'real_estate'
        elif 'فنادق' in category_name or 'فندق' in category_name:
            return 'hotel'
        else:
            return 'general'

class AddProductView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/add.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        try:
            # حفظ المنتج أولاً
            form.instance.seller = self.request.user
            response = super().form_valid(form)
            
            # معالجة الصور
            images = self.request.FILES.getlist('images')
            print(f"Number of images received: {len(images)}")  # للتشخيص
            
            for i, image in enumerate(images):
                print(f"Processing image {i+1}: {image.name}")  # للتشخيص
                ProductImage.objects.create(
                    product=self.object,
                    image=image,
                    is_main=(i == 0)  # الصورة الأولى تكون الرئيسية
                )
            
            messages.success(self.request, f'تم إضافة المنتج بنجاح مع {len(images)} صورة! سيتم مراجعته من قبل المسؤولين.')
            return response
            
        except Exception as e:
            print(f"Error in form_valid: {e}")  # للتشخيص
            messages.error(self.request, f'حدث خطأ أثناء إضافة المنتج: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        print(f"Form errors: {form.errors}")  # للتشخيص
        messages.error(self.request, 'يرجى تصحيح الأخطاء في الفورم.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.object.pk})

class EditProductView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/edit.html'
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # تحديد نوع المنتج الحالي
        product = self.object
        context['current_product_type'] = self.get_product_type(product)
        
        # إضافة بيانات التفاصيل الحالية
        context['car_details'] = getattr(product, 'car_details', None)
        context['realestate_details'] = getattr(product, 'realestate_details', None)
        context['hotel_details'] = getattr(product, 'hotel_details', None)
        
        # إضافة الصور الحالية
        context['current_images'] = product.images.all()
        
        return context
    
    def get_product_type(self, product):
        """تحديد نوع المنتج بناءً على الفئة"""
        category_name = product.category.name.lower()
        category_slug = product.category.slug.lower() if hasattr(product.category, 'slug') else ''
        
        if 'سيارات' in category_name or 'car' in category_slug:
            return 'car'
        elif 'عقارات' in category_name or 'real' in category_slug:
            return 'real_estate'
        elif 'فنادق' in category_name or 'hotel' in category_slug:
            return 'hotel'
        else:
            return 'general'
    
    def form_valid(self, form):
        try:
            # حفظ المنتج الأساسي
            response = super().form_valid(form)
            
            # معالجة الصور الجديدة
            new_images = self.request.FILES.getlist('images')
            for i, image in enumerate(new_images):
                ProductImage.objects.create(
                    product=self.object,
                    image=image,
                    is_main=(i == 0 and not self.object.images.exists())
                )
            
            # معالجة تفاصيل المنتج حسب النوع
            product_type = self.request.POST.get('product_type', self.get_product_type(self.object))
            self.handle_product_details(product_type)
            
            messages.success(self.request, 'تم تحديث المنتج بنجاح!')
            return response
            
        except Exception as e:
            print(f"Error in edit form_valid: {e}")
            messages.error(self.request, f'حدث خطأ أثناء تحديث المنتج: {str(e)}')
            return self.form_invalid(form)
    
    def handle_product_details(self, product_type):
        """معالجة تفاصيل المنتج حسب النوع"""
        from .models import Car, RealEstate, HotelBooking
        
        if product_type == 'car':
            # حذف التفاصيل الأخرى إذا وجدت
            if hasattr(self.object, 'realestate_details'):
                self.object.realestate_details.delete()
            if hasattr(self.object, 'hotel_details'):
                self.object.hotel_details.delete()
            
            # إنشاء أو تحديث تفاصيل السيارة
            car_data = {
                'make': self.request.POST.get('make', ''),
                'model': self.request.POST.get('model', ''),
                'year': self.request.POST.get('year', 2024),
                'mileage': self.request.POST.get('mileage', 0),
                'transmission_type': self.request.POST.get('transmission_type', 'automatic'),
                'fuel_type': self.request.POST.get('fuel_type', 'gasoline'),
                'color': self.request.POST.get('color', ''),
                'is_new': self.request.POST.get('is_new') == 'on',
            }
            
            car, created = Car.objects.get_or_create(
                product=self.object,
                defaults=car_data
            )
            if not created:
                for key, value in car_data.items():
                    setattr(car, key, value)
                car.save()
                
        elif product_type == 'real_estate':
            # حذف التفاصيل الأخرى
            if hasattr(self.object, 'car_details'):
                self.object.car_details.delete()
            if hasattr(self.object, 'hotel_details'):
                self.object.hotel_details.delete()
            
            # إنشاء أو تحديث تفاصيل العقار
            real_estate_data = {
                'property_type': self.request.POST.get('property_type', 'apartment'),
                'area_sqm': self.request.POST.get('area_sqm', 0),
                'num_bedrooms': self.request.POST.get('num_bedrooms') or None,
                'num_bathrooms': self.request.POST.get('num_bathrooms') or None,
                'is_furnished': self.request.POST.get('is_furnished') == 'on',
                'for_rent': self.request.POST.get('for_rent') == 'on',
            }
            
            real_estate, created = RealEstate.objects.get_or_create(
                product=self.object,
                defaults=real_estate_data
            )
            if not created:
                for key, value in real_estate_data.items():
                    setattr(real_estate, key, value)
                real_estate.save()
                
        elif product_type == 'hotel':
            # حذف التفاصيل الأخرى
            if hasattr(self.object, 'car_details'):
                self.object.car_details.delete()
            if hasattr(self.object, 'realestate_details'):
                self.object.realestate_details.delete()
            
            # إنشاء أو تحديث تفاصيل الفندق
            from datetime import date
            hotel_data = {
                'hotel_name': self.request.POST.get('hotel_name', ''),
                'room_type': self.request.POST.get('room_type', 'single'),
                'num_guests': self.request.POST.get('num_guests', 1),
                'check_in_date': self.request.POST.get('check_in_date') or date.today(),
                'check_out_date': self.request.POST.get('check_out_date') or date.today(),
            }
            
            hotel, created = HotelBooking.objects.get_or_create(
                product=self.object,
                defaults=hotel_data
            )
            if not created:
                for key, value in hotel_data.items():
                    setattr(hotel, key, value)
                hotel.save()
    
    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.object.pk})

class DeleteProductView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/delete.html'
    success_url = reverse_lazy('products:my_products')
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف المنتج بنجاح!')
        return super().delete(request, *args, **kwargs)

class MyProductsView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/my_products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by('-created_at')

class ProductSearchView(ListView):
    model = Product
    template_name = 'products/search.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        products = Product.objects.filter(status='active', is_approved=True)
        
        if query:
            products = products.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if category:
            products = products.filter(category_id=category)
        
        if min_price:
            products = products.filter(price__gte=min_price)
        
        if max_price:
            products = products.filter(price__lte=max_price)
        
        return products.select_related('seller', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        return context

class CarsListView(ListView):
    model = Product
    template_name = 'products/cars.html'
    context_object_name = 'cars'
    paginate_by = 12
    
    def get_queryset(self):
        from .models import Car
        
        # البحث عن فئة السيارات
        cars_categories = Category.objects.filter(
            Q(name__icontains='سيارات') | Q(name__icontains='سيارة') | Q(slug__icontains='cars')
        )
        
        if not cars_categories.exists():
            return Product.objects.none()
        
        # البدء بجميع السيارات النشطة والمعتمدة
        queryset = Product.objects.filter(
            category__in=cars_categories,
            status='active',
            is_approved=True
        ).select_related('seller', 'category', 'car_details').prefetch_related('images')
        
        # تطبيق الفلاتر
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(car_details__make__icontains=search) |
                Q(car_details__model__icontains=search)
            )
        
        # فلتر الماركة
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(car_details__make__icontains=brand)
        
        # فلتر السنة
        year_from = self.request.GET.get('year_from')
        year_to = self.request.GET.get('year_to')
        if year_from:
            try:
                queryset = queryset.filter(car_details__year__gte=int(year_from))
            except (ValueError, TypeError):
                pass
        if year_to:
            try:
                queryset = queryset.filter(car_details__year__lte=int(year_to))
            except (ValueError, TypeError):
                pass
        
        # فلتر السعر
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        if price_from:
            try:
                queryset = queryset.filter(price__gte=float(price_from))
            except (ValueError, TypeError):
                pass
        if price_to:
            try:
                queryset = queryset.filter(price__lte=float(price_to))
            except (ValueError, TypeError):
                pass
        
        # فلتر نوع الوقود
        fuel_type = self.request.GET.get('fuel_type')
        if fuel_type:
            fuel_mapping = {
                'petrol': 'gasoline',
                'diesel': 'diesel',
                'hybrid': 'hybrid',
                'electric': 'electric'
            }
            if fuel_type in fuel_mapping:
                queryset = queryset.filter(car_details__fuel_type=fuel_mapping[fuel_type])
        
        # فلتر ناقل الحركة
        transmission = self.request.GET.get('transmission')
        if transmission:
            queryset = queryset.filter(car_details__transmission_type=transmission)
        
        # فلتر المسافة المقطوعة
        mileage = self.request.GET.get('mileage')
        if mileage:
            try:
                if mileage == '0-50000':
                    queryset = queryset.filter(car_details__mileage__lt=50000)
                elif mileage == '50000-100000':
                    queryset = queryset.filter(car_details__mileage__gte=50000, car_details__mileage__lt=100000)
                elif mileage == '100000-150000':
                    queryset = queryset.filter(car_details__mileage__gte=100000, car_details__mileage__lt=150000)
                elif mileage == '150000+':
                    queryset = queryset.filter(car_details__mileage__gte=150000)
            except Exception:
                pass
        
        # ترتيب النتائج
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-views_count')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إحصائيات السيارات
        cars_queryset = self.get_queryset()
        context['cars_count'] = cars_queryset.count()
        
        # عدد الماركات المختلفة
        brands_count = cars_queryset.exclude(car_details__isnull=True).values('car_details__make').distinct().count()
        context['brands_count'] = brands_count
        
        # نطاق السنوات (من 2000 إلى السنة الحالية + 1)
        from datetime import datetime
        current_year = datetime.now().year
        context['years_range'] = range(2000, current_year + 2)
        
        # معلومات الفلترة الحالية
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'brand': self.request.GET.get('brand', ''),
            'year_from': self.request.GET.get('year_from', ''),
            'year_to': self.request.GET.get('year_to', ''),
            'price_from': self.request.GET.get('price_from', ''),
            'price_to': self.request.GET.get('price_to', ''),
            'fuel_type': self.request.GET.get('fuel_type', ''),
            'transmission': self.request.GET.get('transmission', ''),
            'mileage': self.request.GET.get('mileage', ''),
            'sort': self.request.GET.get('sort', 'newest'),
        }
        
        # إحصائيات إضافية للعرض
        cars_categories = Category.objects.filter(
            Q(name__icontains='سيارات') | Q(name__icontains='سيارة') | Q(slug__icontains='cars')
        )
        context['total_cars'] = Product.objects.filter(
            category__in=cars_categories,
            status='active',
            is_approved=True
        ).count()
        
        # أشهر الماركات
        popular_brands = cars_queryset.exclude(car_details__isnull=True).values('car_details__make').annotate(
            count=models.Count('id')
        ).order_by('-count')[:6]
        context['popular_brands'] = popular_brands
        
        return context

class RealEstateListView(ListView):
    model = Product
    template_name = 'products/real_estate.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        real_estate_category = Category.objects.filter(slug='real-estate').first()
        if real_estate_category:
            return Product.objects.filter(
                category=real_estate_category, 
                status='active', 
                is_approved=True
            ).select_related('seller', 'category')
        return Product.objects.none()

class HotelsListView(ListView):
    model = Product
    template_name = 'products/hotels.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        hotels_category = Category.objects.filter(slug='hotels').first()
        if hotels_category:
            return Product.objects.filter(
                category=hotels_category, 
                status='active', 
                is_approved=True
            ).select_related('seller', 'category')
        return Product.objects.none()

def debug_form_view(request):
    """View للتشخيص - يمكن حذفها لاحقاً"""
    if request.method == 'POST':
        print("=== DEBUG INFO ===")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        print(f"Images count: {len(request.FILES.getlist('images'))}")
        for i, img in enumerate(request.FILES.getlist('images')):
            print(f"Image {i+1}: {img.name}, Size: {img.size}")
        print("==================")
    
    return render(request, 'products/debug_form.html')

class SimpleAddProductView(LoginRequiredMixin, CreateView):
    """View بسيط لاختبار إضافة المنتج"""
    model = Product
    form_class = ProductForm
    template_name = 'products/simple_add.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        try:
            print("=== SIMPLE ADD DEBUG ===")
            print(f"POST data: {self.request.POST}")
            print(f"FILES data: {self.request.FILES}")
            print(f"Images count: {len(self.request.FILES.getlist('images'))}")
            
            # حفظ المنتج
            form.instance.seller = self.request.user
            response = super().form_valid(form)
            
            # معالجة الصور
            images = self.request.FILES.getlist('images')
            for i, image in enumerate(images):
                print(f"Processing image {i+1}: {image.name}")
                ProductImage.objects.create(
                    product=self.object,
                    image=image,
                    is_main=(i == 0)
                )
            
            messages.success(self.request, f'تم إضافة المنتج بنجاح مع {len(images)} صورة!')
            return response
            
        except Exception as e:
            print(f"Error: {e}")
            messages.error(self.request, f'خطأ: {str(e)}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.object.pk})

@login_required
@csrf_exempt
def delete_product_image(request, image_id):
    """حذف صورة منتج"""
    try:
        image = get_object_or_404(ProductImage, id=image_id, product__seller=request.user)
        
        # التأكد من عدم حذف الصورة الرئيسية إذا كانت الوحيدة
        if image.is_main and image.product.images.count() > 1:
            # جعل صورة أخرى رئيسية
            next_image = image.product.images.exclude(id=image.id).first()
            if next_image:
                next_image.is_main = True
                next_image.save()
        
        image.delete()
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

class ProductMapView(ListView):
    """عرض المنتجات على الخريطة"""
    model = Product
    template_name = 'products/map.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # إرجاع المنتجات التي لها إحداثيات صحيحة فقط
        return Product.objects.filter(
            status='active',
            is_approved=True,
            location_latitude__isnull=False,
            location_longitude__isnull=False
        ).select_related('seller', 'category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # تحويل المنتجات إلى JSON للخريطة
        products_data = []
        for product in self.get_queryset():
            if product.location_latitude and product.location_longitude:
                product_data = {
                    'id': product.id,
                    'title': product.title,
                    'price': str(product.price),
                    'category': product.category.name,
                    'seller': product.seller.get_full_name() or product.seller.username,
                    'image': product.images.first().image.url if product.images.first() else None,
                    'latitude': float(product.location_latitude),
                    'longitude': float(product.location_longitude),
                    'url': f'/products/{product.id}/',
                    'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
                    'views_count': product.views_count,
                    'created_at': product.created_at.strftime('%Y-%m-%d')
                }
                products_data.append(product_data)
        
        context['products_json'] = products_data
        context['products_count'] = len(products_data)
        return context
