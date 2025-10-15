# 📚 Ders Dağıtım Programı - Kullanıcı Kılavuzu

## 🎯 Hoş Geldiniz!

Bu kılavuz, Ders Dağıtım Programı'nı kullanmaya başlamanız için gereken tüm bilgileri içerir.

---

## 📋 İçindekiler

1. [Kurulum](#kurulum)
2. [İlk Başlangıç](#ilk-başlangıç)
3. [Temel Kavramlar](#temel-kavramlar)
4. [Adım Adım Kullanım](#adım-adım-kullanım)
5. [Gelişmiş Özellikler](#gelişmiş-özellikler)
6. [Sorun Giderme](#sorun-giderme)
7. [SSS](#sss)

---

## 🚀 Kurulum

### Sistem Gereksinimleri

- **İşletim Sistemi:** Windows 10/11, macOS 10.14+, Linux
- **Python:** 3.8 veya üzeri
- **RAM:** Minimum 4 GB (8 GB önerilir)
- **Disk Alanı:** 500 MB

### Kurulum Adımları

#### 1. Python Kurulumu

Python'un sisteminizde kurulu olduğundan emin olun:

```bash
python --version
```

Eğer Python kurulu değilse, [python.org](https://www.python.org/downloads/) adresinden indirin.

#### 2. Projeyi İndirin

```bash
git clone https://github.com/DolphinLong/dersdagitimprogrami.git
cd dersdagitimprogrami
```

#### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

#### 4. Programı Başlatın

```bash
python main.py
```

---

## 🎬 İlk Başlangıç

### İlk Açılış

Program ilk kez açıldığında:

1. **Okul Türü Seçimi** ekranı açılır
2. Okulunuzun türünü seçin:
   - İlkokul (6 saat/gün)
   - Ortaokul (7 saat/gün)
   - Lise (8 saat/gün)
   - Anadolu Lisesi (8 saat/gün)
   - Fen Lisesi (8 saat/gün)
   - Sosyal Bilimler Lisesi (8 saat/gün)

3. **Kaydet** butonuna tıklayın

### Ana Ekran

Ana ekranda şu bölümler bulunur:

- **Menü Çubuğu:** Tüm işlevlere erişim
- **Araç Çubuğu:** Hızlı erişim butonları
- **Program Görünümü:** Ders programı tablosu
- **Durum Çubuğu:** İşlem durumu ve bilgiler

---

## 📖 Temel Kavramlar

### Sınıf (Class)

Öğrencilerin bulunduğu grup. Örnek: 9-A, 10-B

### Öğretmen (Teacher)

Ders veren kişi. Her öğretmenin bir branşı vardır.

### Ders (Lesson)

Okutulacak konu. Örnek: Matematik, Fizik, Edebiyat

### Ders Atama (Lesson Assignment)

Bir sınıfa, bir dersin, bir öğretmen tarafından, haftada kaç saat okutulacağının belirlenmesi.

### Öğretmen Uygunluğu (Teacher Availability)

Öğretmenin hangi gün ve saatlerde müsait olduğu bilgisi.

### Ders Programı (Schedule)

Tüm derslerin gün ve saatlere yerleştirilmiş hali.

---

## 📝 Adım Adım Kullanım

### 1. Sınıfları Ekleyin

**Menü:** Yönetim → Sınıf Yönetimi

1. **Yeni Sınıf** butonuna tıklayın
2. Sınıf adını girin (örn: 9-A)
3. Sınıf seviyesini seçin (örn: 9)
4. **Kaydet** butonuna tıklayın

**İpucu:** Toplu ekleme için birden fazla sınıf ekleyebilirsiniz.

### 2. Öğretmenleri Ekleyin

**Menü:** Yönetim → Öğretmen Yönetimi

1. **Yeni Öğretmen** butonuna tıklayın
2. Öğretmen adını girin
3. Branşını seçin
4. **Kaydet** butonuna tıklayın

**Örnek:**
- Ad: Ahmet Yılmaz
- Branş: Matematik

### 3. Dersleri Tanımlayın

**Menü:** Yönetim → Ders Yönetimi

1. **Yeni Ders** butonuna tıklayın
2. Ders adını girin
3. Haftalık saat sayısını belirleyin
4. **Kaydet** butonuna tıklayın

**Not:** Bazı dersler otomatik olarak yüklenmiş olabilir.

### 4. Öğretmen Uygunluğunu Ayarlayın

**Menü:** Yönetim → Öğretmen Uygunluk

1. Öğretmeni seçin
2. Müsait olduğu günleri ve saatleri işaretleyin
3. **Kaydet** butonuna tıklayın

**Önemli:** Öğretmen uygunluğu doğru ayarlanmazsa program oluşturulamayabilir!

### 5. Ders Atamalarını Yapın

**Menü:** Yönetim → Ders Atama

#### Manuel Atama

1. Sınıfı seçin
2. Dersi seçin
3. Öğretmeni seçin
4. Haftalık saat sayısını girin
5. **Ekle** butonuna tıklayın

#### Hızlı Atama (Önerilir)

1. **Hızlı Atama** butonuna tıklayın
2. Sistem otomatik olarak uygun eşleştirmeleri önerir
3. Önerileri gözden geçirin
4. **Onayla** butonuna tıklayın

### 6. Ders Programını Oluşturun

**Ana Ekran → PROGRAMI OLUŞTUR**

1. **PROGRAMI OLUŞTUR** butonuna tıklayın
2. Algoritma otomatik olarak seçilir (Hybrid Optimal)
3. Program oluşturma işlemi başlar
4. İşlem tamamlandığında sonuç gösterilir

**Süre:** Okul büyüklüğüne göre 10-60 saniye

### 7. Programı Görüntüleyin

#### Sınıf Programı

**Menü:** Görüntüle → Sınıf Programı

1. Sınıfı seçin
2. Program otomatik olarak gösterilir

#### Öğretmen Programı

**Menü:** Görüntüle → Öğretmen Programı

1. Öğretmeni seçin
2. Program otomatik olarak gösterilir

### 8. Rapor Oluşturun

**Menü:** Raporlar → Rapor Oluştur

#### Excel Raporu

1. **Excel** sekmesini seçin
2. Rapor türünü seçin (Sınıf/Öğretmen/Tümü)
3. **Oluştur** butonuna tıklayın
4. Dosya konumunu seçin

#### PDF Raporu

1. **PDF** sekmesini seçin
2. Rapor türünü seçin
3. **Oluştur** butonuna tıklayın
4. Dosya konumunu seçin

---

## 🎓 Gelişmiş Özellikler

### Boşluk Doldurma

Eğer programda boş saatler varsa:

1. **BOŞLUKLARI DOLDUR** butonuna tıklayın
2. Sistem otomatik olarak boş saatleri doldurmaya çalışır

### Manuel Düzenleme

Oluşturulan programı manuel olarak düzenleyebilirsiniz:

1. Program tablosunda düzenlemek istediğiniz hücreye çift tıklayın
2. Dersi değiştirin veya silin
3. **Kaydet** butonuna tıklayın

**Uyarı:** Manuel değişiklikler çakışmalara neden olabilir!

### Çakışma Kontrolü

**Menü:** Araçlar → Çakışma Kontrolü

1. Sistem tüm programı tarar
2. Varsa çakışmaları listeler
3. Çakışmaları otomatik çöz seçeneği sunar

### Veritabanı Yedekleme

**Menü:** Araçlar → Yedekle/Geri Yükle

#### Yedekleme

1. **Yedekle** sekmesini seçin
2. Yedek dosya adını girin
3. **Yedekle** butonuna tıklayın

#### Geri Yükleme

1. **Geri Yükle** sekmesini seçin
2. Yedek dosyasını seçin
3. **Geri Yükle** butonuna tıklayın

**Önemli:** Geri yükleme mevcut verileri siler!

---

## 🔧 Sorun Giderme

### Program Oluşturulamıyor

**Olası Nedenler:**

1. **Öğretmen uygunluğu yetersiz**
   - Çözüm: Öğretmenlerin uygunluğunu artırın

2. **Ders atamaları eksik**
   - Çözüm: Tüm sınıflar için ders atamalarını kontrol edin

3. **Haftalık saat sayısı fazla**
   - Çözüm: Toplam ders saatini azaltın veya gün sayısını artırın

### Bazı Dersler Yerleşmiyor

**Çözüm Adımları:**

1. Explanation raporunu kontrol edin (otomatik gösterilir)
2. Öğretmen uygunluğunu artırın
3. Alternatif öğretmen atayın
4. "Boşlukları Doldur" özelliğini kullanın

### Çakışmalar Oluşuyor

**Çözüm:**

1. Menü → Araçlar → Çakışma Kontrolü
2. Çakışmaları görüntüleyin
3. **Otomatik Çöz** butonuna tıklayın
4. Gerekirse manuel düzeltme yapın

### Program Yavaş Çalışıyor

**Optimizasyon İpuçları:**

1. Veritabanı indexlerini oluşturun:
   ```bash
   python database/create_indexes.py --action create
   ```

2. Cache'i temizleyin:
   - Menü → Araçlar → Cache Temizle

3. Eski programları silin:
   - Menü → Araçlar → Veritabanı Temizle

### Veritabanı Hatası

**Çözüm:**

1. Programı kapatın
2. Yedek dosyasından geri yükleyin
3. Eğer yedek yoksa, veritabanını sıfırlayın:
   ```bash
   python migrate_db.py
   ```

---

## ❓ SSS (Sık Sorulan Sorular)

### Kaç sınıf ekleyebilirim?

Sınırsız. Ancak performans için 50'den az sınıf önerilir.

### Programı değiştirebilir miyim?

Evet, manuel düzenleme yapabilirsiniz. Ancak çakışmalara dikkat edin.

### Hafta sonu programı yapılabilir mi?

Hayır, şu anda sadece Pazartesi-Cuma destekleniyor.

### Birden fazla okul yönetebilir miyim?

Evet, her okul için ayrı veritabanı dosyası kullanabilirsiniz:

```bash
python main.py --db okul1.db
python main.py --db okul2.db
```

### Programı nasıl yazdırabilirim?

PDF raporu oluşturun ve yazdırın:
- Menü → Raporlar → PDF Raporu

### Veri kaybı yaşarsam ne yapmalıyım?

Düzenli yedekleme yapın:
- Menü → Araçlar → Yedekle/Geri Yükle

### Hangi algoritma en iyisi?

**Hybrid Optimal** (varsayılan) en iyi sonuçları verir. Ancak:
- Hızlı sonuç için: **Simple Perfect**
- Maksimum kapsama için: **Ultra Aggressive**

### Mobil versiyonu var mı?

Şu anda hayır. Ancak web tabanlı versiyon geliştirilmekte.

---

## 📞 Destek

### Yardım Alma

- **Dokümantasyon:** [README.md](README.md)
- **API Referansı:** [docs/](docs/)
- **GitHub Issues:** [github.com/DolphinLong/dersdagitimprogrami/issues](https://github.com/DolphinLong/dersdagitimprogrami/issues)

### Hata Bildirimi

Hata bulduysanız:

1. GitHub Issues'da yeni bir issue açın
2. Hatanın detaylarını yazın
3. Hata mesajını ekleyin
4. Adımları tekrarlayın

### Özellik İsteği

Yeni özellik önerileriniz için:

1. GitHub Issues'da "Feature Request" açın
2. Özelliği detaylı açıklayın
3. Kullanım senaryosunu belirtin

---

## 🎉 İpuçları ve Püf Noktaları

### ⚡ Hızlı Başlangıç

1. Okul türünü doğru seçin
2. Önce az sayıda sınıf ile test edin
3. Öğretmen uygunluğunu geniş tutun
4. Hızlı Atama özelliğini kullanın

### 🎯 En İyi Sonuçlar İçin

1. **Öğretmen uygunluğunu maksimize edin**
   - Her öğretmen için en az 30 saat müsait olsun

2. **Ders atamalarını dengeleyin**
   - Bir öğretmene çok fazla ders atamayın

3. **Haftalık saatleri kontrol edin**
   - Toplam ders saati, günlük saat × 5'i geçmesin

4. **Düzenli yedekleme yapın**
   - Her program oluşturmadan önce yedekleyin

### 🚀 Performans İyileştirme

1. Veritabanı indexlerini oluşturun
2. Eski programları silin
3. Cache'i düzenli temizleyin
4. Gereksiz ders atamalarını kaldırın

---

## 📚 Ek Kaynaklar

- **Geliştirici Kılavuzu:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Algoritma Dokümantasyonu:** [ALGORITHM_ANALYSIS_REPORT.md](ALGORITHM_ANALYSIS_REPORT.md)
- **Kısa Vadeli İyileştirmeler:** [SHORT_TERM_IMPROVEMENTS.md](SHORT_TERM_IMPROVEMENTS.md)

---

## 📄 Lisans

Bu yazılım MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

**Son Güncelleme:** 2024  
**Versiyon:** 3.4  
**Yazar:** DolphinLong

---

🎓 **Başarılı programlar dileriz!**
