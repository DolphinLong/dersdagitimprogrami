"""
Initialize grade data for Anatolian High School and Social Sciences High School
based on the official curriculum rules.
"""

# Curriculum rules for Anatolian High School
anatolian_high_school_rules = {
    "name": "Anadolu Lisesi",
    "grades": [9, 10, 11, 12],
    "total_weekly_hours": 40,
    "mandatory_courses": {
        9: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Fizik": 2,
            "Kimya": 2,
            "Biyoloji": 2,
            "Tarih": 2,
            "Coğrafya": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Birinci Yabancı Dil": 4,
            "Beden Eğitimi / Görsel Sanatlar / Müzik": 2,
            "Felsefe": 0,  # Starts in 10th grade
            "Sağlık Bilgisi ve Trafik Kültürü": 1,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 0,  # Only in 12th grade
            "Rehberlik ve Yönlendirme": 1
        },
        10: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Fizik": 2,
            "Kimya": 2,
            "Biyoloji": 2,
            "Tarih": 2,
            "Coğrafya": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Birinci Yabancı Dil": 4,
            "Beden Eğitimi / Görsel Sanatlar / Müzik": 2,
            "Felsefe": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 0,  # Only in 9th grade
            "T.C. İnkılap Tarihi ve Atatürkçülük": 0,  # Only in 12th grade
            "Rehberlik ve Yönlendirme": 1
        },
        11: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 0,  # Supported by elective courses
            "Fizik": 0,  # Supported by elective courses
            "Kimya": 0,  # Supported by elective courses
            "Biyoloji": 0,  # Supported by elective courses
            "Tarih": 2,
            "Coğrafya": 0,  # Supported by elective courses
            "Din Kültürü ve Ahlak Bilgisi": 0,  # Supported by elective courses
            "Birinci Yabancı Dil": 4,
            "Beden Eğitimi / Görsel Sanatlar / Müzik": 2,
            "Felsefe": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 0,  # Only in 9th grade
            "T.C. İnkılap Tarihi ve Atatürkçülük": 0,  # Only in 12th grade
            "Rehberlik ve Yönlendirme": 1
        },
        12: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 0,  # Supported by elective courses
            "Fizik": 0,  # Supported by elective courses
            "Kimya": 0,  # Supported by elective courses
            "Biyoloji": 0,  # Supported by elective courses
            "Tarih": 0,  # Supported by elective "Çağdaş Türk ve Dünya Tarihi"
            "Coğrafya": 0,  # Supported by elective courses
            "Din Kültürü ve Ahlak Bilgisi": 0,  # Supported by elective courses
            "Birinci Yabancı Dil": 4,
            "Beden Eğitimi / Görsel Sanatlar / Müzik": 2,
            "Felsefe": 0,  # Ends in 11th grade
            "Sağlık Bilgisi ve Trafik Kültürü": 0,  # Only in 9th grade
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Rehberlik ve Yönlendirme": 1
        }
    },
    "elective_courses": {
        "available_hours": {
            9: 7,
            10: 6,
            11: 20,
            12: 24
        },
        "groups": {
            "Kültür, Sanat ve Spor": [
                "Spor Eğitimi",
                "Sanat Eğitimi"
            ],
            "Din, Ahlak ve Değer": [
                "Peygamberimizin Hayatı",
                "Temel Dini Bilgiler",
                "Kur'an-ı Kerim",
                "İslam Bilim Tarihi",
                "Adabımuaşeret"
            ],
            "İnsan, Toplum ve Bilim": [
                "Astronomi",
                "Düşünme Eğitimi",
                "Fen Bilimleri Uygulamaları",
                "Matematik Uygulamaları",
                "Sosyal Bilim Çalışmaları"
            ],
            "Akademik Çalışmalar": [
                "Seçmeli Matematik",
                "Seçmeli Fizik",
                "Seçmeli Kimya",
                "Seçmeli Biyoloji",
                "Seçmeli Tarih",
                "Seçmeli Edebiyat",
                "Seçmeli Coğrafya"
            ],
            "Dil Alanı": [
                "Osmanlı Türkçesi",
                "Ortak Türk Edebiyatı",
                "İkinci Yabancı Dil"
            ]
        }
    }
}

# Curriculum rules for Social Sciences High School
social_sciences_high_school_rules = {
    "name": "Sosyal Bilimler Lisesi",
    "grades": [9, 10, 11, 12],
    "total_weekly_hours": 40,
    "mandatory_courses": {
        9: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Tarih": 2,
            "Coğrafya": 2,
            "Felsefe": 0,  # Starts in 10th grade
            "Sosyoloji": 0,  # Starts in 11th grade
            "Psikoloji": 0,  # Starts in 11th grade
            "Mantık": 0,  # Starts in 11th grade
            "Çağdaş Türk ve Dünya Tarihi": 0,  # Starts in 12th grade
            "Birinci Yabancı Dil": 4,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Osmanlı Türkçesi": 2,
            "Sanat Tarihi": 0,  # Starts in 12th grade
            "Sosyal Bilim Çalışmaları": 0,  # Starts in 10th grade
            "Beden Eğitimi / Görsel Sanatlar / Müzik": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 1,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 0,  # Only in 12th grade
            "Rehberlik ve Yönlendirme": 1
        },
        10: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Tarih": 2,
            "Coğrafya": 2,
            "Felsefe": 2,
            "Sosyoloji": 0,  # Starts in 11th grade
            "Psikoloji": 0,  # Starts in 11th grade
            "Mantık": 0,  # Starts in 11th grade
            "Çağdaş Türk ve Dünya Tarihi": 0,  # Starts in 12th grade
            "Birinci Yabancı Dil": 4,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Osmanlı Türkçesi": 2,
            "Sanat Tarihi": 0,  # Starts in 12th grade
            "Sosyal Bilim Çalışmaları": 2,
            "Beden Eğitimi / Görsel Sanatlar / Müzik": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 0,  # Only in 9th grade
            "T.C. İnkılap Tarihi ve Atatürkçülük": 0,  # Only in 12th grade
            "Rehberlik ve Yönlendirme": 1
        },
        11: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Tarih": 2,
            "Coğrafya": 4,
            "Felsefe": 2,
            "Sosyoloji": 2,
            "Psikoloji": 2,
            "Mantık": 2,
            "Çağdaş Türk ve Dünya Tarihi": 0,  # Starts in 12th grade
            "Birinci Yabancı Dil": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Osmanlı Türkçesi": 2,
            "Sanat Tarihi": 0,  # Starts in 12th grade
            "Sosyal Bilim Çalışmaları": 2,
            "Beden Eğitimi / Görsel Sanatlar / Müzik": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 0,  # Only in 9th grade
            "T.C. İnkılap Tarihi ve Atatürkçülük": 0,  # Only in 12th grade
            "Rehberlik ve Yönlendirme": 1
        },
        12: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Tarih": 2,
            "Coğrafya": 4,
            "Felsefe": 0,  # Ends in 11th grade
            "Sosyoloji": 2,
            "Psikoloji": 0,  # Ends in 11th grade
            "Mantık": 0,  # Ends in 11th grade
            "Çağdaş Türk ve Dünya Tarihi": 2,
            "Birinci Yabancı Dil": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Osmanlı Türkçesi": 0,  # Ends in 11th grade
            "Sanat Tarihi": 2,
            "Sosyal Bilim Çalışmaları": 2,
            "Beden Eğitimi / Görsel Sanatlar / Müzik": 2,
            "Sağlık Bilgisi ve Trafik Kültürü": 0,  # Only in 9th grade
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Rehberlik ve Yönlendirme": 1
        }
    },
    "elective_courses": {
        "available_hours": {
            9: 7,
            10: 4,
            11: 3,
            12: 8
        },
        "groups": {
            "Din, Ahlak ve Değer": [
                "Kur'an-ı Kerim",
                "Temel Dini Bilgiler",
                "Peygamberimizin Hayatı",
                "İslam Kültür ve Medeniyeti"
            ],
            "Kültür, Sanat ve Spor": [
                "Spor Eğitimi",
                "Sanat Eğitimi"
            ],
            "İnsan, Toplum ve Bilim": [
                "Fen Bilimleri Uygulamaları",
                "Matematik Uygulamaları",
                "Sosyal Bilim Çalışmaları"
            ],
            "Akademik Çalışmalar": [
                "Seçmeli Matematik",
                "Edebiyat Uygulamaları",
                "Proje Tasarımı"
            ],
            "Dil Alanı": [
                "Ortak Türk Edebiyatı",
                "İkinci Yabancı Dil",
                "Türk Dünyası Coğrafyası"
            ]
        }
    }
}

def get_school_rules(school_type):
    """
    Get curriculum rules for a specific school type.
    
    Args:
        school_type (str): Either "anatolian" or "social_sciences"
        
    Returns:
        dict: Curriculum rules for the specified school type
    """
    if school_type.lower() == "anatolian":
        return anatolian_high_school_rules
    elif school_type.lower() == "social_sciences":
        return social_sciences_high_school_rules
    else:
        raise ValueError("Invalid school type. Use 'anatolian' or 'social_sciences'")

if __name__ == "__main__":
    # Example usage
    print("Available school types:")
    print("- Anatolian High School")
    print("- Social Sciences High School")
    print("\nUse get_school_rules('anatolian') or get_school_rules('social_sciences') to access the data.")