"""Music models — Artists, Albums, Tracks (sortable inline)."""

from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify

from django_yp_admin.models import OrderedModel


class Artist(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Album(models.Model):
    GENRE_CHOICES = [
        ("rock", "Rock"),
        ("pop", "Pop"),
        ("jazz", "Jazz"),
        ("electronic", "Electronic"),
        ("classical", "Classical"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT, related_name="albums")
    release_date = models.DateField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default="other")
    cover = models.ImageField(upload_to="albums/", blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)


class Track(OrderedModel):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="tracks")
    title = models.CharField(max_length=200)
    duration_seconds = models.PositiveIntegerField(default=0)

    order_with_respect_to = "album"

    class Meta(OrderedModel.Meta):
        constraints = [
            UniqueConstraint(fields=["album", "order"], name="track_album_order_uniq"),
        ]

    def __str__(self):
        return self.title
