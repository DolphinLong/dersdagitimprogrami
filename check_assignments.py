#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ders atamalarını kontrol et
"""

import sys
import os
import io

if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
import sqlite3

print("=" * 80)
print("🔍 DERS ATAMALARI KONTROLÜ")
print("=" * 80)

# Veritabanı tablolarını kontrol et
conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# schedule tablosu
cursor.execute("SELECT COUNT(*) FROM schedule")
schedule_count = cursor.fetchone()[0]
print(f"\n📋 schedule tablosu: {schedule_count} kayıt")

if schedule_count > 0:
    cursor.execute("SELECT * FROM schedule LIMIT 5")
    rows = cursor.fetchall()
    print("\n   İlk 5 kayıt:")
    for row in rows:
        print(f"   {row}")
else:
    print("   ⚠️  BOŞŞ! Ders atamaları yok!")

# schedule_entries tablosu
cursor.execute("SELECT COUNT(*) FROM schedule_entries")
entries_count = cursor.fetchone()[0]
print(f"\n📅 schedule_entries tablosu: {entries_count} kayıt")

if entries_count > 0:
    cursor.execute("SELECT * FROM schedule_entries LIMIT 5")
    rows = cursor.fetchall()
    print("\n   İlk 5 kayıt:")
    for row in rows:
        print(f"   {row}")

conn.close()

# DB Manager ile kontrol
print("\n" + "=" * 80)
print("DB Manager ile kontrol:")
print("=" * 80)

assignments = db_manager.get_schedule_by_school_type()
print(f"\n📝 DB Manager - Atamalar: {len(assignments)} kayıt")

if len(assignments) == 0:
    print("\n❌ SORUN BULUNDU!")
    print("   • Ders atamaları yapılmamış!")
    print("   • Lütfen UI'dan 'Ders Atama' menüsüne gidin")
    print("   • Öğretmenlere ders atayın")
    print("   • Sonra tekrar program oluşturun")
else:
    print("\n✅ Ders atamaları mevcut")
    print(f"\n   İlk 5 atama:")
    for i, assignment in enumerate(assignments[:5], 1):
        print(f"   {i}. Sınıf:{assignment.class_id}, Ders:{assignment.lesson_id}, Öğretmen:{assignment.teacher_id}")
