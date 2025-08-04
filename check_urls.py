import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def print_patterns(patterns, prefix=''):
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            print(f"\nResolver: {prefix + str(pattern.pattern)}")
            print_patterns(pattern.url_patterns, prefix=prefix + str(pattern.pattern))
        elif isinstance(pattern, URLPattern):
            print(f"Pattern: {prefix + str(pattern.pattern)}")
            if hasattr(pattern, 'callback') and pattern.callback:
                print(f"  Callback: {pattern.callback.__module__}.{pattern.callback.__name__}")
            print()

resolver = get_resolver()

# Find the API resolver
api_resolver = None
for pattern in resolver.url_patterns:
    if hasattr(pattern, 'pattern') and str(pattern.pattern) == 'api/':
        api_resolver = pattern
        break

if api_resolver:
    print("API URL Patterns:")
    print_patterns(api_resolver.url_patterns)
else:
    print("API resolver not found")