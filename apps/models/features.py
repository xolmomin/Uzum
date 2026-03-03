# from django.db.models import Model, CharField, ForeignKey, CASCADE, ManyToManyField
#
#
# class ProductModel(Model):
#     name = CharField(max_length=50)
#     category = ManyToManyField('Category',related_name='models')
#
#
# class Brand(Model):
#     title = CharField(max_length=100)
#     category = ManyToManyField('Category', related_name='brands')
#
# class Country(Model):
#     name = CharField(max_length=50)
#     category = ManyToManyField('Category', related_name='countries')
#
#
# class Color(Model):
#     name = CharField(max_length=50)
#     category = ManyToManyField('Category', related_name='colors')
#
# class Ram(Model):
#     name = CharField(max_length=50)
#     category = ManyToManyField('Category', related_name='rams')