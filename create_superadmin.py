#!/usr/bin/env python
"""
Script untuk membuat super admin dengan mudah
Jalankan dengan: python create_superadmin.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

from django.core.management import call_command

def main():
    print("="*60)
    print("           MEMBUAT SUPER ADMIN FCO PROJECT")
    print("="*60)
    
    try:
        # Jalankan command create_superadmin secara interaktif
        call_command('create_superadmin', interactive=True)
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "="*60)
        print("Super admin berhasil dibuat!")
        print("Anda sekarang bisa login menggunakan kredensial yang dibuat.")
        print("="*60)
    else:
        print("\nGagal membuat super admin. Silakan coba lagi.")
        sys.exit(1)