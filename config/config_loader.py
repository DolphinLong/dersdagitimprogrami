# -*- coding: utf-8 -*-
"""
Configuration loader with validation
Loads configuration from YAML files and validates against schema
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from config.config_validator import ConfigValidator


class ConfigLoader:
    """
    Loads and validates scheduler configuration
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or Path("config/scheduler_config.yaml")
        self.validator = ConfigValidator()
        self._config = None
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration from file
        
        Returns:
            Configuration dictionary if valid, default config if validation fails
        """
        if self._config is not None:
            return self._config
            
        # Try to load the config file
        validation_result = self.validator.validate_config_file(str(self.config_path))
        
        if validation_result['valid']:
            self._config = validation_result['config']
            self.logger.info("Configuration loaded and validated successfully")
        else:
            # Log validation errors and use default config
            self.logger.warning("Configuration validation failed, using default values")
            for field, error in validation_result['errors'].items():
                self.logger.warning(f"Config error in '{field}': {error}")
            
            # Use default config
            self._config = self._get_default_config()
            
        # Add warnings to logs
        for warning in validation_result.get('warnings', []):
            self.logger.warning(f"Config warning: {warning}")
            
        return self._config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values
        
        Returns:
            Default configuration dictionary
        """
        return {
            'algorithms': {
                'simple_perfect': {
                    'enabled': True,
                    'max_attempts': 100
                },
                'ultimate': {
                    'enabled': True,
                    'max_backtrack': 4000,
                    'use_forward_checking': True
                },
                'enhanced_strict': {
                    'enabled': True,
                    'pressure_tracking': True,
                    'max_consecutive_lessons': 3
                },
                'hybrid_optimal': {
                    'enabled': True,
                    'arc_consistency': True,
                    'soft_constraints_weight': 0.3,
                    'simulated_annealing': {
                        'enabled': True,
                        'initial_temperature': 100.0,
                        'cooling_rate': 0.95
                    }
                },
                'ultra_aggressive': {
                    'enabled': True,
                    'max_iterations': 1000,
                    'relaxation_threshold': 100,
                    'aggressive_threshold': 50,
                    'final_validation': True
                }
            },
            'performance': {
                'max_execution_time': 120,
                'memory_limit': 500,
                'enable_parallel_processing': False,
                'thread_pool_size': 4
            },
            'constraints': {
                'hard': {
                    'no_class_conflicts': True,
                    'no_teacher_conflicts': True,
                    'respect_weekly_hours': True
                },
                'soft': {
                    'teacher_availability': {
                        'weight': 1.0,
                        'relaxable_after_iterations': 100
                    },
                    'consecutive_lessons': {
                        'weight': 0.8,
                        'max_consecutive': 3
                    },
                    'preferred_time_slots': {
                        'weight': 0.6,
                        'morning_heavy_subjects': True
                    },
                    'balanced_daily_load': {
                        'weight': 0.7,
                        'target_variance': 1.5
                    }
                }
            },
            'blocks': {
                'enabled': True,
                'preferred_sizes': [2, 2, 2],
                'allow_single_hours': True,
                'max_block_size': 3
            },
            'logging': {
                'level': 'INFO',
                'console': True,
                'file': True,
                'rotation': {
                    'max_bytes': 10485760,  # 10 MB
                    'backup_count': 5
                }
            },
            'ui': {
                'show_progress': True,
                'update_interval': 100,
                'show_statistics': True,
                'conflict_warnings': True
            },
            'database': {
                'backup_before_generation': True,
                'auto_save': True,
                'transaction_mode': True
            },
            'validation': {
                'check_conflicts': True,
                'auto_resolve_conflicts': True,
                'max_conflict_resolution_attempts': 3
            },
            'coverage': {
                'target_percentage': 95.0,
                'min_acceptable_percentage': 85.0,
                'report_empty_slots': True
            },
            'development': {
                'enable_debug_mode': False,
                'save_intermediate_results': False,
                'profile_performance': False,
                'generate_reports': True
            }
        }
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a specific configuration value using dot notation
        
        Args:
            key_path: Path to the config value using dot notation (e.g. 'algorithms.hybrid_optimal.enabled')
            default: Default value if the key doesn't exist
            
        Returns:
            Configuration value or default
        """
        config = self.load_config()
        
        # Navigate through the config dictionary using the key path
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def save_config(self, config: Dict[str, Any], path: Optional[str] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary to save
            path: Path to save to (defaults to config_path)
            
        Returns:
            True if successful, False otherwise
        """
        save_path = path or str(self.config_path)
        
        try:
            # Validate before saving
            validation_result = self.validator.validate_config_dict(config)
            
            if not validation_result['valid']:
                self.logger.error("Configuration validation failed before saving")
                for field, error in validation_result['errors'].items():
                    self.logger.error(f"Validation error in '{field}': {error}")
                return False
            
            # Create directory if it doesn't exist
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save the config
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def reload_config(self) -> Dict[str, Any]:
        """
        Reload the configuration from file
        
        Returns:
            Configuration dictionary
        """
        self._config = None
        return self.load_config()


# Singleton instance for easy access
_config_loader = None


def get_config() -> Dict[str, Any]:
    """
    Get the global configuration
    
    Returns:
        Configuration dictionary
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.load_config()


def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    Get a specific configuration value using dot notation
    
    Args:
        key_path: Path to the config value using dot notation
        default: Default value if the key doesn't exist
        
    Returns:
        Configuration value or default
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.get_config_value(key_path, default)