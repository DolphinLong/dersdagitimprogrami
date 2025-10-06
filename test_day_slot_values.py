# -*- coding: utf-8 -*-
"""
Day ve Slot değerlerini kontrol et
"""

import sys
import io

if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import db_manager

print("="*80)
print("🔍 DAY VE SLOT DEĞERLERİ KONTROLÜ")
print("="*80)

# İlk sınıfı seç
classes = db_manager.get_all_classes()
if not classes:
    print("❌ Hiç sınıf bulunamadı!")
    sys.exit(1)

selected_class = classes[0]
print(f"\n📊 Sınıf: {selected_class.name} (ID: {selected_class.class_id})")

# Bu sınıfın programını al
schedule = db_manager.get_schedule_program_by_school_type()
class_schedule = [s for s in schedule if s.class_id == selected_class.class_id]

print(f"\n✅ Toplam kayıt: {len(class_schedule)}")

# Day ve Slot istatistikleri
day_counts = {}
slot_counts = {}
duplicates = {}

for entry in class_schedule:
    # Day sayısı
    day_counts[entry.day] = day_counts.get(entry.day, 0) + 1
    
    # Slot sayısı
    slot_counts[entry.time_slot] = slot_counts.get(entry.time_slot, 0) + 1
    
    # Duplicate kontrolü
    key = (entry.day, entry.time_slot)
    if key in duplicates:
        duplicates[key].append(entry)
    else:
        duplicates[key] = [entry]

print("\n📊 GÜN BAZLI DAĞILIM:")
days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
for day in sorted(day_counts.keys()):
    day_name = days_tr[day] if day < 5 else f"Gün {day}"
    print(f"   {day_name}: {day_counts[day]} ders")

print("\n⏰ SAAT BAZLI DAĞILIM:")
for slot in sorted(slot_counts.keys()):
    print(f"   {slot+1}. saat: {slot_counts[slot]} ders")

# DUPLICATE kontrolü (ÇAKIŞMA!)
print("\n🚨 ÇAKIŞMA KONTROLÜ:")
has_duplicates = False
for key, entries in duplicates.items():
    if len(entries) > 1:
        has_duplicates = True
        day, slot = key
        day_name = days_tr[day] if day < 5 else f"Gün {day}"
        print(f"\n   ❌ ÇAKIŞMA BULUNDU: {day_name} - {slot+1}. saat")
        for entry in entries:
            lesson = db_manager.get_lesson_by_id(entry.lesson_id)
            teacher = db_manager.get_teacher_by_id(entry.teacher_id)
            lesson_name = lesson.name if lesson else "?"
            teacher_name = teacher.name if teacher else "?"
            print(f"      → {lesson_name} ({teacher_name})")

if not has_duplicates:
    print("   ✅ Çakışma yok!")

# GEÇERSIZ DEĞER kontrolü
print("\n⚠️  GEÇERSIZ DEĞER KONTROLÜ:")
invalid_found = False

for entry in class_schedule:
    if entry.day < 0 or entry.day >= 5:
        print(f"   ❌ Geçersiz gün: {entry.day}")
        invalid_found = True
    
    if entry.time_slot < 0 or entry.time_slot >= 8:  # Max 8 saat
        print(f"   ❌ Geçersiz slot: {entry.time_slot}")
        invalid_found = True

if not invalid_found:
    print("   ✅ Tüm değerler geçerli!")

# TÜM SLOTLARI GÖSTER
print("\n" + "="*80)
print("📋 TÜM DERSLER (DAY, SLOT):")
print("="*80)

for entry in class_schedule:
    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
    teacher = db_manager.get_teacher_by_id(entry.teacher_id)
    
    lesson_name = lesson.name if lesson else "?"
    teacher_name = teacher.name if teacher else "?"
    day_name = days_tr[entry.day] if entry.day < 5 else f"Gün {entry.day}"
    
    print(f"   {day_name:12s} {entry.time_slot+1:2d}. saat → {lesson_name:20s} ({teacher_name})")

print("\n" + "="*80)
