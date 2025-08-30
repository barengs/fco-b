# Authentication Endpoints Summary

## Overview

This document describes the authentication endpoints implemented for the FCO Fish Catch Management System.

## Endpoints Implemented

### 1. User Registration

- **URL**: `/api/owners/auth/register/`
- **Method**: POST
- **Description**: Registers a new user account
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "password_confirm": "string"
  }
  ```
- **Response** (Success - 201):
  ```json
  {
    "token": "string",
    "user_id": "integer",
    "username": "string"
  }
  ```
- **Response** (Error - 400):
  ```json
  {
    "error": "string"
  }
  ```

### 2. User Login

- **URL**: `/api/owners/login/`
- **Method**: POST
- **Description**: Authenticates a user and returns an authentication token
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response** (Success - 200):
  ```json
  {
    "token": "string",
    "user_id": "integer",
    "username": "string",
    "is_owner": "boolean",
    "is_captain": "boolean"
  }
  ```
- **Response** (Error - 400):
  ```json
  {
    "error": "string"
  }
  ```

## Implementation Details

### RegistrationViewSet

A new `RegistrationViewSet` was created in [views.py](file:///Users/ROFI/Develop/proyek/fco_project/owners/views.py) that handles user registration:

- Uses `UserRegistrationSerializer` for validation
- Creates a new user with the provided credentials
- Generates an authentication token for the new user
- Returns the token and user information upon successful registration

### UserRegistrationSerializer

A new serializer was added in [serializers.py](file:///Users/ROFI/Develop/proyek/fco_project/owners/serializers.py) that:

- Validates that the password and password confirmation match
- Creates a new user with properly hashed password
- Excludes the password_confirm field from the user model

### URL Configuration

The new registration endpoint was added to [urls.py](file:///Users/ROFI/Develop/proyek/fco_project/owners/urls.py):

- `/api/owners/auth/register/` maps to the registration view
- The existing login endpoint at `/api/owners/login/` was enhanced with better documentation

## Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:8000/api/owners/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### Login as an Existing User

```bash
curl -X POST http://localhost:8000/api/owners/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123"
  }'
```

## Security Considerations

- Passwords are properly hashed using Django's built-in password hashing
- Authentication tokens are generated using Django REST Framework's token authentication
- The registration endpoint validates password confirmation to prevent typos
- All endpoints follow REST conventions and return appropriate HTTP status codes

## Testing

Unit tests were created in [tests.py](file:///Users/ROFI/Develop/proyek/fco_project/owners/tests.py) to verify:

- Serializer validation for correct and incorrect data
- User creation with proper password hashing
- Endpoint functionality (when available)
