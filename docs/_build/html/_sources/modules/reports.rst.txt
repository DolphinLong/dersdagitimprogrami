Reports Modülü
==============

Bu modül, rapor üretimini sağlar.

Excel Generator
---------------

.. automodule:: reports.excel_generator
   :members:
   :undoc-members:
   :show-inheritance:

PDF Generator
-------------

.. automodule:: reports.pdf_generator
   :members:
   :undoc-members:
   :show-inheritance:

HTML Generator
--------------

.. automodule:: reports.html_generator
   :members:
   :undoc-members:
   :show-inheritance:

Kullanım Örnekleri
------------------

Excel Raporu Oluşturma
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from reports.excel_generator import ExcelGenerator
   from database.db_manager import DatabaseManager
   
   db = DatabaseManager("schedule.db")
   generator = ExcelGenerator(db)
   
   # Sınıf programı
   generator.generate_class_schedule(class_id=1, output_file="9A_program.xlsx")
   
   # Öğretmen programı
   generator.generate_teacher_schedule(teacher_id=1, output_file="teacher_program.xlsx")

PDF Raporu Oluşturma
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from reports.pdf_generator import PDFGenerator
   
   generator = PDFGenerator(db)
   
   # PDF oluştur
   generator.generate_class_schedule(class_id=1, output_file="9A_program.pdf")
