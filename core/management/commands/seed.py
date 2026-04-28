"""Idempotent seed command — wipes domain data and re-creates demo content."""

from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from blog.models import Author, BlogPost, Category, Comment, Tag
from core.models import MenuItem, SiteConfig
from shop.models import FAQ, Brand, Product, ProductCategory

try:
    from faker import Faker

    fake = Faker("es_ES")
except ImportError:  # pragma: no cover
    fake = None


SPANISH_NAMES = ["Sofía García", "Mateo Rodríguez", "Lucía Fernández"]
TAGS = [
    ("Python", "#3776ab"),
    ("Django", "#092e20"),
    ("HTMX", "#3366cc"),
    ("AI", "#ff6f61"),
    ("DevOps", "#2496ed"),
    ("Frontend", "#f7df1e"),
    ("Backend", "#6a1b9a"),
    ("Cloud", "#ff9900"),
]
ROOT_CATS = ["Tech", "Lifestyle", "Business"]
SUB_CATS = [("AI", "Tech"), ("Travel", "Lifestyle")]
BRANDS = ["Acme", "Globex", "Initech"]
PRODUCT_ROOT_CATS = ["Electronics", "Books"]
PRODUCT_SUB_CATS = [("Laptops", "Electronics"), ("Fiction", "Books")]
STATUSES = ["draft", "scheduled", "published"]
FAQ_DATA = [
    ("How long does shipping take?", "Usually 3-5 business days.", "shipping"),
    ("What is your return policy?", "30 days, no questions asked.", "returns"),
    ("Which payment methods do you accept?", "All major cards, PayPal.", "payment"),
    ("Do you ship internationally?", "Yes, to 40+ countries.", "shipping"),
    ("Can I cancel an order?", "Yes, within 1 hour of placing it.", "returns"),
    ("Is my data secure?", "All payments use TLS + tokenization.", "general"),
]


class Command(BaseCommand):
    help = "Seed the demo database with realistic sample data."

    def handle(self, *args, **opts):
        self.stdout.write("Wiping existing demo data...")
        Comment.objects.all().delete()
        BlogPost.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Author.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Brand.objects.all().delete()
        FAQ.objects.all().delete()
        MenuItem.objects.all().delete()
        # SingletonQuerySet refuses bulk delete — use raw SQL to wipe.
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {SiteConfig._meta.db_table}")

        # Superuser
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write("  + superuser admin/admin")

        # SiteConfig
        SiteConfig.objects.create(
            site_name="yp-admin Demo",
            contact_email="hello@example.com",
            default_seo_description="A demo site showcasing django-yp-admin features.",
        )

        # Menu items (nested)
        home = MenuItem.objects.create(label="Home", url="/")
        blog = MenuItem.objects.create(label="Blog", url="/blog/")
        MenuItem.objects.create(label="Latest", url="/blog/latest/", parent=blog)
        MenuItem.objects.create(label="Categories", url="/blog/categories/", parent=blog)
        shop = MenuItem.objects.create(label="Shop", url="/shop/")
        MenuItem.objects.create(label="Products", url="/shop/products/", parent=shop)
        MenuItem.objects.create(label="Brands", url="/shop/brands/", parent=shop)
        MenuItem.objects.create(label="About", url="/about/")
        # Note: Home/Blog/Shop/About are 4 root + 4 children = 8 total; spec says 6
        # Trim to spec: keep Home + Blog (with 2 sub) + Shop (with 2 sub) + About via earlier deletion of one
        # Actually spec: 6 menu items total (Home, Blog [Latest, Categories], Shop [Products, Brands], About)
        # That equals 7. Re-reading: list says 6 but enumerates 7. Leave as-is.
        _ = home

        # Authors
        authors = []
        bios = [
            "Escritora apasionada por la tecnología y los gatos.",
            "Ingeniero de software con 10 años de experiencia en backend.",
            "Diseñadora UX que ama los detalles tipográficos.",
        ]
        emails = ["sofia@example.com", "mateo@example.com", "lucia@example.com"]
        for name, bio, email in zip(SPANISH_NAMES, bios, emails):
            authors.append(Author.objects.create(name=name, bio=bio, email=email, slug=slugify(name)))

        # Tags
        tags = [Tag.objects.create(name=n, color=c, slug=slugify(n)) for n, c in TAGS]

        # Categories
        cat_map = {}
        for n in ROOT_CATS:
            cat_map[n] = Category.objects.create(name=n, slug=slugify(n))
        for child, parent in SUB_CATS:
            cat_map[child] = Category.objects.create(name=child, slug=slugify(child), parent=cat_map[parent])

        # Blog posts
        posts = []
        for i in range(12):
            title = fake.sentence(nb_words=6).rstrip(".") if fake else f"Post número {i + 1}"
            body = fake.paragraph(nb_sentences=8) if fake else "Lorem ipsum dolor sit amet. " * 10
            status = random.choice(STATUSES)
            published_at = timezone.now() - timedelta(days=random.randint(0, 90)) if status != "draft" else None
            slug = slugify(title)[:200] + f"-{i}"
            post = BlogPost.objects.create(
                title=title,
                slug=slug,
                author=random.choice(authors),
                category=random.choice(list(cat_map.values())),
                body=body,
                status=status,
                published_at=published_at,
                view_count=random.randint(0, 5000),
            )
            post.tags.set(random.sample(tags, k=random.randint(1, 4)))
            posts.append(post)

        # Comments (with ~20% threaded)
        comments = []
        for _ in range(30):
            post = random.choice(posts)
            parent = None
            if comments and random.random() < 0.2:
                parent_candidate = random.choice(comments)
                if parent_candidate.post_id == post.pk:
                    parent = parent_candidate
            author_name = fake.name() if fake else f"Anon{random.randint(1, 999)}"
            body = fake.sentence() if fake else "Great post!"
            comments.append(Comment.objects.create(post=post, parent=parent, author_name=author_name, body=body))

        # Brands
        brand_objs = [Brand.objects.create(name=n, slug=slugify(n)) for n in BRANDS]

        # Product categories
        pcat_map = {}
        for n in PRODUCT_ROOT_CATS:
            pcat_map[n] = ProductCategory.objects.create(name=n, slug=slugify(n))
        for child, parent in PRODUCT_SUB_CATS:
            pcat_map[child] = ProductCategory.objects.create(name=child, slug=slugify(child), parent=pcat_map[parent])

        # Products
        for i in range(20):
            name = fake.catch_phrase() if fake else f"Product {i + 1}"
            sku = f"SKU-{i + 1:04d}"
            slug = slugify(name)[:180] + f"-{i}"
            Product.objects.create(
                sku=sku,
                name=name,
                slug=slug,
                brand=random.choice(brand_objs),
                category=random.choice(list(pcat_map.values())),
                price=Decimal(random.randint(10, 2000)),
                stock=random.randint(0, 100),
                is_active=random.random() > 0.1,
            )

        # FAQs
        for q, a, c in FAQ_DATA:
            FAQ.objects.create(question=q, answer=a, category=c)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded: 1 SiteConfig, {MenuItem.objects.count()} MenuItems, "
                f"{len(authors)} Authors, {len(tags)} Tags, {len(cat_map)} Categories, "
                f"{len(posts)} BlogPosts, {len(comments)} Comments, "
                f"{len(brand_objs)} Brands, {len(pcat_map)} ProductCategories, "
                f"{Product.objects.count()} Products, {FAQ.objects.count()} FAQs."
            )
        )
