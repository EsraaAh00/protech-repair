# categories/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def get_full_path(self):
        """Returns the full category path like 'Cars > Sedans'"""
        if self.parent:
            return "{} > {}".format(self.parent.get_full_path(), self.name)
        return self.name

