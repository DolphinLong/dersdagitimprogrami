import os
import django

# Django ayarlarını yapılandır
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ders_dagitim.settings')
django.setup()

# Superuser oluştur
from django.contrib.auth import get_user_model

User = get_user_model()

# Kullanıcı zaten varsa sil
try:
    user = User.objects.get(username='admin')
    user.delete()
    print("Mevcut admin kullanıcısı silindi.")
except User.DoesNotExist:
    pass

# Yeni superuser oluştur
user = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)

print("Superuser oluşturuldu:")
print("Kullanıcı adı: admin")
print("Şifre: admin123")