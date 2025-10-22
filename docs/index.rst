Ders Dağıtım Programı - API Dokümantasyonu
==========================================

Hoş Geldiniz!
-------------

Bu dokümantasyon, Ders Dağıtım Programı'nın API referansını içerir.

Modern ve akıllı okul ders programı oluşturma sistemi. Yapay zeka destekli 
algoritmalar ile otomatik ders dağılımı, öğretmen yük dengeleme ve çakışma önleme.

.. toctree::
   :maxdepth: 2
   :caption: İçindekiler:

   algorithm_selection
   modules/algorithms
   modules/database
   modules/ui
   modules/utils
   modules/config
   modules/reports

Hızlı Başlangıç
---------------

Kurulum
^^^^^^^

.. code-block:: bash

   pip install -r requirements.txt

Kullanım
^^^^^^^^

.. code-block:: python

   from database.db_manager import DatabaseManager
   from algorithms.hybrid_optimal_scheduler import HybridOptimalScheduler

   # Veritabanı bağlantısı
   db = DatabaseManager("schedule.db")
   
   # Zamanlayıcı oluştur
   scheduler = HybridOptimalScheduler(db)
   
   # Program oluştur
   result = scheduler.generate_schedule()

Özellikler
----------

* 🚀 8+ farklı zamanlama algoritması
* 🎯 Hard ve soft constraint desteği
* 🤖 Makine öğrenmesi entegrasyonu
* 📊 Excel/PDF/HTML rapor üretimi
* 🧪 174+ test (45% coverage)
* 🔒 Güvenli şifre hashleme (bcrypt/PBKDF2)
* 🎨 Modern PyQt5 arayüzü

İndeksler ve Tablolar
---------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
