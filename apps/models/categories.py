import uuid

from django.contrib.postgres.indexes import GinIndex
from django.core.validators import FileExtensionValidator
from django.db.models import Model, ForeignKey, CharField, CASCADE, ManyToManyField, JSONField, SET_NULL, TextField, \
    BigIntegerField, SlugField, DecimalField, PositiveIntegerField
from django.db.models.base import ModelBase
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from image.video_field import VideoField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from apps.models.base import SlugBaseModel, CreatedBaseModel, ImageBaseModel
from apps.models.utils import upload_to_image, validate_video


class Attribute(Model):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name


class AttributeValue(Model):
    attribute = ForeignKey("apps.Attribute", CASCADE, related_name='values')
    value = CharField(max_length=255)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Category(MPTTModel, SlugBaseModel):
    name = CharField(max_length=255)
    parent = TreeForeignKey('self', CASCADE, null=True, blank=True, related_name='subcategory')

    attributes = ManyToManyField("apps.Attribute", blank=True)


class Product(CreatedBaseModel):
    category = ForeignKey('apps.Category', CASCADE,
                          related_name='products')

    name_uz = CharField(max_length=92)

    model = ForeignKey("apps.ProductModel", SET_NULL, null=True, blank=True)
    brand = ForeignKey('apps.Brand', SET_NULL, null=True, blank=True)
    country = ForeignKey("apps.Country", SET_NULL, null=True, blank=True)

    description_uz = CKEditor5Field()
    short_description_uz = TextField(null=True, blank=True)

    dimensions_uz = CKEditor5Field(null=True, blank=True)
    composition_uz = CKEditor5Field(null=True, blank=True)
    instructions_uz = CKEditor5Field(null=True, blank=True)
    certificate_uz = CKEditor5Field(null=True, blank=True)

    features_uz = JSONField(default=list, null=True, blank=True)


class ProductImage(ImageBaseModel):
    product = ForeignKey('apps.Product', CASCADE, related_name='images')


class ProductVideo(ModelBase):
    product = ForeignKey('apps.Product', CASCADE, related_name='videos')
    video = VideoField(upload_to=upload_to_image,
                       validators=[FileExtensionValidator(['mp4', 'avi', 'mov', 'mkv'], validate_video)])


class ProductVariantModel(Model):
    product = ForeignKey('apps.Product', CASCADE, related_name='variants')

    sku_id = BigIntegerField(unique=True, editable=False, db_index=True)

    variant_slug = SlugField(max_length=255, unique=True, blank=True, db_index=True)

    price = DecimalField(max_digits=15, decimal_places=2)
    old_price = DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    stock = PositiveIntegerField(default=0)

    attributes_cache = JSONField(default=dict, blank=True)
    attribute_values = ManyToManyField('apps.AttributeValue', related_name='variants')

    class Meta:
        db_table = 'product_variants'
        indexes = [
            GinIndex(fields=['attributes_cache'], name='variant_attr_gin_idx')
        ]

    def update_metadata(self):
        attrs = self.attribute_values.select_related('attribute').all()

        new_cache = {a.attribute.slug: a.slug for a in attrs}

        attr_slugs = "-".join([a.slug for a in attrs])
        new_slug = slugify(f"{self.product.name_uz}-{attr_slugs}-{self.product.id}")

        self.attributes_cache = new_cache
        self.variant_slug = new_slug
        self.save()

    def save(self, *args, **kwargs):
        if not self.sku_id:
            self.sku_id = int(str(uuid.uuid4().int)[:10])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name_uz} | SKU: {self.sku_id} | {self.attributes_cache}"
