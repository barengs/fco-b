# Role System Documentation

## Overview

The FCO Fish Catch Management System implements a flexible role-based access control system that supports both a simple role field and a more sophisticated role management system.

## Role Models

### 1. Simple Role System (owners.CustomUser)

The basic role system uses the [role](file:///Users/ROFI/Develop/proyek/fco_project/owners/models.py#L11-L11) field in the [CustomUser](file:///Users/ROFI/Develop/proyek/fco_project/owners/models.py#L5-L12) model:

```python
USER_ROLE_CHOICES = [
    ('admin', 'Administrator'),
    ('owner', 'Pemilik Kapal'),
    ('captain', 'Nahkoda'),
]
```

### 2. Flexible Role System (admin_module)

The flexible role system consists of several models:

- [Role](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L24-L35): Defines roles with names, descriptions, and permissions
- [UserRole](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L37-L48): Links users to roles (many-to-many relationship)
- [Permission](file:///Users/ROFI/Develop/proyek/fco_project/django/contrib/auth/models.py#L308-L332): Django's built-in permission system
- [Menu](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L50-L69) and [RoleMenu](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L71-L89): Menu access control based on roles

## Implementation Details

### Authentication Response

The authentication system now returns role information in the response:

```json
{
  "token": "auth_token",
  "user_id": 1,
  "username": "testuser",
  "is_owner": true,
  "is_captain": false,
  "is_admin": false,
  "roles": ["owner"]
}
```

### Role Determination Logic

The system determines user roles using this hierarchy:

1. First, check the flexible role system ([UserRole](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L37-L48) model)
2. If no flexible roles are assigned, fall back to the simple [role](file:///Users/ROFI/Develop/proyek/fco_project/owners/models.py#L11-L11) field

### Management Commands

#### initialize_admin

Sets up default roles and an admin user:

```bash
python manage.py initialize_admin
```

#### sync_user_roles

Synchronizes existing users with the flexible role system:

```bash
python manage.py sync_user_roles
```

## Usage Examples

### Assigning Roles

```python
# Using the flexible system
user = CustomUser.objects.get(username='testuser')
role = Role.objects.get(name='owner')
UserRole.objects.create(user=user, role=role)
```

### Checking Roles

```python
# Check flexible roles
user_roles = [ur.role.name for ur in user.userrole_set.all()]

# Check simple role (fallback)
is_admin = user.role == 'admin'
```

## Benefits

1. **Backward Compatibility**: Existing code using the simple role field continues to work
2. **Flexibility**: Users can have multiple roles
3. **Extensibility**: New roles can be added without changing the code
4. **Granular Permissions**: Role-based menu access control
