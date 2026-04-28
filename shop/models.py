"""Shop models — brands, ordered categories/products, sortable inline images, ordered FAQs."""

from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify

from django_yp_admin.models import OrderedModel


class Brand(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductCategory(OrderedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    order_with_respect_to = "parent"

    class Meta(OrderedModel.Meta):
        verbose_name_plural = "Product categories"
        constraints = [
            UniqueConstraint(
                fields=["parent", "order"],
                name="productcategory_parent_order_uniq",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(OrderedModel):
    sku = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    order_with_respect_to = "category"

    class Meta(OrderedModel.Meta):
        constraints = [
            UniqueConstraint(
                fields=["category", "order"],
                name="product_category_order_uniq",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:200]
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Sortable inline — uses SortableInline mixin in admin."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.caption or f"image #{self.pk}"


class FAQ(OrderedModel):
    CATEGORY_CHOICES = [
        ("shipping", "Shipping"),
        ("returns", "Returns"),
        ("payment", "Payment"),
        ("general", "General"),
    ]

    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="general")

    class Meta(OrderedModel.Meta):
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        constraints = [
            UniqueConstraint(fields=["order"], name="faq_order_uniq"),
        ]

    def __str__(self):
        return self.question
