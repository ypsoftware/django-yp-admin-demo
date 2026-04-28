"""Survey models — versioned Surveys with ordered Questions and ordered Choices (3-level nested)."""

from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify
from simple_history.models import HistoricalRecords

from django_yp_admin.models import OrderedModel


class Survey(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    opens_at = models.DateTimeField(null=True, blank=True)
    closes_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)


class Question(OrderedModel):
    KIND_CHOICES = [
        ("single", "Single choice"),
        ("multi", "Multiple choice"),
        ("text", "Text"),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=400)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="single")

    order_with_respect_to = "survey"

    class Meta(OrderedModel.Meta):
        constraints = [
            UniqueConstraint(fields=["survey", "order"], name="question_survey_order_uniq"),
        ]

    def __str__(self):
        return self.text


class Choice(OrderedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField(max_length=200)

    order_with_respect_to = "question"

    class Meta(OrderedModel.Meta):
        constraints = [
            UniqueConstraint(fields=["question", "order"], name="choice_question_order_uniq"),
        ]

    def __str__(self):
        return self.label
