# -*- coding: utf-8 -*-
"""
Tests for configuration loader
"""

import pytest
import tempfile
import os
from config.config_loader import ConfigLoader


def test_config_loader_default():
    """Test config loader with default config"""
    # Use non-existent file to trigger default config
    loader = ConfigLoader('/tmp/nonexistent_config.yaml')
    
    assert loader.config is not None
    assert 'algorithms' in loader.config
    assert 'performance' in loader.config


def test_config_get():
    """Test getting config values"""
    loader = ConfigLoader()
    
    # Test nested path
    value = loader.get('algorithms.ultra_aggressive.max_iterations', default=500)
    assert isinstance(value, int)
    
    # Test non-existent path
    value = loader.get('non.existent.path', default='default_value')
    assert value == 'default_value'


def test_config_set():
    """Test setting config values"""
    loader = ConfigLoader()
    
    # Set value
    loader.set('test.nested.value', 123)
    
    # Get value back
    value = loader.get('test.nested.value')
    assert value == 123


def test_config_save_load():
    """Test saving and loading config"""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_file = f.name
    
    try:
        # Create config and set values
        loader = ConfigLoader(temp_file)
        loader.set('test.value', 456)
        loader.save()
        
        # Load in new instance
        new_loader = ConfigLoader(temp_file)
        value = new_loader.get('test.value')
        
        assert value == 456
        
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
