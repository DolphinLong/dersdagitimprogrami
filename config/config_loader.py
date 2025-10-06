# -*- coding: utf-8 -*-
"""
Configuration Loader
Loads and manages configuration from YAML files
"""

import os
import yaml
import logging
from typing import Dict, Any


class ConfigLoader:
    """Load and manage application configuration"""
    
    def __init__(self, config_file: str = None):
        """
        Initialize config loader
        
        Args:
            config_file: Path to YAML config file
        """
        self.logger = logging.getLogger(__name__)
        
        if config_file is None:
            # Default config file
            config_dir = os.path.join(os.path.dirname(__file__))
            config_file = os.path.join(config_dir, 'scheduler_config.yaml')
        
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Returns:
            Configuration dictionary
        """
        try:
            if not os.path.exists(self.config_file):
                self.logger.warning(f"Config file not found: {self.config_file}")
                return self._get_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.logger.info(f"Configuration loaded from {self.config_file}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}", exc_info=True)
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            'algorithms': {
                'ultra_aggressive': {
                    'enabled': True,
                    'max_iterations': 1000,
                    'relaxation_threshold': 100
                }
            },
            'performance': {
                'max_execution_time': 120,
                'memory_limit': 500
            },
            'logging': {
                'level': 'INFO',
                'console': True,
                'file': True
            }
        }
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by path
        
        Args:
            path: Dot-separated path (e.g., 'algorithms.ultra_aggressive.max_iterations')
            default: Default value if path not found
        
        Returns:
            Configuration value
        """
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, path: str, value: Any):
        """
        Set configuration value by path
        
        Args:
            path: Dot-separated path
            value: Value to set
        """
        if self.config is None:
            self.config = {}
        
        keys = path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if not isinstance(config, dict):
                config = {}
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}", exc_info=True)


# Global config instance
_config_loader = None


def get_config() -> ConfigLoader:
    """
    Get global configuration instance
    
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
