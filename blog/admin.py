"""Blog admin — demonstrates autocomplete, nested inlines, versioning, htmx, filters."""

from django.contrib import admin
from django.utils.html import format_html

from django_yp_admin import ModelAdmin, NestedInline
from django_yp_admin.filters import (
    ChoicesDropdownFilter,
    DateRangeFilter,
    MultiSelectFilter,
    RelatedDropdownFilter,
)

from .models import Author, BlogPost, Category, Comment, Tag


@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ["name", "email", "slug"]
    search_fields = ["name", "email", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ["name", "color_swatch", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:1em;height:1em;background:{};'
            'border:1px solid #ccc;vertical-align:middle"></span> {}',
            obj.color,
            obj.color,
        )

    color_swatch.short_description = "Color"


class CategoryInline(NestedInline, admin.TabularInline):
    """Self-referencing inline for subcategories."""

    model = Category
    fk_name = "parent"
    extra = 0
    fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "parent", "slug"]
    search_fields = ["name", "slug"]
    autocomplete_fields = ["parent"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryInline]


class CommentInline(NestedInline, admin.TabularInline):
    """Comments on a blog post."""

    model = Comment
    fk_name = "post"
    extra = 0
    fields = ("author_name", "parent", "body")
    autocomplete_fields = ["parent"]


class MultiSelectTagsFilter(MultiSelectFilter):
    title = "tags"
    parameter_name = "tags"

    def lookups(self, request, model_admin):
        return [(t.pk, t.name) for t in Tag.objects.all()]

    def queryset(self, request, queryset):
        values = self.value()
        if not values:
            return queryset
        return queryset.filter(tags__in=values).distinct()


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    htmx_changelist = True
    htmx_inline_save = True
    versioning = True

    list_display = ["title", "author", "category", "status", "published_at"]
    list_filter = [
        ("status", ChoicesDropdownFilter),
        ("author", RelatedDropdownFilter),
        MultiSelectTagsFilter,
        ("category", RelatedDropdownFilter),
        ("published_at", DateRangeFilter),
    ]
    search_fields = ["title", "body"]
    autocomplete_fields = ["author", "tags", "category"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ["author_name", "post", "parent", "created_at"]
    search_fields = ["author_name", "body"]
    autocomplete_fields = ["post", "parent"]
    list_filter = [("post", RelatedDropdownFilter)]
