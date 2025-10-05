"""
Update MEB subjects in the database with current 2025-2026 curriculum
"""

from database import db_manager

def update_meb_subjects():
    """Update the database with current MEB subjects, especially elective courses"""
    
    print("Updating MEB subjects in the database...")
    
    # Get current school type
    school_type = db_manager.get_school_type()
    if not school_type:
        print("No school type set. Please set a school type first.")
        return
    
    print(f"Current school type: {school_type}")
    
    # Define updated MEB subjects by school type with focus on elective courses
    meb_subjects = {
        "İlkokul": {
            "mandatory": [
                ("Türkçe", 6),
                ("Matematik", 5),
                ("Hayat Bilgisi", 2),
                ("Görsel Sanatlar", 1),
                ("Müzik", 1),
                ("Beden Eğitimi ve Oyun", 2),
                ("Yabancı Dil", 2),
                ("Din Kültürü ve Ahlak Bilgisi", 1)
            ],
            "elective": [
                ("Bilişim", 1),
                ("Rehberlik ve Yönlendirme", 1),
                ("Serbest Etkinlikler", 1),
                ("Trafik Güvenliği", 1),
                ("İnsan Hakları, Vatandaşlık ve Demokrasi", 1),
                ("Oyun ve Fiziki Etkinlikler", 2),
                ("Değerler Eğitimi", 1),
                ("Yaşam Becerileri", 1),
                ("Çevre Eğitimi", 1),
                ("Okuma Yazma Hazırlığı", 2),
                ("Temel Matematik Becerileri", 2)
            ]
        },
        "Ortaokul": {
            "mandatory": [
                ("Türkçe", 6),
                ("Matematik", 5),
                ("Fen Bilimleri", 4),
                ("Sosyal Bilgiler", 3),
                ("Görsel Sanatlar", 1),
                ("Müzik", 1),
                ("Beden Eğitimi ve Spor", 2),
                ("Yabancı Dil", 3),
                ("Din Kültürü ve Ahlak Bilgisi", 2),
                ("Teknoloji ve Tasarım", 2)
            ],
            "elective": [
                ("Bilişim Teknolojileri ve Yazılım", 2),
                ("Rehberlik ve Yönlendirme", 1),
                ("T.C. İnkılap Tarihi ve Atatürkçülük", 2),
                ("Dijital Vatandaşlık", 1),
                ("Finansal Okuryazarlık", 1),
                ("Görsel Sanatlar Uygulamaları", 1),
                ("Müzik Uygulamaları", 1),
                ("İtalyanca", 2),
                ("Japonca", 2),
                ("Robotik Kodlama", 2),
                ("Yapay Zeka Uygulamaları", 2),
                ("Drama", 1),
                ("Geleneksel Sanatlar", 1)
            ]
        },
        "Lise": {
            "mandatory": [
                ("Türk Dili ve Edebiyatı", 5),
                ("Matematik", 6),
                ("Fizik", 2),
                ("Kimya", 2),
                ("Biyoloji", 2),
                ("Tarih", 2),
                ("Coğrafya", 2),
                ("Felsefe", 2),
                ("Yabancı Dil", 4),
                ("Din Kültürü ve Ahlak Bilgisi", 2),
                ("Görsel Sanatlar", 1),
                ("Müzik", 1),
                ("Beden Eğitimi", 2),
                ("Bilişim", 2),
                ("Rehberlik", 1)
            ],
            "elective": [
                ("Sağlık Bilgisi ve İlk Yardım", 1),
                ("Yapay Zeka ve Makine Öğrenmesi", 2),
                ("Veri Bilimi", 2),
                ("Siber Güvenlik", 2),
                ("Oyun Geliştirme", 2),
                ("Mobil Uygulama Geliştirme", 2),
                ("Seçmeli 1", 2),
                ("Seçmeli 2", 2),
                ("Seçmeli 3", 1)
            ]
        },
        "Anadolu Lisesi": {
            "mandatory": [
                ("Türk Dili ve Edebiyatı", 5),
                ("Matematik", 6),
                ("Fizik", 2),
                ("Kimya", 2),
                ("Biyoloji", 2),
                ("Tarih", 2),
                ("Coğrafya", 2),
                ("Felsefe", 2),
                ("Yabancı Dil", 4),
                ("Din Kültürü ve Ahlak Bilgisi", 2),
                ("Görsel Sanatlar", 1),
                ("Müzik", 1),
                ("Beden Eğitimi", 2),
                ("Bilişim", 2),
                ("Rehberlik", 1)
            ],
            "elective": [
                ("Sağlık Bilgisi ve İlk Yardım", 1),
                ("Yapay Zeka ve Makine Öğrenmesi", 2),
                ("Veri Bilimi", 2),
                ("Siber Güvenlik", 2),
                ("Oyun Geliştirme", 2),
                ("Mobil Uygulama Geliştirme", 2),
                ("Seçmeli 1", 2),
                ("Seçmeli 2", 2),
                ("Seçmeli 3", 1)
            ]
        },
        "Fen Lisesi": {
            "mandatory": [
                ("Türk Dili ve Edebiyatı", 5),
                ("Matematik", 6),
                ("Fizik", 3),
                ("Kimya", 3),
                ("Biyoloji", 3),
                ("Tarih", 2),
                ("Coğrafya", 2),
                ("Felsefe", 2),
                ("Birinci Yabancı Dil", 4),
                ("Din Kültürü ve Ahlak Bilgisi", 2),
                ("Beden Eğitimi ve Spor", 2),
                ("Görsel Sanatlar", 1),
                ("Müzik", 1),
                ("Sağlık Bilgisi ve Trafik Kültürü", 1),
                ("Bilişim Teknolojileri ve Yazılım", 2),
                ("Rehberlik ve Yönlendirme", 1)
            ],
            "elective": [
                ("Seçmeli Matematik", 2),
                ("Seçmeli Fizik", 2),
                ("Seçmeli Kimya", 2),
                ("Seçmeli Biyoloji", 2),
                ("Genetik Bilimine Giriş", 2),
                ("Tıp Bilimine Giriş", 2),
                ("Astronomi ve Uzay Bilimleri", 2),
                ("Sosyal Bilim Çalışmaları", 2),
                ("Düşünme Eğitimi", 2),
                ("Kur'an-ı Kerim", 1),
                ("Peygamberimizin Hayatı (Fen Lise)", 1),
                ("Temel Dini Bilgiler", 1),
                ("Spor Eğitimi", 1),
                ("Sanat Eğitimi", 1),
                ("İslam Kültür ve Medeniyeti", 1),
                ("Osmanlı Türkçesi", 1),
                ("İkinci Yabancı Dil", 2)
            ]
        },
        "Sosyal Bilimler Lisesi": {
            "mandatory": [
                ("Türk Dili ve Edebiyatı", 5),
                ("Matematik", 6),
                ("Tarih", 3),
                ("Coğrafya", 3),
                ("Felsefe", 2),
                ("Psikoloji", 2),
                ("Sosyoloji", 2),
                ("İktisat", 2),
                ("Hukuk", 2),
                ("Yabancı Dil", 4),
                ("Din Kültürü ve Ahlak Bilgisi", 2),
                ("Görsel Sanatlar", 1),
                ("Müzik", 1),
                ("Beden Eğitimi", 2),
                ("Bilişim", 2),
                ("Rehberlik", 1)
            ],
            "elective": [
                ("Seçmeli 1", 2),
                ("Seçmeli 2", 2),
                ("Seçmeli 3", 1),
                ("Mantık", 2),
                ("Çağdaş Türk ve Dünya Tarihi", 2),
                ("Sanat Tarihi", 2),
                ("Osmanlı Türkçesi", 2),
                ("Sosyal Bilim Çalışmaları", 2),
                ("Fen Bilimleri Uygulamaları", 2),
                ("Matematik Uygulamaları", 2),
                ("Proje Tasarımı", 2),
                ("Ortak Türk Edebiyatı", 2),
                ("İkinci Yabancı Dil", 2),
                ("Türk Dünyası Coğrafyası", 2)
            ]
        }
    }
    
    # Get subjects for current school type
    subjects_data = meb_subjects.get(school_type, {})
    
    # Add mandatory subjects
    mandatory_subjects = subjects_data.get("mandatory", [])
    print(f"\nAdding {len(mandatory_subjects)} mandatory subjects...")
    
    for subject_name, weekly_hours in mandatory_subjects:
        try:
            lesson_id = db_manager.add_lesson(subject_name, weekly_hours)
            if lesson_id:
                print(f"  ✓ Added mandatory subject: {subject_name} ({weekly_hours} hours)")
            else:
                print(f"  - Subject already exists: {subject_name}")
        except Exception as e:
            print(f"  ✗ Error adding subject {subject_name}: {e}")
    
    # Add elective subjects
    elective_subjects = subjects_data.get("elective", [])
    print(f"\nAdding {len(elective_subjects)} elective subjects...")
    
    for subject_name, weekly_hours in elective_subjects:
        try:
            lesson_id = db_manager.add_lesson(subject_name, weekly_hours)
            if lesson_id:
                print(f"  ✓ Added elective subject: {subject_name} ({weekly_hours} hours)")
            else:
                print(f"  - Subject already exists: {subject_name}")
        except Exception as e:
            print(f"  ✗ Error adding subject {subject_name}: {e}")
    
    print(f"\nMEB subjects update completed for {school_type}!")
    print("Total subjects in database:", len(db_manager.get_all_lessons()))

if __name__ == "__main__":
    update_meb_subjects()
    db_manager.close()