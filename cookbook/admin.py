"""Cookbook admin — versioned recipes, sortable ingredient & step inlines."""

from django.contrib import admin

from django_yp_admin import ModelAdmin, SortableInline
from django_yp_admin.filters import (
    ChoicesDropdownFilter,
    NumericRangeFilter,
)

from .models import Cuisine, Ingredient, Recipe, Step


@admin.register(Cuisine)
class CuisineAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class IngredientInline(SortableInline, admin.TabularInline):
    model = Ingredient
    extra = 0
    sortable_field = "order"
    fields = ("name", "quantity", "order")


class StepInline(SortableInline, admin.TabularInline):
    model = Step
    extra = 0
    sortable_field = "order"
    fields = ("instruction", "order")


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    versioning = True
    htmx_changelist = True

    list_display = ["title", "cuisine", "difficulty", "cook_time_minutes", "servings"]
    list_filter = [
        ("difficulty", ChoicesDropdownFilter),
        ("cook_time_minutes", NumericRangeFilter),
    ]
    search_fields = ["title", "body"]
    autocomplete_fields = ["cuisine"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [IngredientInline, StepInline]
