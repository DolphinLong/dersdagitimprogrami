#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blok kuralı ihlallerini kontrol eden script
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
from collections import defaultdict

def check_block_violations():
    """Blok kuralı ihlallerini kontrol et"""
    
    print("=" * 80)
    print("🔍 BLOK KURALI İHLALLERİ KONTROLÜ")
    print("=" * 80)
    
    schedule_program = db_manager.get_schedule_program_by_school_type()
    classes = db_manager.get_all_classes()
    lessons = db_manager.get_all_lessons()
    
    print(f"\n📊 Toplam kayıt: {len(schedule_program)}")
    
    violations = []
    
    # Her sınıf için her dersi kontrol et
    for class_obj in classes:
        class_entries = [e for e in schedule_program if e.class_id == class_obj.class_id]
        
        # Dersleri grupla
        lesson_groups = defaultdict(list)
        for entry in class_entries:
            lesson_groups[entry.lesson_id].append(entry)
        
        print(f"\n📚 {class_obj.name}:")
        
        for lesson_id, entries in lesson_groups.items():
            lesson = next((l for l in lessons if l.lesson_id == lesson_id), None)
            if not lesson:
                continue
            
            # Haftalık saat gereksinimi
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson_id, class_obj.grade)
            
            # Günlere göre grupla
            day_groups = defaultdict(list)
            for entry in entries:
                day_groups[entry.day].append(entry.time_slot)
            
            # Her gün için sıralı slotları kontrol et
            day_blocks = {}
            for day, slots in day_groups.items():
                sorted_slots = sorted(slots)
                blocks = []
                current_block = [sorted_slots[0]]
                
                for i in range(1, len(sorted_slots)):
                    if sorted_slots[i] == sorted_slots[i-1] + 1:
                        # Ardışık
                        current_block.append(sorted_slots[i])
                    else:
                        # Yeni blok
                        blocks.append(current_block)
                        current_block = [sorted_slots[i]]
                
                blocks.append(current_block)
                day_blocks[day] = blocks
            
            # Blok kurallarını kontrol et
            total_hours = len(entries)
            num_days = len(day_groups)
            
            # Beklenen blok dağılımı
            expected_blocks = get_expected_blocks(weekly_hours)
            expected_days = len(expected_blocks)
            
            # Gerçek blok dağılımı
            actual_blocks = []
            for day, blocks in sorted(day_blocks.items()):
                for block in blocks:
                    actual_blocks.append(len(block))
            
            # Tek saatlik dersler (1 saat) için sorun yok
            if weekly_hours == 1:
                status = "✅"
            # 2 saatlik dersler MUTLAKA tek blok olmalı
            elif weekly_hours == 2:
                if len(actual_blocks) == 1 and actual_blocks[0] == 2:
                    status = "✅"
                else:
                    status = "❌"
                    violations.append({
                        'class': class_obj.name,
                        'lesson': lesson.name,
                        'problem': f"2 saatlik ders blok değil! Dağılım: {actual_blocks}",
                        'expected': "[2]",
                        'actual': str(actual_blocks)
                    })
            # 3+ saatlik dersler için blok kontrolü
            else:
                # Tek saatlik parçalar var mı kontrol et
                has_singles = any(b == 1 for b in actual_blocks)
                
                # Beklenen blok yapısına uyuyor mu
                blocks_match = sorted(actual_blocks) == sorted(expected_blocks)
                
                if blocks_match and num_days == expected_days:
                    status = "✅"
                elif has_singles and weekly_hours >= 2:
                    status = "⚠️"
                    violations.append({
                        'class': class_obj.name,
                        'lesson': lesson.name,
                        'problem': f"Paramparça! Tek saatlik dağılımlar var",
                        'expected': str(expected_blocks),
                        'actual': str(actual_blocks)
                    })
                elif num_days != expected_days:
                    status = "⚠️"
                    violations.append({
                        'class': class_obj.name,
                        'lesson': lesson.name,
                        'problem': f"Gün sayısı yanlış! {num_days} gün olmalıydı {expected_days}",
                        'expected': str(expected_blocks),
                        'actual': str(actual_blocks)
                    })
                else:
                    status = "⚠️"
                    violations.append({
                        'class': class_obj.name,
                        'lesson': lesson.name,
                        'problem': "Blok kuralına uymuyor",
                        'expected': str(expected_blocks),
                        'actual': str(actual_blocks)
                    })
            
            # Detaylı rapor
            day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
            day_details = []
            for day in sorted(day_blocks.keys()):
                blocks = day_blocks[day]
                block_strs = [f"{len(b)}saat" for b in blocks]
                day_details.append(f"{day_names[day]}:{'+'.join(block_strs)}")
            
            print(f"   {status} {lesson.name} ({total_hours}saat): {' | '.join(day_details)}")
            if status != "✅":
                print(f"      Beklenen: {expected_blocks} blok, {expected_days} gün")
                print(f"      Gerçek: {actual_blocks} blok, {num_days} gün")
    
    # Özet
    print("\n" + "=" * 80)
    print(f"📊 SONUÇ: {len(violations)} İHLAL TESPİT EDİLDİ")
    print("=" * 80)
    
    if violations:
        print("\n❌ İHLALLER:")
        for v in violations[:10]:  # İlk 10 ihlal
            print(f"\n   • {v['class']} - {v['lesson']}")
            print(f"     Sorun: {v['problem']}")
            print(f"     Beklenen: {v['expected']}")
            print(f"     Gerçek: {v['actual']}")
    else:
        print("\n✅ TÜM DERSLER BLOK KURALINA UYGUN!")
    
    return violations

def get_expected_blocks(weekly_hours):
    """Beklenen blok dağılımını döndür"""
    if weekly_hours >= 6:
        return [2, 2, 2]
    elif weekly_hours == 5:
        return [2, 2, 1]
    elif weekly_hours == 4:
        return [2, 2]
    elif weekly_hours == 3:
        return [2, 1]
    elif weekly_hours == 2:
        return [2]
    elif weekly_hours == 1:
        return [1]
    else:
        return []

if __name__ == "__main__":
    violations = check_block_violations()
    
    if violations:
        print(f"\n⚠️  {len(violations)} ihlal bulundu!")
        print("\n💡 Çözüm: Ultra aggressive gap filling'i devre dışı bırakın")
        print("   veya blok kurallarını koruyacak şekilde yeniden yazın.")
    else:
        print("\n🎉 Mükemmel! Tüm dersler blok kuralına uygun!")
