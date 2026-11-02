from owners.models import CustomUser

def activate_superuser(username):
    """Mengaktifkan is_superuser = True untuk user tertentu"""
    try:
        user = CustomUser.objects.get(username=username)
        user.is_superuser = True
        user.is_staff = True  # Biasanya superuser juga staff
        user.save()

        print(f"✅ Berhasil mengaktifkan superuser untuk: {username}")
        print(f"   - is_superuser: {user.is_superuser}")
        print(f"   - is_staff: {user.is_staff}")
        print(f"   - role: {user.role}")

    except CustomUser.DoesNotExist:
        print(f"❌ User dengan username '{username}' tidak ditemukan")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Ganti 'username_yang_ingin_dijadikan_superuser' dengan username yang diinginkan
    target_username = 'testing'  # Contoh: mengubah user 'testing' menjadi superuser

    print(f"Mengaktifkan superuser untuk user: {target_username}")
    activate_superuser(target_username)
    