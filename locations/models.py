# locations/models.py
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Location(models.Model):
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    level = models.CharField(max_length=20, choices=[
        ('country', 'Country'),
        ('region', 'Region'),
        ('city', 'City'),
        ('district', 'District'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_full_path(self):
        """Returns the full location path like 'Saudi Arabia > Riyadh > Al-Malaz'"""
        if self.parent:
            return "{} > {}".format(self.parent.get_full_path(), self.name)
        return self.name

class ProductLocation(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='location_details')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='products')
    address = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    is_exact_location = models.BooleanField(default=False)  # True if exact coordinates, False if approximate
    
    def __str__(self):
        return "Location for {}".format(self.product.title)

class SavedLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_locations')
    name = models.CharField(max_length=100)  # e.g., "Home", "Work", "Shop"
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return "{} - {}".format(self.user.username, self.name)

