"""
Schedule requirements for all school levels (grades 1-12)
Based on Turkish Ministry of National Education guidelines - 2025-2026 Academic Year
Updated with latest MEB curriculum requirements
"""


class ScheduleRequirements:
    """Handles schedule requirements for elementary and middle schools"""

    # Total weekly hours by school level (2025-2026 güncel MEB)
    TOTAL_HOURS = {
        "İlkokul": 30,  # Grades 1-4
        "Ortaokul": 35,  # Grades 5-8
        "Lise": 40,  # Grades 9-12 (Genel Lise)
        "Anadolu Lisesi": 40,  # Grades 9-12 (Anadolu Lisesi)
        "Fen Lisesi": 40,  # Grades 9-12 (Fen Lisesi)
        "Sosyal Bilimler Lisesi": 40,  # Grades 9-12 (Sosyal Bilimler Lisesi)
    }

    # Optional subjects with their hour limits (2025-2026 güncel MEB)
    OPTIONAL_SUBJECTS = {
        # İlkokul Seçmeli Dersleri (2025-2026)
        "Oyun ve Fiziki Etkinlikler": 2,
        "Değerler Eğitimi": 1,
        "Yaşam Becerileri": 2,
        "Çevre Eğitimi": 1,
        "Okuma Yazma Hazırlığı": 2,
        "Temel Matematik Becerileri": 2,
        # Ortaokul Seçmeli Dersleri (2025-2026)
        "Matematik Uygulamaları": 2,
        "Fen Uygulamaları": 2,
        "Robotik ve Kodlama": 2,
        "3D Tasarım ve Modelleme": 2,
        "Bilim Uygulamaları": 2,
        "Proje Tasarımı ve Üretimi": 2,
        "Zeka Oyunları": 2,
        "Satranç": 2,
        "Okuma Becerileri": 2,
        "Yazarlık ve Yazma Becerileri": 2,
        "Medya Okuryazarlığı": 2,
        "Dijital Vatandaşlık": 2,
        "Girişimcilik": 2,
        "Finansal Okuryazarlık": 2,
        "Hukuk ve Adalet": 2,
        "Demokrasi ve İnsan Hakları": 2,
        "Kültürümüzden Esintiler": 2,
        "Peygamberimizin Hayatı": 2,
        "Temel Dini Bilgiler": 2,
        "Kur'an-ı Kerim": 2,
        "Hz. Muhammed'in Hayatı": 2,
        "Spor ve Fiziksel Etkinlikler": 2,
        "Atletizm": 2,
        "Futbol": 2,
        "Basketbol": 2,
        "Voleybol": 2,
        "Halk Oyunları": 2,
        "Modern Dans": 2,
        "Drama": 2,
        "Tiyatro": 2,
        "Müze Eğitimi": 2,
        "Görsel Sanatlar Uygulamaları": 2,
        "Müzik Uygulamaları": 2,
        "Çalgı Eğitimi": 2,
        "Koro": 2,
        "İkinci Yabancı Dil": 4,
        "Almanca": 4,
        "Fransızca": 4,
        "Rusça": 4,
        "Arapça": 4,
        "Çince": 4,
        "İspanyolca": 4,
        "İtalyanca": 4,
        "Japonca": 4,
        # Lise Seçmeli Dersleri (2025-2026)
        "İleri Matematik": 4,
        "Matematik Uygulamaları": 4,
        "İleri Fizik": 4,
        "Fizik Uygulamaları": 4,
        "İleri Kimya": 4,
        "Kimya Uygulamaları": 4,
        "İleri Biyoloji": 4,
        "Biyoloji Uygulamaları": 4,
        "Astronomi ve Uzay Bilimleri": 2,
        "Çevre Bilimi": 2,
        "Genetik ve Biyoteknoloji": 2,
        "Sağlık Bilgisi ve İlk Yardım": 2,
        "Spor Bilimleri": 2,
        "Beslenme ve Diyetetik": 2,
        "Psikoloji": 2,
        "Sosyoloji": 2,
        "Mantık": 2,
        "Felsefe Tarihi": 2,
        "Karşılaştırmalı Edebiyat": 2,
        "Dil ve Anlatım Uygulamaları": 2,
        "Türk Dili": 2,
        "Türk Edebiyatı": 2,
        "Dünya Edebiyatından Seçmeler": 2,
        "Coğrafya Uygulamaları": 2,
        "Tarih Uygulamaları": 2,
        "Sanat Tarihi": 2,
        "Müze Bilimi": 2,
        "Arkeoloji": 2,
        "Antropoloji": 2,
        "Ekonomi": 4,
        "İşletme": 4,
        "Muhasebe": 4,
        "Hukuk": 4,
        "Uluslararası İlişkiler": 2,
        "Siyaset Bilimi": 2,
        "İstatistik": 2,
        "Bilgisayar Bilimleri": 4,
        "Programlama": 4,
        "Web Tasarımı": 2,
        "Grafik Tasarım": 2,
        "Endüstriyel Tasarım": 2,
        "Mimarlık": 2,
        "Mühendislik Uygulamaları": 2,
        "Yapay Zeka ve Makine Öğrenmesi": 2,
        "Veri Bilimi": 2,
        "Siber Güvenlik": 2,
        "Oyun Geliştirme": 2,
        "Mobil Uygulama Geliştirme": 2,
    }

    # Mandatory subjects and their weekly hours by grade (2025-2026 güncel MEB müfredatı)
    MANDATORY_SUBJECTS = {
        # Elementary School (Grades 1-4) - İlkokul (2025-2026)
        1: {
            "Türkçe": 10,
            "Matematik": 5,
            "Hayat Bilgisi": 4,
            "Görsel Sanatlar": 2,
            "Müzik": 2,
            "Beden Eğitimi ve Oyun": 2,
            "Serbest Etkinlikler": 5,
        },
        2: {
            "Türkçe": 10,
            "Matematik": 5,
            "Hayat Bilgisi": 3,
            "Görsel Sanatlar": 2,
            "Müzik": 2,
            "Beden Eğitimi ve Oyun": 2,
            "Yabancı Dil": 2,
            "Serbest Etkinlikler": 4,
        },
        3: {
            "Türkçe": 8,
            "Matematik": 5,
            "Hayat Bilgisi": 3,
            "Fen Bilimleri": 3,
            "Görsel Sanatlar": 2,
            "Müzik": 2,
            "Beden Eğitimi ve Oyun": 2,
            "Yabancı Dil": 2,
            "Serbest Etkinlikler": 3,
        },
        4: {
            "Türkçe": 7,
            "Matematik": 5,
            "Fen Bilimleri": 3,
            "Sosyal Bilgiler": 3,
            "Görsel Sanatlar": 2,
            "Müzik": 2,
            "Beden Eğitimi ve Spor": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 2,
            "Trafik Güvenliği": 1,
            "İnsan Hakları, Vatandaşlık ve Demokrasi": 1,
        },
        # Middle School (Grades 5-8) - Ortaokul (Resimdeki çizelgeye göre)
        5: {
            "Türkçe": 6,
            "Matematik": 5,
            "Fen Bilimleri": 4,
            "Sosyal Bilgiler": 3,
            "Yabancı Dil": 3,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Görsel Sanatlar": 1,
            "Müzik": 1,
            "Beden Eğitimi ve Spor": 2,
            "Bilişim Teknolojileri ve Yazılım": 2,
            "Rehberlik ve Yönlendirme": 1,
        },
        6: {
            "Türkçe": 6,
            "Matematik": 5,
            "Fen Bilimleri": 4,
            "Sosyal Bilgiler": 3,
            "Yabancı Dil": 3,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Görsel Sanatlar": 1,
            "Müzik": 1,
            "Beden Eğitimi ve Spor": 2,
            "Bilişim Teknolojileri ve Yazılım": 2,
            "Rehberlik ve Yönlendirme": 1,
        },
        7: {
            "Türkçe": 5,
            "Matematik": 5,
            "Fen Bilimleri": 4,
            "Sosyal Bilgiler": 3,
            "Yabancı Dil": 4,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Görsel Sanatlar": 1,
            "Müzik": 1,
            "Beden Eğitimi ve Spor": 2,
            "Teknoloji ve Tasarım": 2,
            "Rehberlik ve Yönlendirme": 1,
        },
        8: {
            "Türkçe": 5,
            "Matematik": 5,
            "Fen Bilimleri": 4,
            "Sosyal Bilgiler": 3,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Yabancı Dil": 4,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Görsel Sanatlar": 1,
            "Müzik": 1,
            "Beden Eğitimi ve Spor": 2,
            "Teknoloji ve Tasarım": 2,
            "Rehberlik ve Yönlendirme": 1,
        },
        # High School (Grades 9-12) - Lise (2025-2026 güncel)
        # Genel Lise / Anadolu Lisesi
        9: {
            "Türk Dili ve Edebiyatı": 4,
            "Matematik": 4,
            "Fizik": 2,
            "Kimya": 2,
            "Biyoloji": 2,
            "Tarih": 2,
            "Coğrafya": 2,
            "Felsefe": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Görsel Sanatlar": 2,
            "Müzik": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 1,
            "Bilgisayar Bilimleri": 2,
            "Seçmeli Ders": 5,
        },
        10: {
            "Türk Dili ve Edebiyatı": 4,
            "Matematik": 4,
            "Fizik": 2,
            "Kimya": 2,
            "Biyoloji": 2,
            "Tarih": 2,
            "Coğrafya": 2,
            "Felsefe": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Dil ve Anlatım": 2,
            "Bilgisayar Bilimleri": 2,
            "Seçmeli Ders": 8,
        },
        11: {
            "Türk Dili ve Edebiyatı": 4,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Seçmeli Ders": 26,  # Alan dersleri ve seçmeli dersler
        },
        12: {
            "Türk Dili ve Edebiyatı": 4,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Seçmeli Ders": 26,  # Alan dersleri ve seçmeli dersler
        },
    }

    # Fen Lisesi için özel ders programı (2025-2026)
    FEN_LISESI_SUBJECTS = {
        9: {
            "Türk Dili ve Edebiyatı": 4,
            "Matematik": 6,
            "Fizik": 3,
            "Kimya": 3,
            "Biyoloji": 3,
            "Tarih": 2,
            "Coğrafya": 2,
            "Felsefe": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Görsel Sanatlar": 2,
            "Müzik": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 1,
            "Bilgisayar Bilimleri": 2,
            "Seçmeli Ders": 0,
        },
        10: {
            "Türk Dili ve Edebiyatı": 4,
            "Matematik": 6,
            "Fizik": 3,
            "Kimya": 3,
            "Biyoloji": 3,
            "Tarih": 2,
            "Coğrafya": 2,
            "Felsefe": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Dil ve Anlatım": 2,
            "Bilgisayar Bilimleri": 2,
            "Seçmeli Ders": 3,
        },
        11: {
            "Türk Dili ve Edebiyatı": 4,
            "Matematik": 6,
            "Fizik": 6,
            "Kimya": 6,
            "Biyoloji": 6,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Seçmeli Ders": 2,
        },
        12: {
            "Türk Dili ve Edebiyatı": 4,
            "Matematik": 6,
            "Fizik": 6,
            "Kimya": 6,
            "Biyoloji": 6,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Seçmeli Ders": 2,
        },
    }

    # Sosyal Bilimler Lisesi için özel ders programı (2025-2026)
    SOSYAL_BILIMLER_LISESI_SUBJECTS = {
        9: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 4,
            "Fizik": 2,
            "Kimya": 2,
            "Biyoloji": 2,
            "Tarih": 3,
            "Coğrafya": 3,
            "Felsefe": 3,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Görsel Sanatlar": 2,
            "Müzik": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 1,
            "Bilgisayar Bilimleri": 2,
            "Seçmeli Ders": 1,
        },
        10: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 4,
            "Fizik": 2,
            "Kimya": 2,
            "Biyoloji": 2,
            "Tarih": 3,
            "Coğrafya": 3,
            "Felsefe": 3,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Dil ve Anlatım": 2,
            "Bilgisayar Bilimleri": 2,
            "Seçmeli Ders": 4,
        },
        11: {
            "Türk Dili ve Edebiyatı": 6,
            "Tarih": 6,
            "Coğrafya": 6,
            "Felsefe": 4,
            "Sosyoloji": 4,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Seçmeli Ders": 4,
        },
        12: {
            "Türk Dili ve Edebiyatı": 6,
            "Tarih": 6,
            "Coğrafya": 6,
            "Felsefe": 4,
            "Sosyoloji": 4,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Seçmeli Ders": 4,
        },
    }

    # Subjects that exist only in specific grade ranges
    SUBJECT_GRADE_RESTRICTIONS = {
        "Hayat Bilgisi": (1, 3),  # Only grades 1-3
        "Sosyal Bilgiler": (4, 8),  # Grades 4-8 (including grade 8, but with different hours)
        "Yabancı Dil": (2, 8),  # Starts from grade 2
        "Trafik Güvenliği": (4, 4),  # Only grade 4
        "İnsan Hakları, Vatandaşlık ve Demokrasi": (4, 4),  # Only grade 4
        "Teknoloji ve Tasarım": (7, 8),  # Grades 7-8
        "Serbest Etkinlikler": (1, 4),  # Only grades 1-4
        "Beden Eğitimi ve Oyun": (1, 4),  # Only grades 1-4
        "Beden Eğitimi ve Spor": (5, 12),  # Grades 5-12
        "Sağlık Bilgisi ve Trafik Kültürü": (9, 9),  # Only grade 9 in Fen Lisesi
        "Felsefe": (10, 10),  # Only grade 10 in Fen Lisesi
        "Birinci Yabancı Dil": (9, 12),  # Grades 9-12 in Fen Lisesi
        "Türk Dili ve Edebiyatı": (9, 12),  # Grades 9-12 in Fen Lisesi
        "Görsel Sanatlar": (1, 10),  # Grades 1-10 (including Fen Lisesi grades 9-10)
        "Müzik": (1, 10),  # Grades 1-10 (including Fen Lisesi grades 9-10)
        "Fizik": (3, 12),  # Grades 3-12 (different hours for different levels)
        "Kimya": (3, 12),  # Grades 3-12 (different hours for different levels)
        "Biyoloji": (3, 12),  # Grades 3-12 (different hours for different levels)
        "Tarih": (3, 11),  # Grades 3-11 (different hours for different levels)
        "Coğrafya": (4, 10),  # Grades 4-10 (different hours for different levels)
        "Din Kültürü ve Ahlak Bilgisi": (4, 12),  # Grades 4-12 (including Fen Lisesi)
        "Rehberlik ve Yönlendirme": (1, 12),  # Grades 1-12
    }

    # Special handling for subjects that exist in multiple grade ranges
    SPECIAL_SUBJECT_RANGES = {
        "Bilişim Teknolojileri ve Yazılım": [(5, 6), (9, 10)],  # Grades 5-6 and 9-10
        "T.C. İnkılap Tarihi ve Atatürkçülük": [
            (8, 8),
            (12, 12),
        ],  # Grade 8 in middle school, grade 12 in high school
    }

    # Optional subject hour limits by grade for Fen Lisesi
    OPTIONAL_SUBJECT_HOURS = {
        9: 5,  # 5 hours for optional subjects
        10: 4,  # 4 hours for optional subjects
        11: 4,  # 4 hours for optional subjects
        12: 8,  # 8 hours for optional subjects
    }

    @classmethod
    def get_mandatory_subjects_for_grade(cls, grade, school_type="lise"):
        """Get mandatory subjects for a specific grade and school type"""
        if school_type.lower() == "fen lisesi" and 9 <= grade <= 12:
            return cls.FEN_LISESI_SUBJECTS.get(grade, {})
        return cls.MANDATORY_SUBJECTS.get(grade, {})

    @classmethod
    def get_total_hours_for_grade(cls, grade, school_type="lise"):
        """Get total weekly hours for a specific grade and school type"""
        if 1 <= grade <= 4:
            return cls.TOTAL_HOURS["ilkokul"]
        elif 5 <= grade <= 8:
            return cls.TOTAL_HOURS["ortaokul"]
        elif 9 <= grade <= 12:
            if school_type.lower() == "fen lisesi":
                return cls.TOTAL_HOURS["fen_lisesi"]
            elif school_type.lower() == "anadolu lisesi":
                return cls.TOTAL_HOURS["anadolu_lisesi"]
            elif school_type.lower() == "sosyal bilimler lisesi":
                return cls.TOTAL_HOURS["sosyal_bilimler_lisesi"]
            else:
                return cls.TOTAL_HOURS["lise"]
        return 0

    @classmethod
    def is_subject_available_for_grade(cls, subject, grade):
        """Check if a subject is available for a specific grade"""
        # Special handling for subjects that change names
        if subject == "Beden Eğitimi ve Oyun" and 1 <= grade <= 4:
            return True
        elif subject == "Beden Eğitimi ve Spor" and 5 <= grade <= 12:
            return True
        # Special handling for subjects with multiple ranges
        elif subject in cls.SPECIAL_SUBJECT_RANGES:
            ranges = cls.SPECIAL_SUBJECT_RANGES[subject]
            for min_grade, max_grade in ranges:
                if min_grade <= grade <= max_grade:
                    return True
            return False
        elif subject in cls.SUBJECT_GRADE_RESTRICTIONS:
            min_grade, max_grade = cls.SUBJECT_GRADE_RESTRICTIONS[subject]
            return min_grade <= grade <= max_grade
        # For subjects without restrictions, check if they appear in the mandatory subjects for this grade
        elif grade in cls.MANDATORY_SUBJECTS:
            return subject in cls.MANDATORY_SUBJECTS[grade]
        return False  # Default to not available

    @classmethod
    def get_available_optional_subjects_for_grade(cls, grade):
        """Get optional subjects that can be selected for a specific grade"""
        available_subjects = {}
        for subject, hours in cls.OPTIONAL_SUBJECTS.items():
            # Check if this optional subject is available for this grade
            if cls.is_subject_available_for_grade(subject, grade):
                available_subjects[subject] = hours
        return available_subjects

    @classmethod
    def get_optional_hours_limit_for_grade(cls, grade):
        """Get the maximum optional hours allowed for a specific grade"""
        if 9 <= grade <= 12:
            return cls.OPTIONAL_SUBJECT_HOURS.get(grade, 0)
        return 0  # No optional hours for elementary and middle school in current implementation

    @classmethod
    def validate_schedule(
        cls, grade, mandatory_subjects, optional_subjects=None, free_activities_hours=0
    ):
        """Validate if a schedule meets the requirements"""
        if optional_subjects is None:
            optional_subjects = {}

        # Check if all mandatory subjects are included
        required_subjects = cls.get_mandatory_subjects_for_grade(grade)
        for subject, required_hours in required_subjects.items():
            if subject not in mandatory_subjects:
                return False, f"Mandatory subject '{subject}' is missing"
            if mandatory_subjects[subject] != required_hours:
                return (
                    False,
                    f"Mandatory subject '{subject}' should have {required_hours} hours, but has {mandatory_subjects[subject]}",
                )

        # Calculate total hours
        total_mandatory_hours = sum(mandatory_subjects.values())
        total_optional_hours = sum(optional_subjects.values())
        total_free_activities_hours = free_activities_hours if 1 <= grade <= 4 else 0
        total_hours = total_mandatory_hours + total_optional_hours + total_free_activities_hours

        # Check if total hours exceed the limit
        max_hours = cls.get_total_hours_for_grade(grade)
        if total_hours > max_hours:
            return (
                False,
                f"Total hours ({total_hours}) exceed the limit ({max_hours}) for grade {grade}",
            )

        # For Fen Lisesi, check optional subject hour limits
        if 9 <= grade <= 12:
            max_optional_hours = cls.get_optional_hours_limit_for_grade(grade)
            if total_optional_hours > max_optional_hours:
                return (
                    False,
                    f"Optional subject hours ({total_optional_hours}) exceed the limit ({max_optional_hours}) for grade {grade}",
                )

        return True, f"Schedule is valid. Total hours: {total_hours}/{max_hours}"
