# django-yp-admin demo

A reference Django project that exercises every public feature of
[`django-yp-admin`](https://github.com/your-org/django-yp-admin) — htmx-powered
theme + helpers for `django.contrib.admin`.

## Quick start

```bash
git clone <this-repo> django-yp-admin-demo
cd django-yp-admin-demo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Then open <http://127.0.0.1:8000/admin/> and log in as **admin / admin**.

## Feature tour

| Feature | URL | Look for |
| --- | --- | --- |
| `SingletonModel` | `/admin/core/siteconfig/` | No add/delete buttons; redirects to single instance |
| `OrderedModel` + nested | `/admin/core/menuitem/` | Drag handle column, keyboard arrows reorder |
| `HtmxAutocomplete` (FK) | `/admin/blog/blogpost/add/` | Tom Select dropdown for author/category |
| `HtmxAutocompleteMultiple` (M2M) | `/admin/blog/blogpost/add/` | Tags multi-select |
| `NestedInline` | `/admin/blog/category/<id>/change/` | Subcategories inline |
| Versioning (yp) | `/admin/blog/blogpost/<id>/yp-history/` | Version list + revert |
| `simple-history` mirror | `/admin/blog/blogpost/<id>/history/` | Mirror history table |
| `SortableInline` | `/admin/shop/product/<id>/change/` | Drag images to reorder |
| `import-export` | `/admin/shop/product/` | Import/Export buttons in toolbar |
| Filters: dropdown / related / multiselect / range | `/admin/blog/blogpost/` and `/admin/shop/product/` | Right-side filter panel |

## Structure

- `core/` — `SiteConfig` (singleton), `MenuItem` (nested ordered)
- `blog/` — `Author`, `Tag`, `Category` (nested), `BlogPost` (versioned), `Comment` (threaded)
- `shop/` — `Brand`, `ProductCategory` (nested ordered), `Product` (versioned, sortable images, import/export), `FAQ`
- `core/management/commands/seed.py` — idempotent seeder

## Docker matrix

End-to-end validation across the supported Python x Django combos. Each combo
builds a slim Python image, installs `django-yp-admin[full]==0.1.0a2`, runs
`migrate` + `seed` + `check` + `collectstatic`, and renders the admin login,
a changelist, an add form, and a sortable-inline change form via the Django
test client — catching runtime template bugs the unit suite misses.

```bash
./docker/test-matrix.sh 2>&1 | tee docker/matrix-results.log
```

Matrix:

| Python | Django |
| --- | --- |
| 3.11 | 4.2 |
| 3.11 | 5.0 |
| 3.12 | 5.0 |
| 3.12 | 5.1 |
| 3.13 | 5.1 |

Override the version with `YP_ADMIN_VERSION=0.1.0aN ./docker/test-matrix.sh`.

## Reset

```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed
```
