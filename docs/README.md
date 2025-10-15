# API Dokümantasyonu

Bu dizin, Ders Dağıtım Programı'nın API dokümantasyonunu içerir.

## Dokümantasyon Oluşturma

### Gereksinimler

```bash
pip install -r requirements.txt
```

### HTML Dokümantasyon Oluşturma

```bash
cd docs
make html
```

Dokümantasyon `_build/html/index.html` dosyasında oluşturulacaktır.

### PDF Dokümantasyon Oluşturma

```bash
cd docs
make latexpdf
```

### Dokümantasyonu Görüntüleme

```bash
# Windows
start _build/html/index.html

# Linux/Mac
open _build/html/index.html
```

## Dokümantasyon Yapısı

```
docs/
├── conf.py                 # Sphinx yapılandırması
├── index.rst              # Ana sayfa
├── modules/               # Modül dokümantasyonları
│   ├── algorithms.rst     # Algoritmalar
│   ├── database.rst       # Veritabanı
│   ├── ui.rst            # Kullanıcı arayüzü
│   ├── utils.rst         # Yardımcı araçlar
│   ├── config.rst        # Yapılandırma
│   └── reports.rst       # Raporlama
├── Makefile              # Build komutları
└── requirements.txt      # Dokümantasyon gereksinimleri
```

## Otomatik Dokümantasyon

Dokümantasyon, kod içindeki docstring'lerden otomatik olarak oluşturulur. 

### Docstring Formatı

Google style docstring kullanılır:

```python
def my_function(param1: int, param2: str) -> bool:
    """
    Fonksiyonun kısa açıklaması.
    
    Daha detaylı açıklama buraya yazılır.
    
    Args:
        param1: İlk parametre açıklaması
        param2: İkinci parametre açıklaması
        
    Returns:
        Dönüş değeri açıklaması
        
    Raises:
        ValueError: Hata durumu açıklaması
        
    Example:
        >>> my_function(1, "test")
        True
    """
    return True
```

## Online Dokümantasyon

Dokümantasyon GitHub Pages üzerinde yayınlanabilir:

1. Dokümantasyonu oluştur: `make html`
2. `_build/html` içeriğini `gh-pages` branch'ine push et
3. GitHub Pages'i aktifleştir

## Katkıda Bulunma

Dokümantasyona katkıda bulunmak için:

1. Kod içindeki docstring'leri güncelleyin
2. Gerekirse yeni `.rst` dosyaları ekleyin
3. `make html` ile test edin
4. Pull request oluşturun
