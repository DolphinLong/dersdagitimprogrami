# 📊 Ders Programı Algoritması Analiz Raporu

## 🔴 Tespit Edilen Sorunlar

### 1. **Aşırı Katı Kurallar**
#### Problem:
- **3 saat üst üste aynı ders yasağı**: Matematik gibi 6 saatlik derslerde sorun çıkarıyor
- **Aynı güne bölünmüş ders yasağı**: 2+1 gibi yerleştirmeler engelleniyor
- **Öğretmen uygunluk kontrolü**: İlk 100 iterasyonda çok katı

#### Etki:
- Boş hücreler kalıyor
- %85-90 dolulukta takılıyor

---

### 2. **Yetersiz Backtracking**
#### Problem:
- İlk yerleştirme başarısız olursa, önceki kararlar değiştirilmiyor
- "Greedy" yaklaşım kullanılıyor
- Çıkmaz sokağa girince geri dönülmüyor

#### Etki:
- Bazı dersler hiç yerleştirilemiyor
- Boş slotlar kalıyor ama doldurulmuyor

---

### 3. **Sıralama Stratejisi Zayıf**
#### Problem:
```python
# Sadece haftalık saate göre sıralama
all_needs.sort(key=lambda x: -x['weekly_hours'])
```

#### Eksikler:
- Öğretmen yoğunluğu dikkate alınmıyor
- Sınıf yoğunluğu hesaplanmıyor
- Zor yerleşecek dersler önceliklendirilmiyor

---

### 4. **İterasyon Limitleri Düşük**
#### Problem:
- `_try_any_available`: Sadece 10x deneme (satır 442)
- UltraAggressive: 50 iterasyonda iyileşme yoksa duruyor (satır 260)
- Max 5000 iterasyon ama genelde 50-100'de bitiyor

---

## ✅ Önerilen Çözümler

### Çözüm 1: **Kuralları Esnetme Stratejisi**
```python
# Öncelik sırası:
1. İlk 50 iterasyon: Tüm kurallar aktif
2. 50-200 iterasyon: 3 saat üst üste kuralını kaldır
3. 200-500 iterasyon: Aynı güne bölünmüş ders yasağını kaldır
4. 500+ iterasyon: Sadece çakışma kontrolü (öğretmen uygunluğu esnek)
```

### Çözüm 2: **Akıllı Sıralama**
```python
def calculate_difficulty_score(need):
    # Zor yerleşecek dersleri önce yerleştir
    teacher_load = get_teacher_total_hours(need['teacher_id'])
    class_load = get_class_total_hours(need['class_id'])
    
    # Yüksek puan = Zor ders
    score = (
        need['weekly_hours'] * 10 +  # Fazla saatli dersler
        teacher_load * 5 +             # Yoğun öğretmenler
        class_load * 3                 # Yoğun sınıflar
    )
    return score

all_needs.sort(key=calculate_difficulty_score, reverse=True)
```

### Çözüm 3: **Gerçek Backtracking**
```python
def backtrack_schedule(assignments, index):
    if index == len(assignments):
        return True  # Tüm dersler yerleşti
    
    assignment = assignments[index]
    
    # Tüm olası slotları dene
    for day in range(5):
        for slot in range(time_slots):
            if can_place(assignment, day, slot):
                place(assignment, day, slot)
                
                if backtrack_schedule(assignments, index + 1):
                    return True  # Başarılı
                
                remove(assignment, day, slot)  # GERİ AL
    
    return False  # Bu ders yerleştirilemedi
```

### Çözüm 4: **Dinamik İterasyon Limiti**
```python
# Doluluk oranına göre limit artır
if coverage < 80:
    max_iterations = 10000
elif coverage < 90:
    max_iterations = 5000
else:
    max_iterations = 2000

# İyileşme varsa devam et
no_improvement_limit = min(100, max_iterations // 10)
```

---

## 🎯 Hızlı Çözüm (Minimum Değişiklik)

### Adım 1: 3 Saat Üst Üste Kuralını Kaldır
**Dosya**: `simple_perfect_scheduler.py`
**Satır**: 527-531

```python
# ÖNCEDEN:
if lesson_id is not None:
    if self._would_create_three_consecutive_lessons(class_id, lesson_id, day, slot):
        return False

# SONRA:
# Bu kuralı tamamen kaldır veya sadece 4+ saat için uygula
if lesson_id is not None and weekly_hours <= 3:
    if self._would_create_three_consecutive_lessons(class_id, lesson_id, day, slot):
        return False
```

### Adım 2: Aynı Güne Bölünmüş Ders Yasağını Esnet
**Dosya**: `simple_perfect_scheduler.py`
**Satır**: 493-508

```python
# ÖNCEDEN: Hiç ardışık değilse ENGELLE
if min_distance > 1:
    return False

# SONRA: Sadece uyarı ver, engelleme
# (Bu kontrolü tamamen kaldır)
```

### Adım 3: İterasyon Limitlerini Artır
**Dosya**: `ultra_aggressive_scheduler.py`
**Satır**: 49, 260

```python
# ÖNCEDEN:
self.max_iterations = 5000
max_no_improvement = 50

# SONRA:
self.max_iterations = 10000
max_no_improvement = 200
```

### Adım 4: Rastgele Deneme Sayısını Artır
**Dosya**: `simple_perfect_scheduler.py`
**Satır**: 442

```python
# ÖNCEDEN:
max_attempts = hours_needed * 10

# SONRA:
max_attempts = hours_needed * 100
```

---

## 📈 Beklenen İyileşme

| Metrik | Önce | Sonra (Tahmini) |
|--------|------|-----------------|
| Doluluk Oranı | %85-90 | %95-100 |
| Boş Hücre | 10-15 | 0-5 |
| Süre | 5-10 sn | 10-30 sn |
| Başarı Oranı | %70 | %95 |

---

## ⚠️ Dikkat Edilmesi Gerekenler

1. **Performans**: Daha fazla iterasyon = Daha uzun süre
2. **Öğretmen Yorgunluğu**: 3 saat üst üste kuralı kaldırılırsa öğretmenler yorulabilir
3. **Eğitimsel Kalite**: Aynı güne bölünmüş dersler öğrenci konsantrasyonunu etkileyebilir

---

## 🚀 Uygulama Önerisi

**Aşama 1**: Hızlı çözümü uygula (yukarıdaki 4 adım)
**Aşama 2**: Test et ve doluluk oranını ölç
**Aşama 3**: Gerekirse gerçek backtracking ekle
**Aşama 4**: Akıllı sıralama stratejisi ekle

---

**Hazırlayan**: Cascade AI
**Tarih**: 2025-10-17
