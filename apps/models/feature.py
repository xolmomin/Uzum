from django.db.models import Model, CharField, ImageField, ForeignKey, CASCADE, ManyToManyField

from apps.models.base import SlugBaseModel


class Brand(Model):
    name = CharField(max_length=100)
    logo = ImageField(upload_to='brands/', null=True, blank=True)


class ProductModel(SlugBaseModel):
    name = CharField(max_length=100)
    brand = ForeignKey("apps.Brand", CASCADE, related_name='models')


class Country(Model):
    name_uz = CharField(max_length=100)


class Attribute(Model):
    name = CharField(max_length=100)


class AttributeValue(Model):
    attribute = ForeignKey("apps.Attribute", CASCADE, related_name='values')
    value = CharField(max_length=100)


class Color(Model):
    name = CharField(max_length=50)
    category = ManyToManyField('Category', related_name='colors')
