from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)
    logo_url = models.URLField(null=True)

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    class ProductGender(models.TextChoices):
        MEN = 'M', _('Men')
        WOMEN = 'W', _('Women')
        UNISEX = 'UX', _('Unisex')

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=False)
    price = models.DecimalField(decimal_places=2, max_digits=6)
    discount_price = models.DecimalField(decimal_places=2, max_digits=6)
    gender = models.CharField(choices=ProductGender.choices, default=ProductGender.MEN, max_length=6)
    categories = models.ManyToManyField(Category, related_name="products", blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    thumbnail = models.URLField()
    is_featured = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['name', 'brand']]

    def __str__(self) -> str:
        return self.name

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price and self.discount_price < self.price else self.price

class ProductsImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(blank=False, null=False)

    def __str__(self) -> str:
        return f"Image for {self.product}"

class ShoeVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=1)
    sku = models.CharField(unique=True, max_length=25)

    class Meta:
        unique_together = [['product', 'size', 'color']]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.size} - {self.color}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ])
    comment = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} - {self.product} ({self.rating})"
