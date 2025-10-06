# -*- coding: utf-8 -*-
"""
Belirli bir sınıfın programını kontrol et
"""

import sys
import io

if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import db_manager

# İlk sınıfı seç
classes = db_manager.get_all_classes()
if not classes:
    print("❌ Hiç sınıf bulunamadı!")
    sys.exit(1)

selected_class = classes[0]

print("="*80)
print(f"🔍 SINIF PROGRAMI ANALİZİ: {selected_class.name}")
print("="*80)

# Okul bilgileri
school_type = db_manager.get_school_type() or "Lise"
SCHOOL_TIME_SLOTS = {
    "İlkokul": 7,
    "Ortaokul": 7,
    "Lise": 8,
    "Anadolu Lisesi": 8,
    "Fen Lisesi": 8,
    "Sosyal Bilimler Lisesi": 8
}
time_slots_count = SCHOOL_TIME_SLOTS.get(school_type, 8)

print(f"\n📊 Sınıf ID: {selected_class.class_id}")
print(f"📊 Sınıf Adı: {selected_class.name}")
print(f"📊 Seviye: {selected_class.grade}")
print(f"⏰ Günlük Saat: {time_slots_count}")

# Bu sınıfın programını al
schedule = db_manager.get_schedule_program_by_school_type()
class_schedule = [s for s in schedule if s.class_id == selected_class.class_id]

print(f"\n✅ Yerleşen Ders: {len(class_schedule)}")
print(f"🎯 Beklenen: {5 * time_slots_count}")

# Tablo formatında göster
days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]

print("\n" + "="*80)
print("📅 HAFTALIK PROGRAM")
print("="*80)

# Tablo başlığı
print(f"\n{'Saat':^6s} |", end="")
for day in days_tr:
    print(f" {day:^15s} |", end="")
print()
print("-" * 80)

# Her saat için
for slot in range(time_slots_count):
    print(f"{slot+1:^6d} |", end="")
    
    for day in range(5):
        # Bu slotta ders var mı?
        lesson_found = None
        for entry in class_schedule:
            if entry.day == day and entry.time_slot == slot:
                lesson_found = entry
                break
        
        if lesson_found:
            # Ders ve öğretmen bilgisi
            lesson = db_manager.get_lesson_by_id(lesson_found.lesson_id)
            teacher = db_manager.get_teacher_by_id(lesson_found.teacher_id)
            
            lesson_name = lesson.name if lesson else "?"
            teacher_name = teacher.name if teacher else "?"
            
            # Kısa gösterim
            display = f"{lesson_name[:7]}"
            print(f" {display:^15s} |", end="")
        else:
            # BOŞ
            print(f" {'[BOŞ]':^15s} |", end="")
    
    print()

print("-" * 80)

# Boş slotları say
empty_count = 0
empty_slots = []
for day in range(5):
    for slot in range(time_slots_count):
        found = False
        for entry in class_schedule:
            if entry.day == day and entry.time_slot == slot:
                found = True
                break
        if not found:
            empty_count += 1
            empty_slots.append((day, slot))

print(f"\n📊 İSTATİSTİK:")
print(f"   ✅ Dolu Slot: {len(class_schedule)}")
print(f"   ❌ Boş Slot: {empty_count}")
print(f"   📈 Doluluk: %{len(class_schedule) / (5 * time_slots_count) * 100:.1f}")

if empty_slots:
    print(f"\n⚠️  BOŞ SLOTLAR:")
    for day, slot in empty_slots:
        print(f"   • {days_tr[day]} - {slot+1}. saat")

print("\n" + "="*80)
