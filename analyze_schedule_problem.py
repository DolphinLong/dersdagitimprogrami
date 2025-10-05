# -*- coding: utf-8 -*-
"""
Program Doluluğu Analiz Scripti
Neden programın tam dolmadığını tespit eder
"""

import sys
import io

# UTF-8 encoding için
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import db_manager
from collections import defaultdict


def analyze_schedule():
    """Mevcut program durumunu analiz et"""
    
    print("\n" + "="*80)
    print("📊 PROGRAM DOLULUĞU ANALİZ RAPORU")
    print("="*80)
    
    # Temel bilgiler
    classes = db_manager.get_all_classes()
    teachers = db_manager.get_all_teachers()
    lessons = db_manager.get_all_lessons()
    assignments = db_manager.get_schedule_by_school_type()
    schedule = db_manager.get_schedule_program_by_school_type()
    
    school_type = db_manager.get_school_type() or "Lise"
    
    print(f"\n🏫 Okul Bilgileri:")
    print(f"   • Okul Türü: {school_type}")
    print(f"   • Sınıf Sayısı: {len(classes)}")
    print(f"   • Öğretmen Sayısı: {len(teachers)}")
    print(f"   • Ders Sayısı: {len(lessons)}")
    print(f"   • Ders Atamaları: {len(assignments)}")
    print(f"   • Program Girdileri: {len(schedule)}")
    
    # Öğretmen yükü analizi
    print(f"\n" + "="*80)
    print("👨‍🏫 ÖĞRETMEN YÜKÜ ANALİZİ")
    print("="*80)
    
    teacher_load = defaultdict(lambda: {'classes': set(), 'total_hours': 0, 'schedule_hours': 0})
    
    for assignment in assignments:
        teacher = db_manager.get_teacher_by_id(assignment.teacher_id)
        class_obj = db_manager.get_class_by_id(assignment.class_id)
        lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
        
        if teacher and class_obj and lesson:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
            if weekly_hours:
                teacher_load[teacher.teacher_id]['name'] = teacher.name
                teacher_load[teacher.teacher_id]['subject'] = teacher.subject
                teacher_load[teacher.teacher_id]['classes'].add(class_obj.name)
                teacher_load[teacher.teacher_id]['total_hours'] += weekly_hours
    
    # Programdaki öğretmen saatlerini say
    for entry in schedule:
        if entry.teacher_id in teacher_load:
            teacher_load[entry.teacher_id]['schedule_hours'] += 1
    
    # Öğretmenleri yüke göre sırala
    sorted_teachers = sorted(teacher_load.items(), key=lambda x: x[1]['total_hours'], reverse=True)
    
    print(f"\n📋 Öğretmen Detayları:")
    print(f"{'Öğretmen':<25} {'Branş':<20} {'Sınıf':<10} {'Gerekli':<10} {'Yerleşen':<10} {'Oran':<10}")
    print("-" * 95)
    
    high_load_teachers = []
    
    for teacher_id, data in sorted_teachers:
        name = data['name']
        subject = data['subject']
        class_count = len(data['classes'])
        total_hours = data['total_hours']
        schedule_hours = data['schedule_hours']
        rate = (schedule_hours / total_hours * 100) if total_hours > 0 else 0
        
        status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
        
        print(f"{name:<25} {subject:<20} {class_count:<10} {total_hours:<10} {schedule_hours:<10} {status} {rate:.1f}%")
        
        # Yüksek yüklü öğretmenler (3+ sınıf)
        if class_count >= 3:
            high_load_teachers.append({
                'name': name,
                'class_count': class_count,
                'total_hours': total_hours,
                'rate': rate
            })
    
    # Sınıf bazlı analiz
    print(f"\n" + "="*80)
    print("📚 SINIF BAZLI ANALİZ")
    print("="*80)
    
    class_analysis = {}
    
    for class_obj in classes:
        # Bu sınıfa atanan dersleri bul
        class_lessons = []
        for assignment in assignments:
            if assignment.class_id == class_obj.class_id:
                lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
                if lesson:
                    weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                    if weekly_hours:
                        class_lessons.append({
                            'lesson': lesson.name,
                            'weekly_hours': weekly_hours,
                            'lesson_id': lesson.lesson_id
                        })
        
        # Bu sınıfın programındaki ders sayısı
        schedule_count = sum(1 for entry in schedule if entry.class_id == class_obj.class_id)
        
        # Toplam gerekli saat
        total_required = sum(l['weekly_hours'] for l in class_lessons)
        
        class_analysis[class_obj.name] = {
            'required': total_required,
            'scheduled': schedule_count,
            'lessons': class_lessons,
            'grade': class_obj.grade
        }
    
    print(f"\n📊 Sınıf Detayları:")
    print(f"{'Sınıf':<15} {'Seviye':<10} {'Ders Sayısı':<12} {'Gerekli':<10} {'Yerleşen':<10} {'Oran':<10}")
    print("-" * 80)
    
    problematic_classes = []
    
    for class_name, data in sorted(class_analysis.items()):
        required = data['required']
        scheduled = data['scheduled']
        lesson_count = len(data['lessons'])
        rate = (scheduled / required * 100) if required > 0 else 0
        
        status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
        
        print(f"{class_name:<15} {data['grade']:<10} {lesson_count:<12} {required:<10} {scheduled:<10} {status} {rate:.1f}%")
        
        if rate < 90:
            problematic_classes.append({
                'name': class_name,
                'required': required,
                'scheduled': scheduled,
                'rate': rate,
                'lessons': data['lessons']
            })
    
    # Ders bazlı analiz
    print(f"\n" + "="*80)
    print("📖 DERS BAZLI ANALİZ")
    print("="*80)
    
    lesson_analysis = defaultdict(lambda: {'required': 0, 'scheduled': 0, 'classes': []})
    
    for assignment in assignments:
        lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
        class_obj = db_manager.get_class_by_id(assignment.class_id)
        
        if lesson and class_obj:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
            if weekly_hours:
                lesson_analysis[lesson.name]['required'] += weekly_hours
                lesson_analysis[lesson.name]['classes'].append(class_obj.name)
    
    # Programdaki ders saatlerini say
    for entry in schedule:
        lesson = db_manager.get_lesson_by_id(entry.lesson_id)
        if lesson:
            lesson_analysis[lesson.name]['scheduled'] += 1
    
    print(f"\n📝 Ders Detayları:")
    print(f"{'Ders Adı':<35} {'Sınıf':<10} {'Gerekli':<10} {'Yerleşen':<10} {'Oran':<10}")
    print("-" * 80)
    
    problematic_lessons = []
    
    for lesson_name, data in sorted(lesson_analysis.items(), key=lambda x: x[1]['required'], reverse=True):
        required = data['required']
        scheduled = data['scheduled']
        class_count = len(data['classes'])
        rate = (scheduled / required * 100) if required > 0 else 0
        
        status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
        
        print(f"{lesson_name:<35} {class_count:<10} {required:<10} {scheduled:<10} {status} {rate:.1f}%")
        
        if rate < 90:
            problematic_lessons.append({
                'name': lesson_name,
                'required': required,
                'scheduled': scheduled,
                'rate': rate
            })
    
    # Genel Özet
    print(f"\n" + "="*80)
    print("🎯 GENEL ÖZET VE ÖNERİLER")
    print("="*80)
    
    total_required = sum(data['required'] for data in class_analysis.values())
    total_scheduled = len(schedule)
    overall_rate = (total_scheduled / total_required * 100) if total_required > 0 else 0
    
    print(f"\n📊 Genel İstatistikler:")
    print(f"   • Toplam Gerekli Saat: {total_required}")
    print(f"   • Yerleştirilen Saat: {total_scheduled}")
    print(f"   • Genel Doluluk Oranı: {overall_rate:.1f}%")
    print(f"   • Eksik Saat: {total_required - total_scheduled}")
    
    # Sorun tespiti
    print(f"\n🔍 Tespit Edilen Sorunlar:")
    
    if high_load_teachers:
        print(f"\n   ⚠️  Yüksek Yüklü Öğretmenler ({len(high_load_teachers)} kişi):")
        for t in high_load_teachers[:5]:  # En yüklü 5'i göster
            print(f"      • {t['name']}: {t['class_count']} sınıfa {t['total_hours']} saat ders veriyor ({t['rate']:.1f}% yerleşti)")
        print(f"      💡 Çözüm: Bu öğretmenlerin yükünü azaltın veya yeni öğretmen ekleyin")
    
    if problematic_classes:
        print(f"\n   ❌ Sorunlu Sınıflar ({len(problematic_classes)} adet):")
        for c in problematic_classes[:5]:  # En sorunlu 5'i göster
            print(f"      • {c['name']}: {c['scheduled']}/{c['required']} saat yerleşti ({c['rate']:.1f}%)")
        print(f"      💡 Çözüm: Bu sınıfların derslerini kontrol edin ve öğretmen uygunluğunu artırın")
    
    if problematic_lessons:
        print(f"\n   ❌ Yerleştirilemeyen Dersler ({len(problematic_lessons)} adet):")
        for l in problematic_lessons[:5]:  # En sorunlu 5'i göster
            print(f"      • {l['name']}: {l['scheduled']}/{l['required']} saat yerleşti ({l['rate']:.1f}%)")
        print(f"      💡 Çözüm: Bu derslerin öğretmenlerinin uygunluk saatlerini kontrol edin")
    
    # Öğretmen çakışma analizi
    print(f"\n   🔍 Öğretmen Çakışma Analizi:")
    teacher_conflicts = 0
    for teacher_id, data in teacher_load.items():
        if len(data['classes']) >= 3 and data['schedule_hours'] < data['total_hours'] * 0.9:
            teacher_conflicts += 1
    
    if teacher_conflicts > 0:
        print(f"      • {teacher_conflicts} öğretmen muhtemelen çakışma yaşıyor")
        print(f"      💡 Çözüm: Öğretmen uygunluk saatlerini genişletin veya ders yükünü dengeleyin")
    
    # Öneriler
    print(f"\n💡 ÖNERİLER:")
    
    if overall_rate < 90:
        print(f"   1. 🎯 Öğretmen Uygunluğu:")
        print(f"      • Öğretmenlerin haftanın her gününe ve her saatine uygun olduklarından emin olun")
        print(f"      • 'Öğretmen Müsaitliği' menüsünden uygunluk saatlerini artırın")
    
    if high_load_teachers:
        print(f"   2. ⚖️ Öğretmen Yükü Dengeleme:")
        print(f"      • {len(high_load_teachers)} öğretmenin yükü çok yüksek")
        print(f"      • Mümkünse bu öğretmenlerin bazı sınıflarını başka öğretmenlere atayın")
        print(f"      • Veya yeni öğretmen ekleyin")
    
    if problematic_lessons:
        print(f"   3. 📚 Ders Müfredatı:")
        print(f"      • Bazı derslerin haftalık saat sayısı çok yüksek olabilir")
        print(f"      • Müfredat ayarlarını gözden geçirin")
    
    print(f"\n   4. 🚀 Algoritma İyileştirmesi:")
    print(f"      • Mevcut algoritma %{overall_rate:.1f} başarı sağlıyor")
    print(f"      • Daha esnek yerleştirme algoritması kullanılabilir")
    print(f"      • Backtracking ve slot optimizasyonu eklenebilir")
    
    print(f"\n" + "="*80)
    print(f"✅ Analiz Tamamlandı")
    print(f"="*80 + "\n")


if __name__ == "__main__":
    try:
        analyze_schedule()
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
