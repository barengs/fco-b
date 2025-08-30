# Registration Role Feature

## Overview

This feature allows users to specify their role during registration, providing more flexibility in user onboarding.

## Changes Made

### 1. Updated UserRegistrationSerializer

Modified [/Users/ROFI/Develop/proyek/fco_project/authentication/serializers.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/serializers.py) to include the `role` field:

- Added `role` field to the serializer fields
- Made the role field optional during registration
- Set a default role of 'owner' if no role is specified
- Added validation to ensure only valid roles can be selected

### 2. Updated API Documentation

Modified [/Users/ROFI/Develop/proyek/fco_project/authentication/views.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/views.py) to update the OpenAPI schema:

- Updated the description to mention the optional role parameter
- Maintained the same response structure for backward compatibility

## Usage

### Registration without Role (uses default)

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "testpassword123",
  "password_confirm": "testpassword123"
}
```

### Registration with Role

```json
{
  "username": "testcaptain",
  "email": "captain@example.com",
  "password": "testpassword123",
  "password_confirm": "testpassword123",
  "role": "captain"
}
```

## Valid Roles

The system supports the following roles:

- `admin` - Administrator
- `owner` - Pemilik Kapal (Ship Owner)
- `captain` - Nahkoda (Captain)

## Default Behavior

If no role is specified during registration, the system will automatically assign the `owner` role as default.

## Benefits

1. **Flexibility**: Users can specify their role during registration
2. **Backward Compatibility**: Existing registration flows continue to work
3. **User Experience**: Reduces post-registration steps for role assignment
4. **Admin Efficiency**: Reduces the need for manual role assignment
