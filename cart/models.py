from django.db import models
from products.models import ShoeVariant
from users.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Cart {self.pk} for {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    shoe_varient = models.ForeignKey(ShoeVariant, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [['cart', 'shoe_varient']]

    def __str__(self) -> str:
        return f"{self.quantity}x {self.shoe_varient}"
