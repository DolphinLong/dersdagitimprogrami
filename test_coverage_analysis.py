# -*- coding: utf-8 -*-
"""
Test Coverage Analysis - Kapsama analizini test et
"""

import io
import sys

if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from database import db_manager

print("=" * 80)
print("🔍 GERÇEK DOLULUK ANALİZİ")
print("=" * 80)

# Okul bilgileri
school_type = db_manager.get_school_type() or "Lise"
SCHOOL_TIME_SLOTS = {
    "İlkokul": 7,
    "Ortaokul": 7,
    "Lise": 8,
    "Anadolu Lisesi": 8,
    "Fen Lisesi": 8,
    "Sosyal Bilimler Lisesi": 8,
}
time_slots_count = SCHOOL_TIME_SLOTS.get(school_type, 8)

print(f"\n📊 Okul Tipi: {school_type}")
print(f"⏰ Günlük Ders Saati: {time_slots_count}")
print(f"📅 Haftalık Gün: 5")

# Sınıfları al
classes = db_manager.get_all_classes()
print(f"\n🏫 Toplam Sınıf: {len(classes)}")

# Ders programını al
schedule = db_manager.get_schedule_program_by_school_type()
print(f"📚 Yerleşen Ders: {len(schedule)}")

# Toplam mevcut slot sayısı
total_slots = len(classes) * 5 * time_slots_count
print(f"\n🎯 TOPLAM SLOT SAYISI: {total_slots}")
print(f"   (Sınıf Sayısı × 5 Gün × {time_slots_count} Saat)")

# Dolu slotlar
filled_slots = len(schedule)
print(f"\n✅ DOLU SLOT: {filled_slots}")

# Boş slotlar
empty_slots = total_slots - filled_slots
print(f"❌ BOŞ SLOT: {empty_slots}")

# Gerçek doluluk oranı
real_coverage = (filled_slots / total_slots * 100) if total_slots > 0 else 0
print(f"\n📊 GERÇEK DOLULUK: %{real_coverage:.1f}")

# Sınıf bazlı analiz
print("\n" + "=" * 80)
print("🏫 SINIF BAZLI ANALİZ")
print("=" * 80)

for class_obj in classes:
    # Bu sınıfa yerleşen dersler
    class_schedule = [s for s in schedule if s.class_id == class_obj.class_id]

    # Dolu slotlar
    filled = len(class_schedule)

    # Toplam slot
    total = 5 * time_slots_count

    # Boş
    empty = total - filled

    # Yüzde
    percentage = (filled / total * 100) if total > 0 else 0

    status = "✅" if empty == 0 else "❌"
    print(
        f"{status} {class_obj.name:10s}: {filled:2d}/{total:2d} slot | Boş: {empty:2d} | %{percentage:.1f}"
    )

    # Boş slotları göster
    if empty > 0:
        occupied_slots = set((s.day, s.time_slot) for s in class_schedule)
        empty_slots_list = []
        for day in range(5):
            for slot in range(time_slots_count):
                if (day, slot) not in occupied_slots:
                    empty_slots_list.append((day, slot))

        # İlk 10 boş slotu göster
        days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        print(f"   Boş slotlar: ", end="")
        for i, (day, slot) in enumerate(empty_slots_list[:10]):
            print(f"{days_tr[day]} {slot+1}. saat", end="")
            if i < min(9, len(empty_slots_list) - 1):
                print(", ", end="")
        if len(empty_slots_list) > 10:
            print(f" ... (+{len(empty_slots_list) - 10} daha)")
        else:
            print()

print("\n" + "=" * 80)
print("🎯 SONUÇ")
print("=" * 80)

if empty_slots == 0:
    print("🎉 MÜKEMMEL! Hiç boş slot yok!")
elif empty_slots <= 5:
    print(f"✅ ÇOK İYİ! Sadece {empty_slots} boş slot var")
elif empty_slots <= 20:
    print(f"⚠️  DİKKAT! {empty_slots} boş slot var")
else:
    print(f"❌ SORUN VAR! {empty_slots} boş slot var")
    print("\nOlası Nedenler:")
    print("  1. Öğretmen uygunluğu yetersiz")
    print("  2. Ders atamaları eksik")
    print("  3. Kapsama analizi yanlış hesaplıyor")
    print("  4. İterasyon limiti yeterli değil")

print(f"\n📊 Gerçek Doluluk: %{real_coverage:.1f}")
print(f"🎯 Hedef: %100")
print(f"📉 Fark: %{100 - real_coverage:.1f}")
