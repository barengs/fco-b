#!/usr/bin/env python
"""
Script untuk memverifikasi super admin yang sudah dibuat
Jalankan dengan: python verify_superadmin.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

from owners.models import CustomUser
from admin_module.models import AdminProfile, Role, UserRole

def main():
    print("="*60)
    print("           VERIFIKASI SUPER ADMIN FCO PROJECT")
    print("="*60)
    
    # Check super admin users
    print("\n🔍 MENCARI SUPER ADMIN USERS:")
    print("-" * 40)
    superusers = CustomUser.objects.filter(is_superuser=True)
    
    if superusers.exists():
        for user in superusers:
            print(f"✓ Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Is Superuser: {user.is_superuser}")
            print(f"  Is Staff: {user.is_staff}")
            print(f"  Is Active: {user.is_active}")
            print(f"  Date Joined: {user.date_joined}")
            
            # Check admin profile
            try:
                admin_profile = AdminProfile.objects.get(user=user)
                print(f"  Admin Profile: ✓")
                print(f"    Full Name: {admin_profile.full_name}")
                print(f"    Department: {admin_profile.department}")
                print(f"    Position: {admin_profile.position}")
            except AdminProfile.DoesNotExist:
                print(f"  Admin Profile: ✗ (Tidak ada)")
            
            # Check user roles
            user_roles = UserRole.objects.filter(user=user)
            if user_roles.exists():
                print(f"  Roles: ✓")
                for ur in user_roles:
                    print(f"    - {ur.role.name}: {ur.role.description}")
            else:
                print(f"  Roles: ✗ (Tidak ada role)")
            
            print("-" * 40)
    else:
        print("❌ Tidak ada super admin yang ditemukan!")
        return False
    
    # Check admin role users
    print("\n👥 SEMUA ADMIN USERS (role=admin):")
    print("-" * 40)
    admin_users = CustomUser.objects.filter(role='admin')
    
    if admin_users.exists():
        for user in admin_users:
            status = "✓ SUPER ADMIN" if user.is_superuser else "⚠️  ADMIN BIASA"
            print(f"{status} - {user.username} ({user.email})")
    else:
        print("❌ Tidak ada admin yang ditemukan!")
    
    # Check admin role permissions
    print("\n🔐 ADMIN ROLE PERMISSIONS:")
    print("-" * 40)
    try:
        admin_role = Role.objects.get(name='admin')
        permissions_count = admin_role.permissions.count()
        print(f"✓ Admin role ditemukan: {admin_role.description}")
        print(f"✓ Total permissions: {permissions_count}")
        
        if permissions_count > 0:
            print("✓ Admin role memiliki permissions")
        else:
            print("⚠️  Admin role tidak memiliki permissions")
            
    except Role.DoesNotExist:
        print("❌ Admin role tidak ditemukan!")
        return False
    
    print("\n" + "="*60)
    print("VERIFIKASI SELESAI!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️  Ada masalah dengan setup super admin.")
        print("Silakan jalankan: python create_superadmin.py")
        sys.exit(1)
    else:
        print("\n✅ Super admin setup sudah benar!")