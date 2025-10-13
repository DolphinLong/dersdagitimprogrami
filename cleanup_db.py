
import sqlite3
import logging
import os

# Proje kök dizinini al
project_root = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(project_root, "schedule.db")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cleanup_triggers():
    """Veritabanında 'lessons_old' tablosuna referans veren bozuk tetikleyicileri temizler."""
    if not os.path.exists(DB_FILE):
        logging.warning(f"Veritabanı dosyası bulunamadı: {DB_FILE}. İşlem iptal edildi.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        logging.info(f"Veritabanı bağlantısı kuruldu: {DB_FILE}")

        # 1. 'lessons_old' referansı içeren tüm tetikleyicileri bul
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND sql LIKE '%lessons_old%'")
        triggers_to_drop = cursor.fetchall()

        if not triggers_to_drop:
            logging.info("Temizlenecek bozuk bir tetikleyici bulunamadı. Veritabanı temiz görünüyor.")
            return

        logging.warning(f"{len(triggers_to_drop)} adet bozuk tetikleyici bulundu. Temizleme işlemi başlıyor...")

        # 2. Bulunan her tetikleyiciyi sil
        for trigger_name, trigger_sql in triggers_to_drop:
            try:
                logging.info(f"'{trigger_name}' adlı tetikleyici siliniyor...")
                cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
                logging.info(f"'{trigger_name}' başarıyla silindi.")
            except sqlite3.Error as e:
                logging.error(f"'{trigger_name}' silinirken bir hata oluştu: {e}")
        
        conn.commit()
        logging.info("Tetikleyici temizleme işlemi başarıyla tamamlandı.")

    except sqlite3.Error as e:
        logging.error(f"Temizleme sırasında bir veritabanı hatası oluştu: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        logging.error(f"Beklenmedik bir hata oluştu: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logging.info("Veritabanı bağlantısı kapatıldı.")

if __name__ == "__main__":
    cleanup_triggers()
