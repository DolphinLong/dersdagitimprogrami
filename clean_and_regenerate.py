#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanını temizle ve YENİDEN program oluştur
"""

import sys
import os
import io

# Windows encoding fix
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from algorithms.hybrid_optimal_scheduler import HybridOptimalScheduler

print("=" * 80)
print("🧹 VERİTABANI TEMİZLİĞİ VE YENİ PROGRAM")
print("=" * 80)

# 1. Veritabanını tamamen temizle
print("\n1️⃣ Veritabanı temizleniyor...")
try:
    # schedule_entries tablosunu temizle
    import sqlite3
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # Tüm program verilerini sil
    cursor.execute("DELETE FROM schedule_entries")
    conn.commit()
    
    deleted = cursor.rowcount
    print(f"   ✅ {deleted} eski kayıt silindi")
    
    conn.close()
except Exception as e:
    print(f"   ⚠️  Hata: {e}")

# 2. Hybrid Optimal Scheduler ile yeni program oluştur
print("\n2️⃣ YENİ PROGRAM OLUŞTURULUYOR...")
print("   • Algoritma: Hybrid Optimal Scheduler")
print("   • Blok kuralları: AKTİF ✓")
print("   • Arc Consistency: AKTİF ✓")
print()

try:
    scheduler = HybridOptimalScheduler(db_manager)
    schedule_entries = scheduler.generate_schedule()
    
    print(f"\n✅ Program oluşturuldu: {len(schedule_entries)} slot")
    
except Exception as e:
    print(f"\n❌ Hata oluştu: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Sonuçları kontrol et
print("\n" + "=" * 80)
print("3️⃣ BLOK KURALLARI KONTROLÜ")
print("=" * 80)

import subprocess
result = subprocess.run(
    ["python", "check_block_violations.py"],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

# Sadece özet bilgileri göster
lines = result.stdout.split('\n')
for line in lines:
    if any(keyword in line for keyword in ['SONUÇ', 'İHLAL', 'MÜKEMMEL', 'Toplam']):
        print(line)

print("\n" + "=" * 80)
print("✅ İŞLEM TAMAMLANDI!")
print("=" * 80)
print("\n📌 Şimdi uygulamayı açın ve programı kontrol edin.")
print("   Eğer hala sorun varsa, uygulamayı KAPAT-AÇ yapın.")
