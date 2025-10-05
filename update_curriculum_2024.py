#!/usr/bin/env python3
"""
2024-2025 eğitim öğretim yılı güncel müfredatını veritabanına yükler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from utils.schedule_requirements import ScheduleRequirements

def update_lessons_for_school_type(school_type):
    """Belirli bir okul türü için dersleri günceller"""
    print(f"\n{school_type} için dersler güncelleniyor...")
    
    # Mevcut okul türünü ayarla
    db_manager.set_school_type(school_type)
    
    # Mevcut dersleri temizle
    existing_lessons = db_manager.get_all_lessons()
    for lesson in existing_lessons:
        db_manager.delete_lesson(lesson.lesson_id)
    
    # Okul türüne göre sınıf aralığını belirle
    if school_type == "İlkokul":
        grade_range = range(1, 5)
    elif school_type == "Ortaokul":
        grade_range = range(5, 9)
    else:  # Lise türleri
        grade_range = range(9, 13)
    
    # Her sınıf için zorunlu dersleri ekle
    added_lessons = set()
    for grade in grade_range:
        mandatory_subjects = ScheduleRequirements.get_mandatory_subjects_for_grade(grade, school_type)
        
        for subject_name, weekly_hours in mandatory_subjects.items():
            if subject_name not in added_lessons:
                lesson_id = db_manager.add_lesson(subject_name, weekly_hours)
                if lesson_id:
                    print(f"  ✓ {subject_name} ({weekly_hours} saat/hafta)")
                    added_lessons.add(subject_name)
                else:
                    print(f"  ✗ {subject_name} eklenemedi")
    
    # Seçmeli dersleri ekle
    optional_subjects = ScheduleRequirements.OPTIONAL_SUBJECTS
    for subject_name, weekly_hours in optional_subjects.items():
        if subject_name not in added_lessons:
            # Okul türüne uygun seçmeli dersleri filtrele
            if is_subject_appropriate_for_school_type(subject_name, school_type):
                lesson_id = db_manager.add_lesson(subject_name, weekly_hours)
                if lesson_id:
                    print(f"  ✓ {subject_name} (Seçmeli - {weekly_hours} saat/hafta)")
                    added_lessons.add(subject_name)

def is_subject_appropriate_for_school_type(subject_name, school_type):
    """Dersin okul türü için uygun olup olmadığını kontrol eder"""
    # İlkokul için sadece temel seçmeli dersler
    if school_type == "İlkokul":
        ilkokul_subjects = [
            "Satranç", "Halk Oyunları", "Drama", "Müzik", "Görsel Sanatlar",
            "Spor ve Fiziksel Etkinlikler", "Kur'an-ı Kerim", "Peygamberimizin Hayatı"
        ]
        return subject_name in ilkokul_subjects
    
    # Ortaokul için ortaokul seçmeli dersleri
    elif school_type == "Ortaokul":
        ortaokul_subjects = [
            "Matematik Uygulamaları", "Fen Uygulamaları", "Robotik ve Kodlama",
            "3D Tasarım ve Modelleme", "Bilim Uygulamaları", "Proje Tasarımı ve Üretimi",
            "Zeka Oyunları", "Satranç", "Okuma Becerileri", "Yazarlık ve Yazma Becerileri",
            "Medya Okuryazarlığı", "Girişimcilik", "Finansal Okuryazarlığı",
            "Hukuk ve Adalet", "Demokrasi ve İnsan Hakları", "Kültürümüzden Esintiler",
            "Peygamberimizin Hayatı", "Temel Dini Bilgiler", "Kur'an-ı Kerim",
            "Hz. Muhammed'in Hayatı", "Spor ve Fiziksel Etkinlikler", "Atletizm",
            "Futbol", "Basketbol", "Voleybol", "Halk Oyunları", "Modern Dans",
            "Drama", "Tiyatro", "Müze Eğitimi", "Görsel Sanatlar", "Müzik",
            "Çalgı Eğitimi", "Koro", "İkinci Yabancı Dil", "Almanca", "Fransızca",
            "Rusça", "Arapça", "Çince", "İspanyolca"
        ]
        return subject_name in ortaokul_subjects
    
    # Lise türleri için lise seçmeli dersleri
    else:
        lise_subjects = [
            "İleri Matematik", "Matematik Uygulamaları (Lise)", "İleri Fizik",
            "Fizik Uygulamaları", "İleri Kimya", "Kimya Uygulamaları",
            "İleri Biyoloji", "Biyoloji Uygulamaları", "Astronomi ve Uzay Bilimleri",
            "Çevre Bilimi", "Genetik ve Biyoteknoloji", "Sağlık Bilgisi",
            "Spor Bilimleri", "Beslenme ve Diyetetik", "Psikoloji", "Sosyoloji",
            "Mantık", "Felsefe Tarihi", "Karşılaştırmalı Edebiyat",
            "Dil ve Anlatım Uygulamaları", "Türk Dili", "Türk Edebiyatı",
            "Dünya Edebiyatından Seçmeler", "Coğrafya Uygulamaları",
            "Tarih Uygulamaları", "Sanat Tarihi", "Müze Bilimi", "Arkeoloji",
            "Antropoloji", "Ekonomi", "İşletme", "Muhasebe", "Hukuk",
            "Uluslararası İlişkiler", "Siyaset Bilimi", "İstatistik",
            "Bilgisayar Bilimleri", "Programlama", "Web Tasarımı", "Grafik Tasarım",
            "Endüstriyel Tasarım", "Mimarlık", "Mühendislik Uygulamaları",
            "İkinci Yabancı Dil", "Almanca", "Fransızca", "Rusça", "Arapça",
            "Çince", "İspanyolca"
        ]
        return subject_name in lise_subjects

def update_all_school_types():
    """Tüm okul türleri için dersleri günceller"""
    school_types = ["İlkokul", "Ortaokul", "Lise", "Anadolu Lisesi", "Fen Lisesi", "Sosyal Bilimler Lisesi"]
    
    print("2024-2025 Eğitim Öğretim Yılı Güncel Müfredatı Yükleniyor...")
    print("=" * 60)
    
    for school_type in school_types:
        update_lessons_for_school_type(school_type)
    
    print("\n" + "=" * 60)
    print("Müfredat güncelleme tamamlandı!")
    print("\nGüncel özellikler:")
    print("• 2024-2025 eğitim öğretim yılı ders saatleri")
    print("• Güncel seçmeli ders listesi")
    print("• Okul türüne göre uygun ders filtreleme")
    print("• MEB müfredatına tam uyum")

def show_current_lessons():
    """Mevcut dersleri gösterir"""
    school_types = ["İlkokul", "Ortaokul", "Lise", "Anadolu Lisesi", "Fen Lisesi", "Sosyal Bilimler Lisesi"]
    
    for school_type in school_types:
        db_manager.set_school_type(school_type)
        lessons = db_manager.get_all_lessons()
        
        print(f"\n{school_type} Dersleri ({len(lessons)} ders):")
        print("-" * 40)
        for lesson in lessons:
            print(f"  • {lesson.name} ({lesson.weekly_hours} saat/hafta)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--show":
        show_current_lessons()
    else:
        update_all_school_types()
        
        # Güncelleme sonrası özet göster
        print("\nGüncelleme Özeti:")
        show_current_lessons()