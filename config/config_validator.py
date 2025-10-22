# -*- coding: utf-8 -*-
"""
Configuration validator for scheduler parameters
Validates YAML configuration files using schema validation
"""
import yaml
from typing import Dict, Any, List
from pathlib import Path
import logging
from cerberus import Validator


class ConfigValidator:
    """
    Validates scheduler configuration files against defined schemas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.schema = self._get_config_schema()
        
    def _get_config_schema(self) -> Dict[str, Any]:
        """
        Defines the schema for scheduler configuration validation
        """
        return {
            'algorithms': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'simple_perfect': {
                        'type': 'dict',
                        'schema': {
                            'enabled': {'type': 'boolean', 'default': True},
                            'max_attempts': {'type': 'integer', 'min': 1, 'default': 100}
                        }
                    },
                    'ultimate': {
                        'type': 'dict',
                        'schema': {
                            'enabled': {'type': 'boolean', 'default': True},
                            'max_backtrack': {'type': 'integer', 'min': 1, 'default': 4000},
                            'use_forward_checking': {'type': 'boolean', 'default': True}
                        }
                    },
                    'enhanced_strict': {
                        'type': 'dict',
                        'schema': {
                            'enabled': {'type': 'boolean', 'default': True},
                            'pressure_tracking': {'type': 'boolean', 'default': True},
                            'max_consecutive_lessons': {'type': 'integer', 'min': 1, 'max': 5, 'default': 3}
                        }
                    },
                    'hybrid_optimal': {
                        'type': 'dict',
                        'schema': {
                            'enabled': {'type': 'boolean', 'default': True},
                            'arc_consistency': {'type': 'boolean', 'default': True},
                            'soft_constraints_weight': {'type': 'float', 'min': 0.0, 'max': 1.0, 'default': 0.3},
                            'simulated_annealing': {
                                'type': 'dict',
                                'schema': {
                                    'enabled': {'type': 'boolean', 'default': True},
                                    'initial_temperature': {'type': 'float', 'min': 1.0, 'default': 100.0},
                                    'cooling_rate': {'type': 'float', 'min': 0.1, 'max': 0.99, 'default': 0.95}
                                }
                            }
                        }
                    },
                    'ultra_aggressive': {
                        'type': 'dict',
                        'schema': {
                            'enabled': {'type': 'boolean', 'default': True},
                            'max_iterations': {'type': 'integer', 'min': 1, 'default': 1000},
                            'relaxation_threshold': {'type': 'integer', 'min': 1, 'default': 100},
                            'aggressive_threshold': {'type': 'integer', 'min': 1, 'default': 50},
                            'final_validation': {'type': 'boolean', 'default': True}
                        }
                    }
                }
            },
            'performance': {
                'type': 'dict',
                'schema': {
                    'max_execution_time': {'type': 'integer', 'min': 1, 'default': 120},
                    'memory_limit': {'type': 'integer', 'min': 1, 'default': 500},
                    'enable_parallel_processing': {'type': 'boolean', 'default': False},
                    'thread_pool_size': {'type': 'integer', 'min': 1, 'max': 32, 'default': 4}
                }
            },
            'constraints': {
                'type': 'dict',
                'schema': {
                    'hard': {
                        'type': 'dict',
                        'schema': {
                            'no_class_conflicts': {'type': 'boolean', 'default': True},
                            'no_teacher_conflicts': {'type': 'boolean', 'default': True},
                            'respect_weekly_hours': {'type': 'boolean', 'default': True}
                        }
                    },
                    'soft': {
                        'type': 'dict',
                        'schema': {
                            'teacher_availability': {
                                'type': 'dict',
                                'schema': {
                                    'weight': {'type': 'float', 'min': 0.0, 'max': 1.0, 'default': 1.0},
                                    'relaxable_after_iterations': {'type': 'integer', 'min': 1, 'default': 100}
                                }
                            },
                            'consecutive_lessons': {
                                'type': 'dict',
                                'schema': {
                                    'weight': {'type': 'float', 'min': 0.0, 'max': 1.0, 'default': 0.8},
                                    'max_consecutive': {'type': 'integer', 'min': 1, 'default': 3}
                                }
                            },
                            'preferred_time_slots': {
                                'type': 'dict',
                                'schema': {
                                    'weight': {'type': 'float', 'min': 0.0, 'max': 1.0, 'default': 0.6},
                                    'morning_heavy_subjects': {'type': 'boolean', 'default': True}
                                }
                            },
                            'balanced_daily_load': {
                                'type': 'dict',
                                'schema': {
                                    'weight': {'type': 'float', 'min': 0.0, 'max': 1.0, 'default': 0.7},
                                    'target_variance': {'type': 'float', 'min': 0.1, 'default': 1.5}
                                }
                            }
                        }
                    }
                }
            },
            'blocks': {
                'type': 'dict',
                'schema': {
                    'enabled': {'type': 'boolean', 'default': True},
                    'preferred_sizes': {'type': 'list', 'schema': {'type': 'integer', 'min': 1, 'max': 5}, 'default': [2, 2, 2]},
                    'allow_single_hours': {'type': 'boolean', 'default': True},
                    'max_block_size': {'type': 'integer', 'min': 1, 'max': 5, 'default': 3}
                }
            },
            'logging': {
                'type': 'dict',
                'schema': {
                    'level': {'type': 'string', 'allowed': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 'default': 'INFO'},
                    'console': {'type': 'boolean', 'default': True},
                    'file': {'type': 'boolean', 'default': True},
                    'rotation': {
                        'type': 'dict',
                        'schema': {
                            'max_bytes': {'type': 'integer', 'min': 1024, 'default': 10485760},  # 10 MB
                            'backup_count': {'type': 'integer', 'min': 1, 'max': 10, 'default': 5}
                        }
                    }
                }
            },
            'ui': {
                'type': 'dict',
                'schema': {
                    'show_progress': {'type': 'boolean', 'default': True},
                    'update_interval': {'type': 'integer', 'min': 10, 'default': 100},
                    'show_statistics': {'type': 'boolean', 'default': True},
                    'conflict_warnings': {'type': 'boolean', 'default': True}
                }
            },
            'database': {
                'type': 'dict',
                'schema': {
                    'backup_before_generation': {'type': 'boolean', 'default': True},
                    'auto_save': {'type': 'boolean', 'default': True},
                    'transaction_mode': {'type': 'boolean', 'default': True}
                }
            },
            'validation': {
                'type': 'dict',
                'schema': {
                    'check_conflicts': {'type': 'boolean', 'default': True},
                    'auto_resolve_conflicts': {'type': 'boolean', 'default': True},
                    'max_conflict_resolution_attempts': {'type': 'integer', 'min': 1, 'default': 3}
                }
            },
            'coverage': {
                'type': 'dict',
                'schema': {
                    'target_percentage': {'type': 'float', 'min': 0.0, 'max': 100.0, 'default': 95.0},
                    'min_acceptable_percentage': {'type': 'float', 'min': 0.0, 'max': 100.0, 'default': 85.0},
                    'report_empty_slots': {'type': 'boolean', 'default': True}
                }
            },
            'development': {
                'type': 'dict',
                'schema': {
                    'enable_debug_mode': {'type': 'boolean', 'default': False},
                    'save_intermediate_results': {'type': 'boolean', 'default': False},
                    'profile_performance': {'type': 'boolean', 'default': False},
                    'generate_reports': {'type': 'boolean', 'default': True}
                }
            }
        }
    
    def validate_config_file(self, config_path: str) -> Dict[str, Any]:
        """
        Validates a configuration file and returns validation results
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Load the config file
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate against schema
            v = Validator(self.schema)
            is_valid = v.validate(config)
            
            result = {
                'valid': is_valid,
                'errors': v.errors if not is_valid else {},
                'config': config if is_valid else None,
                'warnings': []
            }
            
            if is_valid:
                # Check for additional logical constraints
                result['warnings'].extend(self._check_logical_constraints(config))
                self.logger.info(f"Configuration validation passed: {config_path}")
            else:
                self.logger.error(f"Configuration validation failed: {config_path}")
                for field, error in v.errors.items():
                    self.logger.error(f"Validation error in '{field}': {error}")
            
            return result
            
        except FileNotFoundError:
            error_msg = f"Configuration file not found: {config_path}"
            self.logger.error(error_msg)
            return {'valid': False, 'errors': {'file': error_msg}, 'config': None, 'warnings': []}
        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error in {config_path}: {str(e)}"
            self.logger.error(error_msg)
            return {'valid': False, 'errors': {'yaml': error_msg}, 'config': None, 'warnings': []}
        except Exception as e:
            error_msg = f"Unexpected error validating config {config_path}: {str(e)}"
            self.logger.error(error_msg)
            return {'valid': False, 'errors': {'unexpected': error_msg}, 'config': None, 'warnings': []}
    
    def _check_logical_constraints(self, config: Dict[str, Any]) -> List[str]:
        """
        Check for logical constraints that go beyond schema validation
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        # Check if performance values are reasonable
        perf = config.get('performance', {})
        max_time = perf.get('max_execution_time', 120)
        if max_time < 30:
            warnings.append(f"Max execution time ({max_time}s) may be too low for large schools")
        
        # Check if thread pool size is appropriate for available cores
        thread_pool = perf.get('thread_pool_size', 4)
        if thread_pool > 8:
            warnings.append(f"Thread pool size ({thread_pool}) may be too high, consider reducing for better performance")
        
        # Check if simulated annealing parameters are reasonable
        if config.get('algorithms', {}).get('hybrid_optimal', {}).get('simulated_annealing', {}).get('enabled', True):
            sa = config['algorithms']['hybrid_optimal']['simulated_annealing']
            if sa.get('cooling_rate', 0.95) > 0.99:
                warnings.append("Simulated annealing cooling rate is very high, may converge too quickly")
            if sa.get('cooling_rate', 0.95) < 0.5:
                warnings.append("Simulated annealing cooling rate is very low, may take too long to converge")
        
        # Check coverage thresholds
        coverage = config.get('coverage', {})
        target = coverage.get('target_percentage', 95.0)
        min_acceptable = coverage.get('min_acceptable_percentage', 85.0)
        if target < min_acceptable:
            warnings.append("Target coverage percentage is less than minimum acceptable percentage")
        
        return warnings
    
    def validate_config_dict(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates a configuration dictionary directly
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary with validation results
        """
        v = Validator(self.schema)
        is_valid = v.validate(config)
        
        result = {
            'valid': is_valid,
            'errors': v.errors if not is_valid else {},
            'config': config if is_valid else None,
            'warnings': []
        }
        
        if is_valid:
            result['warnings'].extend(self._check_logical_constraints(config))
        
        return result