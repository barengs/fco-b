# Custom User Model Migration Order Solution

This document explains how to ensure the CustomUser model is migrated before other models that depend on it.

## Problem

When using a custom user model in Django, it's crucial that the user model is created before other models that reference it. Otherwise, you'll encounter errors like:

```
django.db.utils.OperationalError: no such table: owners_customuser
```

## Solutions

### Solution 1: Reset and Reapply Migrations (Recommended)

This is the cleanest approach when starting a new development environment:

1. **Remove the database file**:

   ```bash
   rm /Users/ROFI/Develop/proyek/fco_project/db.sqlite3
   ```

2. **Remove migration files** (but keep [**init**.py](file:///Users/ROFI/Develop/proyek/fco_project/blockchain/__init__.py)):

   ```bash
   find /Users/ROFI/Develop/proyek/fco_project -path "*/migrations/*.py" -not -name "__init__.py" -delete
   find /Users/ROFI/Develop/proyek/fco_project -path "*/migrations/*.pyc" -delete
   ```

3. **Regenerate migrations**:

   ```bash
   cd /Users/ROFI/Develop/proyek/fco_project
   source venv/bin/activate
   python manage.py makemigrations owners
   python manage.py makemigrations
   ```

4. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

### Solution 2: Manual Migration Order Fix

Modify migration dependencies to ensure proper order. The key is to make sure migrations that reference the CustomUser model depend on the migration that creates it (`owners.0002_customuser`).

For example, in [ships/migrations/0001_initial.py](file:///Users/ROFI/Develop/proyek/fco_project/ships/migrations/0001_initial.py), change:

```python
dependencies = [
    ('owners', '0001_initial'),
]
```

to:

```python
dependencies = [
    ('owners', '0002_customuser'),
]
```

### Solution 3: Custom Management Command

A custom management command has been created to ensure proper migration order:

```bash
python manage.py ensure_user_migration
```

This command checks if the CustomUser table exists and applies migrations in the correct order if needed.

## Best Practices

1. **Always use `settings.AUTH_USER_MODEL`** when referencing the user model in ForeignKey or OneToOneField relationships.

2. **Use `migrations.swappable_dependency(settings.AUTH_USER_MODEL)`** in migration dependencies when the migration creates models that reference the user model.

3. **Apply migrations in the correct order**:

   - First apply the app containing the custom user model
   - Then apply other apps that depend on it

4. **When in doubt, reset migrations** during development to ensure a clean state.

## Verification

After applying migrations, you can verify that the CustomUser table exists:

```bash
sqlite3 db.sqlite3 "SELECT name FROM sqlite_master WHERE type='table' AND name='owners_customuser';"
```

This should return `owners_customuser` if the table exists.
