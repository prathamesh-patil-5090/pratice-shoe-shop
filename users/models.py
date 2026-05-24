from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class UserRoles(models.TextChoices):
        CUSTOMER = 'CU' , _('Customer'),
        ADMIN = 'AD', _('Admin')

    username = None
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(region='IN', blank=False)
    address = models.TextField(blank=False)
    role = models.CharField(choices=UserRoles.choices, max_length=2, default=UserRoles.CUSTOMER)
    created_at = models.DateField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.get_full_name() or self.email
