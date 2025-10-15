Config Modülü
=============

Bu modül, yapılandırma yönetimini sağlar.

Config Loader
-------------

.. automodule:: config.config_loader
   :members:
   :undoc-members:
   :show-inheritance:

Kullanım Örnekleri
------------------

Yapılandırma Yükleme
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from config.config_loader import ConfigLoader
   
   # Config yükle
   config = ConfigLoader("config/scheduler_config.yaml")
   
   # Değer al
   max_iterations = config.get("algorithms.ultra_aggressive.max_iterations")
   print(f"Max iterations: {max_iterations}")

Yapılandırma Değiştirme
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Değer değiştir
   config.set("algorithms.ultra_aggressive.max_iterations", 2000)
   
   # Kaydet
   config.save()

Global Config Kullanımı
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from config.config_loader import get_config
   
   # Global config instance
   config = get_config()
   
   # Kullan
   log_level = config.get("logging.level", "INFO")
