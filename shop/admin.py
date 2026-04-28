"""Shop admin — demonstrates ordered admin, sortable inlines, import-export, range filters."""

from django.contrib import admin

from django_yp_admin import ModelAdmin, SortableInline
from django_yp_admin.contrib.ordered_admin import OrderedAdmin
from django_yp_admin.filters import (
    ChoicesDropdownFilter,
    DateRangeFilter,
    FieldDropdownFilter,
    NumericRangeFilter,
    RelatedDropdownFilter,
)

try:
    from django_yp_admin.contrib.import_export_admin import ImportExportAdmin
except ImportError:  # pragma: no cover
    ImportExportAdmin = None

from .models import FAQ, Brand, Product, ProductCategory, ProductImage


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductCategory)
class ProductCategoryAdmin(OrderedAdmin, ModelAdmin):
    list_display = ["name", "parent", "slug", "order"]
    search_fields = ["name"]
    autocomplete_fields = ["parent"]
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(SortableInline, admin.TabularInline):
    model = ProductImage
    extra = 0
    sortable_field = "order"
    fields = ("image", "caption", "order")


# Build base classes for ProductAdmin dynamically depending on import-export availability.
_PRODUCT_BASES = (OrderedAdmin,)
if ImportExportAdmin is not None:
    _PRODUCT_BASES = (ImportExportAdmin,) + _PRODUCT_BASES
_PRODUCT_BASES = _PRODUCT_BASES + (ModelAdmin,)


@admin.register(Product)
class ProductAdmin(*_PRODUCT_BASES):
    versioning = True
    htmx_changelist = True

    list_display = ["sku", "name", "brand", "category", "price", "stock", "is_active"]
    list_filter = [
        ("price", NumericRangeFilter),
        ("created_at", DateRangeFilter),
        ("brand", RelatedDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("is_active", FieldDropdownFilter),
    ]
    search_fields = ["sku", "name"]
    autocomplete_fields = ["brand", "category"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(FAQ)
class FAQAdmin(OrderedAdmin):
    list_display = ["question", "category", "order"]
    list_filter = [("category", ChoicesDropdownFilter)]
    search_fields = ["question", "answer"]
