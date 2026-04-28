"""Kanban models — Boards, Labels, Tasks (ordered per board+status)."""

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify

from django_yp_admin.models import OrderedModel


class Board(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Label(models.Model):
    name = models.CharField(max_length=60, unique=True)
    color = models.CharField(max_length=16, default="#888")

    def __str__(self):
        return self.name


class Task(OrderedModel):
    STATUS_CHOICES = [
        ("todo", "To do"),
        ("in_progress", "In progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("med", "Medium"),
        ("high", "High"),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    title = models.CharField(max_length=200)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kanban_tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="med")
    labels = models.ManyToManyField(Label, blank=True, related_name="tasks")

    order_with_respect_to = ("board", "status")

    def _wrt_filter_kwargs(self):
        # OrderedModel default appends `_id` to every wrt field, but `status`
        # is a CharField (not FK). Override to filter by raw value for status.
        return {
            "board_id": self.board_id,
            "status": self.status,
        }

    class Meta(OrderedModel.Meta):
        constraints = [
            UniqueConstraint(
                fields=["board", "status", "order"],
                name="task_board_status_order_uniq",
            ),
        ]

    def __str__(self):
        return self.title
