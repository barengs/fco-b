# Refresh Token Feature

## Overview

This feature adds refresh token support to the authentication system, allowing clients to obtain new authentication tokens without requiring users to re-enter their credentials.

## Changes Made

### 1. Added RefreshToken Model

Created [/Users/ROFI/Develop/proyek/fco_project/authentication/models.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/models.py) with a RefreshToken model:

- Stores refresh tokens with expiration dates
- Tracks revoked tokens for security
- Includes a helper method for generating new tokens

### 2. Updated Authentication View

Modified [/Users/ROFI/Develop/proyek/fco_project/authentication/views.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/views.py) to include refresh tokens:

- Added refresh_token to login response
- Created RefreshAuthToken viewset for token refreshing
- Implemented proper token validation and expiration checking

### 3. Updated URLs

Modified [/Users/ROFI/Develop/proyek/fco_project/authentication/urls.py](file:///Users/ROFI/Develop/proyek/fco_project/authentication/urls.py) to include the refresh endpoint:

- Added `/api/auth/refresh/` endpoint for token refreshing

### 4. Updated API Documentation

Enhanced the OpenAPI schema documentation:

- Added refresh_token field to authentication responses
- Documented the new refresh endpoint
- Provided comprehensive error responses

## New Endpoints

### Login Endpoint

**URL**: `/api/auth/login/`
**Method**: POST
**Request**:

```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:

```json
{
  "token": "string",
  "refresh_token": "string",
  "user_id": "integer",
  "username": "string",
  "user_as": "string",
  "roles": ["string"],
  "profile": {
    // Profile data
  }
}
```

### Refresh Token Endpoint

**URL**: `/api/auth/refresh/`
**Method**: POST
**Request**:

```json
{
  "refresh_token": "string"
}
```

**Response**:

```json
{
  "token": "string",
  "refresh_token": "string"
}
```

## Token Lifecycle

1. **Login**: User authenticates and receives both an authentication token and a refresh token
2. **Usage**: Client uses the authentication token for API requests
3. **Refresh**: When the authentication token expires, client uses the refresh token to get new tokens
4. **Security**: Refresh tokens are revoked after use to prevent replay attacks

## Security Features

1. **Expiration**: Refresh tokens expire after 7 days
2. **Revocation**: Used refresh tokens are immediately revoked
3. **Validation**: Tokens are validated for expiration and revocation status
4. **Error Handling**: Proper error responses for invalid, expired, or revoked tokens

## Usage Examples

### Login Request

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### Refresh Token Request

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token_here"
  }'
```

## Benefits

1. **Improved User Experience**: Users don't need to re-enter credentials frequently
2. **Security**: Short-lived authentication tokens with long-lived refresh tokens
3. **Standards Compliance**: Follows OAuth 2.0 refresh token patterns
4. **Extensibility**: Easy to modify expiration times and validation rules

## Frontend Implementation Guide

### Token Storage

```javascript
// Store both tokens securely
localStorage.setItem("authToken", response.token);
localStorage.setItem("refreshToken", response.refresh_token);
```

### Token Usage

```javascript
// Use auth token for API requests
const authToken = localStorage.getItem("authToken");
fetch("/api/some-endpoint/", {
  headers: {
    Authorization: `Token ${authToken}`,
  },
});
```

### Token Refresh

```javascript
// Refresh when auth token expires
async function refreshToken() {
  const refreshToken = localStorage.getItem("refreshToken");
  const response = await fetch("/api/auth/refresh/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem("authToken", data.token);
    localStorage.setItem("refreshToken", data.refresh_token);
    return data.token;
  } else {
    // Handle refresh failure (redirect to login)
    throw new Error("Token refresh failed");
  }
}
```

This implementation provides a secure and standards-compliant refresh token system that enhances the authentication experience.
