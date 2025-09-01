# Ship Linking During User Registration

## Overview

This feature allows automatic linking of newly registered users (owners or captains) to existing ships based on ship registration codes provided during registration.

## How It Works

### For Owner Registration

When a new owner registers and provides a `ship_code`:

1. The system creates the owner profile as usual
2. If a ship with the provided registration number exists, the system updates that ship to link it to the newly created owner
3. If no ship is found with that registration number, the registration proceeds normally without linking

### For Captain Registration

When a new captain registers and provides a `ship_code`:

1. The system creates both an owner profile (as a placeholder) and the captain profile
2. If a ship with the provided registration number exists, the system updates that ship to link it to the newly created captain
3. If no ship is found with that registration number, the registration proceeds normally without linking

## API Request Format

### Owner Registration with Ship Linking

```json
{
  "username": "new_owner",
  "email": "owner@example.com",
  "password": "securepassword",
  "password_confirm": "securepassword",
  "role": "owner",
  "full_name": "John Owner",
  "contact_info": "Contact details",
  "address": "123 Main St",
  "phone": "123-456-7890",
  "ship_code": "SHIP123456"
}
```

### Captain Registration with Ship Linking

```json
{
  "username": "new_captain",
  "email": "captain@example.com",
  "password": "securepassword",
  "password_confirm": "securepassword",
  "role": "captain",
  "full_name": "Captain Smith",
  "contact_info": "Contact details",
  "address": "456 Harbor St",
  "phone": "098-765-4321",
  "ship_code": "SHIP789012"
}
```

## Error Handling

- If the provided ship code doesn't match any existing ship, the registration continues without linking
- No error is returned to the frontend in this case to ensure registration success
- The ship linking is considered an additional feature that enhances the data relationship but isn't critical to registration

## Benefits

1. **Streamlined Workflow**: Owners and captains can be linked to ships during registration
2. **Data Consistency**: Ensures proper relationships between users and ships
3. **Frontend Integration**: Allows frontend to provide ship codes during registration
4. **Backward Compatibility**: Registration without ship codes works as before
