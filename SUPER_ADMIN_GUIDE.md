# Panduan Super Admin FCO Project

## 📋 Daftar Isi
1. [Cara Membuat Super Admin](#cara-membuat-super-admin)
2. [Cara Verifikasi Super Admin](#cara-verifikasi-super-admin)
3. [Cara Login Super Admin](#cara-login-super-admin)
4. [Fitur Super Admin](#fitur-super-admin)
5. [Troubleshooting](#troubleshooting)

## 🚀 Cara Membuat Super Admin

### Metode 1: Menggunakan Script Python (Recommended)
```bash
python create_superadmin.py
```

Script ini akan meminta input:
- Username
- Email
- Password
- Konfirmasi Password

### Metode 2: Menggunakan Django Management Command
```bash
# Mode interaktif
python manage.py create_superadmin --interactive

# Mode non-interaktif
python manage.py create_superadmin --username=admin --email=admin@kkp.go.id --password=admin123
```

### Metode 3: Menggunakan Command yang Sudah Ada
```bash
python manage.py initialize_admin
```
Ini akan membuat user default:
- Username: `admin`
- Email: `admin@kkp.go.id`
- Password: `admin123`

## ✅ Cara Verifikasi Super Admin

### Menggunakan Script Verifikasi
```bash
python verify_superadmin.py
```

### Menggunakan Script Check Manual
```bash
python manage.py shell -c "exec(open('check_superuser.py').read())"
```

### Manual Check via Django Shell
```bash
python manage.py shell
```
```python
from owners.models import CustomUser
from admin_module.models import AdminProfile, UserRole

# Check superusers
superusers = CustomUser.objects.filter(is_superuser=True)
for user in superusers:
    print(f"Username: {user.username}, Email: {user.email}")
```

## 🔐 Cara Login Super Admin

### 1. Via Django Admin Panel
```
http://localhost:8000/admin/
```

### 2. Via API Login Endpoint
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### 3. Via Frontend (jika ada)
Gunakan kredensial yang sudah dibuat untuk login di aplikasi frontend.

## 🛠️ Fitur Super Admin

Super Admin memiliki akses penuh ke:

### 1. Django Admin Panel
- Manage semua models
- User management
- Permission management
- System configuration

### 2. API Endpoints
- Semua CRUD operations
- Admin-only endpoints
- System monitoring endpoints

### 3. Role & Permission Management
- Assign roles ke users
- Manage permissions
- Create custom roles

### 4. System Administration
- Database management
- Backup & restore
- System logs
- Performance monitoring

## 🔧 Troubleshooting

### Problem: "User sudah ada"
**Solusi:**
```bash
# Check existing users
python verify_superadmin.py

# Atau hapus user existing
python manage.py shell
```
```python
from owners.models import CustomUser
CustomUser.objects.filter(username='admin').delete()
```

### Problem: "Permission denied"
**Solusi:**
```bash
# Pastikan user memiliki is_superuser=True
python manage.py shell
```
```python
from owners.models import CustomUser
user = CustomUser.objects.get(username='admin')
user.is_superuser = True
user.is_staff = True
user.save()
```

### Problem: "Admin profile tidak ada"
**Solusi:**
```bash
python manage.py shell
```
```python
from owners.models import CustomUser
from admin_module.models import AdminProfile

user = CustomUser.objects.get(username='admin')
AdminProfile.objects.create(
    user=user,
    full_name='Administrator',
    email=user.email,
    department='IT',
    position='Super Administrator'
)
```

### Problem: "Role tidak ada"
**Solusi:**
```bash
# Jalankan initialize admin untuk setup roles
python manage.py initialize_admin
```

## 📝 Default Credentials

Jika menggunakan `initialize_admin` command:
- **Username:** `admin`
- **Email:** `admin@kkp.go.id`
- **Password:** `admin123`

⚠️ **PENTING:** Ganti password default setelah login pertama!

## 🔄 Reset Super Admin

Jika perlu reset super admin:

```bash
# 1. Hapus user existing
python manage.py shell -c "
from owners.models import CustomUser
CustomUser.objects.filter(username='admin').delete()
"

# 2. Buat ulang
python create_superadmin.py
```

## 📞 Support

Jika ada masalah:
1. Cek log Django: `tail -f django_import_debug.log`
2. Jalankan verifikasi: `python verify_superadmin.py`
3. Check database: `python manage.py dbshell`

---

**Dibuat untuk FCO Project - Fisheries Compliance Officer**