# 🐳 Docker Kullanım Kılavuzu

Bu kılavuz, Ders Dağıtım Programı'nı Docker ile çalıştırmak için gerekli bilgileri içerir.

---

## 📋 İçindekiler

1. [Docker Kurulumu](#docker-kurulumu)
2. [Image Oluşturma](#image-oluşturma)
3. [Container Çalıştırma](#container-çalıştırma)
4. [Docker Compose Kullanımı](#docker-compose-kullanımı)
5. [Veri Kalıcılığı](#veri-kalıcılığı)
6. [GUI Uygulaması Çalıştırma](#gui-uygulaması-çalıştırma)
7. [Sorun Giderme](#sorun-giderme)

---

## 🚀 Docker Kurulumu

### Windows

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) indirin
2. Kurulumu tamamlayın
3. Docker Desktop'ı başlatın

### macOS

1. [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop) indirin
2. Kurulumu tamamlayın
3. Docker Desktop'ı başlatın

### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Fedora
sudo dnf install docker docker-compose

# Docker servisini başlat
sudo systemctl start docker
sudo systemctl enable docker

# Kullanıcıyı docker grubuna ekle
sudo usermod -aG docker $USER
```

### Kurulumu Doğrulama

```bash
docker --version
docker-compose --version
```

---

## 🏗️ Image Oluşturma

### Basit Build

```bash
docker build -t dersdagitim:latest .
```

### Build Argümanları ile

```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t dersdagitim:3.4 \
  .
```

### Multi-stage Build (Gelecek)

```bash
docker build \
  --target production \
  -t dersdagitim:prod \
  .
```

---

## 🎮 Container Çalıştırma

### Basit Çalıştırma

```bash
docker run -it --rm dersdagitim:latest
```

### Veri Kalıcılığı ile

```bash
docker run -it --rm \
  -v $(pwd)/schedule.db:/app/schedule.db \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/reports:/app/reports \
  dersdagitim:latest
```

### GUI ile Çalıştırma (Linux)

```bash
# X11 forwarding
xhost +local:docker

docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/schedule.db:/app/schedule.db \
  dersdagitim:latest

xhost -local:docker
```

### GUI ile Çalıştırma (Windows)

1. [VcXsrv](https://sourceforge.net/projects/vcxsrv/) indirin ve kurun
2. XLaunch'ı başlatın (tüm varsayılan ayarlar)
3. Container'ı çalıştırın:

```powershell
docker run -it --rm `
  -e DISPLAY=host.docker.internal:0 `
  -v ${PWD}/schedule.db:/app/schedule.db `
  dersdagitim:latest
```

### GUI ile Çalıştırma (macOS)

1. [XQuartz](https://www.xquartz.org/) indirin ve kurun
2. XQuartz'ı başlatın
3. Preferences → Security → "Allow connections from network clients" işaretleyin
4. Terminal'de:

```bash
xhost + 127.0.0.1

docker run -it --rm \
  -e DISPLAY=host.docker.internal:0 \
  -v $(pwd)/schedule.db:/app/schedule.db \
  dersdagitim:latest
```

---

## 🎼 Docker Compose Kullanımı

### Başlatma

```bash
# Arka planda çalıştır
docker-compose up -d

# Logları görüntüle
docker-compose logs -f

# Durdur
docker-compose down
```

### Yeniden Build

```bash
docker-compose build
docker-compose up -d
```

### Belirli Servisi Çalıştırma

```bash
docker-compose up app
```

---

## 💾 Veri Kalıcılığı

### Volume Kullanımı

Docker Compose otomatik olarak şu dizinleri persist eder:

- `./schedule.db` - Veritabanı
- `./logs/` - Log dosyaları
- `./reports/` - Raporlar

### Manuel Yedekleme

```bash
# Veritabanını yedekle
docker cp dersdagitim-app:/app/schedule.db ./backup_$(date +%Y%m%d).db

# Veritabanını geri yükle
docker cp ./backup_20240101.db dersdagitim-app:/app/schedule.db
```

### Volume Yönetimi

```bash
# Volume'ları listele
docker volume ls

# Volume'u temizle
docker volume prune
```

---

## 🖥️ GUI Uygulaması Çalıştırma

### Linux (X11)

```bash
# X11 erişimini aç
xhost +local:docker

# Docker Compose ile çalıştır
DISPLAY=$DISPLAY docker-compose up

# Bitince X11 erişimini kapat
xhost -local:docker
```

### Windows (VcXsrv)

1. VcXsrv'i başlat
2. `docker-compose.yml` dosyasında:
   ```yaml
   environment:
     - DISPLAY=host.docker.internal:0
   ```
3. Çalıştır:
   ```bash
   docker-compose up
   ```

### macOS (XQuartz)

1. XQuartz'ı başlat
2. X11 forwarding'i aktifleştir:
   ```bash
   xhost + 127.0.0.1
   ```
3. `docker-compose.yml` dosyasında:
   ```yaml
   environment:
     - DISPLAY=host.docker.internal:0
   ```
4. Çalıştır:
   ```bash
   docker-compose up
   ```

---

## 🔧 Sorun Giderme

### GUI Görünmüyor

**Linux:**
```bash
# X11 erişimini kontrol et
echo $DISPLAY
xhost

# X11 socket'i kontrol et
ls -la /tmp/.X11-unix
```

**Windows:**
- VcXsrv'in çalıştığından emin olun
- Windows Firewall'da izin verin

**macOS:**
- XQuartz'ın çalıştığından emin olun
- `xhost + 127.0.0.1` komutunu çalıştırın

### Permission Denied

```bash
# Linux'ta docker grubuna ekle
sudo usermod -aG docker $USER

# Logout/login yapın veya
newgrp docker
```

### Container Başlamıyor

```bash
# Logları kontrol et
docker logs dersdagitim-app

# Container'ı interaktif modda çalıştır
docker run -it dersdagitim:latest /bin/bash
```

### Veritabanı Erişim Hatası

```bash
# Volume'u kontrol et
docker volume inspect dersdagitim_db-data

# Yeni veritabanı ile başlat
docker-compose down -v
docker-compose up
```

### Image Boyutu Çok Büyük

```bash
# Unused image'ları temizle
docker image prune

# Build cache'i temizle
docker builder prune
```

---

## 📊 Performans Optimizasyonu

### Resource Limits

`docker-compose.yml` dosyasında:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 512M
```

### Build Cache Kullanımı

```bash
# Cache kullanarak build
docker build --cache-from dersdagitim:latest -t dersdagitim:latest .

# Cache kullanmadan build
docker build --no-cache -t dersdagitim:latest .
```

---

## 🚀 Production Deployment

### Docker Hub'a Push

```bash
# Login
docker login

# Tag
docker tag dersdagitim:latest yourusername/dersdagitim:3.4

# Push
docker push yourusername/dersdagitim:3.4
```

### Docker Hub'dan Pull

```bash
docker pull yourusername/dersdagitim:3.4
docker run -it yourusername/dersdagitim:3.4
```

---

## 📝 Örnek Kullanım Senaryoları

### Senaryo 1: Geliştirme Ortamı

```bash
docker-compose -f docker-compose.dev.yml up
```

### Senaryo 2: Test Ortamı

```bash
docker run -it --rm \
  -v $(pwd)/test_data:/app/data \
  dersdagitim:latest \
  python -m pytest tests/
```

### Senaryo 3: Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔐 Güvenlik

### Best Practices

1. **Non-root user kullan** (Dockerfile'da zaten var)
2. **Secrets kullan:**
   ```bash
   docker secret create db_password password.txt
   ```
3. **Network izolasyonu:**
   ```yaml
   networks:
     - internal
   ```
4. **Read-only filesystem:**
   ```yaml
   read_only: true
   ```

---

## 📚 Ek Kaynaklar

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Son Güncelleme:** 2024  
**Versiyon:** 3.4
