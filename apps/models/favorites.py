from django.db.models import ForeignKey, CASCADE, PositiveIntegerField

from apps.models.base import CreatedBaseModel


class Favorite(CreatedBaseModel):
    product = ForeignKey('apps.Product', CASCADE, related_name='favorites')
    user = ForeignKey('apps.User', CASCADE, related_name='favorites')

    class Meta:
        unique_together = ('product', 'user')
