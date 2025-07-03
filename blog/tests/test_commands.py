from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from django.utils.text import slugify
from io import StringIO
from unittest.mock import patch

from blog.models import BlogPost

class CommandTestCase(TestCase):
    def setUp(self):
        # Create test posts with different slug conditions
        self.post1 = BlogPost.objects.create(
            title="Test Post With Null Slug",
            slug=None,
            content="Test content"
        )
        self.post2 = BlogPost.objects.create(
            title="Test Post With Empty Slug",
            slug="",
            content="Test content"
        )
        self.post3 = BlogPost.objects.create(
            title="Test Post With Valid Slug",
            slug="valid-slug",
            content="Test content"
        )

    def test_fix_slugs_all_mode(self):
        # Test the fix_slugs command with all mode
        out = StringIO()
        
        # Call command with all mode
        call_command('fix_slugs', mode='all', stdout=out)
        
        # Get output
        output = out.getvalue()
        
        # Verify command ran successfully
        self.assertIn('Fixed', output)
        
        # Refresh from database
        self.post1.refresh_from_db()
        self.post2.refresh_from_db()
        self.post3.refresh_from_db()
        
        # Verify slugs are fixed
        self.assertEqual(self.post1.slug, slugify(self.post1.title))
        self.assertEqual(self.post2.slug, slugify(self.post2.title))
        self.assertEqual(self.post3.slug, "valid-slug")  # unchanged
        
    def test_fix_slugs_null_mode(self):
        # Test the fix_slugs command with null mode
        out = StringIO()
        
        # Call command with null mode
        call_command('fix_slugs', mode='null', stdout=out)
        
        # Refresh from database
        self.post1.refresh_from_db()
        self.post2.refresh_from_db()
        
        # Verify only null slug is fixed
        self.assertEqual(self.post1.slug, slugify(self.post1.title))
        self.assertEqual(self.post2.slug, "")  # should remain empty
        
    def test_fix_slugs_dry_run(self):
        # Test the fix_slugs command with dry run
        out = StringIO()
        
        # Call command with dry run
        call_command('fix_slugs', dry_run=True, stdout=out)
        
        # Get output
        output = out.getvalue()
        
        # Verify command mentioned dry run
        self.assertIn('DRY RUN', output)
        
        # Refresh from database
        self.post1.refresh_from_db()
        self.post2.refresh_from_db()
        
        # Verify no changes were made
        self.assertIsNone(self.post1.slug)
        self.assertEqual(self.post2.slug, "") 