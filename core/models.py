"""Core models — site-wide singleton config and ordered menu items."""

from django.db import models
from django.db.models import UniqueConstraint

from django_yp_admin.models import OrderedModel, SingletonModel


class SiteConfig(SingletonModel):
    """Singleton — exactly one row, edited from the admin."""

    site_name = models.CharField(max_length=100, default="Demo Site")
    contact_email = models.EmailField(default="hello@example.com")
    default_seo_description = models.TextField(blank=True)
    maintenance_mode = models.BooleanField(default=False)
    logo = models.ImageField(upload_to="site/", blank=True, null=True)

    class Meta:
        verbose_name = "Site configuration"
        verbose_name_plural = "Site configuration"

    def __str__(self):
        return self.site_name


class MenuItem(OrderedModel):
    """Nested ordered menu — order_with_respect_to=parent."""

    label = models.CharField(max_length=80)
    url = models.CharField(max_length=200, blank=True)
    is_external = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    order_with_respect_to = "parent"

    class Meta(OrderedModel.Meta):
        constraints = [
            UniqueConstraint(fields=["parent", "order"], name="menuitem_parent_order_uniq"),
        ]

    def __str__(self):
        return self.label
