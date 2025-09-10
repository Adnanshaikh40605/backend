# Database Migration Conflict Resolution Guide

## Overview
This guide helps resolve conflicts in the blog application's database migrations, particularly around comment nesting functionality.

## Current Migration Issues

### Comment Nesting Migrations
The following migrations have potential conflicts:
- `0003_add_comment_nesting_fields.py` - Adds level and path fields
- `0004_populate_comment_nesting_fields.py` - Populates existing data
- `0005_comment_parent_and_more.py` - Adds parent field and indexes

### Root Cause
Multiple migrations were created to add comment nesting functionality, which can cause conflicts when applied in different orders or when rolling back.

## Resolution Strategies

### Strategy 1: Fresh Migration (Recommended for Development)

1. **Backup your data** (if you have important data):
   ```bash
   python manage.py dumpdata blog > blog_data_backup.json
   ```

2. **Reset migrations**:
   ```bash
   # Remove migration files (keep __init__.py)
   rm blog/migrations/0003_*.py
   rm blog/migrations/0004_*.py
   rm blog/migrations/0005_*.py
   rm blog/migrations/0006_*.py
   rm blog/migrations/0007_*.py
   rm blog/migrations/0008_*.py
   rm blog/migrations/0009_*.py
   
   # Reset database
   rm db.sqlite3
   
   # Create fresh migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Restore data** (if needed):
   ```bash
   python manage.py loaddata blog_data_backup.json
   ```

### Strategy 2: Rollback and Reapply (For Production)

1. **Use the rollback utility**:
   ```bash
   python rollback_migrations.py
   ```

2. **Choose option 1** to rollback comment nesting migrations

3. **Reapply migrations**:
   ```bash
   python manage.py migrate
   ```

### Strategy 3: Manual Conflict Resolution

1. **Check migration status**:
   ```bash
   python manage.py showmigrations blog
   ```

2. **Identify conflicts**:
   - Look for migrations marked with `[X]` (applied) vs `[ ]` (not applied)
   - Check for duplicate field additions

3. **Resolve conflicts**:
   ```bash
   # Fake apply problematic migrations
   python manage.py migrate blog 0003 --fake
   python manage.py migrate blog 0004 --fake
   python manage.py migrate blog 0005 --fake
   
   # Apply remaining migrations
   python manage.py migrate
   ```

## Prevention Strategies

### 1. Migration Best Practices
- Always test migrations on a copy of production data
- Use `--dry-run` flag to preview migrations
- Create data migrations separately from schema migrations
- Use descriptive migration names

### 2. Code Review Checklist
- [ ] Migration doesn't conflict with existing fields
- [ ] Data migration handles existing data properly
- [ ] Rollback operations are defined
- [ ] Indexes are added efficiently

### 3. Testing Migrations
```bash
# Test migration on fresh database
python manage.py migrate --run-syncdb

# Test rollback
python manage.py migrate blog 0002
python manage.py migrate blog 0005
```

## Emergency Recovery

### If Database is Corrupted
1. **Stop the application**
2. **Restore from backup**:
   ```bash
   cp db_backup.sqlite3 db.sqlite3
   ```
3. **Check migration status**:
   ```bash
   python manage.py showmigrations
   ```
4. **Apply missing migrations**:
   ```bash
   python manage.py migrate
   ```

### If Migrations are Stuck
1. **Check for locks**:
   ```bash
   # For SQLite, check if database is locked
   lsof db.sqlite3
   ```
2. **Force unlock** (SQLite):
   ```bash
   # Kill any processes using the database
   pkill -f "python.*manage.py"
   ```
3. **Reset migration state**:
   ```bash
   python manage.py migrate --fake-initial
   ```

## Monitoring and Maintenance

### Regular Checks
- Monitor migration status: `python manage.py showmigrations`
- Check for unused migrations: `python manage.py migrate --plan`
- Validate data integrity after migrations

### Backup Strategy
- Create database backups before major migrations
- Test rollback procedures regularly
- Document custom migration procedures

## Common Issues and Solutions

### Issue: "Table already exists"
**Solution**: Use `--fake` flag to mark migration as applied without running it

### Issue: "Field already exists"
**Solution**: Check if field was added in a previous migration, use `--fake` if needed

### Issue: "Circular dependency"
**Solution**: Split migration into multiple steps, use `--fake` for dependencies

### Issue: "Data migration fails"
**Solution**: Create a separate data migration, handle edge cases in the migration code

## Contact and Support

For complex migration issues:
1. Check Django migration documentation
2. Review the rollback utility: `python rollback_migrations.py`
3. Create a minimal reproduction case
4. Document the exact error messages and migration state
