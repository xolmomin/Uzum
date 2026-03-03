from django_elasticsearch_dsl import Document, ObjectField, IntegerField, TextField, NestedField, DoubleField
from django_elasticsearch_dsl.registries import registry

from apps.models import Product


@registry.register_document
class ProductDocument(Document):
    category = ObjectField(properties={
        'id': IntegerField(),
        'name_uz': TextField(),

    })
    brand = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
    })

    variants = NestedField(properties={
        'sku': TextField(),
        'price': DoubleField(),
        'attributes_data': ObjectField(),
        'stock': IntegerField(),
    })

    class Index:
        name = 'products'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Product
        fields = [
            'id',
            'name_uz',
            'name_ru',
            'short_description_uz',
            'short_description_ru',
        ]
