from owners.models import CustomUser

print('Super Admin Users:')
superusers = CustomUser.objects.filter(is_superuser=True)
if superusers.exists():
    for user in superusers:
        print(f'- Username: {user.username}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}')
else:
    print('Tidak ada super admin yang ditemukan.')

print('\nSemua Admin Users (role=admin):')
admin_users = CustomUser.objects.filter(role='admin')
if admin_users.exists():
    for user in admin_users:
        print(f'- Username: {user.username}, Email: {user.email}, Superuser: {user.is_superuser}, Active: {user.is_active}')
else:
    print('Tidak ada admin yang ditemukan.')