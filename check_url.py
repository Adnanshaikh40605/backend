from django.urls import resolve
from django.urls.exceptions import Resolver404
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

try:
    print(resolve('/api/posts/slugs/'))
except Resolver404 as e:
    print(f'Resolver404: {e}')