# -*- coding: utf-8 -*-
"""
Tests for password hashing utilities
"""

import pytest

from utils.password_hasher import PasswordHasher, hash_password, verify_password


class TestPasswordHasher:
    """Test password hashing functionality"""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        password = "test_password_123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_for_same_input(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        # Hashes should be different due to random salt
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that correct password verifies successfully"""
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(hashed, password) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification"""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)
        assert verify_password(hashed, wrong_password) is False

    def test_verify_password_empty(self):
        """Test verification with empty password"""
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(hashed, "") is False

    def test_hash_special_characters(self):
        """Test hashing password with special characters"""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(hashed, password) is True

    def test_hash_unicode_characters(self):
        """Test hashing password with unicode characters"""
        password = "şifre_türkçe_123_ğüşıöç"
        hashed = hash_password(password)
        assert verify_password(hashed, password) is True

    def test_hash_long_password(self):
        """Test hashing very long password"""
        password = "a" * 1000
        hashed = hash_password(password)
        assert verify_password(hashed, password) is True

    def test_verify_invalid_hash_format(self):
        """Test verification with invalid hash format"""
        invalid_hash = "not_a_valid_hash"
        password = "test_password"
        assert verify_password(invalid_hash, password) is False

    def test_class_methods(self):
        """Test PasswordHasher class methods directly"""
        password = "test_password_123"
        hashed = PasswordHasher.hash_password(password)
        assert PasswordHasher.verify_password(hashed, password) is True
        assert PasswordHasher.verify_password(hashed, "wrong") is False

    def test_pbkdf2_hash_format(self):
        """Test PBKDF2 hash format (fallback)"""
        # Force PBKDF2 by using internal method
        password = "test_password_123"
        hashed = PasswordHasher._hash_pbkdf2(password)
        
        # Check format
        assert hashed.startswith("pbkdf2_sha256$")
        parts = hashed.split("$")
        assert len(parts) == 4
        
        # Verify it works
        assert PasswordHasher._verify_pbkdf2(hashed, password) is True
        assert PasswordHasher._verify_pbkdf2(hashed, "wrong") is False

    def test_pbkdf2_custom_iterations(self):
        """Test PBKDF2 with custom iterations"""
        password = "test_password_123"
        iterations = 50_000
        hashed = PasswordHasher._hash_pbkdf2(password, iterations=iterations)
        
        # Check iterations in hash
        assert f"${iterations}$" in hashed
        
        # Verify it works
        assert PasswordHasher._verify_pbkdf2(hashed, password) is True

    def test_bcrypt_hash_format(self):
        """Test bcrypt hash format (if available)"""
        try:
            import bcrypt
            password = "test_password_123"
            hashed = PasswordHasher._hash_bcrypt(password)
            
            # Check format (bcrypt hashes start with $2b$ or $2a$)
            assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
            
            # Verify it works
            assert PasswordHasher._verify_bcrypt(hashed, password) is True
            assert PasswordHasher._verify_bcrypt(hashed, "wrong") is False
        except ImportError:
            pytest.skip("bcrypt not available")

    def test_bcrypt_custom_rounds(self):
        """Test bcrypt with custom rounds (if available)"""
        try:
            import bcrypt
            password = "test_password_123"
            rounds = 10
            hashed = PasswordHasher._hash_bcrypt(password, rounds=rounds)
            
            # Verify it works
            assert PasswordHasher._verify_bcrypt(hashed, password) is True
        except ImportError:
            pytest.skip("bcrypt not available")

    def test_mixed_hash_verification(self):
        """Test that verify_password can handle both bcrypt and PBKDF2"""
        password = "test_password_123"
        
        # Test PBKDF2
        pbkdf2_hash = PasswordHasher._hash_pbkdf2(password)
        assert verify_password(pbkdf2_hash, password) is True
        
        # Test bcrypt (if available)
        try:
            import bcrypt
            bcrypt_hash = PasswordHasher._hash_bcrypt(password)
            assert verify_password(bcrypt_hash, password) is True
        except ImportError:
            pass  # Skip bcrypt test if not available

    def test_empty_password_handling(self):
        """Test handling of empty password"""
        empty_password = ""
        hashed = hash_password(empty_password)
        assert verify_password(hashed, empty_password) is True
        assert verify_password(hashed, "not_empty") is False

    def test_case_sensitivity(self):
        """Test that password verification is case-sensitive"""
        password = "TestPassword123"
        hashed = hash_password(password)
        assert verify_password(hashed, password) is True
        assert verify_password(hashed, "testpassword123") is False
        assert verify_password(hashed, "TESTPASSWORD123") is False
