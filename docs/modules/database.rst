Database Modülü
================

Bu modül, veritabanı işlemlerini yönetir.

Database Manager
----------------

.. automodule:: database.db_manager
   :members:
   :undoc-members:
   :show-inheritance:

Models
------

.. automodule:: database.models
   :members:
   :undoc-members:
   :show-inheritance:

Kullanım Örnekleri
------------------

Veritabanı Bağlantısı
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from database.db_manager import DatabaseManager
   
   # Veritabanı oluştur
   db = DatabaseManager("schedule.db")
   
   # Context manager ile kullan
   with DatabaseManager("schedule.db") as db:
       classes = db.get_all_classes()

Sınıf Ekleme
^^^^^^^^^^^^

.. code-block:: python

   # Sınıf ekle
   class_id = db.add_class("9-A", 9)
   
   # Sınıfları listele
   classes = db.get_all_classes()
   for cls in classes:
       print(f"{cls.name} - {cls.grade}")

Öğretmen Ekleme
^^^^^^^^^^^^^^^

.. code-block:: python

   # Öğretmen ekle
   teacher_id = db.add_teacher("Ahmet Yılmaz", "Matematik")
   
   # Öğretmenleri listele
   teachers = db.get_all_teachers()

Ders Atama
^^^^^^^^^^

.. code-block:: python

   # Ders atama ekle
   assignment_id = db.add_lesson_assignment(
       class_id=1,
       lesson_id=2,
       teacher_id=3,
       weekly_hours=4
   )
