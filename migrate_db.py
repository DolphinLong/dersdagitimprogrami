
import sqlite3
import logging
import os

# Proje kök dizinini al
project_root = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(project_root, "schedule.db")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def migrate():
    """Veritabanı şemasını eski UNIQUE(name) kısıtlamasından yeni UNIQUE(name, school_type) kısıtlamasına geçirir."""
    if not os.path.exists(DB_FILE):
        logging.warning(f"Veritabanı dosyası bulunamadı: {DB_FILE}. İşlem iptal edildi.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        logging.info(f"Veritabanı bağlantısı kuruldu: {DB_FILE}")

        # 1. Mevcut şemayı kontrol et
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='lessons';")
        result = cursor.fetchone()
        if not result:
            logging.warning("'lessons' tablosu bulunamadı. İşlem iptal edildi.")
            return

        schema_sql = result[0].upper()
        
        # 2. Taşıma gerekip gerekmediğini kontrol et
        if "UNIQUE(NAME, SCHOOL_TYPE)" in schema_sql:
            logging.info("Veritabanı şeması zaten güncel. Taşıma işlemine gerek yok.")
            return

        # Hem `UNIQUE (NAME)` hem de `NAME TEXT UNIQUE` formatlarını kontrol et
        if "UNIQUE (NAME)" not in schema_sql and "NAME TEXT UNIQUE" not in schema_sql:
            logging.warning(f"Beklenmedik şema yapısı. Şema: {schema_sql}. Güvenlik için taşıma işlemi iptal edildi.")
            return

        logging.info("Eski şema tespit edildi. Taşıma işlemi başlatılıyor...")
        
        # 3. İşlemi başlat (Transaction)
        cursor.execute('BEGIN TRANSACTION;')
        logging.info("Veritabanı işlemi (transaction) başlatıldı.")

        # 4. Eski tabloyu yeniden adlandır
        cursor.execute('ALTER TABLE lessons RENAME TO lessons_old;')
        logging.info("Eski 'lessons' tablosu 'lessons_old' olarak yeniden adlandırıldı.")

        # 5. Yeni tabloyu doğru şema ile oluştur
        cursor.execute("""
            CREATE TABLE lessons (
                lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weekly_hours INTEGER DEFAULT 0,
                school_type TEXT NOT NULL,
                UNIQUE(name, school_type)
            )
        """)
        logging.info("Yeni 'lessons' tablosu doğru şema ile oluşturuldu.")

        # 6. Verileri eski tablodan yeni tabloya kopyala
        # Önce school_type sütununun var olup olmadığını kontrol et
        cursor.execute("PRAGMA table_info(lessons_old);")
        columns = [row[1] for row in cursor.fetchall()]
        if 'school_type' in columns:
            cursor.execute("""
                INSERT INTO lessons (lesson_id, name, weekly_hours, school_type)
                SELECT lesson_id, name, weekly_hours, school_type
                FROM lessons_old;
            """)
        else:
            # school_type sütunu yoksa, varsayılan bir değerle ekle (örn: 'Lise')
            # Bu durumun yaşanması beklenmez ama bir güvenlik önlemi
            logging.warning("'school_type' sütunu eski tabloda bulunamadı. Varsayılan değer 'Lise' olarak atanacak.")
            cursor.execute("""
                INSERT INTO lessons (lesson_id, name, weekly_hours, school_type)
                SELECT lesson_id, name, weekly_hours, 'Lise'
                FROM lessons_old;
            """)

        logging.info("Veriler eski tablodan yeni tabloya kopyalandı.")

        # 7. Eski tabloyu sil
        cursor.execute('DROP TABLE lessons_old;')
        logging.info("Eski 'lessons_old' tablosu silindi.")

        # 8. İşlemi onayla
        conn.commit()
        logging.info("İşlem başarıyla tamamlandı ve veritabanına kaydedildi.")

    except sqlite3.Error as e:
        logging.error(f"Taşıma sırasında bir veritabanı hatası oluştu: {e}")
        if conn:
            conn.rollback()
            logging.info("Hata nedeniyle yapılan tüm değişiklikler geri alındı.")
    except Exception as e:
        logging.error(f"Beklenmedik bir hata oluştu: {e}")
        if conn:
            conn.rollback()
            logging.info("Hata nedeniyle yapılan tüm değişiklikler geri alındı.")
    finally:
        if conn:
            conn.close()
            logging.info("Veritabanı bağlantısı kapatıldı.")

if __name__ == "__main__":
    migrate()

