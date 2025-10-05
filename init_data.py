"""
Initialize sample data for the Class Scheduling Program
"""

from database import db_manager

def init_sample_data():
    """Veri tabanına örnek veri ekler"""
    
    # Örnek kullanıcılar ekle
    print("Örnek kullanıcılar ekleniyor...")
    try:
        db_manager.add_user("1", "1", "admin")
    except:
        print("Admin kullanıcısı zaten mevcut")
    
    try:
        db_manager.add_user("ogretmen1", "sifre123", "teacher")
    except:
        print("Öğretmen kullanıcısı zaten mevcut")
    
    try:
        db_manager.add_user("ogrenci1", "sifre123", "student")
    except:
        print("Öğrenci kullanıcısı zaten mevcut")
    
    # Örnek öğretmenler ekle
    print("Örnek öğretmenler ekleniyor...")
    # Önce okul türünü ayarlayalım
    db_manager.set_school_type("Ortaokul")
    
    db_manager.add_teacher("Ali", "Türkçe")
    db_manager.add_teacher("Veli", "Türkçe")
    db_manager.add_teacher("Ayşe", "Matematik")
    db_manager.add_teacher("Yunus", "Matematik")
    db_manager.add_teacher("Yeliz", "Fen Bilimleri")
    db_manager.add_teacher("Tarık", "Fen Bilimleri")
    db_manager.add_teacher("Leyla", "Sosyal Bilgiler")
    db_manager.add_teacher("Zeynep", "Görsel Sanatlar")
    db_manager.add_teacher("Aslı", "Müzik")
    db_manager.add_teacher("Esen", "Beden Eğitimi")
    db_manager.add_teacher("Osman", "Yabancı Dil")
    db_manager.add_teacher("Mehmet", "Din Kültürü ve Ahlak Bilgisi")
    db_manager.add_teacher("Büşra", "Bilişim")
    db_manager.add_teacher("Cem", "Bilişim")  # Additional Bilişim teacher
    db_manager.add_teacher("Derya", "Bilişim")  # Additional Bilişim teacher
    db_manager.add_teacher("Faruk", "Seçmeli 1")  # Teacher for Seçmeli 1
    db_manager.add_teacher("Gamze", "Seçmeli 2")  # Teacher for Seçmeli 2
    db_manager.add_teacher("Hasan", "Seçmeli 3")  # Teacher for Seçmeli 3
    db_manager.add_teacher("Erkan", "Rehberlik")  # Teacher for Rehberlik
    
    # Örnek sınıflar ekle
    print("Örnek sınıflar ekleniyor...")
    db_manager.add_class("5A", 5)
    db_manager.add_class("5B", 5)
    db_manager.add_class("5C", 5)
    db_manager.add_class("5D", 5)
    db_manager.add_class("6A", 6)
    db_manager.add_class("6B", 6)
    db_manager.add_class("6C", 6)
    db_manager.add_class("6D", 6)
    
    # Örnek derslikler ekle
    print("Örnek derslikler ekleniyor...")
    db_manager.add_classroom("Classroom 1", 30)
    db_manager.add_classroom("Classroom 2", 25)
    db_manager.add_classroom("Science Lab", 20)
    db_manager.add_classroom("Computer Lab", 15)
    db_manager.add_classroom("Library", 25)
    
    # Örnek dersler ekle (35 hours total per class)
    print("Örnek dersler ekleniyor...")
    db_manager.add_lesson("Türkçe", 6)              # 6 hours
    db_manager.add_lesson("Matematik", 5)           # 5 hours
    db_manager.add_lesson("Fen Bilimleri", 4)       # 4 hours
    db_manager.add_lesson("Sosyal Bilgiler", 3)     # 3 hours
    db_manager.add_lesson("Yabancı Dil", 3)         # 3 hours
    db_manager.add_lesson("Bilişim", 2)             # 2 hours
    db_manager.add_lesson("Beden Eğitimi", 2)       # 2 hours
    db_manager.add_lesson("Din Kültürü ve Ahlak Bilgisi", 2)  # 2 hours
    db_manager.add_lesson("Müzik", 1)               # 1 hour
    db_manager.add_lesson("Görsel Sanatlar", 1)     # 1 hour
    db_manager.add_lesson("Rehberlik", 1)           # 1 hour
    db_manager.add_lesson("Seçmeli 1", 2)           # 2 hours
    db_manager.add_lesson("Seçmeli 2", 2)           # 2 hours
    db_manager.add_lesson("Seçmeli 3", 1)           # 1 hour
    # Total: 35 hours
    
    print("Örnek veri başlatma tamamlandı!")

if __name__ == "__main__":
    init_sample_data()
    db_manager.close()