# services/models.py
from django.db import models
from django.utils.text import slugify

class ServiceCategory(models.Model):
    """
    فئات الخدمات (مثل: خدمات الصيانة، خدمات التركيب)
    Service Categories (e.g., Repair Services, Installation Services)
    """
    name = models.CharField(max_length=100, verbose_name="Category Name")
    name_en = models.CharField(max_length=100, verbose_name="Category Name (English)", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., fa-wrench)")
    order = models.IntegerField(default=0, verbose_name="Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")
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
    title = models.CharField(max_length=200, verbose_name="Service Title")
    title_en = models.CharField(max_length=200, verbose_name="Service Title (English)", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        ServiceCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='services',
        verbose_name="Category"
    )
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Short Description")
    description = models.TextField(verbose_name="Description")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Image")
    
    # Pricing
    starting_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Starting Price",
        help_text="Starting price (optional)"
    )
    
    # Features - what's included
    features = models.TextField(
        blank=True,
        verbose_name="Features",
        help_text="One feature per line"
    )
    
    # Display options
    order = models.IntegerField(default=0, verbose_name="Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_featured = models.BooleanField(default=False, verbose_name="Featured")
    
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
    image = models.ImageField(upload_to='services/gallery/', verbose_name="Image")
    title = models.CharField(max_length=200, blank=True, verbose_name="Title")
    caption = models.CharField(max_length=300, blank=True, verbose_name="Caption")
    is_before_after = models.BooleanField(default=False, verbose_name="Before/After Image")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Service Image"
        verbose_name_plural = "Service Images"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"Image for {self.service.title}"
