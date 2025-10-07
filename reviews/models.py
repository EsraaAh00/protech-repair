# reviews/models.py
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, related_name='reviews')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        target = "منتج" if self.product else "مستخدم"
        return "Review for {} by {}".format(target, self.reviewer.username)

