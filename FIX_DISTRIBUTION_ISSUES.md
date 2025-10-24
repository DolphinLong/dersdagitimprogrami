# 🔧 Ders Dağıtım Sorunları ve Çözümler

## 📊 Mevcut Durum

**Kapsama Oranı:** %98.2 (275/280 saat)
**Eksik:** 5 saat

### Sınıf Bazında Eksikler:
- 8A: 33/35 (2 saat eksik)
- 8B: 33/35 (2 saat eksik) 
- 7A: 34/35 (1 saat eksik)

---

## 🎯 Sorunun Nedenleri

### 1. **Öğretmen Uygunluk Kısıtı**
Algoritmalar öğretmen uygunluğunu zorunlu kontrol ediyor. Eğer öğretmen bir slotta müsait değilse ders yerleştirilmiyor.

### 2. **Blok Kuralları Çakışması**
- 2 saatlik dersler MUTLAKA ardışık olmalı
- Her blok farklı güne yerleşmeli
- Bu kurallar bazı durumlarda slot bulmasını zorlaştırıyor

### 3. **Son Dersler İçin Yer Kalmaması**
İlk yerleştirilen dersler en iyi slotları alıyor, son derslere uygun slot kalmıyor.

---

## ✅ Çözümler

### **Çözüm 1: Öğretmen Uygunluğunu Genişlet**

Tüm öğretmenlerin tüm günleri uygun yapın:

```sql
-- Tüm öğretmenler için tüm günleri uygun yap
DELETE FROM teacher_availability;
INSERT INTO teacher_availability (teacher_id, day, time_slot, is_available)
SELECT t.teacher_id, d.day, s.time_slot, 1
FROM teachers t
CROSS JOIN (SELECT 0 AS day UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) d
CROSS JOIN (SELECT 0 AS time_slot UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) s;
```

### **Çözüm 2: Esnek Yerleştirme Modu Ekle**

Algoritmaya "relaxed mode" parametresi ekle:

```python
# algorithms/simple_perfect_scheduler.py içinde

def __init__(self, db_manager, heuristics=None, relaxed_mode=False):
    self.db_manager = db_manager
    self.schedule_entries = []
    self.teacher_slots = defaultdict(set)
    self.class_slots = defaultdict(set)
    self.logger = logging.getLogger(__name__)
    self.heuristics = heuristics
    self.relaxed_mode = relaxed_mode  # ✨ YENİ

def _can_place_all(self, class_id, teacher_id, day, slots, lesson_id):
    """Tüm slotlar uygun mu?"""
    for slot in slots:
        # Sınıf çakışması
        if (day, slot) in self.class_slots[class_id]:
            return False

        # Öğretmen çakışması
        if (day, slot) in self.teacher_slots[teacher_id]:
            return False

        # Öğretmen uygunluğu kontrolü - GEVŞEK MOD
        if not self.relaxed_mode:  # ✨ Sadece relaxed mode değilse kontrol et
            try:
                if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                    return False
            except Exception:
                pass
    return True
```

### **Çözüm 3: Gap Filling Geliştir**

Algoritmanın sonunda eksik saatleri agresif şekilde yerleştir:

```python
def _ultra_aggressive_gap_filling(self):
    """
    Son çare: Kalan tüm eksiklikleri yerleştir
    """
    print("\n🔥 ULTRA AGRESİF BOŞLUK DOLDURMA")
    
    classes = self.db_manager.get_all_classes()
    lessons = self.db_manager.get_all_lessons()
    assignments = self.db_manager.get_schedule_by_school_type()
    
    assignment_map = {(a.class_id, a.lesson_id): a.teacher_id for a in assignments}
    
    for class_obj in classes:
        for lesson in lessons:
            key = (class_obj.class_id, lesson.lesson_id)
            if key in assignment_map:
                # Haftalık gereksinim
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                    lesson.lesson_id, class_obj.grade
                )
                
                # Mevcut yerleşme
                current_count = sum(
                    1 for entry in self.schedule_entries 
                    if entry["class_id"] == class_obj.class_id 
                    and entry["lesson_id"] == lesson.lesson_id
                )
                
                # Eksik varsa
                if current_count < weekly_hours:
                    remaining = weekly_hours - current_count
                    teacher_id = assignment_map[key]
                    
                    print(f"   📌 {class_obj.name} - {lesson.name}: {remaining} saat eksik")
                    
                    # Her gün, her slotu dene
                    for day in range(5):
                        for slot in range(7):
                            if remaining <= 0:
                                break
                                
                            # SADECE çakışma kontrolü (availability kontrolü yok)
                            if (day, slot) not in self.class_slots[class_obj.class_id] and \
                               (day, slot) not in self.teacher_slots[teacher_id]:
                                # Yerleştir
                                self._add_entry(
                                    class_obj.class_id,
                                    teacher_id,
                                    lesson.lesson_id,
                                    1,  # classroom_id
                                    day,
                                    slot
                                )
                                remaining -= 1
                                print(f"      ✅ Yerleştirildi: Gün {day+1}, Slot {slot+1}")
```

### **Çözüm 4: Algoritma Seçeneği Değiştir**

UI'da kullanıcıya algoritma seçimi sun:

```python
# ui/schedule_widget.py içinde

def generate_schedule(self):
    """Program oluştur"""
    
    # Kullanıcıya sor
    options = QMessageBox()
    options.setWindowTitle("Algoritma Seçimi")
    options.setText("Hangi modu kullanmak istersiniz?")
    
    strict_btn = options.addButton("Katı Mod (Öğretmen uygunluğu kontrol edilir)", QMessageBox.YesRole)
    relaxed_btn = options.addButton("Esnek Mod (%100 doluluk hedeflenir)", QMessageBox.NoRole)
    cancel_btn = options.addButton("İptal", QMessageBox.RejectRole)
    
    options.exec_()
    
    if options.clickedButton() == relaxed_btn:
        # Esnek mod - Öğretmen uygunluğu kontrolü gevşetilir
        scheduler = SimplePerfectScheduler(self.db_manager, relaxed_mode=True)
    elif options.clickedButton() == strict_btn:
        # Normal mod
        scheduler = Scheduler(self.db_manager)
    else:
        return  # İptal
    
    # Program oluştur
    schedule_entries = scheduler.generate_schedule()
    # ...
```

---

## 🚀 Hızlı Çözüm

### Manuel Fix Script

Eksik saatleri manuel olarak yerleştiren script:

```python
#!/usr/bin/env python3
# fix_missing_hours.py

from database import db_manager

def fix_missing_hours():
    """Eksik saatleri otomatik yerleştir"""
    
    print("🔧 Eksik saatler düzeltiliyor...")
    
    # 8A için 2 saat eksik
    # 8B için 2 saat eksik
    # 7A için 1 saat eksik
    
    # Hangi derslerin eksik olduğunu bul
    classes = db_manager.get_all_classes()
    schedule_program = db_manager.get_schedule_program_by_school_type()
    
    for class_obj in classes:
        if class_obj.name in ["8A", "8B", "7A"]:
            print(f"\n{class_obj.name} için eksikler:")
            
            # Bu sınıfın tüm derslerini kontrol et
            assignments = [a for a in db_manager.get_schedule_by_school_type() 
                          if a.class_id == class_obj.class_id]
            
            for assignment in assignments:
                lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
                weekly_hours = db_manager.get_weekly_hours_for_lesson(
                    assignment.lesson_id, class_obj.grade
                )
                
                # Mevcut yerleşme sayısı
                current_count = sum(
                    1 for entry in schedule_program
                    if entry.class_id == class_obj.class_id 
                    and entry.lesson_id == assignment.lesson_id
                )
                
                if current_count < weekly_hours:
                    print(f"   • {lesson.name}: {current_count}/{weekly_hours}")
                    
                    # Boş slot bul ve yerleştir
                    for day in range(5):
                        for slot in range(7):
                            # Bu slot sınıf için boş mu?
                            slot_used = any(
                                e.class_id == class_obj.class_id and 
                                e.day == day and 
                                e.time_slot == slot
                                for e in schedule_program
                            )
                            
                            if not slot_used:
                                # Yerleştir
                                db_manager.add_schedule_program(
                                    class_obj.class_id,
                                    assignment.teacher_id,
                                    assignment.lesson_id,
                                    1,  # classroom_id
                                    day,
                                    slot
                                )
                                print(f"      ✅ Yerleştirildi: Gün {day+1}, Slot {slot+1}")
                                current_count += 1
                                
                            if current_count >= weekly_hours:
                                break
                        if current_count >= weekly_hours:
                            break

if __name__ == "__main__":
    fix_missing_hours()
    print("\n✅ Tamamlandı!")
```

---

## 📈 Öncelik Sırası

1. **Önce dene:** Öğretmen uygunluklarını kontrol et ve gerekirse güncelle
2. **Sonra:** Ultra aggressive gap filling ekle
3. **En son:** Esnek mod parametresi ekle

---

## ✅ Test Et

```bash
# 1. Mevcut durumu analiz et
python test_schedule_problem.py

# 2. Fix script çalıştır
python fix_missing_hours.py

# 3. Tekrar analiz et
python test_schedule_problem.py
```
