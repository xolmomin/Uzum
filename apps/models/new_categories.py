from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CharField, SlugField, URLField,
    PositiveIntegerField, BooleanField, DateTimeField,
    Index, SET_NULL, IntegerField,
)
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    title = CharField(max_length=255)
    slug = SlugField(
        max_length=300,
        unique=True,
        allow_unicode=True,
    )
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='children',
        db_index=True,
    )
    link = URLField(
        blank=True,
        null=True,
    )
    path = ArrayField(IntegerField(), blank=True, null=True, help_text='otalarini idlarini saqlaydi')
    product_quantity = PositiveIntegerField(default=0)
    is_adult = BooleanField(default=False)
    is_active = BooleanField(default=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        indexes = [
            Index(fields=['level', 'is_active'], name='cat_level_active_idx'),
        ]

    def __str__(self):
        return f"[L{self.level}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def url_path(self) -> str:
        return f"{self.slug}-{self.pk}"


"""
- elektronika [1]
    - computer [2]
        - desktop computer [5]
            (zor computer yangisi 200$)
            
    - notebook [3]
        (macbook pro m1)
        (asus notebook)
        
    - smartphone [4]
        - naushniklar [6]
        - telephone [7]
            (iphone 16 pro)
            (samsung s25)
    

select id from categories where 1 in path
1
2
3
4
5
6
7

select * from products where category_id in categories_ids


id name path
1 elektronika [1]
2 computer [1, 2]
3 notebook [1, 3]
4 smartphone [1, 4]
5 desktop computer [1, 2, 5]

"""
