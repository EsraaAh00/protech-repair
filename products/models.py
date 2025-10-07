# products/models.py
from django.db import models
from django.contrib.auth import get_user_model
from categories.models import Category

User = get_user_model()

class Product(models.Model):
    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('hidden', 'Hidden'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_approval')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "Image for {}".format(self.product.title)

class Car(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='car_details')
    make = models.CharField(max_length=50)  # Toyota, Ford, etc.
    model = models.CharField(max_length=50)  # Camry, F-150, etc.
    year = models.IntegerField()
    mileage = models.IntegerField()  # in kilometers
    transmission_type = models.CharField(max_length=20, choices=[
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
    ])
    fuel_type = models.CharField(max_length=20, choices=[
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    ])
    color = models.CharField(max_length=30)
    is_new = models.BooleanField(default=False)
    
    def __str__(self):
        return "{} {} {}".format(self.year, self.make, self.model)

class RealEstate(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='realestate_details')
    property_type = models.CharField(max_length=50, choices=[
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
    ])
    area_sqm = models.DecimalField(max_digits=8, decimal_places=2)
    num_bedrooms = models.IntegerField(blank=True, null=True)
    num_bathrooms = models.IntegerField(blank=True, null=True)
    is_furnished = models.BooleanField(default=False)
    for_rent = models.BooleanField(default=False)  # False = for sale, True = for rent
    
    def __str__(self):
        return "{} - {} sqm".format(self.property_type, self.area_sqm)

class HotelBooking(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='hotel_details')
    hotel_name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=50, choices=[
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('suite', 'Suite'),
        ('family', 'Family Room'),
    ])
    num_guests = models.IntegerField()
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    
    def __str__(self):
        return "{} - {}".format(self.hotel_name, self.room_type)

