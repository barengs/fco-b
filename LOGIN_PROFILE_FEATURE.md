# Login Profile Feature

## Overview

This feature enhances the login response to include user profile data based on their role, providing a more complete user context immediately after authentication.

## Changes Made

### 1. Updated CustomAuthToken View

Modified [/Users/ROFI/Develop/proyek/fco_project/authentication/views.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/views.py) to include profile data:

- Added a unified [profile](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L79-L79) object in the login response
- Implemented role-based profile data retrieval:
  - Admin users: Retrieves data from [AdminProfile](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L6-L20) model
  - Owner users: Retrieves data from [Owner](file:///Users/ROFI/Develop/proyek/fco_project/owners/models.py#L15-L33) model
  - Captain users: Retrieves data from [Captain](file:///Users/ROFI/Develop/proyek/fco_project/owners/models.py#L36-L58) model
  - Other users: Provides a default profile with basic user information

### 2. Updated API Documentation

Modified the OpenAPI schema to document the new profile field:

- Replaced the specific [admin_profile](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L13-L20) field with a unified [profile](file:///Users/ROFI/Develop/proyek/fco_project/admin_module/models.py#L79-L79) field
- Added comprehensive documentation for the profile object structure
- Documented all possible profile types and their fields

## Profile Data Structure

The profile object in the login response has different structures based on user role:

### Admin Profile

```json
{
  "type": "admin",
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "department": "string",
  "position": "string"
}
```

### Owner Profile

```json
{
  "type": "owner",
  "name": "string",
  "owner_type": "string",
  "email": "string",
  "phone": "string",
  "address": "string"
}
```

### Captain Profile

```json
{
  "type": "captain",
  "name": "string",
  "license_number": "string",
  "email": "string",
  "phone": "string",
  "address": "string",
  "years_of_experience": "integer"
}
```

### Default Profile

```json
{
  "type": "user",
  "full_name": "string"
}
```

## Usage Examples

### Admin Login Response

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "adminuser",
  "is_owner": false,
  "is_captain": false,
  "is_admin": true,
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

### Owner Login Response

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 2,
  "username": "owneruser",
  "is_owner": true,
  "is_captain": false,
  "is_admin": false,
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

1. **Complete User Context**: Frontend applications receive all necessary profile data in a single API call
2. **Role-Based Data**: Each user type receives relevant profile information
3. **Backward Compatibility**: Existing fields remain unchanged, ensuring no breaking changes
4. **Unified Interface**: Single profile field simplifies frontend logic
5. **Extensibility**: Easy to add new profile types in the future
