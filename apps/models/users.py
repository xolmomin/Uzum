from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, IntegerChoices, ImageField, IntegerField, EmailField, TextChoices, OneToOneField
from django.db.models import Model, ForeignKey, CASCADE
from django.db.models.fields import BooleanField, DateField
from django.db.models.fields import FloatField, PositiveIntegerField, TextField
from apps.managers import CustomUserManager, SellerCustomManager, ManagerCustomManager, AdminCustomManager
from apps.models.base import CreatedBaseModel
from apps.models.base import ImageBaseModel
from apps.models.utils import uz_phone_validator


class BaseUser(AbstractUser, ImageBaseModel):
    class TypeChoice(TextChoices):
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'
        SELLER = 'seller', 'Seller'
        MANAGER = 'manager', 'Manager'

    class Gender(IntegerChoices):
        MALE = 1, 'Male'
        FEMALE = 0, 'Female'

    email = EmailField(unique=True, null=True, blank=True)
    phone = CharField(max_length=12, validators=[uz_phone_validator], unique=True)
    password = CharField(max_length=128, null=True, blank=True)
    is_online = BooleanField(default=False)
    patronymic = CharField(max_length=30, null=True, blank=True)
    type = CharField(max_length=12, choices=TypeChoice.choices, default=TypeChoice.USER)
    gender = IntegerField(null=True, blank=True, choices=Gender.choices, help_text='True Male False Female')
    birth_date = DateField(null=True, blank=True)
    username = None
    USERNAME_FIELD = "phone"

    objects = CustomUserManager()
    sellers = SellerCustomManager()
    managers = ManagerCustomManager()
    admins = AdminCustomManager()

    @property
    def is_admin(self):
        return self.type == self.TypeChoice.ADMIN or self.is_superuser


class Seller(CreatedBaseModel):
    user = OneToOneField('apps.User', CASCADE, related_name='seller')


class Shop(CreatedBaseModel, ImageBaseModel):
    name = CharField(max_length=125)
    seller = ForeignKey('apps.Seller', CASCADE, related_name='shops')
    description = TextField(null=True, blank=True)
    banner = ImageField(upload_to='seller/banner/%Y/%m/%d', null=True, blank=True)
    rating = FloatField(default=0)
    comment_count = PositiveIntegerField(default=0)
    order_count = PositiveIntegerField(default=0)
