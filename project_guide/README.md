# Blog CMS Management Commands

This directory contains custom Django management commands for the Blog CMS application.

## Available Commands

### `check_db`

Verifies database connectivity with retry capabilities.

**Usage:**
```
python manage.py check_db [--retry] [--retry-count COUNT] [--retry-delay SECONDS]
```

**Options:**
- `--retry`: Enables connection retry if initial connection fails
- `--retry-count`: Number of retry attempts (default: 5)
- `--retry-delay`: Delay between retries in seconds (default: 2)

**Examples:**
```
# Basic check
python manage.py check_db

# Check with retry enabled
python manage.py check_db --retry

# Check with custom retry settings
python manage.py check_db --retry --retry-count 10 --retry-delay 5
```

### `fix_slugs`

Fixes or populates slugs for blog posts that have NULL or empty slugs.

**Usage:**
```
python manage.py fix_slugs [--mode {null|empty|all}] [--dry-run]
```

**Options:**
- `--mode`: Specify which slugs to fix:
  - `null`: Only fix NULL slugs
  - `empty`: Only fix empty string slugs
  - `all`: Fix both NULL and empty slugs (default)
- `--dry-run`: Show what would be done without making changes

**Examples:**
```
# Fix all problematic slugs
python manage.py fix_slugs

# Fix only NULL slugs
python manage.py fix_slugs --mode=null

# Show what would be fixed without making changes
python manage.py fix_slugs --dry-run
```

### `generate_swagger`

Generates Swagger/OpenAPI documentation for the API.

**Usage:**
```
python manage.py generate_swagger [--format {json|yaml}] [--file FILENAME] [--url BASE_URL]
```

**Options:**
- `--format`: Output format, either 'json' or 'yaml' (default: json)
- `--file`: Output filename without extension (default: 'api-docs')
- `--url`: Base URL for API server (default: 'http://localhost:8000/')

**Examples:**
```
# Generate JSON documentation
python manage.py generate_swagger

# Generate YAML documentation
python manage.py generate_swagger --format=yaml

# Generate with custom filename and URL
python manage.py generate_swagger --file=my-api-docs --url=https://api.example.com/
```

## Removed Legacy Commands

The following commands have been removed and replaced by the `fix_slugs` command:

- ~~`fix_null_slugs`~~: Use `fix_slugs --mode=null` instead
- ~~`populate_slugs`~~: Use `fix_slugs --mode=empty` instead