from django_filters import FilterSet, NumberFilter, CharFilter

from .models import Product


class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name="variants__price", lookup_expr='gte')
    max_price = NumberFilter(field_name="variants__price", lookup_expr='lte')
    category = NumberFilter(field_name="category_id")
    brand = CharFilter(field_name="brand__slug")

    class Meta:
        model = Product
        fields = ['category', 'brand']

    @property
    def qs(self):
        parent_qs = super().qs
        params = self.request.query_params

        exclude_fields = ['category', 'brand', 'min_price', 'max_price', 'page', 'q', 'ordering']

        dynamic_query = {}
        for key, value in params.items():
            if key not in exclude_fields and value:
                dynamic_query[key] = value

        if dynamic_query:
            return parent_qs.filter(variants__attributes_cache__contains=dynamic_query).distinct()

        return parent_qs
