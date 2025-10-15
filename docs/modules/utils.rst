Utils Modülü
============

Bu modül, yardımcı araçları içerir.

Password Hasher
---------------

.. automodule:: utils.password_hasher
   :members:
   :undoc-members:
   :show-inheritance:

Kullanım Örnekleri
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from utils.password_hasher import hash_password, verify_password
   
   # Şifre hashleme
   password = "my_secure_password"
   hashed = hash_password(password)
   
   # Şifre doğrulama
   is_valid = verify_password(hashed, password)
   print(f"Şifre geçerli: {is_valid}")

Helpers
-------

.. automodule:: utils.helpers
   :members:
   :undoc-members:
   :show-inheritance:
