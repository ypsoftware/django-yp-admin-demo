"""Cookbook models — Cuisines, Recipes (versioned), Ingredients & Steps (sortable)."""

from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify
from simple_history.models import HistoricalRecords

from django_yp_admin.models import OrderedModel


class Cuisine(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.PROTECT, related_name="recipes")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="easy")
    cook_time_minutes = models.PositiveIntegerField(default=30)
    servings = models.PositiveIntegerField(default=4)
    body = models.TextField(blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)


class Ingredient(OrderedModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    name = models.CharField(max_length=200)
    quantity = models.CharField(max_length=80, blank=True)

    order_with_respect_to = "recipe"

    class Meta(OrderedModel.Meta):
        constraints = [
            UniqueConstraint(fields=["recipe", "order"], name="ingredient_recipe_order_uniq"),
        ]

    def __str__(self):
        return f"{self.quantity} {self.name}".strip()


class Step(OrderedModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    instruction = models.TextField()

    order_with_respect_to = "recipe"

    class Meta(OrderedModel.Meta):
        constraints = [
            UniqueConstraint(fields=["recipe", "order"], name="step_recipe_order_uniq"),
        ]

    def __str__(self):
        return f"Step {self.order} of {self.recipe_id}"
