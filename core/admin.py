"""Core admin registrations."""

from django.contrib import admin

from django_yp_admin.contrib.ordered_admin import OrderedAdmin
from django_yp_admin.contrib.solo_admin import SingletonModelAdmin

from .models import MenuItem, SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(SingletonModelAdmin):
    list_display = ("site_name", "contact_email", "maintenance_mode")
    fieldsets = (
        (None, {"fields": ("site_name", "contact_email", "logo")}),
        ("SEO", {"fields": ("default_seo_description",)}),
        ("Status", {"fields": ("maintenance_mode",)}),
    )


@admin.register(MenuItem)
class MenuItemAdmin(OrderedAdmin):
    list_display = ("label", "parent", "url", "is_external")
    list_filter = ("is_external", "parent")
    search_fields = ("label", "url")
    autocomplete_fields = ("parent",)
