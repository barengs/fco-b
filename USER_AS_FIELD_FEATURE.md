# User As Field Feature

## Overview

This feature simplifies the authentication response by replacing multiple boolean fields (is_admin, is_owner, is_captain) with a single `user_as` field that indicates the primary role of the user.

## Changes Made

### 1. Updated CustomAuthToken View

Modified [/Users/ROFI/Develop/proyek/fco_project/authentication/views.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/views.py) to use a single `user_as` field:

- Replaced `is_admin`, `is_owner`, and `is_captain` boolean fields with a single `user_as` string field
- Added logic to determine the primary user role and set the `user_as` value accordingly
- Maintained the `roles` array for detailed role information
- Kept the `profile` object unchanged

### 2. Updated API Documentation

Modified the OpenAPI schema to reflect the new field structure:

- Removed the `is_admin`, `is_owner`, and `is_captain` fields from the schema
- Added the `user_as` field with enum values: `admin`, `owner`, `captain`, `user`
- Maintained all other fields including `profile` and `roles`

## New Response Structure

The authentication response now includes a single `user_as` field instead of multiple boolean fields:

```json
{
  "token": "string",
  "user_id": "integer",
  "username": "string",
  "user_as": "string", // Possible values: "admin", "owner", "captain", "user"
  "roles": ["string"],
  "profile": {
    // Profile data based on user role
  }
}
```

## Usage Examples

### Admin User Response

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "adminuser",
  "user_as": "admin",
  "roles": ["admin"],
  "profile": {
    "type": "admin",
    "full_name": "Admin User",
    "email": "admin@example.com",
    "phone": "1234567890",
    "department": "IT",
    "position": "System Administrator"
  }
}
```

### Owner User Response

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 2,
  "username": "owneruser",
  "user_as": "owner",
  "roles": ["owner"],
  "profile": {
    "type": "owner",
    "name": "Test Owner",
    "owner_type": "individual",
    "email": "owner@example.com",
    "phone": "0987654321",
    "address": "123 Owner Street"
  }
}
```

## Benefits

1. **Simplified Logic**: Frontend applications only need to check one field instead of multiple boolean fields
2. **Cleaner Code**: Reduces conditional complexity in frontend code
3. **Maintainable**: Easier to extend with new user types
4. **Backward Compatibility**: The `roles` array still provides detailed role information
5. **Intuitive**: The `user_as` field clearly indicates the primary role of the user

## Migration Guide

For frontend applications currently using the boolean fields:

### Before

```javascript
if (response.is_admin) {
  // Admin logic
} else if (response.is_captain) {
  // Captain logic
} else if (response.is_owner) {
  // Owner logic
}
```

### After

```javascript
switch (response.user_as) {
  case "admin":
    // Admin logic
    break;
  case "captain":
    // Captain logic
    break;
  case "owner":
    // Owner logic
    break;
  default:
  // Default user logic
}
```

This change makes the frontend code more readable and maintainable while providing the same functionality.
