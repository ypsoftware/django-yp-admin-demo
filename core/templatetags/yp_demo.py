"""Local template helpers — work around upstream yp-admin template bugs."""

from django import template

register = template.Library()


@register.filter
def model_app_label(model):
    """Return ``model._meta.app_label`` from a template (Django bans leading underscore)."""

    return model._meta.app_label


@register.filter
def model_name(model):
    """Return ``model._meta.model_name`` from a template (Django bans leading underscore)."""

    return model._meta.model_name
