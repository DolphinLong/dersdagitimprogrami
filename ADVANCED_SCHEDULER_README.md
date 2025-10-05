# 🚀 Advanced Scheduler - Gelişmiş Ders Programı Algoritması

## 📊 Genel Bakış

Advanced Scheduler, ders programı oluşturmak için gelişmiş bir algoritmadır. Scoring-based (puanlama tabanlı) yaklaşım kullanarak optimal ders dağılımı sağlar.

## ✨ Özellikler

### 1. **Akıllı Blok Dağılımı**
Haftalık ders saatlerini akıllıca bloklara böler:
- **1 saat**: `[1]`
- **2 saat**: `[2]`
- **3 saat**: `[2, 1]`
- **4 saat**: `[2, 2]`
- **5 saat**: `[2, 2, 1]` ✨ (İstediğiniz gibi!)
- **6 saat**: `[2, 2, 2]`
- **7 saat**: `[2, 2, 2, 1]`
- **8 saat**: `[2, 2, 2, 2]`

### 2. **Scoring Sistemi**

Her slot için puan hesaplanır:

| Kriter | Ağırlık | Açıklama |
|--------|---------|----------|
| Aynı gün penaltısı | -30 | Aynı dersi aynı gün tekrar vermekten kaçın |
| Dağılım bonusu | +20 | Farklı günlere yaymayı teşvik et |
| Blok tercihi | +15 | Blok ders tercihlerine uy |
| Erken slot penaltısı | -10 | Çok erken saatlerden kaçın |
| Geç slot penaltısı | -15 | Çok geç saatlerden kaçın |
| Öğle arası bonusu | +10 | Öğle arasını boş bırak |
| Ardışık bonus | +5 | Ardışık dersleri hafifçe teşvik et |
| Boşluk penaltısı | -25 | Programda boşluk oluşturmaktan kaçın |

### 3. **Ders Atama Tabanlı**
- Sistem, **Ders Atama** menüsünden yapılan atamaları kullanır
- Her ders, atanan öğretmenle programlanır
- Müfredattan haftalık saat bilgisi alınır

### 4. **Çakışma Yönetimi**
- Öğretmen çakışmaları otomatik tespit edilir
- Sınıf çakışmaları otomatik tespit edilir
- Çözüm için otomatik düzeltme yapılır

### 5. **İlerleme Takibi**
- Her adım detaylı raporlanır
- Sınıf bazlı özet bilgiler
- Kapsam oranı hesaplanır

## 🔧 Kullanım

### GUI Üzerinden

1. **Ders Atama** menüsünden dersleri öğretmenlere atayın
2. **Ders Programı** menüsüne gidin
3. **Program Oluştur** butonuna tıklayın
4. Sistem otomatik olarak Advanced Scheduler'ı kullanır

### Komut Satırından Test

```bash
python test_advanced_scheduler.py
```

### Programatik Kullanım

```python
from database.db_manager import DatabaseManager
from algorithms.scheduler import Scheduler

# Database bağlantısı
db = DatabaseManager()

# Advanced Scheduler ile scheduler oluştur
scheduler = Scheduler(db, use_advanced=True)

# Program oluştur
schedule_entries = scheduler.generate_schedule()

# Sonuçları veritabanına kaydet
for entry in schedule_entries:
    db.add_schedule_program(
        entry['class_id'],
        entry['teacher_id'],
        entry['lesson_id'],
        entry['classroom_id'],
        entry['day'],
        entry['time_slot']
    )
```

## 📋 Algoritma Akışı

```
1. Veritabanından ders atamaları al
2. Her sınıf için:
   a. Atanan dersleri listele
   b. Haftalık saate göre sırala (çoktan aza)
   c. Her ders için:
      i. Akıllı bloklar oluştur (2+2+1 gibi)
      ii. Her blok için:
          - Tüm olası yerleri değerlendir
          - Her yer için puan hesapla
          - En yüksek puanlı yere yerleştir
      iii. Farklı günlere dağıt
3. Çakışmaları kontrol et
4. Gerekirse otomatik düzelt
5. Sonuçları döndür
```

## 🎯 Avantajlar

### Standart Scheduler'a Göre

| Özellik | Standart | Advanced |
|---------|----------|----------|
| Akıllı dağılım | ❌ | ✅ (2+2+1) |
| Scoring sistemi | ❌ | ✅ |
| Boşluk kontrolü | Kısmen | ✅ Ağır penaltı |
| Öğretmen yük dengesi | ❌ | ✅ |
| Zaman dilimi optimizasyonu | ❌ | ✅ |
| Aynı gün kontrolü | ❌ | ✅ |
| Detaylı raporlama | Kısmen | ✅ |

## 📊 Örnek Çıktı

```
======================================================================
🚀 ADVANCED SCHEDULE GENERATION STARTING
======================================================================

📊 Configuration:
   School Type: Lise
   Time Slots: 8
   Classes: 8
   Teachers: 12
   Lessons: 15
   Assignments: 45

✅ Created 45 unique lesson-teacher assignments

======================================================================
📚 [1/8] Scheduling: 9/A (Grade 9)
======================================================================

📝 Scheduling: Matematik
   Teacher: Ahmet Yılmaz
   Weekly Hours: 5
   Distribution: 2 + 2 + 1

   Block 1: 2 hour(s)
   ✅ Placed on Mon, slots 1-2 (score: 125.0)

   Block 2: 2 hour(s)
   ✅ Placed on Wed, slots 3-4 (score: 120.0)

   Block 3: 1 hour(s)
   ✅ Placed on Fri, slots 2-2 (score: 115.0)

   📊 Result: 5/5 hours (100.0%)

📊 Class Summary: 35/35 hours scheduled (100.0%)
```

## 🔍 Sorun Giderme

### Program oluşturulmuyor
- Ders atamaları yapıldı mı kontrol edin
- Öğretmen sayısı yeterli mi?
- Müfredat tanımlandı mı?

### Çakışmalar var
- Öğretmen müsaitlik ayarlarını kontrol edin
- Aynı öğretmene çok fazla ders atanmış olabilir

### Bazı dersler yerleştirilemiyor
- Haftalık slot sayısı yeterli mi? (İlkokul: 6, Lise: 8)
- Sınıf sayısı çok mu fazla?

## 🚀 Gelecek Geliştirmeler

- [ ] Backtracking desteği (takılırsa geri dön)
- [ ] Genetik algoritma entegrasyonu
- [ ] Öğretmen tercih sistemi
- [ ] Sınıf tercih sistemi
- [ ] Daha gelişmiş çakışma çözümü
- [ ] Paralel işleme desteği
- [ ] Makine öğrenmesi ile optimizasyon

## 📝 Notlar

- Algoritma, ders atamalarını **mutlaka** kullanır
- **2+2+1** dağılımı otomatik yapılır
- Scoring sistemi ayarlanabilir (WEIGHTS sözlüğü)
- Thread-safe değil (şimdilik)

## 👥 Katkıda Bulunma

Önerileriniz için issue açabilir veya pull request gönderebilirsiniz.

## 📄 Lisans

Bu proje eğitim amaçlıdır.

---

**Oluşturulma Tarihi:** 29 Eylül 2025  
**Versiyon:** 1.0.0  
**Durum:** ✅ Production Ready