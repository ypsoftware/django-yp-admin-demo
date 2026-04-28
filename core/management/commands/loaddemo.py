"""Idempotent demo fixtures for the new apps (cookbook, music, survey, kanban).

Uses get_or_create so re-running is a no-op. Keep this small and fast — just
enough realistic data to populate screenshots.
"""

from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from cookbook.models import Cuisine, Ingredient, Recipe, Step
from kanban.models import Board, Label, Task
from music.models import Album, Artist, Track
from survey.models import Choice, Question, Survey


class Command(BaseCommand):
    help = "Load idempotent demo fixtures for cookbook, music, survey, kanban."

    def handle(self, *args, **opts):
        self._cookbook()
        self._music()
        self._survey()
        self._kanban()
        self.stdout.write(self.style.SUCCESS("loaddemo complete."))

    # ---------------------------------------------------------------- cookbook
    def _cookbook(self):
        cuisines = {}
        for name in ["Italian", "Japanese", "Mexican", "Indian"]:
            cuisines[name], _ = Cuisine.objects.get_or_create(slug=slugify(name), defaults={"name": name})

        recipes_data = [
            ("Classic Carbonara", "Italian", "medium", 25, 4),
            ("Vegetable Sushi Rolls", "Japanese", "hard", 60, 2),
            ("Chicken Tacos", "Mexican", "easy", 20, 4),
            ("Butter Chicken", "Indian", "medium", 45, 4),
            ("Margherita Pizza", "Italian", "medium", 35, 2),
        ]
        for title, cuisine_name, diff, t, servings in recipes_data:
            recipe, created = Recipe.objects.get_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "cuisine": cuisines[cuisine_name],
                    "difficulty": diff,
                    "cook_time_minutes": t,
                    "servings": servings,
                    "body": f"A delicious {cuisine_name.lower()} dish.",
                },
            )
            if created:
                for i, (qty, name) in enumerate([("200g", "main ingredient"), ("2", "eggs"), ("100g", "cheese")]):
                    Ingredient.objects.create(recipe=recipe, name=name, quantity=qty, order=i)
                for i, instr in enumerate(["Prepare ingredients.", "Cook over medium heat.", "Serve hot."]):
                    Step.objects.create(recipe=recipe, instruction=instr, order=i)

    # ------------------------------------------------------------------ music
    def _music(self):
        artists_data = [
            ("Daft Punk", "Pioneers of French house electronic music."),
            ("Miles Davis", "Iconic jazz trumpeter and bandleader."),
            ("The Beatles", "Legendary rock band from Liverpool."),
            ("Adele", "British pop singer-songwriter."),
        ]
        artists = {}
        for name, bio in artists_data:
            artists[name], _ = Artist.objects.get_or_create(slug=slugify(name), defaults={"name": name, "bio": bio})

        albums_data = [
            ("Discovery", "Daft Punk", date(2001, 3, 12), "electronic"),
            ("Kind of Blue", "Miles Davis", date(1959, 8, 17), "jazz"),
            ("Abbey Road", "The Beatles", date(1969, 9, 26), "rock"),
            ("25", "Adele", date(2015, 11, 20), "pop"),
        ]
        for title, artist_name, rdate, genre in albums_data:
            album, created = Album.objects.get_or_create(
                slug=slugify(title) or f"album-{artist_name}",
                defaults={
                    "title": title,
                    "artist": artists[artist_name],
                    "release_date": rdate,
                    "genre": genre,
                },
            )
            if created:
                for i, t in enumerate([("Track One", 210), ("Track Two", 180), ("Track Three", 240)]):
                    Track.objects.create(album=album, title=t[0], duration_seconds=t[1], order=i)

    # ----------------------------------------------------------------- survey
    def _survey(self):
        now = timezone.now()
        surveys_data = [
            ("Customer Satisfaction Q1", "open", now, now + timedelta(days=14)),
            ("Product Feedback", "draft", None, None),
            ("Annual Engagement Survey", "closed", now - timedelta(days=60), now - timedelta(days=30)),
        ]
        for title, status, opens_at, closes_at in surveys_data:
            survey, created = Survey.objects.get_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "status": status,
                    "opens_at": opens_at,
                    "closes_at": closes_at,
                },
            )
            if created:
                q1 = Question.objects.create(survey=survey, text="How satisfied are you?", kind="single", order=0)
                for i, lbl in enumerate(["Very", "Somewhat", "Not at all"]):
                    Choice.objects.create(question=q1, label=lbl, order=i)
                q2 = Question.objects.create(survey=survey, text="Which features do you use?", kind="multi", order=1)
                for i, lbl in enumerate(["Reports", "Dashboard", "API"]):
                    Choice.objects.create(question=q2, label=lbl, order=i)
                Question.objects.create(survey=survey, text="Any other comments?", kind="text", order=2)

    # ----------------------------------------------------------------- kanban
    def _kanban(self):
        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()

        boards = {}
        for name in ["Engineering", "Marketing", "Operations"]:
            boards[name], _ = Board.objects.get_or_create(slug=slugify(name), defaults={"name": name})

        labels = {}
        for name, color in [("bug", "#e53935"), ("feature", "#43a047"), ("urgent", "#fb8c00"), ("docs", "#1e88e5")]:
            labels[name], _ = Label.objects.get_or_create(name=name, defaults={"color": color})

        tasks_data = [
            ("Engineering", "todo", "Fix login redirect", "high", ["bug", "urgent"]),
            ("Engineering", "in_progress", "Implement dark mode", "med", ["feature"]),
            ("Engineering", "review", "Refactor auth module", "med", ["feature"]),
            ("Engineering", "done", "Update README", "low", ["docs"]),
            ("Marketing", "todo", "Plan Q2 campaign", "high", ["feature"]),
            ("Marketing", "in_progress", "Write blog post", "med", ["docs"]),
            ("Operations", "todo", "Renew SSL cert", "high", ["urgent"]),
        ]
        # Use board+status grouping to avoid order collisions on re-run.
        for board_name, status, title, priority, label_names in tasks_data:
            task, created = Task.objects.get_or_create(
                board=boards[board_name],
                title=title,
                defaults={
                    "status": status,
                    "priority": priority,
                    "assignee": admin_user,
                    "due_date": date.today() + timedelta(days=7),
                },
            )
            if created:
                task.labels.set([labels[n] for n in label_names])
