from django.db import models
from django.utils.translation import gettext_lazy as _
from products.models import ShoeVariant
from users.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Statuses(models.TextChoices):
    PENDING = "pending", _('Pending'),
    PAID = "paid", _('Paid'),
    SHIPPED = "shipped", _("Shipped"),
    DELIVERED = 'delivered', _("Delivered"),
    CANCELLED = 'cancelled', _("Cancelled")

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(decimal_places=2, default=0, max_digits=6)
    status = models.CharField(choices=Statuses.choices, default=Statuses.PENDING, max_length=9)
    shipping_address = models.TextField(blank=False)
    payment_method = models.CharField(max_length=60)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    shoe_variant = models.ForeignKey(ShoeVariant, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[MinValueValidator(Decimal('0.0'))])
    total_price = models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[MinValueValidator(Decimal('0.0'))])

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * Decimal(self.unit_price)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}×{self.shoe_variant} for Order #{self.order.pk}"
