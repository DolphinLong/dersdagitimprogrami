#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

# Initialize database
db_manager = DatabaseManager()

print("🔍 Rehberlik ve Yönlendirme Dersi Kontrolü")
print("=" * 50)

# Check lessons table
lessons = db_manager.get_all_lessons()
print(f"📚 Tüm Dersler:")
for lesson in lessons:
    if "Rehberlik" in lesson.name or "rehberlik" in lesson.name.lower():
        print(f"   ⚠️  {lesson.name} (ID: {lesson.lesson_id}) - BU DERS OLMAMALI!")
    else:
        print(f"   ✓ {lesson.name} (ID: {lesson.lesson_id})")

# Check schedule entries for Rehberlik
schedule_entries = db_manager.get_schedule_by_school_type()
rehberlik_entries = []

for entry in schedule_entries:
    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
    if lesson and ("Rehberlik" in lesson.name or "rehberlik" in lesson.name.lower()):
        teacher = db_manager.get_teacher_by_id(entry.teacher_id)
        class_obj = db_manager.get_class_by_id(entry.class_id)
        rehberlik_entries.append({
            'lesson': lesson.name,
            'teacher': teacher.name if teacher else 'Bilinmiyor',
            'class': class_obj.name if class_obj else 'Bilinmiyor'
        })

print(f"\n📋 Rehberlik Atamaları:")
if rehberlik_entries:
    print(f"   ⚠️  {len(rehberlik_entries)} adet Rehberlik ataması bulundu:")
    for entry in rehberlik_entries:
        print(f"      • {entry['class']}: {entry['lesson']} - {entry['teacher']}")
    print(f"\n💡 Bu atamalar silinmeli çünkü Rehberlik ders değil, öğretmen görevi!")
else:
    print(f"   ✅ Rehberlik ataması bulunamadı")

print(f"\n🎯 Sonuç:")
print(f"   • Rehberlik ve Yönlendirme bir ders değil, öğretmen görevi")
print(f"   • Bu ders lessons tablosundan silinmeli")
print(f"   • Mevcut atamalar da silinmeli")
print(f"   • Sınıf öğretmenleri zaten rehberlik yapar")