# Admin Users Endpoint

## Endpoint

```
GET /api/admin/admin-users/
```

## Description

Mengambil daftar semua pengguna dengan peran admin dalam sistem.

## Authentication

Memerlukan autentikasi pengguna.

## Response

Returns a list of admin users with their profile information.

### Success Response

```json
[
  {
    "id": 1,
    "username": "adminuser",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_active": true,
    "date_joined": "2023-01-01T00:00:00Z",
    "admin_profile": {
      "full_name": "Admin User Full Name",
      "email": "admin@example.com",
      "phone": "+621234567890",
      "department": "IT Department",
      "position": "System Administrator"
    }
  }
]
```

### Error Response

```json
{
  "detail": "Data autentikasi tidak diberikan."
}
```

Status code: 401

## Permissions

Hanya pengguna yang telah diautentikasi yang dapat mengakses endpoint ini.
