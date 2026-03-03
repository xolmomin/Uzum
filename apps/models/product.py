# from django.db.models import ForeignKey, SET_NULL, JSONField
# from django_ckeditor_5.fields import CKEditor5Field
# from rest_framework.fields import CharField
#
# from apps.models.base import CreatedBaseModel
# from apps.products.indexes import PRODUCT_ATTRIBUTES_GIN_INDEX
#
#
# class Product(CreatedBaseModel):
#     name = CharField(max_length=90)
#     # tovar belgisi
#     model = ForeignKey('apps.ProductModel', on_delete=SET_NULL, related_name='products', null=True, blank=True)
#     brand = ForeignKey('apps.Brand', on_delete=SET_NULL, related_name='products', null=True, blank=True)
#     country = ForeignKey('apps.Country', on_delete=SET_NULL, related_name='products', null=True, blank=True)
#     description = CKEditor5Field()
#     # 360 gradusli rasm
#     short_description = CharField(max_length=390)
#     feature = CharField(max_length=255, null=True, blank=True)
#     attributes = JSONField(null=True, blank=True)
# # from django.db.models import ForeignKey, CASCADE, SET_NULL
# # from django_ckeditor_5.fields import CKEditor5Field
# # from rest_framework.fields import CharField
# #
# # from apps.models.base import CreatedBaseModel, SlugBaseModel
# #
# #
# # class Product(CreatedBaseModel):
# #     name = CharField(max_length=90)
# #     # tovar belgisi
# #     model = ForeignKey('apps.ProductModel', on_delete=SET_NULL, related_name='products', null=True, blank=True)
# #     brand = ForeignKey('apps.Brand', on_delete=SET_NULL, related_name='products', null=True, blank=True)
# #     country = ForeignKey('apps.Country', on_delete=SET_NULL, related_name='products', null=True, blank=True)
# #     description = CKEditor5Field()
# #     # 360 gradusli rasm
# #     short_description = CharField(max_length=390)
# #     feature = CharField(max_length=255,null=True,blank=True)
#     class Meta:
#         indexes = [
#             PRODUCT_ATTRIBUTES_GIN_INDEX,
#         ]
