from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db.models import CharField, IntegerChoices, ImageField, IntegerField, EmailField, TextChoices
from django.db.models import Model, ForeignKey, CASCADE
from django.db.models.fields import BooleanField, DateField
from django_ckeditor_5.fields import CKEditor5Field

from apps.managers import (
    UserManager,
    AdminUserManager,
    SellerUserManager,
    CustomerUserManager,
)
from apps.models.base import ImageBaseModel, SlugBaseModel
from apps.models.utils import uz_phone_validator, upload_to_image, upload_image_size_5mb_validator



class User(AbstractUser, ImageBaseModel):
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
    is_online = BooleanField(default=False)
    patronymic = CharField(max_length=30, null=True, blank=True)
    type = CharField(max_length=12, choices=TypeChoice.choices, )
    gender = BooleanField(null=True, blank=True, choices=Gender.choices, help_text='True Male False Female')
    birth_date = DateField(null=True, blank=True)

    username = None
    password = None

    USERNAME_FIELD = "phone"

    objects = UserManager()
    admins = AdminUserManager()
    sellers = SellerUserManager()
    customers = CustomerUserManager()

    @property
    def is_admin(self):
        return self.type == self.TypeChoice.ADMIN or self.is_superuser


class Store(ImageBaseModel, SlugBaseModel):
    name = CharField(max_length=50, )
    banner = ImageField(upload_to=upload_to_image, null=True, blank=True,
                        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
                                    upload_image_size_5mb_validator],
                        help_text="Hajmi 5 mb dan oshmasin")
    product_quantity = IntegerField(null=True, blank=True, default=0)
    is_online = BooleanField(default=False)


class Seller(User):
    class BusinessType(IntegerChoices):
        YATT = 1, 'YATT'
        NOT_CONFIRMED = 2, 'NOT_CONFIRMED'
        LEGAL_ENTITY = 3, 'LEGAL ENTITY'

    business_type = IntegerField(choices=BusinessType.choices, null=True, blank=True)
    balance = IntegerField(default=0)
    store = ForeignKey('apps.Store', CASCADE, related_name='sellers')



class QuestionCategory(Model):
    question = CharField(max_length=255)

    def __str__(self):
        return f"{self.question}"


class Answer(Model):
    question_category = ForeignKey('apps.QuestionCategory', CASCADE, related_name='answers')
    question = CKEditor5Field(max_length=255)
    answer = CKEditor5Field()

    def __str__(self):
        return f"{self.question}"
