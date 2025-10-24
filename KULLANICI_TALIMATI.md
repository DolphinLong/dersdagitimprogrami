# ⚠️ SORUN TESPİT EDİLDİ!

## 🔍 Asıl Sorun

**DERS ATAMALARI YAPILMAMIŞ!**

Algoritmalar çalışıyor ama veritabanında **ders atamaları yok**. 
Bu yüzden program oluşturulamıyor.

## ✅ ÇÖZÜM - Adım Adım

### 1️⃣ Uygulamayı Aç

### 2️⃣ "Ders Atama" Menüsüne Git
Ana menüden **"Ders Atama"** kartına tıklayın.

### 3️⃣ Dersleri Öğretmenlere Atayın

Her sınıf için her dersi uygun öğretmene atayın:

**Örnek:**
- 5A - Matematik → Ayşe (5 saat/hafta)
- 5A - Türkçe → Veli (6 saat/hafta)
- 5A - Fen Bilimleri → Yeliz (4 saat/hafta)
- ...

### 4️⃣ "Hızlı Ders Atama" Kullan (Önerilen)

Eğer UI'da varsa **"Hızlı Ders Atama"** veya **"Otomatik Atama"** butonunu kullanın.
Bu tüm dersleri otomatik olarak uygun öğretmenlere atar.

### 5️⃣ Program Oluştur

Ders atamaları tamamlandıktan sonra:
- Ana menüden **"Ders Programı"** kartına gidin
- **"PROGRAMI OLUŞTUR"** butonuna tıklayın
- Bekleyin...
- ✅ Düzgün program hazır!

---

## 📋 Kontrol Listesi

Ders atamalarını kontrol etmek için:

```bash
python check_assignments.py
```

Eğer çıktıda **"📝 DB Manager - Atamalar: 112"** gibi bir sayı görüyorsanız ✅
Eğer **"📝 DB Manager - Atamalar: 0"** görüyorsanız ❌ (Atama yapın!)

---

## 🎯 Beklenen Sonuç

Ders atamaları yapıldıktan sonra:
- ✅ Program otomatik oluşturulur
- ✅ Dersler düzgün dağıtılır
- ✅ Blok kuralları korunur
- ✅ 2 saatlik dersler ardışık olur
- ✅ Kapsama %96-98 olur

---

## ❓ Sık Sorulan Sorular

**S: Neden otomatik atama yapmıyor?**
C: Ders atamaları kullanıcı tarafından yapılmalı. Bu eğitim kurumuna özgü bir karar.

**S: Her sınıf için tek tek atama yapmak gerekiyor mu?**
C: Eğer UI'da "Hızlı Atama" yoksa evet. Ama bir kere yapıldıktan sonra kaydedilir.

**S: Ders atamaları kaydedilmedi mi?**
C: Veritabanında farklı okul türü (Anadolu Lisesi) için kayıtlar var.
   Mevcut okul türü (Ortaokul) için atama gerekiyor.

---

## 🚨 Acil Durum - Manuel Atama Script'i

Eğer UI'dan atama çok zaman alıyorsa, manuel script çalıştırabilirsiniz:

**NOT:** Bu geliştiriciler için. Kullanıcılar UI'ı kullanmalı.

```bash
# Geliştirici için - Veritabanına direkt atama
python scripts/create_default_assignments.py
```

---

**Sonuç:** Ders atamaları yapıldıktan sonra her şey düzgün çalışacak! ✅
