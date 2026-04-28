"""Survey admin — 3-level nested inlines with versioning + filters."""

from django.contrib import admin

from django_yp_admin import ModelAdmin, NestedInline, SortableInline
from django_yp_admin.contrib.ordered_admin import OrderedAdmin
from django_yp_admin.filters import (
    ChoicesDropdownFilter,
    DateRangeFilter,
)

from .models import Choice, Question, Survey


class ChoiceInline(NestedInline, SortableInline, admin.TabularInline):
    model = Choice
    extra = 0
    sortable_field = "order"
    fields = ("label", "order")


class QuestionInline(NestedInline, SortableInline, admin.TabularInline):
    model = Question
    extra = 0
    sortable_field = "order"
    fields = ("text", "kind", "order")
    inlines = [ChoiceInline]


@admin.register(Survey)
class SurveyAdmin(ModelAdmin):
    versioning = True
    htmx_changelist = True

    list_display = ["title", "status", "opens_at", "closes_at"]
    list_filter = [
        ("status", ChoicesDropdownFilter),
        ("opens_at", DateRangeFilter),
    ]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(OrderedAdmin, ModelAdmin):
    list_display = ["text", "survey", "kind", "order"]
    list_filter = [("kind", ChoicesDropdownFilter)]
    search_fields = ["text"]
    autocomplete_fields = ["survey"]
    inlines = [ChoiceInline]
