from django.db.models import ForeignKey, CASCADE, SET_NULL, Model, BigIntegerField
from django.db.models.enums import TextChoices
from django.db.models.fields import PositiveSmallIntegerField, CharField, BooleanField
from location_field.forms.plain import PlainLocationField

from apps.models.base import CreatedBaseModel
from apps.models.utils import uz_phone_validator


class Order(CreatedBaseModel):
    class DeliveryType(TextChoices):
        DELIVERY_POINT = 'delivery_point', 'Delivery point'
        DELIVERY = 'delivery', 'Delivery'

    class Status(TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        CANCELED = 'canceled', 'Canceled'

    user = ForeignKey('apps.User', CASCADE, related_name='orders')
    delivery_point = ForeignKey('apps.DeliveryPoint', SET_NULL, null=True)
    payment_type = ForeignKey('apps.PaymentType', SET_NULL, null=True)
    customer_recipient = ForeignKey('apps.CustomerRecipient', SET_NULL, null=True)
    delivery_location = PlainLocationField(based_fields=['address'], zoom=9)
    status = CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # total_price = BigIntegerField()
    # promo_code =


class OrderItem(Model):
    order = ForeignKey('apps.Order', CASCADE, related_name='order_items')
    product = ForeignKey('apps.ProductItem', SET_NULL, null=True)
    is_comment = BooleanField(default=False)
    quantity = PositiveSmallIntegerField()
    price = BigIntegerField()


class PaymentType(Model):
    class StateType(TextChoices):
        ACTIVE = 'active', 'Active'
        DISABLED = 'disabled', 'Disabled'

    title = CharField(max_length=255)
    active = BooleanField()
    state = CharField(choices=StateType.choices)
    description = CharField(max_length=255, null=True, blank=True)
    block_description = CharField(max_length=255, null=True, blank=True)


class CustomerRecipient(Model):
    name = CharField(max_length=255)
    surname = CharField(max_length=255)
    is_default = BooleanField()
    phone = CharField(max_length=50, validators=[uz_phone_validator])
