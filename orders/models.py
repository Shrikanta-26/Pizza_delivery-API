from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class Order(models.Model):
   
    class SizeChoices(models.TextChoices):
        SMALL = "SMALL", "Small"
        MEDIUM = "MEDIUM", "Medium"
        LARGE = "LARGE", "Large"
        EXTRA_LARGE = "EXTRA_LARGE", "Extra Large"

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        DELIVERED = "DELIVERED", "Delivered"

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    size = models.CharField(max_length=20, choices=SizeChoices.choices, default=SizeChoices.SMALL)
    order_status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} | {self.get_size_display()} | Customer {self.customer.id}"