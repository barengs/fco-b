# Admin Module Documentation

## Overview

The Admin Module extends the FCO Fish Catch Management System to support role-based access control (RBAC), menu management, and enhanced user administration. This module allows the Ministry of Marine Affairs and Fisheries (KKP) to manage system users, roles, permissions, and frontend menus.

## Features

1. **Role Management**: Create and manage user roles with specific permissions
2. **User Role Assignment**: Assign roles to users
3. **Menu Management**: Create and organize frontend menus
4. **Role-Menu Permissions**: Control which menus are accessible to which roles
5. **Enhanced Authentication**: Support for admin, owner, and captain user types
6. **Admin User Management**: Retrieve list of all admin users

## API Endpoints

### Roles

- `GET /api/admin/roles/` - List all roles
- `POST /api/admin/roles/` - Create a new role
- `GET /api/admin/roles/{id}/` - Retrieve a specific role
- `PUT /api/admin/roles/{id}/` - Update a specific role
- `DELETE /api/admin/roles/{id}/` - Delete a specific role
- `POST /api/admin/roles/{id}/assign_permission/` - Assign a permission to a role

### User Roles

- `GET /api/admin/user-roles/` - List all user-role assignments
- `POST /api/admin/user-roles/` - Create a new user-role assignment
- `GET /api/admin/user-roles/{id}/` - Retrieve a specific user-role assignment
- `PUT /api/admin/user-roles/{id}/` - Update a specific user-role assignment
- `DELETE /api/admin/user-roles/{id}/` - Delete a specific user-role assignment
- `POST /api/admin/user-roles/assign_role/` - Assign a role to a user

### Menus

- `GET /api/admin/menus/` - List all active menus
- `POST /api/admin/menus/` - Create a new menu
- `GET /api/admin/menus/{id}/` - Retrieve a specific menu
- `PUT /api/admin/menus/{id}/` - Update a specific menu
- `DELETE /api/admin/menus/{id}/` - Delete a specific menu

### Role Menus

- `GET /api/admin/role-menus/` - List all role-menu assignments
- `POST /api/admin/role-menus/` - Create a new role-menu assignment
- `GET /api/admin/role-menus/{id}/` - Retrieve a specific role-menu assignment
- `PUT /api/admin/role-menus/{id}/` - Update a specific role-menu assignment
- `DELETE /api/admin/role-menus/{id}/` - Delete a specific role-menu assignment
- `POST /api/admin/role-menus/assign_menu/` - Assign a menu to a role

### Admin Users

- `GET /api/admin/admin-users/` - List all admin users
  - Description: Mengambil daftar semua pengguna dengan peran admin dalam sistem
  - Authentication: Memerlukan autentikasi pengguna
  - Response: Returns a list of admin users with their profile information

## Models

### Role

Represents a user role in the system.

Fields:

- `name` (CharField): Unique name of the role
- `description` (TextField): Description of the role
- `permissions` (ManyToManyField): Permissions assigned to the role
- `created_at` (DateTimeField): When the role was created
- `updated_at` (DateTimeField): When the role was last updated

### UserRole

Represents the relationship between users and roles.

Fields:

- `user` (ForeignKey): The user
- `role` (ForeignKey): The role
- `assigned_at` (DateTimeField): When the role was assigned to the user

### Menu

Represents a frontend menu item.

Fields:

- `name` (CharField): Name of the menu
- `url` (CharField): URL the menu points to
- `icon` (CharField): Icon for the menu
- `parent` (ForeignKey): Parent menu (for hierarchical menus)
- `order` (IntegerField): Order of the menu
- `is_active` (BooleanField): Whether the menu is active
- `created_at` (DateTimeField): When the menu was created
- `updated_at` (DateTimeField): When the menu was last updated

### RoleMenu

Represents the relationship between roles and menus with specific permissions.

Fields:

- `role` (ForeignKey): The role
- `menu` (ForeignKey): The menu
- `can_view` (BooleanField): Whether the role can view the menu
- `can_create` (BooleanField): Whether the role can create items in the menu
- `can_edit` (BooleanField): Whether the role can edit items in the menu
- `can_delete` (BooleanField): Whether the role can delete items in the menu
- `assigned_at` (DateTimeField): When the menu was assigned to the role

## Authentication

The system supports three types of users:

1. **Admin**: KKP administrators with full system access
2. **Owner**: Ship owners who can report fish catches
3. **Captain**: Ship captains who can report fish catches

Users can log in using their username and password. The authentication system has been extended to support role-based access control.

## Initialization

To initialize the system with default roles and an admin user, run:

```bash
python manage.py initialize_admin
```

This creates:

- Admin, Owner, and Captain roles
- An admin user with username "admin" and password "admin123"
- Assignment of the admin role to the admin user
- All permissions assigned to the admin role

## Database Migrations

The module includes database migrations. To apply them:

```bash
python manage.py migrate
```

## Testing

To run tests for the admin module:

```bash
python manage.py test admin_module
```
