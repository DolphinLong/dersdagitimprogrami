#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Okul türü uyumsuzluğunu düzelt - Anadolu Lisesi atamalarını Ortaokul'a dönüştür
"""

import sqlite3
import io
import sys

if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

print("=" * 80)
print("🔧 OKUL TÜRÜ UYUMSUZLUĞU DÜZELTİLİYOR")
print("=" * 80)

conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# Mevcut okul türü
cursor.execute("SELECT setting_value FROM settings WHERE setting_key='school_type'")
result = cursor.fetchone()
current_school_type = result[0] if result else None

print(f"\n📌 Mevcut okul türü: {current_school_type}")

# schedule tablosundaki okul türleri
cursor.execute("SELECT school_type, COUNT(*) FROM schedule GROUP BY school_type")
schedule_types = cursor.fetchall()

print(f"\n📋 schedule tablosundaki veriler:")
for school_type, count in schedule_types:
    print(f"   • {school_type}: {count} atama")

# Eğer mevcut okul türü için atama yoksa
cursor.execute("SELECT COUNT(*) FROM schedule WHERE school_type = ?", (current_school_type,))
current_type_count = cursor.fetchone()[0]

if current_type_count == 0 and current_school_type:
    print(f"\n⚠️  {current_school_type} için atama yok!")
    print(f"\n❓ Ne yapmak istersiniz?")
    print(f"   1) Diğer okul türündeki atamaları {current_school_type}'a dönüştür")
    print(f"   2) Mevcut okul türünü değiştir")
    print(f"   3) Yeni atamalar oluştur")
    
    print(f"\n📝 OTOMATİK ÇÖZÜM: Tüm atamaları '{current_school_type}' olarak güncelliyorum...")
    
    # Tüm schedule kayıtlarını mevcut okul türüne dönüştür
    cursor.execute("UPDATE schedule SET school_type = ?", (current_school_type,))
    updated = cursor.rowcount
    conn.commit()
    
    print(f"   ✅ {updated} atama '{current_school_type}' olarak güncellendi")
    
    # Kontrol
    cursor.execute("SELECT COUNT(*) FROM schedule WHERE school_type = ?", (current_school_type,))
    new_count = cursor.fetchone()[0]
    print(f"   ✅ {current_school_type} için toplam: {new_count} atama")
    
else:
    print(f"\n✅ {current_school_type} için zaten {current_type_count} atama mevcut")

conn.close()

print("\n" + "=" * 80)
print("✅ İŞLEM TAMAMLANDI!")
print("=" * 80)
print("\nŞimdi programı oluşturabilirsiniz!")
