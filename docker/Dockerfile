ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

ARG DJANGO_VERSION=5.1
ARG YP_ADMIN_VERSION=0.1.0a2

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Copy demo project (excluding venv, db, media, etc — see .dockerignore)
COPY . /app/

RUN pip install --upgrade pip
RUN pip install --pre "django-yp-admin[full]==${YP_ADMIN_VERSION}"
RUN pip install "Django~=${DJANGO_VERSION}.0"
RUN pip install "Pillow>=10" "Faker>=20"

# Smoke checks: migrate + seed + check + collectstatic
RUN python manage.py makemigrations --check --dry-run || python manage.py makemigrations
RUN python manage.py migrate --noinput
RUN python manage.py seed
RUN python manage.py check
RUN python manage.py collectstatic --noinput

# Test-render the admin login + a change form via Django test client
RUN python -c "\
import django, os;\
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings');\
django.setup();\
from django.test import Client;\
from django.contrib.auth import get_user_model;\
U = get_user_model();\
u = U.objects.filter(username='admin').first();\
assert u and u.is_superuser, 'admin user missing';\
c = Client();\
assert c.login(username='admin', password='admin'), 'login failed';\
r = c.get('/admin/');\
assert r.status_code == 200, ('admin index', r.status_code);\
r = c.get('/admin/blog/blogpost/');\
assert r.status_code == 200, ('changelist', r.status_code);\
r = c.get('/admin/blog/blogpost/add/');\
assert r.status_code == 200, ('add form', r.status_code);\
from shop.models import Product;\
p = Product.objects.first();\
assert p, 'no product seeded';\
r = c.get(f'/admin/shop/product/{p.pk}/change/');\
assert r.status_code == 200, ('change form', r.status_code);\
assert b'yp-sortable-group' in r.content, 'sortable wrapper missing';\
print('OK: login, changelist, add form, change_form with sortable inline all rendered')\
"

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
