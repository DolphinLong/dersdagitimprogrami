#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

# Initialize database
db_manager = DatabaseManager()

print("🔧 Rehberlik ve Yönlendirme Düzeltme")
print("=" * 50)

# 1. Rehberlik dersini lessons tablosundan sil
lessons = db_manager.get_all_lessons()
rehberlik_lesson_id = None

for lesson in lessons:
    if "Rehberlik" in lesson.name:
        rehberlik_lesson_id = lesson.lesson_id
        print(f"📚 Bulundu: {lesson.name} (ID: {lesson.lesson_id})")
        break

if rehberlik_lesson_id:
    # 2. Önce schedule_entries tablosundan rehberlik atamalarını sil
    schedule_entries = db_manager.get_schedule_by_school_type()
    deleted_assignments = 0
    
    print(f"\n🗑️  Rehberlik atamalarını siliyorum...")
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Schedule entries'den sil
        cursor.execute("DELETE FROM schedule_entries WHERE lesson_id = ?", (rehberlik_lesson_id,))
        deleted_assignments = cursor.rowcount
        
        # Lessons tablosundan sil
        cursor.execute("DELETE FROM lessons WHERE lesson_id = ?", (rehberlik_lesson_id,))
        
        # Curriculum tablosundan da sil (varsa)
        cursor.execute("DELETE FROM curriculum WHERE lesson_id = ?", (rehberlik_lesson_id,))
        
        conn.commit()
        
        print(f"   ✅ {deleted_assignments} adet Rehberlik ataması silindi")
        print(f"   ✅ Rehberlik dersi lessons tablosundan silindi")
        print(f"   ✅ Curriculum tablosundan da temizlendi")
        
    except Exception as e:
        print(f"   ❌ Hata: {e}")
else:
    print(f"📚 Rehberlik dersi bulunamadı")

# 3. Kontrol et
print(f"\n🔍 Kontrol ediyorum...")
lessons_after = db_manager.get_all_lessons()
schedule_after = db_manager.get_schedule_by_school_type()

rehberlik_found = False
for lesson in lessons_after:
    if "Rehberlik" in lesson.name:
        rehberlik_found = True
        break

rehberlik_assignments = 0
for entry in schedule_after:
    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
    if lesson and "Rehberlik" in lesson.name:
        rehberlik_assignments += 1

if not rehberlik_found and rehberlik_assignments == 0:
    print(f"   ✅ Rehberlik tamamen temizlendi!")
    print(f"   📊 Kalan dersler: {len(lessons_after)}")
    print(f"   📊 Kalan atamalar: {len(schedule_after)}")
else:
    print(f"   ⚠️  Hala Rehberlik kalıntıları var!")

print(f"\n💡 Açıklama:")
print(f"   • Rehberlik ve Yönlendirme bir ders değil, öğretmen görevi")
print(f"   • Sınıf öğretmenleri zaten öğrencilere rehberlik yapar")
print(f"   • Bu yüzden ders programında yer almamalı")
print(f"   • Artık basit scheduler'da görünmeyecek")

print(f"\n✅ Düzeltme tamamlandı!")