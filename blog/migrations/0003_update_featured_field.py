# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_ensure_comment_fields'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Set default value for existing rows where featured is NULL
            UPDATE blog_blogpost SET featured = false WHERE featured IS NULL;
            
            -- Add NOT NULL constraint if it doesn't exist
            ALTER TABLE blog_blogpost ALTER COLUMN featured SET NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ] 