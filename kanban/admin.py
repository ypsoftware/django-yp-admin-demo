"""Kanban admin — htmx changelist + multiple filter types + multi-select label filter."""

from django.contrib import admin

from django_yp_admin import ModelAdmin
from django_yp_admin.contrib.ordered_admin import OrderedAdmin
from django_yp_admin.filters import (
    ChoicesDropdownFilter,
    DateRangeFilter,
    MultiSelectFilter,
    RelatedDropdownFilter,
)

from .models import Board, Label, Task


@admin.register(Board)
class BoardAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Label)
class LabelAdmin(ModelAdmin):
    list_display = ["name", "color"]
    search_fields = ["name"]


class MultiSelectLabelsFilter(MultiSelectFilter):
    title = "labels"
    parameter_name = "labels"

    def lookups(self, request, model_admin):
        return [(label.pk, label.name) for label in Label.objects.all()]

    def queryset(self, request, queryset):
        values = self.value()
        if not values:
            return queryset
        return queryset.filter(labels__in=values).distinct()


@admin.register(Task)
class TaskAdmin(OrderedAdmin, ModelAdmin):
    htmx_changelist = True

    list_display = ["title", "board", "status", "priority", "assignee", "due_date", "order"]
    list_filter = [
        ("status", ChoicesDropdownFilter),
        ("priority", ChoicesDropdownFilter),
        ("board", RelatedDropdownFilter),
        ("assignee", RelatedDropdownFilter),
        ("due_date", DateRangeFilter),
        MultiSelectLabelsFilter,
    ]
    search_fields = ["title"]
    autocomplete_fields = ["board", "assignee", "labels"]
