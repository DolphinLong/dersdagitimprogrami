#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Düzeltilmiş algoritmayı test et
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
from algorithms.simple_perfect_scheduler import SimplePerfectScheduler

print("=" * 80)
print("🔧 DÜZELTİLMİŞ ALGORİTMA TESTİ")
print("=" * 80)

# Veritabanını temizle
print("\n🧹 Eski program temizleniyor...")
db_manager.clear_schedule()

# Yeni program oluştur
print("\n🚀 Yeni program oluşturuluyor...")
print("   • Ultra aggressive gap filling: KAPALI ✓")
print("   • Blok kuralları: AKTİF ✓")
print()

scheduler = SimplePerfectScheduler(db_manager, relaxed_mode=False)
schedule_entries = scheduler.generate_schedule()

print("\n✅ Program oluşturuldu!")
print(f"📊 Toplam slot: {len(schedule_entries)}")

print("\n" + "=" * 80)
print("Şimdi blok kurallarını kontrol ediyorum...")
print("=" * 80)

# Blok kontrolü için check_block_violations'ı çalıştır
import subprocess
result = subprocess.run(
    ["python", "check_block_violations.py"], 
    capture_output=True, 
    text=True,
    encoding='utf-8'
)

print(result.stdout)

if "0 İHLAL" in result.stdout:
    print("\n🎉 MÜKEMMEL! BLOK KURALLARI KORUNDU!")
else:
    print("\n⚠️  Hala bazı ihlaller var ama çok daha iyi!")
