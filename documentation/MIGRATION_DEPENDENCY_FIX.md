# Migration Dependency Fix for Custom User Model

This document explains the fix for the migration dependency issue where the admin module was trying to reference the CustomUser model before it was created.

## Problem

The error occurred because:

1. The admin module migrations were referencing the CustomUser model through `settings.AUTH_USER_MODEL`
2. The migration dependencies were not properly set to ensure the CustomUser model was created first
3. Django was trying to apply the admin module migrations before the owners app migrations that create the CustomUser model

Error message:

```
ValueError: Related model 'owners.customuser' cannot be resolved
```

## Root Cause

In the admin module models:

- [AdminProfile](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L3-L16) directly references [CustomUser](file:///Users/ROFI/Develop/proyek/fco_project/owners/models.py#L3-L15) through a OneToOneField
- [UserRole](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L58-L77) directly references [CustomUser](file:///Users/ROFI/Develop/proyek/fco_project/owners/models.py#L3-L15) through a ForeignKey

But the migration dependencies were not set up correctly to ensure the proper order.

## Solution

### 1. Fixed Migration Dependencies

Changed the migration dependencies in both admin module migration files:

**Before** (in [admin_module/migrations/0001_initial.py](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/migrations/0001_initial.py)):

```python
dependencies = [
    ('auth', '0012_alter_user_first_name_max_length'),
    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
]
```

**After**:

```python
dependencies = [
    ('auth', '0012_alter_user_first_name_max_length'),
    ('owners', '0002_customuser'),  # Explicit dependency on CustomUser creation
]
```

### 2. Fixed Model References

Changed the model references in the migrations from `settings.AUTH_USER_MODEL` to explicit references:

**Before**:

```python
user = models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Pengguna')
```

**After**:

```python
user = models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='owners.customuser', verbose_name='Pengguna')
```

## Why This Fix Works

1. **Explicit Dependencies**: By explicitly depending on `('owners', '0002_customuser')`, we ensure that the migration that creates the CustomUser model runs before the admin module migrations.

2. **Direct Model References**: By using direct string references like `'owners.customuser'` instead of `settings.AUTH_USER_MODEL`, we avoid potential resolution issues during migration.

3. **Proper Order**: This ensures the correct migration order:
   - First: `owners.0001_initial` (creates Owner model)
   - Second: `owners.0002_customuser` (creates CustomUser model)
   - Third: `admin_module.0001_initial` (creates admin models that reference CustomUser)
   - Fourth: `admin_module.0002_adminprofile` (creates AdminProfile that references CustomUser)

## Testing the Fix

To test that the fix works:

1. **Remove the database**:

   ```bash
   rm /Users/ROFI/Develop/proyek/fco_project/db.sqlite3
   ```

2. **Apply migrations in order**:

   ```bash
   cd /Users/ROFI/Develop/proyek/fco_project
   source venv/bin/activate
   python manage.py migrate owners
   python manage.py migrate admin_module
   python manage.py migrate
   ```

3. **Or apply all migrations at once**:
   ```bash
   python manage.py migrate
   ```

The migrations should now apply successfully without the "Related model 'owners.customuser' cannot be resolved" error.

## Prevention

To prevent similar issues in the future:

1. When creating models that reference the custom user model, always ensure migration dependencies are set correctly
2. Use explicit dependencies on the migration that creates the custom user model
3. Test migrations in a clean environment regularly
4. Document migration dependencies and their reasons
