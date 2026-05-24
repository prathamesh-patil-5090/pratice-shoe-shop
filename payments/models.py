from django.db import models
from django.utils.translation import gettext_lazy as _
from orders.models import Order

class PaymentStatuses(models.TextChoices):
    PENDING = 'pending', _("Pending")
    SUCCESS = 'success', _("Sucess")
    FAILED = 'failed', _('Failed')
    REFUNDED = 'refunded', _("Refunded")

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_gateway = models.CharField(max_length=70)
    transaction_id = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(default=0)
    status = models.CharField(choices=PaymentStatuses.choices, default=PaymentStatuses.PENDING, max_length=8)
    paid_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.pk} - {self.status} for Order #{self.order.pk}"
