# -*- coding: utf-8 -*-
"""
Yeni Müzik Öğretmeni Ekleme ve Ders Dağıtımı
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


def add_music_teacher_and_redistribute():
    """Yeni Müzik öğretmeni ekle ve dersleri yeniden dağıt"""
    
    print("\n" + "="*80)
    print("🎵 YENİ MÜZİK ÖĞRETMENİ EKLEME VE DAĞITIM")
    print("="*80)
    
    # 1. Yeni öğretmen ekle
    print("\n📝 1. Adım: Yeni öğretmen ekleniyor...")
    teacher_name = "Sevil"
    subject = "Müzik"
    
    result = db_manager.add_teacher(teacher_name, subject)
    
    if result:
        print(f"   ✅ {teacher_name} ({subject}) başarıyla eklendi!")
        
        # Yeni öğretmenin ID'sini bul
        teachers = db_manager.get_all_teachers()
        new_teacher = None
        for t in teachers:
            if t.name == teacher_name and t.subject == subject:
                new_teacher = t
                break
        
        if not new_teacher:
            print("   ❌ Yeni öğretmen bulunamadı!")
            return
        
        print(f"   📋 Öğretmen ID: {new_teacher.teacher_id}")
        
        # 2. Aslı'nın mevcut Müzik derslerini bul
        print("\n📚 2. Adım: Mevcut Müzik dersleri kontrol ediliyor...")
        
        assignments = db_manager.get_schedule_by_school_type()
        lessons = db_manager.get_all_lessons()
        
        # Müzik dersinin ID'sini bul
        music_lesson = None
        for lesson in lessons:
            if lesson.name == "Müzik":
                music_lesson = lesson
                break
        
        if not music_lesson:
            print("   ❌ Müzik dersi bulunamadı!")
            return
        
        print(f"   📋 Müzik Ders ID: {music_lesson.lesson_id}")
        
        # Aslı'nın öğretmen ID'sini bul
        asli = None
        for t in teachers:
            if t.name == "Aslı" and t.subject == "Müzik":
                asli = t
                break
        
        if not asli:
            print("   ❌ Aslı bulunamadı!")
            return
        
        # Aslı'nın Müzik derslerini bul
        asli_music_classes = []
        for assignment in assignments:
            if assignment.teacher_id == asli.teacher_id and assignment.lesson_id == music_lesson.lesson_id:
                class_obj = db_manager.get_class_by_id(assignment.class_id)
                if class_obj:
                    asli_music_classes.append({
                        'assignment': assignment,
                        'class': class_obj
                    })
        
        print(f"   📊 Aslı'nın {len(asli_music_classes)} sınıfa Müzik dersi var")
        
        # 3. Dersleri yeniden dağıt (yarı yarıya)
        print("\n⚖️  3. Adım: Dersler yeniden dağıtılıyor...")
        
        if len(asli_music_classes) == 0:
            print("   ⚠️  Aslı'nın Müzik dersi ataması bulunamadı!")
            return
        
        # İlk yarısı Aslı'da kalsın, ikinci yarısını Sevil'e aktar
        mid_point = len(asli_music_classes) // 2
        
        transferred_count = 0
        for i, item in enumerate(asli_music_classes):
            if i >= mid_point:
                # Bu sınıfı Sevil'e aktar
                assignment = item['assignment']
                class_obj = item['class']
                
                # Önce eski atamayı sil
                db_manager.delete_schedule_entry(assignment.entry_id)
                
                # Yeni atama yap (Sevil'e)
                if db_manager.add_schedule_entry(
                    assignment.class_id,
                    new_teacher.teacher_id,
                    music_lesson.lesson_id,
                    1,
                    -1,
                    -1
                ):
                    print(f"   ✅ {class_obj.name} sınıfı Sevil'e atandı")
                    transferred_count += 1
                else:
                    print(f"   ❌ {class_obj.name} sınıfı atanamadı!")
        
        print(f"\n✅ Dağıtım tamamlandı!")
        print(f"   • Aslı'da kalan: {mid_point} sınıf")
        print(f"   • Sevil'e aktarılan: {transferred_count} sınıf")
        
    else:
        print(f"   ❌ {teacher_name} eklenemedi!")
    
    print("\n" + "="*80)
    print("✅ İŞLEM TAMAMLANDI")
    print("="*80)
    print("\n💡 Şimdi programı yeniden oluşturun:")
    print("   1. Ana ekrana dönün")
    print("   2. 'Programı Oluştur' butonuna tıklayın")
    print("   3. Yeni doluluk oranını kontrol edin")
    print("\n")


if __name__ == "__main__":
    try:
        add_music_teacher_and_redistribute()
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
