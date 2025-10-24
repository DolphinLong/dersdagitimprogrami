import sqlite3

conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print('Veritabanı tabloları:', tables)

# Her tablo için kayıt sayısını kontrol et
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"- {table}: {count} kayıt")
    except Exception as e:
        print(f"- {table}: Hata - {e}")

conn.close()