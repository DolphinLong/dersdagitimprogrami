# 📚 Ders Dağıtım Programı

Modern ve akıllı okul ders programı oluşturma sistemi. Yapay zeka destekli algoritmalar ile otomatik ders dağılımı, öğretmen yük dengeleme ve çakışma önleme.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Özellikler

### 🎯 Akıllı Programlama
- **Constraint Satisfaction Algorithm**: Karmaşık kısıtlamaları otomatik çözen akıllı algoritma
- **Otomatik Ders Dağılımı**: Tek tıkla tüm sınıflar için program oluşturma
- **Çakışma Önleme**: Öğretmen ve sınıf çakışmalarını otomatik engelleme
- **3 Ardışık Ders Kontrolü**: Aynı dersin 3 saat üst üste gelmesini önleme

### 📊 Ders Dağılım Stratejileri
- **Blok Ders Yerleştirme**: 2 saatlik dersler için ardışık yerleştirme
- **Akıllı Dağılım Desenleri**: 
  - 6 saat → 2+2+2 (üç farklı gün)
  - 5 saat → 2+2+1 (üç farklı gün)
  - 4 saat → 2+2 (iki farklı gün)
  - 3 saat → 2+1 (iki farklı gün)
- **Boşluk Doldurma**: Programdaki eksik saatleri otomatik tamamlama

### 👨‍🏫 Öğretmen Yönetimi
- **Uygunluk Takvimi**: Öğretmenlerin müsait oldukları günleri belirleme
- **Yük Dengeleme**: Dersleri öğretmenler arasında adil dağıtım
- **Otomatik Atama**: Eksik ders atamalarını akıllıca tamamlama

### 🎨 Modern Arayüz
- **PyQt5 Tabanlı UI**: Modern ve kullanıcı dostu arayüz
- **Görselleştirme**: Renkli ve interaktif program görüntüleme
- **Sürükle-Bırak**: Kolay düzenleme ve değişiklik yapma
- **Gerçek Zamanlı Önizleme**: Anlık sonuçları görme

### 📈 Raporlama
- **Excel Export**: Programları Excel formatında dışa aktarma
- **PDF Export**: Yazdırılabilir PDF raporlar
- **Sınıf Programları**: Her sınıf için ayrı program
- **Öğretmen Programları**: Her öğretmen için ders programı

### 🔧 Yönetim Araçları
- **Sınıf Yönetimi**: Sınıfları ekleme, düzenleme, silme
- **Ders Yönetimi**: MEB müfredatına uygun ders tanımlama
- **Öğretmen Yönetimi**: Öğretmen bilgilerini yönetme
- **Yedekleme/Geri Yükleme**: Veritabanı yedekleme sistemi

## 🚀 Kurulum

### Gereksinimler

```bash
Python 3.8 veya üzeri
```

### Adım 1: Projeyi İndirin

```bash
git clone https://github.com/DolphinLong/dersdagitimprogrami.git
cd dersdagitimprogrami
```

### Adım 2: Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

### Adım 3: Programı Başlatın

```bash
python main.py
```

## 📖 Kullanım

### 1️⃣ İlk Kurulum

1. **Okul Türü Seçimi**: İlk açılışta okul türünü seçin (İlkokul, Ortaokul, Lise, vb.)
2. **Sınıfları Tanımlayın**: Ana menüden "Sınıf Yönetimi" → Sınıfları ekleyin
3. **Öğretmenleri Ekleyin**: "Öğretmen Yönetimi" → Öğretmen bilgilerini girin
4. **Dersleri Tanımlayın**: "Ders Yönetimi" → Gerekli dersleri ekleyin

### 2️⃣ Ders Atama

1. **Öğretmen Uygunluğu**: "Öğretmen Uygunluk" → Her öğretmen için müsait günleri işaretleyin
2. **Hızlı Ders Atama**: "Ders Atama" → "Hızlı Atama" ile dersleri öğretmenlere atayın
3. **Otomatik Doldur**: Eksik atamaları "Eksikleri Otomatik Doldur" butonu ile tamamlayın

### 3️⃣ Program Oluşturma

1. **Ders Programı Oluştur**: Ana ekrandan "PROGRAMI OLUŞTUR" butonuna tıklayın
2. **Algoritma Seçimi**: İstediğiniz zamanlama algoritmasını seçin:
   - **Simple Perfect**: Temel algoritma
   - **Enhanced Strict**: Gelişmiş kısıtlama çözücü
   - **Ultimate**: En kapsamlı algoritma
3. **Boşlukları Doldur**: İhtiyaç halinde "BOŞLUKLARI DOLDUR" ile eksik saatleri tamamlayın

### 4️⃣ Programları Görüntüleme ve Dışa Aktarma

1. **Sınıf Programı**: Herhangi bir sınıfın programını görüntüleyin
2. **Öğretmen Programı**: Öğretmenlerin ders programlarını kontrol edin
3. **Rapor Oluştur**: Excel veya PDF formatında programları indirin

## 🛠️ Teknolojiler

- **Python 3.8+**: Ana programlama dili
- **PyQt5**: Grafik arayüz kütüphanesi
- **SQLite**: Hafif ve hızlı veritabanı
- **ReportLab**: PDF oluşturma
- **OpenPyXL**: Excel işlemleri

## 📁 Proje Yapısı

```
dersdagitimprogrami/
├── main.py                      # Ana program giriş noktası
├── algorithms/                  # Zamanlama algoritmaları
│   ├── simple_perfect_scheduler.py
│   ├── enhanced_strict_scheduler.py
│   ├── ultimate_scheduler.py
│   └── scheduler.py
├── database/                    # Veritabanı işlemleri
│   ├── db_manager.py
│   └── models.py
├── ui/                         # Kullanıcı arayüzü
│   ├── main_window.py
│   ├── schedule_widget.py
│   └── dialogs/
├── reports/                    # Rapor oluşturma
│   ├── excel_generator.py
│   └── pdf_generator.py
└── utils/                      # Yardımcı araçlar
    └── helpers.py
```

## 🎯 Algoritmalar

### Simple Perfect Scheduler
Temel kısıtlama tabanlı zamanlama algoritması. Hızlı ve basit çözümler için idealdir.

**Özellikler:**
- Temel çakışma kontrolü
- Öğretmen uygunluğu denetimi
- Blok ders yerleştirme

### Enhanced Strict Scheduler
Gelişmiş kısıtlama çözücü. Daha karmaşık senaryolar için optimize edilmiştir.

**Özellikler:**
- Akıllı blok yerleştirme
- 3 ardışık ders kontrolü
- Aynı güne bölünmüş ders önleme
- Yük dengeleme

### Ultimate Scheduler
En kapsamlı ve akıllı algoritma. Maksimum optimizasyon sağlar.

**Özellikler:**
- Tüm kısıtlamaları karşılama
- Backtracking ile optimal çözüm
- Öğretmen tercihleri
- Dinamik önceliklendirme

## 🎓 Desteklenen Okul Türleri

- İlkokul
- Ortaokul
- Lise
- Anadolu Lisesi
- Fen Lisesi
- Sosyal Bilimler Lisesi

## ⚙️ Yapılandırma

### Ders Saati Sayıları

Program, her okul türü için önceden tanımlanmış ders saati sayılarına sahiptir:

- **İlkokul/Ortaokul**: 7 saat/gün
- **Lise**: 8 saat/gün

### Çalışma Günleri

Varsayılan olarak Pazartesi-Cuma arası 5 gün.

## 🐛 Sorun Giderme

### Program Oluşturulamıyor

- **Çözüm 1**: Tüm öğretmenlerin uygunluk takvimini kontrol edin
- **Çözüm 2**: Ders atamalarının doğru yapıldığını kontrol edin
- **Çözüm 3**: Farklı bir algoritma deneyin

### Bazı Dersler Yerleşmiyor

- **Çözüm 1**: "Boşlukları Doldur" özelliğini kullanın
- **Çözüm 2**: Öğretmen uygunluğunu artırın
- **Çözüm 3**: Manuel olarak düzenleme yapın

### Çakışmalar Oluşuyor

- **Çözüm 1**: Veritabanını yedekleyin ve yeni baştan oluşturun
- **Çözüm 2**: Çakışma kontrolü yapın ve manuel düzeltin

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 👥 Yazarlar

- **DolphinLong** - İlk geliştirme

## 🙏 Teşekkürler

- MEB müfredatı için Milli Eğitim Bakanlığı
- Tüm katkıda bulunan geliştiricilere
- PyQt5 ve Python topluluğuna

## 📞 İletişim

Proje Bağlantısı: [https://github.com/DolphinLong/dersdagitimprogrami](https://github.com/DolphinLong/dersdagitimprogrami)

---

⭐ Bu projeyi faydalı bulduysanız yıldız vermeyi unutmayın!
