# Registration Profile Feature

## Overview

This feature enhances the user registration endpoint to include profile information (full_name, contact_info, address, phone) and returns profile data in the registration response.

## Changes Made

### 1. Updated UserRegistrationSerializer

Modified [/Users/ROFI/Develop/proyek/fco_project/authentication/serializers.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/serializers.py) to include profile fields:

- Added `full_name`, `contact_info`, `address`, and `phone` fields to the serializer
- Enhanced the `create` method to create related Owner or Captain objects based on user role
- Implemented logic to associate users with their profile objects

### 2. Updated RegistrationViewSet

Modified [/Users/ROFI/Develop/proyek/fco_project/authentication/views.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/views.py) to include profile data in the response:

- Added `role` and `profile` fields to the registration response
- Implemented role-based profile data inclusion
- Maintained backward compatibility with existing response fields

### 3. Updated API Documentation

Enhanced the OpenAPI schema documentation:

- Added profile fields to the request schema
- Added role and profile fields to the response schema
- Provided comprehensive documentation for all new fields

## New Request Structure

The registration endpoint now accepts additional profile fields:

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password_confirm": "string",
  "role": "string", // optional, defaults to 'owner'
  "full_name": "string", // optional
  "contact_info": "string", // optional
  "address": "string", // optional
  "phone": "string" // optional
}
```

## New Response Structure

The registration response now includes role and profile information:

```json
{
  "token": "string",
  "user_id": "integer",
  "username": "string",
  "role": "string",
  "profile": {
    "type": "string", // 'owner' or 'captain'
    "full_name": "string",
    "contact_info": "string",
    "address": "string",
    "phone": "string",
    "email": "string"
  }
}
```

For captains, the profile also includes:

```json
{
  "license_number": "string"
}
```

## Usage Examples

### Owner Registration Request

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newowner",
    "email": "owner@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "role": "owner",
    "full_name": "John Doe",
    "contact_info": "Available weekdays 9-5",
    "address": "123 Main St, City",
    "phone": "+1234567890"
  }'
```

### Owner Registration Response

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "newowner",
  "role": "owner",
  "profile": {
    "type": "owner",
    "full_name": "John Doe",
    "contact_info": "Available weekdays 9-5",
    "address": "123 Main St, City",
    "phone": "+1234567890",
    "email": "owner@example.com"
  }
}
```

### Captain Registration Request

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newcaptain",
    "email": "captain@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "role": "captain",
    "full_name": "Jane Smith",
    "contact_info": "Available for charters",
    "address": "456 Harbor St, Port",
    "phone": "+0987654321"
  }'
```

### Captain Registration Response

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 2,
  "username": "newcaptain",
  "role": "captain",
  "profile": {
    "type": "captain",
    "full_name": "Jane Smith",
    "contact_info": "Available for charters",
    "address": "456 Harbor St, Port",
    "phone": "+0987654321",
    "email": "captain@example.com",
    "license_number": "LIC2"
  }
}
```

## Benefits

1. **Complete Registration**: Users can provide all necessary information during registration
2. **Immediate Profile Access**: Profile data is available immediately after registration
3. **Role-Based Profiles**: Different profile structures for owners and captains
4. **Backward Compatibility**: Existing registration flows continue to work
5. **Enhanced User Experience**: Reduced need for additional profile setup steps

## Implementation Details

### Owner Registration

- Creates an Owner object with the provided profile data
- Associates the Owner with the User through the owner relationship
- Uses 'individual' as the default owner_type

### Captain Registration

- Creates both an Owner (as a placeholder) and a Captain object
- Associates the Captain with the User through the captain relationship
- Associates the Captain with the Owner
- Generates a placeholder license number

### Default Values

When profile fields are not provided:

- `full_name` defaults to the username
- Other fields default to empty strings
- `owner_type` defaults to 'individual' for owners

This implementation provides a comprehensive registration flow that captures all necessary user information while maintaining flexibility for different user roles.
