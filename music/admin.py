"""Music admin — autocomplete, range filter, sortable track inline."""

from django.contrib import admin

from django_yp_admin import ModelAdmin, SortableInline
from django_yp_admin.filters import (
    ChoicesDropdownFilter,
    DateRangeFilter,
)

from .models import Album, Artist, Track


@admin.register(Artist)
class ArtistAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name", "slug", "bio"]
    prepopulated_fields = {"slug": ("name",)}


class TrackInline(SortableInline, admin.TabularInline):
    model = Track
    extra = 0
    sortable_field = "order"
    fields = ("title", "duration_seconds", "order")


@admin.register(Album)
class AlbumAdmin(ModelAdmin):
    list_display = ["title", "artist", "genre", "release_date"]
    list_filter = [
        ("release_date", DateRangeFilter),
        ("genre", ChoicesDropdownFilter),
    ]
    search_fields = ["title"]
    autocomplete_fields = ["artist"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TrackInline]
