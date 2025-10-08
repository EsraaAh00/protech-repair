# products/models.py
from django.db import models
from django.utils.text import slugify


class ProductCategory(models.Model):
    """
    فئات المنتجات (مثل: فتاحات الأبواب، الأبواب، الإكسسوارات)
    Product Categories (e.g., Openers, Doors, Accessories)
    """
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    name_en = models.CharField(max_length=100, verbose_name="Category Name", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="الوصف")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="صورة")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    المنتجات (فتاحات، أبواب، إكسسوارات)
    Products (Openers, Doors, Accessories)
    """
    PRODUCT_TYPE_CHOICES = [
        ('opener', 'فتاحة / Opener'),
        ('door', 'باب / Door'),
        ('accessory', 'إكسسوار / Accessory'),
        ('part', 'قطعة غيار / Part'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    name_en = models.CharField(max_length=200, verbose_name="Product Name", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    model_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الموديل")
    
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='products',
        verbose_name="الفئة"
    )
    product_type = models.CharField(
        max_length=20, 
        choices=PRODUCT_TYPE_CHOICES,
        default='opener',
        verbose_name="نوع المنتج"
    )
    
    brand = models.CharField(max_length=100, blank=True, verbose_name="العلامة التجارية")
    
    short_description = models.CharField(max_length=300, blank=True, verbose_name="وصف مختصر")
    description = models.TextField(verbose_name="الوصف")
    features = models.TextField(
        blank=True,
        verbose_name="المميزات",
        help_text="One feature per line"
    )
    specifications = models.TextField(
        blank=True,
        verbose_name="المواصفات التقنية",
        help_text="One specification per line"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="السعر"
    )
    
    # Main image
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="الصورة الرئيسية")
    
    # Display options
    is_featured = models.BooleanField(default=False, verbose_name="منتج مميز")
    is_best_seller = models.BooleanField(default=False, verbose_name="الأكثر مبيعاً")
    is_new = models.BooleanField(default=False, verbose_name="جديد")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.IntegerField(default=0, verbose_name="عدد المشاهدات")
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['order', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.model_number:
            return f"{self.name} ({self.model_number})"
        return self.name
    
    def get_features_list(self):
        """Returns features as a list"""
        if self.features:
            return [f.strip() for f in self.features.split('\n') if f.strip()]
        return []
    
    def get_specifications_list(self):
        """Returns specifications as a list"""
        if self.specifications:
            return [s.strip() for s in self.specifications.split('\n') if s.strip()]
        return []


class ProductImage(models.Model):
    """
    صور إضافية للمنتجات
    Additional product images
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', verbose_name="صورة")
    title = models.CharField(max_length=200, blank=True, verbose_name="العنوان")
    is_main = models.BooleanField(default=False, verbose_name="صورة رئيسية")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ['-is_main', 'order', '-created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class OpenerSpecifications(models.Model):
    """
    مواصفات تفصيلية لفتاحات الأبواب
    Detailed specifications for garage door openers
    """
    DRIVE_TYPE_CHOICES = [
        ('chain', 'Chain Drive'),
        ('belt', 'Belt Drive'),
        ('screw', 'Screw Drive'),
        ('wall_mount', 'Wall Mount'),
        ('jackshaft', 'Jackshaft'),
    ]
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='opener_specs')
    
    drive_type = models.CharField(
        max_length=20, 
        choices=DRIVE_TYPE_CHOICES,
        verbose_name="نوع المحرك"
    )
    horsepower = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name="قوة الحصان",
        help_text="e.g., 1/2 HP, 3/4 HP"
    )
    
    # Smart features
    has_wifi = models.BooleanField(default=False, verbose_name="Wi-Fi مدمج")
    has_battery_backup = models.BooleanField(default=False, verbose_name="بطارية احتياطية")
    has_camera = models.BooleanField(default=False, verbose_name="كاميرا مدمجة")
    has_smart_features = models.BooleanField(default=False, verbose_name="ميزات ذكية")
    
    # Technical specs
    lifting_capacity = models.CharField(max_length=50, blank=True, verbose_name="القدرة على الرفع")
    speed = models.CharField(max_length=50, blank=True, verbose_name="السرعة")
    noise_level = models.CharField(max_length=50, blank=True, verbose_name="مستوى الضجيج")
    
    # Warranty
    warranty_years = models.IntegerField(blank=True, null=True, verbose_name="سنوات الضمان")
    
    class Meta:
        verbose_name = "Opener Specifications"
        verbose_name_plural = "Opener Specifications"
    
    def __str__(self):
        return f"Specs for {self.product.name}"


class DoorSpecifications(models.Model):
    """
    مواصفات تفصيلية للأبواب
    Detailed specifications for garage doors
    """
    PANEL_STYLE_CHOICES = [
        ('long_panel', 'Long Panel'),
        ('short_panel', 'Short Panel'),
        ('carriage_house', 'Carriage House'),
        ('contemporary', 'Contemporary'),
        ('traditional', 'Traditional'),
    ]
    
    MATERIAL_CHOICES = [
        ('steel', 'Steel'),
        ('aluminum', 'Aluminum'),
        ('wood', 'Wood'),
        ('composite', 'Composite'),
        ('vinyl', 'Vinyl'),
    ]
    
    INSULATION_CHOICES = [
        ('none', 'No Insulation'),
        ('single', 'Single Layer'),
        ('double', 'Double Layer'),
        ('triple', 'Triple Layer'),
    ]
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='door_specs')
    
    panel_style = models.CharField(
        max_length=30, 
        choices=PANEL_STYLE_CHOICES,
        blank=True,
        verbose_name="نمط اللوحة"
    )
    material = models.CharField(
        max_length=20, 
        choices=MATERIAL_CHOICES,
        verbose_name="المادة"
    )
    
    # Size options
    width_options = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name="خيارات العرض",
        help_text="e.g., 8ft, 9ft, 10ft, 16ft"
    )
    height_options = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name="خيارات الارتفاع",
        help_text="e.g., 7ft, 8ft"
    )
    
    # Insulation
    insulation_type = models.CharField(
        max_length=20, 
        choices=INSULATION_CHOICES,
        default='none',
        verbose_name="نوع العزل"
    )
    r_value = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name="قيمة R (العزل)",
        help_text="e.g., R-16, R-18"
    )
    
    # Color and texture
    color_options = models.TextField(
        blank=True,
        verbose_name="خيارات الألوان",
        help_text="One color per line"
    )
    texture_options = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name="خيارات الملمس",
        help_text="e.g., Smooth, Woodgrain, Stucco"
    )
    
    # Windows
    has_windows = models.BooleanField(default=False, verbose_name="يحتوي على نوافذ")
    window_options = models.TextField(
        blank=True,
        verbose_name="خيارات النوافذ",
        help_text="Description of window options"
    )
    
    # Warranty
    warranty_years = models.IntegerField(blank=True, null=True, verbose_name="سنوات الضمان")
    
    class Meta:
        verbose_name = "Door Specifications"
        verbose_name_plural = "Door Specifications"
    
    def __str__(self):
        return f"Specs for {self.product.name}"
    
    def get_color_list(self):
        """Returns color options as a list"""
        if self.color_options:
            return [c.strip() for c in self.color_options.split('\n') if c.strip()]
        return []
