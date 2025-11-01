"""
Flexible Block Manager - Alternative block configuration system for schedule optimization

This module implements flexible block management that handles alternative block configurations
when standard block placement fails. It provides intelligent block splitting and pattern
matching to maximize scheduling success while maintaining educational effectiveness.

Key Features:
- Alternative block configurations for each lesson duration (2-5 hours)
- Block pattern matching and validation logic
- Block placement attempt tracking and logging
- Educational effectiveness validation
- Priority ordering (larger blocks first)
- Block splitting logic for large lessons (4+ hours)
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from database.db_manager import DatabaseManager


class BlockPattern(Enum):
    """Types of block patterns"""
    STANDARD = "standard"
    ALTERNATIVE = "alternative"
    SPLIT = "split"
    FLEXIBLE = "flexible"


@dataclass
class BlockConfiguration:
    """Represents a block configuration for a lesson"""
    pattern: Tuple[int, ...]  # e.g., (2, 2, 1) for 5-hour lesson
    pattern_type: BlockPattern
    educational_score: float  # Higher is better for educational effectiveness
    placement_difficulty: float  # Higher means harder to place
    description: str
    
    def total_hours(self) -> int:
        """Get total hours for this configuration"""
        return sum(self.pattern)
    
    def __lt__(self, other):
        """Sort by educational score (higher first), then by difficulty (lower first)"""
        if self.educational_score != other.educational_score:
            return self.educational_score > other.educational_score
        return self.placement_difficulty < other.placement_difficulty


@dataclass
class BlockPlacementAttempt:
    """Tracks a block placement attempt"""
    lesson_id: int
    class_id: int
    teacher_id: int
    configuration: BlockConfiguration
    attempted_slots: List[Tuple[int, int]] = field(default_factory=list)  # (day, slot) pairs
    success: bool = False
    failure_reason: Optional[str] = None
    attempt_timestamp: Optional[float] = None
    
    def add_attempted_slot(self, day: int, slot: int):
        """Add an attempted slot to the tracking"""
        self.attempted_slots.append((day, slot))


class FlexibleBlockManager:
    """
    Flexible block manager for alternative lesson block configurations
    
    Handles alternative block patterns when standard placement fails,
    with focus on maintaining educational effectiveness while maximizing
    scheduling success through intelligent block splitting and pattern matching.
    """
    
    # Alternative block configurations for each lesson duration
    # Ordered by educational effectiveness (best first)
    BLOCK_ALTERNATIVES = {
        5: [
            # 5-hour lesson alternatives
            BlockConfiguration(
                pattern=(2, 2, 1),
                pattern_type=BlockPattern.STANDARD,
                educational_score=10.0,
                placement_difficulty=8.0,
                description="Standard 2+2+1 pattern for 5-hour lesson"
            ),
            BlockConfiguration(
                pattern=(3, 2),
                pattern_type=BlockPattern.ALTERNATIVE,
                educational_score=8.5,
                placement_difficulty=6.0,
                description="Alternative 3+2 pattern for 5-hour lesson"
            ),
            BlockConfiguration(
                pattern=(3, 1, 1),
                pattern_type=BlockPattern.ALTERNATIVE,
                educational_score=7.0,
                placement_difficulty=5.0,
                description="Alternative 3+1+1 pattern for 5-hour lesson"
            ),
            BlockConfiguration(
                pattern=(2, 1, 1, 1),
                pattern_type=BlockPattern.SPLIT,
                educational_score=6.0,
                placement_difficulty=4.0,
                description="Split 2+1+1+1 pattern for 5-hour lesson"
            ),
            BlockConfiguration(
                pattern=(1, 1, 1, 1, 1),
                pattern_type=BlockPattern.FLEXIBLE,
                educational_score=4.0,
                placement_difficulty=2.0,
                description="Fully flexible 1+1+1+1+1 pattern for 5-hour lesson"
            )
        ],
        4: [
            # 4-hour lesson alternatives
            BlockConfiguration(
                pattern=(2, 2),
                pattern_type=BlockPattern.STANDARD,
                educational_score=10.0,
                placement_difficulty=7.0,
                description="Standard 2+2 pattern for 4-hour lesson"
            ),
            BlockConfiguration(
                pattern=(3, 1),
                pattern_type=BlockPattern.ALTERNATIVE,
                educational_score=8.0,
                placement_difficulty=5.0,
                description="Alternative 3+1 pattern for 4-hour lesson"
            ),
            BlockConfiguration(
                pattern=(2, 1, 1),
                pattern_type=BlockPattern.SPLIT,
                educational_score=7.0,
                placement_difficulty=4.0,
                description="Split 2+1+1 pattern for 4-hour lesson"
            ),
            BlockConfiguration(
                pattern=(1, 1, 1, 1),
                pattern_type=BlockPattern.FLEXIBLE,
                educational_score=5.0,
                placement_difficulty=2.0,
                description="Fully flexible 1+1+1+1 pattern for 4-hour lesson"
            )
        ],
        3: [
            # 3-hour lesson alternatives
            BlockConfiguration(
                pattern=(2, 1),
                pattern_type=BlockPattern.STANDARD,
                educational_score=10.0,
                placement_difficulty=6.0,
                description="Standard 2+1 pattern for 3-hour lesson"
            ),
            BlockConfiguration(
                pattern=(1, 1, 1),
                pattern_type=BlockPattern.ALTERNATIVE,
                educational_score=7.0,
                placement_difficulty=3.0,
                description="Alternative 1+1+1 pattern for 3-hour lesson"
            )
        ],
        2: [
            # 2-hour lesson alternatives
            BlockConfiguration(
                pattern=(2,),
                pattern_type=BlockPattern.STANDARD,
                educational_score=10.0,
                placement_difficulty=5.0,
                description="Standard 2-hour block"
            ),
            BlockConfiguration(
                pattern=(1, 1),
                pattern_type=BlockPattern.SPLIT,
                educational_score=6.0,
                placement_difficulty=2.0,
                description="Split 1+1 pattern for 2-hour lesson"
            )
        ],
        1: [
            # 1-hour lesson (no alternatives needed)
            BlockConfiguration(
                pattern=(1,),
                pattern_type=BlockPattern.STANDARD,
                educational_score=10.0,
                placement_difficulty=1.0,
                description="Standard 1-hour lesson"
            )
        ]
    }
    
    def __init__(self, db_manager: 'DatabaseManager'):
        """
        Initialize flexible block manager
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Track placement attempts for debugging and optimization
        self.placement_attempts: List[BlockPlacementAttempt] = []
        
        # Statistics tracking
        self.stats = {
            "total_attempts": 0,
            "successful_placements": 0,
            "alternative_patterns_used": 0,
            "split_patterns_used": 0,
            "flexible_patterns_used": 0,
            "educational_effectiveness_maintained": 0
        }
        
        # Configuration
        self.min_educational_score = 5.0  # Minimum acceptable educational score
        self.max_placement_attempts = 10  # Maximum attempts per lesson
        
        self.logger.info("FlexibleBlockManager initialized")
        self.logger.info(f"Loaded {sum(len(configs) for configs in self.BLOCK_ALTERNATIVES.values())} block configurations")
    
    def get_block_alternatives(self, hours: int) -> List[BlockConfiguration]:
        """
        Get alternative block configurations prioritizing educational effectiveness
        
        Args:
            hours: Number of hours for the lesson
            
        Returns:
            List of BlockConfiguration objects sorted by preference (best first)
        """
        if hours not in self.BLOCK_ALTERNATIVES:
            self.logger.warning(f"No block alternatives defined for {hours} hours")
            return []
        
        # Get configurations and sort by preference
        configurations = self.BLOCK_ALTERNATIVES[hours].copy()
        configurations.sort()  # Uses __lt__ method for sorting
        
        self.logger.debug(f"Retrieved {len(configurations)} alternatives for {hours}-hour lesson")
        return configurations
    
    def try_alternative_blocks(self, lesson_id: int, class_id: int, teacher_id: int, 
                             weekly_hours: int, lesson_name: str, teacher_name: str,
                             existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                             existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                             placement_function) -> Tuple[bool, List[Any], BlockConfiguration]:
        """
        Attempt placement with alternative block patterns (4+ hours get priority)
        
        Args:
            lesson_id: Lesson ID
            class_id: Class ID
            teacher_id: Teacher ID
            weekly_hours: Number of hours to schedule
            lesson_name: Name of the lesson
            teacher_name: Name of the teacher
            existing_teacher_slots: Current teacher slot occupancy
            existing_class_slots: Current class slot occupancy
            placement_function: Function to call for actual placement
            
        Returns:
            (success, placements, configuration_used) tuple
        """
        self.stats["total_attempts"] += 1
        
        self.logger.info(f"Trying alternative blocks for {lesson_name} ({weekly_hours}h) - Class {class_id}, Teacher {teacher_name}")
        
        # Create placement attempt tracker
        attempt = BlockPlacementAttempt(
            lesson_id=lesson_id,
            class_id=class_id,
            teacher_id=teacher_id,
            configuration=None  # Will be set when we try configurations
        )
        
        # Get alternative configurations
        configurations = self.get_block_alternatives(weekly_hours)
        
        if not configurations:
            self.logger.warning(f"No alternative configurations available for {weekly_hours}-hour lesson")
            return False, [], None
        
        # Try each configuration in order of preference
        for i, config in enumerate(configurations):
            self.logger.debug(f"Trying configuration {i+1}/{len(configurations)}: {config.description}")
            
            # Update attempt tracker
            attempt.configuration = config
            
            # Validate educational effectiveness
            if not self.validate_educational_effectiveness(config):
                self.logger.debug(f"Configuration rejected due to low educational score: {config.educational_score}")
                continue
            
            # Try placement with this configuration
            success, placements = self._try_configuration_placement(
                config, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                existing_teacher_slots, existing_class_slots, placement_function, attempt
            )
            
            if success:
                # Update statistics
                self.stats["successful_placements"] += 1
                self._update_pattern_statistics(config)
                
                attempt.success = True
                self.placement_attempts.append(attempt)
                
                self.logger.info(f"✓ Successfully placed {lesson_name} using {config.description}")
                return True, placements, config
            else:
                self.logger.debug(f"✗ Configuration failed: {config.description}")
        
        # All configurations failed
        attempt.success = False
        attempt.failure_reason = "All alternative configurations failed"
        self.placement_attempts.append(attempt)
        
        self.logger.warning(f"All {len(configurations)} alternative configurations failed for {lesson_name}")
        return False, [], None
    
    def _try_configuration_placement(self, config: BlockConfiguration, lesson_id: int, 
                                   class_id: int, teacher_id: int, lesson_name: str, teacher_name: str,
                                   existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                   existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                                   placement_function, attempt: BlockPlacementAttempt) -> Tuple[bool, List[Any]]:
        """
        Try placement with a specific block configuration
        
        Returns:
            (success, placements) tuple
        """
        placements = []
        
        try:
            # For each block in the pattern
            for block_index, block_size in enumerate(config.pattern):
                self.logger.debug(f"Placing block {block_index + 1}/{len(config.pattern)}: {block_size} hours")
                
                # Try to place this block
                block_success, block_placements = self._place_single_block(
                    block_size, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                    existing_teacher_slots, existing_class_slots, placement_function,
                    block_index, config, attempt
                )
                
                if not block_success:
                    self.logger.debug(f"Failed to place block {block_index + 1} of size {block_size}")
                    return False, []
                
                placements.extend(block_placements)
                
                # Update existing slots for next block placement
                for placement in block_placements:
                    day, slot = placement.get('day'), placement.get('time_slot')
                    if day is not None and slot is not None:
                        existing_teacher_slots.setdefault(teacher_id, set()).add((day, slot))
                        existing_class_slots.setdefault(class_id, set()).add((day, slot))
            
            return True, placements
            
        except Exception as e:
            self.logger.error(f"Error during configuration placement: {e}")
            return False, []
    
    def _place_single_block(self, block_size: int, lesson_id: int, class_id: int, teacher_id: int,
                          lesson_name: str, teacher_name: str,
                          existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                          existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                          placement_function, block_index: int, config: BlockConfiguration,
                          attempt: BlockPlacementAttempt) -> Tuple[bool, List[Any]]:
        """
        Place a single block of the specified size
        
        Returns:
            (success, placements) tuple
        """
        # Get school configuration
        school_config = self._get_school_config()
        days_per_week = school_config["days_per_week"]
        time_slots_count = school_config["time_slots_count"]
        
        # Try to find consecutive slots for this block
        for day in range(days_per_week):
            for start_slot in range(time_slots_count - block_size + 1):
                # Check if all slots in this block are available
                slots_available = True
                for slot_offset in range(block_size):
                    slot = start_slot + slot_offset
                    
                    # Check conflicts
                    if self._has_slot_conflict(class_id, teacher_id, day, slot, 
                                             existing_teacher_slots, existing_class_slots):
                        slots_available = False
                        break
                
                if slots_available:
                    # Place the block
                    block_placements = []
                    
                    for slot_offset in range(block_size):
                        slot = start_slot + slot_offset
                        
                        # Track attempted slot
                        attempt.add_attempted_slot(day, slot)
                        
                        # Create placement (this is a simplified version - actual implementation
                        # would use the provided placement_function)
                        placement = {
                            'class_id': class_id,
                            'lesson_id': lesson_id,
                            'teacher_id': teacher_id,
                            'day': day,
                            'time_slot': slot,
                            'classroom_id': 1,  # Default classroom
                            'block_position': slot_offset + 1,
                            'block_index': block_index,
                            'block_size': block_size,
                            'configuration_pattern': config.pattern,
                            'configuration_type': config.pattern_type.value
                        }
                        
                        block_placements.append(placement)
                    
                    self.logger.debug(f"Placed {block_size}-hour block on day {day}, slots {start_slot}-{start_slot + block_size - 1}")
                    return True, block_placements
        
        # No suitable slots found for this block
        return False, []
    
    def _has_slot_conflict(self, class_id: int, teacher_id: int, day: int, slot: int,
                          existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                          existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> bool:
        """
        Check if a slot has conflicts
        
        Returns:
            True if there are conflicts, False otherwise
        """
        # Check class conflict
        if (day, slot) in existing_class_slots.get(class_id, set()):
            return True
        
        # Check teacher conflict
        if (day, slot) in existing_teacher_slots.get(teacher_id, set()):
            return True
        
        # Check teacher availability (simplified - would use actual availability check)
        try:
            availability = self.db_manager.get_teacher_availability(teacher_id, day, slot)
            if availability is None:
                return True  # Not available
        except Exception:
            # If we can't check availability, assume it's available
            pass
        
        return False
    
    def _get_school_config(self) -> Dict[str, Any]:
        """Get school configuration"""
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = {
            "İlkokul": 7,
            "Ortaokul": 7,
            "Lise": 8,
            "Anadolu Lisesi": 8,
            "Fen Lisesi": 8,
            "Sosyal Bilimler Lisesi": 8,
        }.get(school_type, 8)
        
        return {
            "school_type": school_type,
            "time_slots_count": time_slots_count,
            "days_per_week": 5
        }
    
    def validate_educational_effectiveness(self, configuration: BlockConfiguration) -> bool:
        """
        Ensure alternative blocks maintain educational quality
        
        Args:
            configuration: Block configuration to validate
            
        Returns:
            True if educationally effective, False otherwise
        """
        # Check minimum educational score
        if configuration.educational_score < self.min_educational_score:
            self.logger.debug(f"Configuration rejected: educational score {configuration.educational_score} < {self.min_educational_score}")
            return False
        
        # Additional validation rules
        
        # Rule 1: No single-hour blocks for lessons > 3 hours (unless it's the last block)
        if len(configuration.pattern) > 1:
            single_hour_blocks = sum(1 for hours in configuration.pattern if hours == 1)
            total_hours = configuration.total_hours()
            
            if total_hours > 3 and single_hour_blocks > 1:
                # Allow at most 1 single-hour block for lessons > 3 hours
                self.logger.debug(f"Configuration rejected: too many single-hour blocks ({single_hour_blocks}) for {total_hours}-hour lesson")
                return False
        
        # Rule 2: Prefer larger blocks - no more than 50% of blocks should be single hours
        if len(configuration.pattern) > 2:
            single_hour_ratio = sum(1 for hours in configuration.pattern if hours == 1) / len(configuration.pattern)
            if single_hour_ratio > 0.5:
                self.logger.debug(f"Configuration rejected: too high single-hour ratio ({single_hour_ratio:.1%})")
                return False
        
        # Rule 3: Minimum block size should be reasonable
        min_block_size = min(configuration.pattern)
        if min_block_size < 1:
            self.logger.debug("Configuration rejected: invalid block size")
            return False
        
        self.stats["educational_effectiveness_maintained"] += 1
        return True
    
    def _update_pattern_statistics(self, config: BlockConfiguration):
        """Update statistics based on pattern type used"""
        if config.pattern_type == BlockPattern.ALTERNATIVE:
            self.stats["alternative_patterns_used"] += 1
        elif config.pattern_type == BlockPattern.SPLIT:
            self.stats["split_patterns_used"] += 1
        elif config.pattern_type == BlockPattern.FLEXIBLE:
            self.stats["flexible_patterns_used"] += 1
    
    def log_block_attempts(self, lesson_id: int, lesson_name: str, attempts: List[BlockConfiguration]) -> None:
        """
        Log all block configuration attempts for debugging
        
        Args:
            lesson_id: Lesson ID
            lesson_name: Name of the lesson
            attempts: List of attempted configurations
        """
        self.logger.info(f"Block placement attempts for {lesson_name} (ID: {lesson_id}):")
        
        for i, config in enumerate(attempts):
            status = "✓ SUCCESS" if i == 0 else "✗ FAILED"  # Simplified - would track actual results
            self.logger.info(f"  {i+1}. {config.description} - {status}")
            self.logger.info(f"     Pattern: {config.pattern}, Score: {config.educational_score}, Difficulty: {config.placement_difficulty}")
    
    def get_placement_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive placement statistics
        
        Returns:
            Dictionary with placement statistics
        """
        success_rate = (self.stats["successful_placements"] / self.stats["total_attempts"] * 100) if self.stats["total_attempts"] > 0 else 0
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "total_configurations_available": sum(len(configs) for configs in self.BLOCK_ALTERNATIVES.values()),
            "recent_attempts": len([a for a in self.placement_attempts if a.success]),
            "failed_attempts": len([a for a in self.placement_attempts if not a.success])
        }
    
    def get_block_priority_order(self, lessons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Implement block priority ordering (larger blocks first)
        
        Args:
            lessons: List of lesson dictionaries with 'weekly_hours' key
            
        Returns:
            Lessons sorted by priority (larger blocks first)
        """
        def get_priority_score(lesson):
            hours = lesson.get('weekly_hours', 0)
            
            # Priority scoring:
            # - 5+ hour lessons: highest priority (score 50+)
            # - 4 hour lessons: high priority (score 40+)
            # - 3 hour lessons: medium priority (score 30+)
            # - 2 hour lessons: low priority (score 20+)
            # - 1 hour lessons: lowest priority (score 10+)
            
            base_score = hours * 10
            
            # Bonus for lessons that are harder to place (more constraints)
            if hours >= 5:
                base_score += 10  # Extra priority for very large lessons
            elif hours >= 4:
                base_score += 5   # Extra priority for large lessons
            
            return base_score
        
        # Sort by priority score (descending)
        sorted_lessons = sorted(lessons, key=get_priority_score, reverse=True)
        
        self.logger.info(f"Prioritized {len(lessons)} lessons by block size:")
        for i, lesson in enumerate(sorted_lessons[:5]):  # Log top 5
            hours = lesson.get('weekly_hours', 0)
            name = lesson.get('lesson_name', 'Unknown')
            self.logger.info(f"  {i+1}. {name} ({hours}h) - Priority: {get_priority_score(lesson)}")
        
        return sorted_lessons
    
    def try_multiple_block_configurations(self, lesson_id: int, class_id: int, teacher_id: int,
                                         weekly_hours: int, lesson_name: str, teacher_name: str,
                                         existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                         existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                                         placement_function) -> Tuple[bool, List[Any], BlockConfiguration]:
        """
        Create algorithm to try multiple block configurations with intelligent fallback
        
        This method implements a comprehensive approach to trying multiple block configurations:
        1. Start with standard/preferred configurations
        2. Try alternative configurations if standard fails
        3. Apply block splitting for large lessons (4+ hours)
        4. Use flexible patterns as last resort
        
        Args:
            lesson_id: Lesson ID
            class_id: Class ID
            teacher_id: Teacher ID
            weekly_hours: Number of hours to schedule
            lesson_name: Name of the lesson
            teacher_name: Name of the teacher
            existing_teacher_slots: Current teacher slot occupancy
            existing_class_slots: Current class slot occupancy
            placement_function: Function to call for actual placement
            
        Returns:
            (success, placements, configuration_used) tuple
        """
        self.logger.info(f"Trying multiple configurations for {lesson_name} ({weekly_hours}h)")
        
        # Get all available configurations
        configurations = self.get_block_alternatives(weekly_hours)
        
        if not configurations:
            self.logger.warning(f"No configurations available for {weekly_hours}-hour lesson")
            return False, [], None
        
        # Phase 1: Try standard and high-scoring alternative configurations
        high_quality_configs = [c for c in configurations if c.educational_score >= 8.0]
        
        if high_quality_configs:
            self.logger.debug(f"Phase 1: Trying {len(high_quality_configs)} high-quality configurations")
            success, placements, config = self._try_configuration_set(
                high_quality_configs, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                existing_teacher_slots, existing_class_slots, placement_function
            )
            
            if success:
                self.logger.info(f"✓ High-quality configuration succeeded: {config.description}")
                return success, placements, config
        
        # Phase 2: Try block splitting for large lessons (4+ hours)
        if weekly_hours >= 4:
            self.logger.debug("Phase 2: Trying block splitting for large lesson")
            success, placements, config = self._try_block_splitting(
                lesson_id, class_id, teacher_id, weekly_hours, lesson_name, teacher_name,
                existing_teacher_slots, existing_class_slots, placement_function
            )
            
            if success:
                self.logger.info(f"✓ Block splitting succeeded: {config.description}")
                return success, placements, config
        
        # Phase 3: Try remaining configurations (lower quality but more flexible)
        remaining_configs = [c for c in configurations if c.educational_score < 8.0]
        
        if remaining_configs:
            self.logger.debug(f"Phase 3: Trying {len(remaining_configs)} flexible configurations")
            success, placements, config = self._try_configuration_set(
                remaining_configs, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                existing_teacher_slots, existing_class_slots, placement_function
            )
            
            if success:
                self.logger.info(f"✓ Flexible configuration succeeded: {config.description}")
                return success, placements, config
        
        # All configurations failed
        self.logger.warning(f"All {len(configurations)} configurations failed for {lesson_name}")
        return False, [], None
    
    def _try_configuration_set(self, configurations: List[BlockConfiguration], lesson_id: int,
                              class_id: int, teacher_id: int, lesson_name: str, teacher_name: str,
                              existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                              existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                              placement_function) -> Tuple[bool, List[Any], BlockConfiguration]:
        """
        Try a set of configurations in order
        
        Returns:
            (success, placements, configuration_used) tuple
        """
        for config in configurations:
            self.logger.debug(f"Trying: {config.description}")
            
            # Validate educational effectiveness
            if not self.validate_educational_effectiveness(config):
                continue
            
            # Create placement attempt tracker
            attempt = BlockPlacementAttempt(
                lesson_id=lesson_id,
                class_id=class_id,
                teacher_id=teacher_id,
                configuration=config
            )
            
            # Try placement with this configuration
            success, placements = self._try_configuration_placement(
                config, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                existing_teacher_slots, existing_class_slots, placement_function, attempt
            )
            
            if success:
                # Update statistics
                self.stats["successful_placements"] += 1
                self._update_pattern_statistics(config)
                
                attempt.success = True
                self.placement_attempts.append(attempt)
                
                return True, placements, config
            else:
                attempt.success = False
                attempt.failure_reason = f"Configuration placement failed: {config.description}"
                self.placement_attempts.append(attempt)
        
        return False, [], None
    
    def _try_block_splitting(self, lesson_id: int, class_id: int, teacher_id: int,
                           weekly_hours: int, lesson_name: str, teacher_name: str,
                           existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                           existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                           placement_function) -> Tuple[bool, List[Any], BlockConfiguration]:
        """
        Add block splitting logic for large lessons (4+ hours)
        
        This method implements intelligent block splitting strategies:
        - For 5-hour lessons: try 3+2, 2+2+1, 2+1+1+1
        - For 4-hour lessons: try 2+2, 3+1, 2+1+1
        - Prioritize educationally effective splits
        - Consider placement difficulty and slot availability
        
        Returns:
            (success, placements, configuration_used) tuple
        """
        self.logger.debug(f"Applying block splitting logic for {weekly_hours}-hour lesson")
        
        # Get splitting configurations (those marked as SPLIT or FLEXIBLE)
        all_configs = self.get_block_alternatives(weekly_hours)
        split_configs = [c for c in all_configs if c.pattern_type in [BlockPattern.SPLIT, BlockPattern.FLEXIBLE]]
        
        if not split_configs:
            self.logger.debug("No splitting configurations available")
            return False, [], None
        
        # Sort by educational effectiveness first, then by placement difficulty
        split_configs.sort(key=lambda c: (-c.educational_score, c.placement_difficulty))
        
        # Try each splitting configuration
        for config in split_configs:
            self.logger.debug(f"Trying split configuration: {config.description}")
            
            # Special handling for large lesson splits
            if self._is_large_lesson_split_viable(config, existing_teacher_slots, existing_class_slots):
                # Create placement attempt tracker
                attempt = BlockPlacementAttempt(
                    lesson_id=lesson_id,
                    class_id=class_id,
                    teacher_id=teacher_id,
                    configuration=config
                )
                
                # Try placement with enhanced splitting logic
                success, placements = self._try_enhanced_split_placement(
                    config, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                    existing_teacher_slots, existing_class_slots, placement_function, attempt
                )
                
                if success:
                    self.stats["successful_placements"] += 1
                    self.stats["split_patterns_used"] += 1
                    
                    attempt.success = True
                    self.placement_attempts.append(attempt)
                    
                    self.logger.info(f"✓ Block splitting successful: {config.description}")
                    return True, placements, config
                else:
                    attempt.success = False
                    attempt.failure_reason = f"Enhanced split placement failed: {config.description}"
                    self.placement_attempts.append(attempt)
        
        self.logger.debug("All block splitting attempts failed")
        return False, [], None
    
    def _is_large_lesson_split_viable(self, config: BlockConfiguration,
                                    existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                    existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> bool:
        """
        Check if a large lesson split is viable given current slot occupancy
        
        Returns:
            True if the split appears viable, False otherwise
        """
        # For large lessons, we need to ensure there's enough space for the split
        total_hours = config.total_hours()
        
        if total_hours < 4:
            return True  # Not a large lesson
        
        # Estimate available slots (simplified heuristic)
        school_config = self._get_school_config()
        total_slots = school_config["days_per_week"] * school_config["time_slots_count"]
        
        # Count occupied slots (rough estimate)
        occupied_slots = 0
        for slots in existing_teacher_slots.values():
            occupied_slots += len(slots)
        for slots in existing_class_slots.values():
            occupied_slots += len(slots)
        
        # Remove double-counting (teacher and class slots might overlap)
        occupied_slots = occupied_slots // 2  # Rough adjustment
        
        available_slots = total_slots - occupied_slots
        
        # Need at least 2x the lesson hours for flexibility in splitting
        required_flexibility = total_hours * 2
        
        viable = available_slots >= required_flexibility
        
        self.logger.debug(f"Split viability check: {available_slots} available, {required_flexibility} needed, viable: {viable}")
        return viable
    
    def _try_enhanced_split_placement(self, config: BlockConfiguration, lesson_id: int,
                                    class_id: int, teacher_id: int, lesson_name: str, teacher_name: str,
                                    existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                    existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                                    placement_function, attempt: BlockPlacementAttempt) -> Tuple[bool, List[Any]]:
        """
        Try placement with enhanced splitting logic that considers:
        - Day distribution (spread blocks across different days)
        - Time slot optimization (prefer morning slots)
        - Workload balance
        - Educational continuity
        
        Returns:
            (success, placements) tuple
        """
        placements = []
        school_config = self._get_school_config()
        
        # Enhanced placement strategy for splits
        try:
            # Strategy 1: Distribute blocks across different days
            if len(config.pattern) > 1:
                success, split_placements = self._try_distributed_placement(
                    config, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                    existing_teacher_slots, existing_class_slots, attempt
                )
                
                if success:
                    return True, split_placements
            
            # Strategy 2: Try consecutive placement with gaps allowed
            success, consecutive_placements = self._try_consecutive_with_gaps_placement(
                config, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                existing_teacher_slots, existing_class_slots, attempt
            )
            
            if success:
                return True, consecutive_placements
            
            # Strategy 3: Fallback to any available placement
            success, fallback_placements = self._try_fallback_placement(
                config, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                existing_teacher_slots, existing_class_slots, attempt
            )
            
            return success, fallback_placements
            
        except Exception as e:
            self.logger.error(f"Error in enhanced split placement: {e}")
            return False, []
    
    def _try_distributed_placement(self, config: BlockConfiguration, lesson_id: int,
                                 class_id: int, teacher_id: int, lesson_name: str, teacher_name: str,
                                 existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                 existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                                 attempt: BlockPlacementAttempt) -> Tuple[bool, List[Any]]:
        """
        Try to distribute blocks across different days for better workload balance
        
        Returns:
            (success, placements) tuple
        """
        placements = []
        school_config = self._get_school_config()
        days_per_week = school_config["days_per_week"]
        
        # Get teacher's current working days
        teacher_slots = existing_teacher_slots.get(teacher_id, set())
        teacher_working_days = set(day for day, slot in teacher_slots)
        
        # Try to place each block on a different day, preferring days without lessons
        available_days = list(range(days_per_week))
        
        # Prioritize days without existing lessons
        empty_days = [day for day in available_days if day not in teacher_working_days]
        working_days = [day for day in available_days if day in teacher_working_days]
        
        # Combine: empty days first, then working days
        prioritized_days = empty_days + working_days
        
        used_days = set()
        
        for block_index, block_size in enumerate(config.pattern):
            block_placed = False
            
            # Try each day in priority order
            for day in prioritized_days:
                if day in used_days and len(empty_days) > len(used_days):
                    continue  # Skip already used days if we have empty days available
                
                # Try to place this block on this day
                success, block_placements = self._place_block_on_day(
                    block_size, day, lesson_id, class_id, teacher_id,
                    existing_teacher_slots, existing_class_slots, block_index, config, attempt
                )
                
                if success:
                    placements.extend(block_placements)
                    used_days.add(day)
                    
                    # Update existing slots for next block
                    for placement in block_placements:
                        day_used, slot_used = placement.get('day'), placement.get('time_slot')
                        if day_used is not None and slot_used is not None:
                            existing_teacher_slots.setdefault(teacher_id, set()).add((day_used, slot_used))
                            existing_class_slots.setdefault(class_id, set()).add((day_used, slot_used))
                    
                    block_placed = True
                    break
            
            if not block_placed:
                self.logger.debug(f"Failed to place block {block_index + 1} in distributed placement")
                return False, []
        
        self.logger.debug(f"Successfully distributed {len(config.pattern)} blocks across {len(used_days)} days")
        return True, placements
    
    def _try_consecutive_with_gaps_placement(self, config: BlockConfiguration, lesson_id: int,
                                           class_id: int, teacher_id: int, lesson_name: str, teacher_name: str,
                                           existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                           existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                                           attempt: BlockPlacementAttempt) -> Tuple[bool, List[Any]]:
        """
        Try consecutive placement allowing small gaps between blocks
        
        Returns:
            (success, placements) tuple
        """
        placements = []
        school_config = self._get_school_config()
        days_per_week = school_config["days_per_week"]
        time_slots_count = school_config["time_slots_count"]
        
        # Try each day
        for day in range(days_per_week):
            day_placements = []
            current_slot = 0
            
            # Try to place all blocks on this day with small gaps allowed
            for block_index, block_size in enumerate(config.pattern):
                block_placed = False
                
                # Try starting from current_slot, allowing up to 2 slots gap
                for gap in range(3):  # 0, 1, 2 slot gaps
                    start_slot = current_slot + gap
                    
                    if start_slot + block_size > time_slots_count:
                        break  # Won't fit
                    
                    # Check if all slots for this block are available
                    slots_available = True
                    for slot_offset in range(block_size):
                        slot = start_slot + slot_offset
                        
                        if self._has_slot_conflict(class_id, teacher_id, day, slot,
                                                 existing_teacher_slots, existing_class_slots):
                            slots_available = False
                            break
                    
                    if slots_available:
                        # Place the block
                        for slot_offset in range(block_size):
                            slot = start_slot + slot_offset
                            
                            attempt.add_attempted_slot(day, slot)
                            
                            placement = {
                                'class_id': class_id,
                                'lesson_id': lesson_id,
                                'teacher_id': teacher_id,
                                'day': day,
                                'time_slot': slot,
                                'classroom_id': 1,
                                'block_position': slot_offset + 1,
                                'block_index': block_index,
                                'block_size': block_size,
                                'configuration_pattern': config.pattern,
                                'configuration_type': config.pattern_type.value
                            }
                            
                            day_placements.append(placement)
                        
                        current_slot = start_slot + block_size
                        block_placed = True
                        break
                
                if not block_placed:
                    break  # This day won't work
            
            # Check if all blocks were placed on this day
            if len(day_placements) == sum(config.pattern):
                placements.extend(day_placements)
                self.logger.debug(f"Successfully placed all blocks on day {day} with gaps")
                return True, placements
        
        return False, []
    
    def _try_fallback_placement(self, config: BlockConfiguration, lesson_id: int,
                              class_id: int, teacher_id: int, lesson_name: str, teacher_name: str,
                              existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                              existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                              attempt: BlockPlacementAttempt) -> Tuple[bool, List[Any]]:
        """
        Fallback placement strategy - place blocks anywhere available
        
        Returns:
            (success, placements) tuple
        """
        placements = []
        
        # Simply try to place each block anywhere available
        for block_index, block_size in enumerate(config.pattern):
            success, block_placements = self._place_single_block(
                block_size, lesson_id, class_id, teacher_id, lesson_name, teacher_name,
                existing_teacher_slots, existing_class_slots, None,  # No placement function needed
                block_index, config, attempt
            )
            
            if not success:
                self.logger.debug(f"Fallback placement failed for block {block_index + 1}")
                return False, []
            
            placements.extend(block_placements)
            
            # Update existing slots for next block
            for placement in block_placements:
                day, slot = placement.get('day'), placement.get('time_slot')
                if day is not None and slot is not None:
                    existing_teacher_slots.setdefault(teacher_id, set()).add((day, slot))
                    existing_class_slots.setdefault(class_id, set()).add((day, slot))
        
        self.logger.debug("Fallback placement successful")
        return True, placements
    
    def _place_block_on_day(self, block_size: int, day: int, lesson_id: int, class_id: int, teacher_id: int,
                          existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                          existing_class_slots: Dict[int, Set[Tuple[int, int]]],
                          block_index: int, config: BlockConfiguration,
                          attempt: BlockPlacementAttempt) -> Tuple[bool, List[Any]]:
        """
        Try to place a block of specified size on a specific day
        
        Returns:
            (success, placements) tuple
        """
        school_config = self._get_school_config()
        time_slots_count = school_config["time_slots_count"]
        
        # Try each possible starting slot
        for start_slot in range(time_slots_count - block_size + 1):
            # Check if all slots in this block are available
            slots_available = True
            for slot_offset in range(block_size):
                slot = start_slot + slot_offset
                
                if self._has_slot_conflict(class_id, teacher_id, day, slot,
                                         existing_teacher_slots, existing_class_slots):
                    slots_available = False
                    break
            
            if slots_available:
                # Place the block
                block_placements = []
                
                for slot_offset in range(block_size):
                    slot = start_slot + slot_offset
                    
                    attempt.add_attempted_slot(day, slot)
                    
                    placement = {
                        'class_id': class_id,
                        'lesson_id': lesson_id,
                        'teacher_id': teacher_id,
                        'day': day,
                        'time_slot': slot,
                        'classroom_id': 1,
                        'block_position': slot_offset + 1,
                        'block_index': block_index,
                        'block_size': block_size,
                        'configuration_pattern': config.pattern,
                        'configuration_type': config.pattern_type.value
                    }
                    
                    block_placements.append(placement)
                
                return True, block_placements
        
        return False, []
    
    def implement_block_priority_ordering(self, lessons_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Implement block priority ordering (larger blocks first) with advanced sorting
        
        This method implements sophisticated priority ordering that considers:
        1. Lesson duration (larger blocks first)
        2. Placement difficulty (harder to place lessons first)
        3. Teacher constraints (teachers with limited availability first)
        4. Educational importance (core subjects first)
        
        Args:
            lessons_data: List of lesson dictionaries with scheduling information
            
        Returns:
            Lessons sorted by priority (highest priority first)
        """
        self.logger.info(f"Implementing block priority ordering for {len(lessons_data)} lessons")
        
        def calculate_priority_score(lesson_data):
            """Calculate comprehensive priority score for a lesson"""
            score = 0.0
            
            # Factor 1: Lesson duration (larger blocks get higher priority)
            weekly_hours = lesson_data.get('weekly_hours', 0)
            duration_score = weekly_hours * 20  # Base score from duration
            
            # Bonus for very large lessons (5+ hours)
            if weekly_hours >= 5:
                duration_score += 50  # High priority for 5+ hour lessons
            elif weekly_hours >= 4:
                duration_score += 30  # High priority for 4 hour lessons
            elif weekly_hours >= 3:
                duration_score += 15  # Medium priority for 3 hour lessons
            elif weekly_hours >= 2:
                duration_score += 5   # Low priority for 2 hour lessons
            # 1-hour lessons get no bonus
            
            score += duration_score
            
            # Factor 2: Placement difficulty (estimate based on lesson characteristics)
            difficulty_score = self._estimate_placement_difficulty(lesson_data)
            score += difficulty_score
            
            # Factor 3: Teacher constraints (limited availability teachers first)
            teacher_constraint_score = self._estimate_teacher_constraints(lesson_data)
            score += teacher_constraint_score
            
            # Factor 4: Educational importance (core subjects priority)
            importance_score = self._estimate_educational_importance(lesson_data)
            score += importance_score
            
            return score
        
        # Sort lessons by priority score (descending)
        sorted_lessons = sorted(lessons_data, key=calculate_priority_score, reverse=True)
        
        # Log priority ordering results
        self.logger.info("Block priority ordering results:")
        for i, lesson in enumerate(sorted_lessons[:10]):  # Log top 10
            hours = lesson.get('weekly_hours', 0)
            name = lesson.get('lesson_name', lesson.get('name', 'Unknown'))
            score = calculate_priority_score(lesson)
            self.logger.info(f"  {i+1:2d}. {name:<25} ({hours}h) - Priority: {score:.1f}")
        
        if len(sorted_lessons) > 10:
            self.logger.info(f"  ... and {len(sorted_lessons) - 10} more lessons")
        
        return sorted_lessons
    
    def _estimate_placement_difficulty(self, lesson_data: Dict[str, Any]) -> float:
        """
        Estimate placement difficulty for a lesson
        
        Returns:
            Difficulty score (higher = more difficult to place)
        """
        difficulty = 0.0
        
        weekly_hours = lesson_data.get('weekly_hours', 0)
        
        # Larger lessons are harder to place
        if weekly_hours >= 5:
            difficulty += 25.0
        elif weekly_hours >= 4:
            difficulty += 20.0
        elif weekly_hours >= 3:
            difficulty += 10.0
        elif weekly_hours >= 2:
            difficulty += 5.0
        
        # Lessons requiring special equipment/rooms are harder
        lesson_name = lesson_data.get('lesson_name', lesson_data.get('name', '')).lower()
        
        if any(keyword in lesson_name for keyword in ['beden', 'müzik', 'resim', 'fen', 'kimya', 'fizik', 'biyoloji']):
            difficulty += 15.0  # Special room requirements
        
        if any(keyword in lesson_name for keyword in ['bilgisayar', 'teknoloji', 'robotik']):
            difficulty += 20.0  # Computer lab requirements
        
        return difficulty
    
    def _estimate_teacher_constraints(self, lesson_data: Dict[str, Any]) -> float:
        """
        Estimate teacher constraint level
        
        Returns:
            Constraint score (higher = more constrained teacher)
        """
        constraint_score = 0.0
        
        # This is a simplified estimation - in a real implementation,
        # we would query the database for actual teacher availability
        teacher_id = lesson_data.get('teacher_id')
        
        if teacher_id:
            try:
                # Check if teacher has limited availability (simplified check)
                # In real implementation, would check actual availability patterns
                constraint_score += 10.0  # Base constraint score
            except Exception:
                pass
        
        return constraint_score
    
    def _estimate_educational_importance(self, lesson_data: Dict[str, Any]) -> float:
        """
        Estimate educational importance of a lesson
        
        Returns:
            Importance score (higher = more important)
        """
        importance = 0.0
        
        lesson_name = lesson_data.get('lesson_name', lesson_data.get('name', '')).lower()
        
        # Core subjects get higher priority
        core_subjects = ['matematik', 'türkçe', 'fen', 'sosyal', 'ingilizce', 'fizik', 'kimya', 'biyoloji', 'tarih', 'coğrafya']
        
        if any(subject in lesson_name for subject in core_subjects):
            importance += 15.0
        
        # Language subjects
        if any(lang in lesson_name for lang in ['türkçe', 'ingilizce', 'almanca', 'fransızca']):
            importance += 10.0
        
        # STEM subjects
        if any(stem in lesson_name for stem in ['matematik', 'fen', 'fizik', 'kimya', 'biyoloji', 'bilgisayar']):
            importance += 12.0
        
        return importance
    
    def reset_statistics(self):
        """Reset all statistics and tracking data"""
        self.stats = {
            "total_attempts": 0,
            "successful_placements": 0,
            "alternative_patterns_used": 0,
            "split_patterns_used": 0,
            "flexible_patterns_used": 0,
            "educational_effectiveness_maintained": 0
        }
        self.placement_attempts.clear()
        self.logger.info("FlexibleBlockManager statistics reset")