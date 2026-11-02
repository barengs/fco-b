from ships.models import Ship, Quota
from datetime import datetime
import random

def create_test_quotas():
    """Membuat data kuota test untuk kapal yang ada"""
    current_year = datetime.now().year

    # Ambil semua kapal yang aktif
    ships = Ship.objects.filter(active=True)

    print(f"Membuat kuota untuk {ships.count()} kapal aktif...")

    for ship in ships:
        # Cek apakah sudah ada kuota untuk tahun ini
        existing_quota = Quota.objects.filter(ship=ship, year=current_year).first()

        if existing_quota:
            print(f"  Kapal {ship.name} sudah memiliki kuota tahun {current_year}")
            continue

        # Buat kuota baru
        # Total kuota antara 1000-5000 kg
        total_quota = random.randint(1000, 5000)

        # Sisa kuota antara 20%-90% dari total
        remaining_percentage = random.uniform(0.2, 0.9)
        remaining_quota = round(total_quota * remaining_percentage, 2)

        quota = Quota.objects.create(
            ship=ship,
            year=current_year,
            quota=total_quota,
            remaining_quota=remaining_quota,
            is_active=True
        )

        print(f"  ✓ Dibuat kuota untuk {ship.name}: {remaining_quota}/{total_quota} kg ({round((remaining_quota/total_quota)*100, 1)}%)")

    print("Selesai membuat kuota test!")

if __name__ == "__main__":
    create_test_quotas()