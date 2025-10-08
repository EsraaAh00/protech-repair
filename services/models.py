# services/models.py
from django.db import models
from django.utils.text import slugify

class ServiceCategory(models.Model):
    """
    فئات الخدمات (مثل: خدمات الصيانة، خدمات التركيب)
    Service Categories (e.g., Repair Services, Installation Services)
    """
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    name_en = models.CharField(max_length=100, verbose_name="Category Name", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="الوصف")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., fa-wrench)")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Service(models.Model):
    """
    الخدمات المقدمة (مثل: إصلاح الزنبرك، تركيب الفتاحة)
    Services offered (e.g., Spring Repair, Opener Installation)
    """
    title = models.CharField(max_length=200, verbose_name="عنوان الخدمة")
    title_en = models.CharField(max_length=200, verbose_name="Service Title", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        ServiceCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='services',
        verbose_name="الفئة"
    )
    short_description = models.CharField(max_length=300, blank=True, verbose_name="وصف مختصر")
    description = models.TextField(verbose_name="الوصف")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="صورة")
    
    # Pricing
    starting_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="السعر الابتدائي",
        help_text="Starting price (optional)"
    )
    
    # Features - what's included
    features = models.TextField(
        blank=True,
        verbose_name="المميزات",
        help_text="One feature per line"
    )
    
    # Display options
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_featured = models.BooleanField(default=False, verbose_name="خدمة مميزة")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order', 'title']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_en or self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_features_list(self):
        """Returns features as a list"""
        if self.features:
            return [f.strip() for f in self.features.split('\n') if f.strip()]
        return []


class ServiceImage(models.Model):
    """
    صور إضافية للخدمات
    Additional images for services (before/after, examples)
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/gallery/', verbose_name="صورة")
    title = models.CharField(max_length=200, blank=True, verbose_name="العنوان")
    caption = models.CharField(max_length=300, blank=True, verbose_name="التعليق")
    is_before_after = models.BooleanField(default=False, verbose_name="صورة قبل وبعد")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Service Image"
        verbose_name_plural = "Service Images"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"Image for {self.service.title}"
