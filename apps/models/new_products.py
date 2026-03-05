"""
products/models.py

Uzum Market sahifalaridan tahlil qilingan (screenshot asosida):

  Listing sahifasi:
    - price, original_price (strikethrough)
    - installment_monthly (21 179 so'm/oyiga)
    - rating, reviews_count
    - is_price_guaranteed  → "ARZON NARX KAFOLATI" badge
    - rang filtri (SKUAttribute.color_hex)

  Detail sahifasi:
    - price                → 269 100 so'm  (asosiy, ko'k)
    - uzum_card_price      → 299 000 so'm  (Uzum kartasiz)
    - original_price       → 399 000 so'm  (strikethrough, -33%)
    - installment_monthly  → 29 900 so'm
    - installment_months   → 12 oy
    - orders_count         → 1000+ buyurtma
    - max_purchase_qty     → 3 dona xarid qilish mumkin
    - weekly_buyers        → Bu haftada 44 kishi sotib oldi
    - delivery_text        → Ertaga yetkazib beramiz
    - SKU rang (Ko'k) + o'lcham (40–46 RUS)
    - ProductPhoto (27 fotosurat)
"""

from django.db.models import (
    Model, CharField, SlugField, TextField,
    DecimalField, PositiveIntegerField, PositiveSmallIntegerField,
    BooleanField, DateTimeField, URLField,
    ForeignKey, Index, CASCADE, SET_NULL,
)
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse


class Product(Model):
    """
    Mahsulot kartochkasi.

    Narx tuzilmasi (detail sahifadan):
        original_price   = 399 000   ← qizil chizilgan, -33% badge
        price            = 269 100   ← asosiy ko'rsatiladigan (ko'k)
        uzum_card_price  = 299 000   ← "Uzum kartasiz" matn bilan

    Nasiya:
        installment_monthly = 29 900   ← "29 900 so'm × 12 oy"
        installment_months  = 12       ← eng foydali variant
    """

    # ── Asosiy ───────────────────────────────────────────────────────────────
    title = CharField(max_length=500)
    slug = SlugField(
        max_length=550,
        unique=True,
        allow_unicode=True,
    )
    description = TextField(blank=True, null=True)

    category = ForeignKey(
        'categories.Category',
        on_delete=SET_NULL,
        null=True,
        related_name='products',
    )
    shop = ForeignKey(
        'shops.Shop',
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )

    # ── Narxlar (UZS) ────────────────────────────────────────────────────────
    price = DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Asosiy sotuv narxi — ko'k rangda (269 100)",
    )
    original_price = DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Chegirmasiz narx — chiziq bilan (399 000). "
                  "discount_percent shu fielddan hisoblanadi.",
    )
    uzum_card_price = DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Uzum kartasiz narx (299 000)",
    )

    # ── Nasiya ────────────────────────────────────────────────────────────────
    installment_monthly = DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Oylik to'lov: '29 900 so'm × 12 oy' dagi 29 900",
    )
    installment_months = PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Eng qulay nasiya muddati (oy): 3 | 6 | 12 | 24",
    )

    # ── Statistika ────────────────────────────────────────────────────────────
    rating = DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    reviews_count = PositiveIntegerField(
        default=0,
        help_text="253 sharhlar",
    )
    orders_count = PositiveIntegerField(
        default=0,
        help_text="1000+ buyurtma — frontendda '1000+' ko'rsatiladi",
    )
    weekly_buyers = PositiveIntegerField(
        default=0,
        help_text="'Bu haftada 44 kishi sotib oldi'",
    )

    # ── Yetkazish ─────────────────────────────────────────────────────────────
    delivery_text = CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="'Ertaga yetkazib beramiz'",
    )

    # ── Holat ─────────────────────────────────────────────────────────────────
    is_active    = BooleanField(default=True)
    is_available = BooleanField(default=True)
    is_adult     = BooleanField(default=False)
    is_price_guaranteed = BooleanField(
        default=False,
        help_text="'ARZON NARX KAFOLATI' — sariq badge",
    )
    max_purchase_qty = PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="'3 dona xarid qilish mumkin' — None = cheksiz",
    )

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        indexes = [
            Index(fields=['category', 'is_active'],    name='prod_cat_active_idx'),
            Index(fields=['shop',     'is_active'],     name='prod_shop_active_idx'),
            Index(fields=['price'],                     name='prod_price_idx'),
            Index(fields=['rating'],                    name='prod_rating_idx'),
            Index(fields=['orders_count'],              name='prod_orders_idx'),
            Index(fields=['is_available', 'is_active'], name='prod_avail_idx'),
            Index(fields=['created_at'],                name='prod_created_idx'),
        ]

    def __str__(self):
        return self.title[:80]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)[:500]
            candidate, n = base, 1
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{n}"
                n += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    # ── Computed ──────────────────────────────────────────────────────────────

    @property
    def discount_percent(self) -> int:
        """
        original_price=399 000, price=269 100 → 33
        Listing da '-33%' badge sifatida ko'rsatiladi.
        """
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0

    @property
    def main_photo(self):
        return self.photos.filter(is_main=True).first() or self.photos.first()

    def get_frontend_url(self, lang: str = 'uz') -> str:
        return f"/{lang}/product/{self.slug}-{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse('product-detail', kwargs={'pk': self.pk})


# ─────────────────────────────────────────────────────────────────────────────

class ProductPhoto(Model):
    """
    Rasmlar galereya — detail sahifada '27 fotosurat'.
    Listing da faqat main_photo ko'rsatiladi.
    """
    product    = ForeignKey(Product, on_delete=CASCADE, related_name='photos')
    url        = URLField(max_length=500)
    is_main    = BooleanField(default=False)
    sort_order = PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Rasm"
        verbose_name_plural = "Rasmlar"
        ordering = ['sort_order']

    def __str__(self):
        return f"#{self.sort_order} — {self.product.title[:40]}"


# ─────────────────────────────────────────────────────────────────────────────

class ProductAttribute(Model):
    """
    Texnik xususiyatlar — detail sahifada jadval.

    Poyabzal misoli:
        title="Material"     value="Zamsha"
        title="Mavsum"       value="Bahor-yoz"
        title="O'lcham turi" value="RUS"
    """
    product    = ForeignKey(Product, on_delete=CASCADE, related_name='attributes')
    title      = CharField(max_length=255)
    value      = CharField(max_length=500)
    sort_order = PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Xususiyat"
        verbose_name_plural = "Xususiyatlar"
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.title}: {self.value}"


# ─────────────────────────────────────────────────────────────────────────────

class SKU(Model):
    """
    Bitta rang + o'lcham kombinatsiyasi.

    Detail sahifadan:
        Rang:        Ko'k  (thumbnail bosib tanlanadi)
        O'lcham RUS: 40 | 41 | 42 | 43 | 44 | 45 | 46

    Har bir (Ko'k+40), (Ko'k+41)... alohida SKU.
    Narx va stok SKU bo'yicha farqlanishi mumkin.
    """
    product          = ForeignKey(Product, on_delete=CASCADE, related_name='skus')
    price            = DecimalField(max_digits=14, decimal_places=2)
    original_price   = DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    available_amount = PositiveIntegerField(default=0)
    is_available     = BooleanField(default=True)

    class Meta:
        verbose_name = "SKU"
        verbose_name_plural = "SKU lar"

    def __str__(self):
        attrs = " / ".join(a.value for a in self.attributes.all())
        return f"{self.product.title[:40]} [{attrs}]"

    @property
    def discount_percent(self) -> int:
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0


# ─────────────────────────────────────────────────────────────────────────────

class SKUAttribute(Model):
    """
    SKU xususiyati — rang yoki o'lcham.

    attr_type='color' → "Rang: Ko'k"      — thumbnail doiralari
    attr_type='size'  → "O'lcham RUS: 40" — raqamli tugmalar

    color_hex listing sahifasidagi rang filtri doiralari uchun ham ishlatiladi.
    """

    ATTR_TYPE_CHOICES = [
        ('color', 'Rang'),
        ('size',  "O'lcham"),
        ('other', 'Boshqa'),
    ]

    sku       = ForeignKey(SKU, on_delete=CASCADE, related_name='attributes')
    attr_type = CharField(max_length=10, choices=ATTR_TYPE_CHOICES, default='other')
    title     = CharField(max_length=100, help_text="'Rang', 'Erkaklar poyabzali o\\'lchami RUS'")
    value     = CharField(max_length=100, help_text="'Ko\\'k', '40'")
    color_hex = CharField(
        max_length=7,
        blank=True,
        null=True,
        help_text="Faqat rang uchun: '#1A3C6B' — listing filtri va detail thumbnail",
    )

    class Meta:
        verbose_name = "SKU xususiyati"
        verbose_name_plural = "SKU xususiyatlari"

    def __str__(self):
        return f"{self.title}: {self.value}"