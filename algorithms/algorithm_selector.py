# -*- coding: utf-8 -*-
"""
Automatic Algorithm Selector - Selects the optimal scheduler based on input characteristics
"""
from typing import Dict, Any, Type
from algorithms.base_scheduler import BaseScheduler
from algorithms.simple_perfect_scheduler import SimplePerfectScheduler
from algorithms.hybrid_optimal_scheduler import HybridOptimalScheduler
from algorithms.ultra_aggressive_scheduler import UltraAggressiveScheduler
from algorithms.ultimate_scheduler import UltimateScheduler
from algorithms.enhanced_strict_scheduler import EnhancedStrictScheduler
import logging

logger = logging.getLogger(__name__)


class AlgorithmSelector:
    """
    Automatically selects the best scheduling algorithm based on input characteristics.
    
    The selection is based on:
    - Number of classes
    - Number of teachers
    - Number of lessons
    - Required coverage percentage
    - Performance constraints
    """
    
    def __init__(self):
        self.algorithms = {
            'simple_perfect': SimplePerfectScheduler,
            'hybrid_optimal': HybridOptimalScheduler,
            'ultra_aggressive': UltraAggressiveScheduler,
            'ultimate': UltimateScheduler,
            'enhanced_strict': EnhancedStrictScheduler
        }
        
        # Performance characteristics for each algorithm
        self.algorithm_characteristics = {
            'simple_perfect': {
                'performance_score': 10,  # High performance
                'coverage_score': 8,      # Good coverage
                'reliability_score': 10,  # Very reliable
                'memory_usage': 'low',    # Low memory
                'suitable_for_small': True,
                'suitable_for_medium': True,
                'suitable_for_large': True,
            },
            'hybrid_optimal': {
                'performance_score': 7,
                'coverage_score': 10,
                'reliability_score': 9,
                'memory_usage': 'medium',
                'suitable_for_small': True,
                'suitable_for_medium': True,
                'suitable_for_large': False,
            },
            'ultra_aggressive': {
                'performance_score': 3,
                'coverage_score': 10,
                'reliability_score': 9,
                'memory_usage': 'high',
                'suitable_for_small': True,
                'suitable_for_medium': False,
                'suitable_for_large': False,
            },
            'ultimate': {
                'performance_score': 5,
                'coverage_score': 6,
                'reliability_score': 7,
                'memory_usage': 'high',
                'suitable_for_small': True,
                'suitable_for_medium': False,
                'suitable_for_large': False,
            },
            'enhanced_strict': {
                'performance_score': 8,
                'coverage_score': 6,
                'reliability_score': 7,
                'memory_usage': 'medium',
                'suitable_for_small': True,
                'suitable_for_medium': True,
                'suitable_for_large': True,
            }
        }

    def analyze_input(self, db_manager: Any) -> Dict[str, Any]:
        """
        Analyze input data to determine the best algorithm
        
        Args:
            db_manager: Database manager instance
            
        Returns:
            Dictionary with analysis results
        """
        classes = db_manager.get_all_classes()
        teachers = db_manager.get_all_teachers()
        lessons = db_manager.get_all_lessons()
        assignments = db_manager.get_schedule_by_school_type()
        
        analysis = {
            'num_classes': len(classes),
            'num_teachers': len(teachers),
            'num_lessons': len(lessons),
            'num_assignments': len(assignments),
            'teacher_to_class_ratio': len(teachers) / max(1, len(classes)),
            'lesson_to_class_density': len(lessons) / max(1, len(classes)),
            'assignment_density': len(assignments) / max(1, len(classes) * len(lessons))
        }
        
        logger.info(f"Input analysis: {analysis}")
        return analysis

    def calculate_priority_score(self, analysis: Dict, algorithm_name: str) -> float:
        """
        Calculate priority score for an algorithm based on input analysis
        
        Args:
            analysis: Input analysis results
            algorithm_name: Name of the algorithm to score
            
        Returns:
            Priority score (higher is better)
        """
        characteristics = self.algorithm_characteristics[algorithm_name]
        
        # Base score from characteristics
        base_score = (
            characteristics['performance_score'] * 0.3 +
            characteristics['coverage_score'] * 0.4 +
            characteristics['reliability_score'] * 0.3
        )
        
        # Size-based adjustments
        num_classes = analysis['num_classes']
        
        if num_classes <= 5:  # Small school
            if not characteristics['suitable_for_small']:
                base_score -= 10
        elif num_classes <= 15:  # Medium school
            if not characteristics['suitable_for_medium']:
                base_score -= 10
        else:  # Large school
            if not characteristics['suitable_for_large']:
                base_score -= 10
                
        # Memory usage penalty for resource-constrained environments
        if characteristics['memory_usage'] == 'high' and num_classes > 20:
            base_score -= 5
        elif characteristics['memory_usage'] == 'medium' and num_classes > 30:
            base_score -= 2
            
        # Density adjustments
        density = analysis['assignment_density']
        if algorithm_name == 'simple_perfect' and density > 0.8:
            # Simple perfect works better with lower density
            base_score += 2
        elif algorithm_name in ['ultra_aggressive', 'hybrid_optimal'] and density < 0.3:
            # Complex algorithms work better with higher density
            base_score += 1
            
        return base_score

    def select_best_algorithm(self, db_manager: Any) -> Type[BaseScheduler]:
        """
        Select the best algorithm based on input analysis
        
        Args:
            db_manager: Database manager instance
            
        Returns:
            Best algorithm class
        """
        analysis = self.analyze_input(db_manager)
        
        scores = {}
        for alg_name in self.algorithms:
            scores[alg_name] = self.calculate_priority_score(analysis, alg_name)
            
        logger.info(f"Algorithm scores: {scores}")
        
        # Select algorithm with highest score
        best_algorithm = max(scores, key=scores.get)
        
        logger.info(f"Selected algorithm: {best_algorithm} with score: {scores[best_algorithm]}")
        
        return self.algorithms[best_algorithm]
        
    def get_algorithm_recommendation(self, db_manager: Any) -> Dict[str, Any]:
        """
        Get detailed recommendation with reasoning
        
        Args:
            db_manager: Database manager instance
            
        Returns:
            Dictionary with recommendation details
        """
        analysis = self.analyze_input(db_manager)
        
        scores = {}
        for alg_name in self.algorithms:
            scores[alg_name] = self.calculate_priority_score(analysis, alg_name)
            
        best_algorithm = max(scores, key=scores.get)
        
        recommendation = {
            'best_algorithm': best_algorithm,
            'score': scores[best_algorithm],
            'analysis': analysis,
            'all_scores': scores,
            'reasoning': self._generate_reasoning(analysis, best_algorithm)
        }
        
        return recommendation
        
    def _generate_reasoning(self, analysis: Dict, best_algorithm: str) -> str:
        """
        Generate human-readable reasoning for the recommendation
        
        Args:
            analysis: Input analysis
            best_algorithm: Name of recommended algorithm
            
        Returns:
            Reasoning string
        """
        reasons = []
        
        if analysis['num_classes'] <= 5:
            reasons.append("School size: Small (≤5 classes)")
        elif analysis['num_classes'] <= 15:
            reasons.append("School size: Medium (6-15 classes)")
        else:
            reasons.append("School size: Large (>15 classes)")
            
        if analysis['assignment_density'] > 0.7:
            reasons.append("High assignment density (>70%)")
        elif analysis['assignment_density'] < 0.3:
            reasons.append("Low assignment density (<30%)")
        else:
            reasons.append("Medium assignment density (30-70%)")
            
        # Add algorithm-specific reasoning
        if best_algorithm == 'simple_perfect':
            reasons.append("Recommended for quick, reliable results")
        elif best_algorithm == 'hybrid_optimal':
            reasons.append("Recommended for optimal coverage-quality balance")
        elif best_algorithm == 'ultra_aggressive':
            reasons.append("Recommended for maximum coverage requirement")
        elif best_algorithm == 'ultimate':
            reasons.append("Recommended for CSP-based approach")
        elif best_algorithm == 'enhanced_strict':
            reasons.append("Recommended for strict constraint handling")
            
        return " | ".join(reasons)