# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                BEGIN
                    -- Check if ip_address column exists
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'blog_comment'
                        AND column_name = 'ip_address'
                    ) THEN
                        -- Add ip_address column if it doesn't exist
                        ALTER TABLE blog_comment ADD COLUMN ip_address inet NULL;
                    END IF;
                EXCEPTION
                    WHEN others THEN
                        -- Handle any errors
                        RAISE NOTICE 'Error adding ip_address column: %', SQLERRM;
                END;

                BEGIN
                    -- Check if user_agent column exists
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'blog_comment'
                        AND column_name = 'user_agent'
                    ) THEN
                        -- Add user_agent column if it doesn't exist
                        ALTER TABLE blog_comment ADD COLUMN user_agent text NULL;
                    END IF;
                EXCEPTION
                    WHEN others THEN
                        -- Handle any errors
                        RAISE NOTICE 'Error adding user_agent column: %', SQLERRM;
                END;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ] 