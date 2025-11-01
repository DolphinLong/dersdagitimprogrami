"""
Unit tests for FlexibleBlockManager

Tests cover:
- Alternative block configurations for different lesson durations
- Block pattern matching and validation logic
- Block placement attempt tracking
- Educational effectiveness validation
- Block splitting logic for large lessons (4+ hours)
- Block priority ordering (larger blocks first)
"""

import pytest
from unittest.mock import Mock, patch
from algorithms.flexible_block_manager import (
    FlexibleBlockManager, 
    BlockConfiguration, 
    BlockPattern, 
    BlockPlacementAttempt
)


class TestFlexibleBlockManager:
    """Test FlexibleBlockManager core functionality"""
    
    def test_initialization(self, db_manager):
        """Test FlexibleBlockManager initialization"""
        manager = FlexibleBlockManager(db_manager)
        
        assert manager.db_manager == db_manager
        assert manager.min_educational_score == 5.0
        assert manager.max_placement_attempts == 10
        assert len(manager.placement_attempts) == 0
        assert manager.stats["total_attempts"] == 0
    
    def test_get_block_alternatives_5_hours(self, db_manager):
        """Test alternative block configurations for 5-hour lessons"""
        manager = FlexibleBlockManager(db_manager)
        
        alternatives = manager.get_block_alternatives(5)
        
        assert len(alternatives) == 5  # Should have 5 alternatives for 5-hour lessons
        
        # Check that all alternatives sum to 5 hours
        for config in alternatives:
            assert config.total_hours() == 5
        
        # Check that configurations are sorted by preference (educational score)
        scores = [config.educational_score for config in alternatives]
        assert scores == sorted(scores, reverse=True)
        
        # Verify specific patterns exist
        patterns = [config.pattern for config in alternatives]
        assert (2, 2, 1) in patterns  # Standard pattern
        assert (3, 2) in patterns     # Alternative pattern
        assert (1, 1, 1, 1, 1) in patterns  # Flexible pattern
    
    def test_get_block_alternatives_4_hours(self, db_manager):
        """Test alternative block configurations for 4-hour lessons"""
        manager = FlexibleBlockManager(db_manager)
        
        alternatives = manager.get_block_alternatives(4)
        
        assert len(alternatives) == 4  # Should have 4 alternatives for 4-hour lessons
        
        # Check that all alternatives sum to 4 hours
        for config in alternatives:
            assert config.total_hours() == 4
        
        # Verify specific patterns exist
        patterns = [config.pattern for config in alternatives]
        assert (2, 2) in patterns     # Standard pattern
        assert (3, 1) in patterns     # Alternative pattern
        assert (1, 1, 1, 1) in patterns  # Flexible pattern
    
    def test_get_block_alternatives_3_hours(self, db_manager):
        """Test alternative block configurations for 3-hour lessons"""
        manager = FlexibleBlockManager(db_manager)
        
        alternatives = manager.get_block_alternatives(3)
        
        assert len(alternatives) == 2  # Should have 2 alternatives for 3-hour lessons
        
        # Verify patterns
        patterns = [config.pattern for config in alternatives]
        assert (2, 1) in patterns     # Standard pattern
        assert (1, 1, 1) in patterns  # Alternative pattern
    
    def test_get_block_alternatives_2_hours(self, db_manager):
        """Test alternative block configurations for 2-hour lessons"""
        manager = FlexibleBlockManager(db_manager)
        
        alternatives = manager.get_block_alternatives(2)
        
        assert len(alternatives) == 2  # Should have 2 alternatives for 2-hour lessons
        
        # Verify patterns
        patterns = [config.pattern for config in alternatives]
        assert (2,) in patterns       # Standard pattern
        assert (1, 1) in patterns     # Split pattern
    
    def test_get_block_alternatives_1_hour(self, db_manager):
        """Test block configuration for 1-hour lessons"""
        manager = FlexibleBlockManager(db_manager)
        
        alternatives = manager.get_block_alternatives(1)
        
        assert len(alternatives) == 1  # Should have 1 configuration for 1-hour lessons
        assert alternatives[0].pattern == (1,)
    
    def test_get_block_alternatives_invalid_hours(self, db_manager):
        """Test handling of invalid hour values"""
        manager = FlexibleBlockManager(db_manager)
        
        # Test with 0 hours
        alternatives = manager.get_block_alternatives(0)
        assert len(alternatives) == 0
        
        # Test with negative hours
        alternatives = manager.get_block_alternatives(-1)
        assert len(alternatives) == 0
        
        # Test with very large hours (not defined)
        alternatives = manager.get_block_alternatives(10)
        assert len(alternatives) == 0


class TestBlockConfiguration:
    """Test BlockConfiguration class"""
    
    def test_block_configuration_creation(self):
        """Test BlockConfiguration creation and properties"""
        config = BlockConfiguration(
            pattern=(2, 2, 1),
            pattern_type=BlockPattern.STANDARD,
            educational_score=10.0,
            placement_difficulty=8.0,
            description="Test configuration"
        )
        
        assert config.pattern == (2, 2, 1)
        assert config.pattern_type == BlockPattern.STANDARD
        assert config.educational_score == 10.0
        assert config.placement_difficulty == 8.0
        assert config.total_hours() == 5
    
    def test_block_configuration_sorting(self):
        """Test BlockConfiguration sorting logic"""
        config1 = BlockConfiguration(
            pattern=(2, 2, 1), pattern_type=BlockPattern.STANDARD,
            educational_score=10.0, placement_difficulty=8.0, description="High score"
        )
        config2 = BlockConfiguration(
            pattern=(3, 2), pattern_type=BlockPattern.ALTERNATIVE,
            educational_score=8.0, placement_difficulty=6.0, description="Medium score"
        )
        config3 = BlockConfiguration(
            pattern=(1, 1, 1, 1, 1), pattern_type=BlockPattern.FLEXIBLE,
            educational_score=4.0, placement_difficulty=2.0, description="Low score"
        )
        
        configs = [config3, config1, config2]  # Unsorted
        configs.sort()  # Should sort by educational score (higher first)
        
        assert configs[0] == config1  # Highest educational score
        assert configs[1] == config2  # Medium educational score
        assert configs[2] == config3  # Lowest educational score
    
    def test_block_configuration_sorting_same_score(self):
        """Test sorting when educational scores are equal"""
        config1 = BlockConfiguration(
            pattern=(2, 2), pattern_type=BlockPattern.STANDARD,
            educational_score=8.0, placement_difficulty=7.0, description="Higher difficulty"
        )
        config2 = BlockConfiguration(
            pattern=(3, 1), pattern_type=BlockPattern.ALTERNATIVE,
            educational_score=8.0, placement_difficulty=5.0, description="Lower difficulty"
        )
        
        configs = [config1, config2]
        configs.sort()
        
        # When educational scores are equal, lower difficulty should come first
        assert configs[0] == config2  # Lower placement difficulty
        assert configs[1] == config1  # Higher placement difficulty


class TestEducationalEffectiveness:
    """Test educational effectiveness validation"""
    
    def test_validate_educational_effectiveness_high_score(self, db_manager):
        """Test validation with high educational score"""
        manager = FlexibleBlockManager(db_manager)
        
        config = BlockConfiguration(
            pattern=(2, 2, 1), pattern_type=BlockPattern.STANDARD,
            educational_score=10.0, placement_difficulty=8.0,
            description="High quality configuration"
        )
        
        assert manager.validate_educational_effectiveness(config) is True
    
    def test_validate_educational_effectiveness_low_score(self, db_manager):
        """Test validation with low educational score"""
        manager = FlexibleBlockManager(db_manager)
        
        config = BlockConfiguration(
            pattern=(1, 1, 1, 1, 1), pattern_type=BlockPattern.FLEXIBLE,
            educational_score=3.0, placement_difficulty=2.0,
            description="Low quality configuration"
        )
        
        assert manager.validate_educational_effectiveness(config) is False
    
    def test_validate_educational_effectiveness_boundary_score(self, db_manager):
        """Test validation with boundary educational score"""
        manager = FlexibleBlockManager(db_manager)
        
        # Test exactly at minimum threshold with acceptable pattern
        config = BlockConfiguration(
            pattern=(3, 2), pattern_type=BlockPattern.ALTERNATIVE,
            educational_score=5.0, placement_difficulty=4.0,
            description="Boundary configuration"
        )
        
        assert manager.validate_educational_effectiveness(config) is True
        
        # Test just below minimum threshold
        config.educational_score = 4.9
        assert manager.validate_educational_effectiveness(config) is False
    
    def test_validate_educational_effectiveness_too_many_single_blocks(self, db_manager):
        """Test validation rejects configurations with too many single-hour blocks"""
        manager = FlexibleBlockManager(db_manager)
        
        # Configuration with too many single-hour blocks for a large lesson
        config = BlockConfiguration(
            pattern=(1, 1, 1, 1, 1), pattern_type=BlockPattern.FLEXIBLE,
            educational_score=8.0, placement_difficulty=2.0,
            description="Too many single blocks"
        )
        
        # Should be rejected due to too many single-hour blocks for 5-hour lesson
        assert manager.validate_educational_effectiveness(config) is False
    
    def test_validate_educational_effectiveness_acceptable_single_blocks(self, db_manager):
        """Test validation accepts configurations with acceptable single-hour blocks"""
        manager = FlexibleBlockManager(db_manager)
        
        # Configuration with acceptable single-hour blocks
        config = BlockConfiguration(
            pattern=(2, 2, 1), pattern_type=BlockPattern.STANDARD,
            educational_score=8.0, placement_difficulty=6.0,
            description="Acceptable single block"
        )
        
        # Should be accepted (only 1 single-hour block)
        assert manager.validate_educational_effectiveness(config) is True


class TestBlockPriorityOrdering:
    """Test block priority ordering functionality"""
    
    def test_get_block_priority_order_basic(self, db_manager):
        """Test basic block priority ordering"""
        manager = FlexibleBlockManager(db_manager)
        
        lessons = [
            {'lesson_name': 'Matematik', 'weekly_hours': 5, 'lesson_id': 1},
            {'lesson_name': 'Türkçe', 'weekly_hours': 4, 'lesson_id': 2},
            {'lesson_name': 'Beden Eğitimi', 'weekly_hours': 2, 'lesson_id': 3},
            {'lesson_name': 'Müzik', 'weekly_hours': 1, 'lesson_id': 4},
        ]
        
        sorted_lessons = manager.get_block_priority_order(lessons)
        
        # Should be sorted by weekly hours (larger first)
        hours = [lesson['weekly_hours'] for lesson in sorted_lessons]
        assert hours == [5, 4, 2, 1]
        
        # Verify lesson order
        names = [lesson['lesson_name'] for lesson in sorted_lessons]
        assert names == ['Matematik', 'Türkçe', 'Beden Eğitimi', 'Müzik']
    
    def test_implement_block_priority_ordering_comprehensive(self, db_manager):
        """Test comprehensive block priority ordering with all factors"""
        manager = FlexibleBlockManager(db_manager)
        
        lessons = [
            {'lesson_name': 'Müzik', 'weekly_hours': 1, 'lesson_id': 1, 'teacher_id': 1},
            {'lesson_name': 'Matematik', 'weekly_hours': 5, 'lesson_id': 2, 'teacher_id': 2},
            {'lesson_name': 'Beden Eğitimi', 'weekly_hours': 2, 'lesson_id': 3, 'teacher_id': 3},
            {'lesson_name': 'Fen Bilimleri', 'weekly_hours': 4, 'lesson_id': 4, 'teacher_id': 4},
            {'lesson_name': 'Bilgisayar', 'weekly_hours': 3, 'lesson_id': 5, 'teacher_id': 5},
        ]
        
        sorted_lessons = manager.implement_block_priority_ordering(lessons)
        
        # Matematik (5h) should be first due to high hours + core subject
        assert sorted_lessons[0]['lesson_name'] == 'Matematik'
        
        # Fen Bilimleri (4h) should be second due to high hours + STEM subject
        assert sorted_lessons[1]['lesson_name'] == 'Fen Bilimleri'
        
        # Bilgisayar should rank high due to special room requirements
        bilgisayar_index = next(i for i, lesson in enumerate(sorted_lessons) 
                               if lesson['lesson_name'] == 'Bilgisayar')
        assert bilgisayar_index <= 2  # Should be in top 3
    
    def test_estimate_placement_difficulty(self, db_manager):
        """Test placement difficulty estimation"""
        manager = FlexibleBlockManager(db_manager)
        
        # Test high-hour lesson
        lesson_5h = {'lesson_name': 'Matematik', 'weekly_hours': 5}
        difficulty_5h = manager._estimate_placement_difficulty(lesson_5h)
        
        # Test low-hour lesson
        lesson_1h = {'lesson_name': 'Müzik', 'weekly_hours': 1}
        difficulty_1h = manager._estimate_placement_difficulty(lesson_1h)
        
        # Higher hour lessons should be more difficult
        assert difficulty_5h > difficulty_1h
        
        # Test special room requirements
        lesson_lab = {'lesson_name': 'Fen Bilimleri', 'weekly_hours': 3}
        difficulty_lab = manager._estimate_placement_difficulty(lesson_lab)
        
        lesson_regular = {'lesson_name': 'Tarih', 'weekly_hours': 3}
        difficulty_regular = manager._estimate_placement_difficulty(lesson_regular)
        
        # Lab lessons should be more difficult
        assert difficulty_lab > difficulty_regular
    
    def test_estimate_educational_importance(self, db_manager):
        """Test educational importance estimation"""
        manager = FlexibleBlockManager(db_manager)
        
        # Test core subject
        core_lesson = {'lesson_name': 'Matematik'}
        core_importance = manager._estimate_educational_importance(core_lesson)
        
        # Test non-core subject
        non_core_lesson = {'lesson_name': 'Müzik'}
        non_core_importance = manager._estimate_educational_importance(non_core_lesson)
        
        # Core subjects should have higher importance
        assert core_importance > non_core_importance
        
        # Test STEM subject
        stem_lesson = {'lesson_name': 'Fen Bilimleri'}
        stem_importance = manager._estimate_educational_importance(stem_lesson)
        
        # STEM subjects should have high importance
        assert stem_importance > 10.0


class TestBlockSplittingLogic:
    """Test block splitting logic for large lessons"""
    
    def test_is_large_lesson_split_viable_sufficient_space(self, db_manager):
        """Test split viability with sufficient available space"""
        manager = FlexibleBlockManager(db_manager)
        
        config = BlockConfiguration(
            pattern=(2, 2), pattern_type=BlockPattern.SPLIT,
            educational_score=8.0, placement_difficulty=6.0,
            description="4-hour split"
        )
        
        # Empty slots - should be viable
        existing_teacher_slots = {}
        existing_class_slots = {}
        
        viable = manager._is_large_lesson_split_viable(
            config, existing_teacher_slots, existing_class_slots
        )
        
        assert viable is True
    
    def test_is_large_lesson_split_viable_insufficient_space(self, db_manager):
        """Test split viability with insufficient available space"""
        manager = FlexibleBlockManager(db_manager)
        
        config = BlockConfiguration(
            pattern=(2, 2), pattern_type=BlockPattern.SPLIT,
            educational_score=8.0, placement_difficulty=6.0,
            description="4-hour split"
        )
        
        # Fill most slots to simulate insufficient space
        existing_teacher_slots = {
            1: {(d, s) for d in range(5) for s in range(7)}  # Fill most slots
        }
        existing_class_slots = {
            1: {(d, s) for d in range(5) for s in range(6)}  # Fill most slots
        }
        
        viable = manager._is_large_lesson_split_viable(
            config, existing_teacher_slots, existing_class_slots
        )
        
        assert viable is False
    
    def test_is_large_lesson_split_viable_small_lesson(self, db_manager):
        """Test split viability for small lessons (should always be viable)"""
        manager = FlexibleBlockManager(db_manager)
        
        config = BlockConfiguration(
            pattern=(2, 1), pattern_type=BlockPattern.STANDARD,
            educational_score=10.0, placement_difficulty=6.0,
            description="3-hour lesson"
        )
        
        # Even with some occupied slots, small lessons should be viable
        existing_teacher_slots = {1: {(0, 0), (0, 1), (1, 0)}}
        existing_class_slots = {1: {(0, 0), (0, 1), (1, 0)}}
        
        viable = manager._is_large_lesson_split_viable(
            config, existing_teacher_slots, existing_class_slots
        )
        
        assert viable is True  # Small lessons are always considered viable


class TestBlockPlacementAttempt:
    """Test BlockPlacementAttempt tracking"""
    
    def test_block_placement_attempt_creation(self):
        """Test BlockPlacementAttempt creation"""
        config = BlockConfiguration(
            pattern=(2, 2, 1), pattern_type=BlockPattern.STANDARD,
            educational_score=10.0, placement_difficulty=8.0,
            description="Test configuration"
        )
        
        attempt = BlockPlacementAttempt(
            lesson_id=1,
            class_id=2,
            teacher_id=3,
            configuration=config
        )
        
        assert attempt.lesson_id == 1
        assert attempt.class_id == 2
        assert attempt.teacher_id == 3
        assert attempt.configuration == config
        assert len(attempt.attempted_slots) == 0
        assert attempt.success is False
        assert attempt.failure_reason is None
    
    def test_add_attempted_slot(self):
        """Test adding attempted slots to tracking"""
        attempt = BlockPlacementAttempt(
            lesson_id=1, class_id=2, teacher_id=3, configuration=None
        )
        
        attempt.add_attempted_slot(0, 1)
        attempt.add_attempted_slot(1, 2)
        
        assert len(attempt.attempted_slots) == 2
        assert (0, 1) in attempt.attempted_slots
        assert (1, 2) in attempt.attempted_slots


class TestStatisticsAndTracking:
    """Test statistics and tracking functionality"""
    
    def test_get_placement_statistics_empty(self, db_manager):
        """Test statistics with no placement attempts"""
        manager = FlexibleBlockManager(db_manager)
        
        stats = manager.get_placement_statistics()
        
        assert stats["total_attempts"] == 0
        assert stats["successful_placements"] == 0
        assert stats["success_rate"] == 0
        assert stats["alternative_patterns_used"] == 0
        assert stats["split_patterns_used"] == 0
        assert stats["flexible_patterns_used"] == 0
    
    def test_reset_statistics(self, db_manager):
        """Test statistics reset functionality"""
        manager = FlexibleBlockManager(db_manager)
        
        # Simulate some activity
        manager.stats["total_attempts"] = 5
        manager.stats["successful_placements"] = 3
        manager.placement_attempts.append(
            BlockPlacementAttempt(1, 2, 3, None)
        )
        
        # Reset statistics
        manager.reset_statistics()
        
        assert manager.stats["total_attempts"] == 0
        assert manager.stats["successful_placements"] == 0
        assert len(manager.placement_attempts) == 0
    
    def test_update_pattern_statistics(self, db_manager):
        """Test pattern statistics updating"""
        manager = FlexibleBlockManager(db_manager)
        
        # Test alternative pattern
        alt_config = BlockConfiguration(
            pattern=(3, 2), pattern_type=BlockPattern.ALTERNATIVE,
            educational_score=8.0, placement_difficulty=6.0,
            description="Alternative pattern"
        )
        manager._update_pattern_statistics(alt_config)
        assert manager.stats["alternative_patterns_used"] == 1
        
        # Test split pattern
        split_config = BlockConfiguration(
            pattern=(2, 1, 1), pattern_type=BlockPattern.SPLIT,
            educational_score=7.0, placement_difficulty=4.0,
            description="Split pattern"
        )
        manager._update_pattern_statistics(split_config)
        assert manager.stats["split_patterns_used"] == 1
        
        # Test flexible pattern
        flex_config = BlockConfiguration(
            pattern=(1, 1, 1, 1), pattern_type=BlockPattern.FLEXIBLE,
            educational_score=5.0, placement_difficulty=2.0,
            description="Flexible pattern"
        )
        manager._update_pattern_statistics(flex_config)
        assert manager.stats["flexible_patterns_used"] == 1


class TestSlotConflictDetection:
    """Test slot conflict detection"""
    
    def test_has_slot_conflict_no_conflicts(self, db_manager):
        """Test slot conflict detection with no conflicts"""
        manager = FlexibleBlockManager(db_manager)
        
        existing_teacher_slots = {}
        existing_class_slots = {}
        
        has_conflict = manager._has_slot_conflict(
            class_id=1, teacher_id=1, day=0, slot=0,
            existing_teacher_slots=existing_teacher_slots,
            existing_class_slots=existing_class_slots
        )
        
        assert has_conflict is False
    
    def test_has_slot_conflict_class_conflict(self, db_manager):
        """Test slot conflict detection with class conflict"""
        manager = FlexibleBlockManager(db_manager)
        
        existing_teacher_slots = {}
        existing_class_slots = {1: {(0, 0)}}  # Class 1 occupied at day 0, slot 0
        
        has_conflict = manager._has_slot_conflict(
            class_id=1, teacher_id=1, day=0, slot=0,
            existing_teacher_slots=existing_teacher_slots,
            existing_class_slots=existing_class_slots
        )
        
        assert has_conflict is True
    
    def test_has_slot_conflict_teacher_conflict(self, db_manager):
        """Test slot conflict detection with teacher conflict"""
        manager = FlexibleBlockManager(db_manager)
        
        existing_teacher_slots = {1: {(0, 0)}}  # Teacher 1 occupied at day 0, slot 0
        existing_class_slots = {}
        
        has_conflict = manager._has_slot_conflict(
            class_id=1, teacher_id=1, day=0, slot=0,
            existing_teacher_slots=existing_teacher_slots,
            existing_class_slots=existing_class_slots
        )
        
        assert has_conflict is True
    
    def test_has_slot_conflict_both_conflicts(self, db_manager):
        """Test slot conflict detection with both class and teacher conflicts"""
        manager = FlexibleBlockManager(db_manager)
        
        existing_teacher_slots = {1: {(0, 0)}}
        existing_class_slots = {1: {(0, 0)}}
        
        has_conflict = manager._has_slot_conflict(
            class_id=1, teacher_id=1, day=0, slot=0,
            existing_teacher_slots=existing_teacher_slots,
            existing_class_slots=existing_class_slots
        )
        
        assert has_conflict is True


class TestSchoolConfiguration:
    """Test school configuration handling"""
    
    def test_get_school_config_default(self, db_manager):
        """Test school configuration with default values"""
        manager = FlexibleBlockManager(db_manager)
        
        config = manager._get_school_config()
        
        assert "school_type" in config
        assert "time_slots_count" in config
        assert "days_per_week" in config
        assert config["days_per_week"] == 5
        assert config["time_slots_count"] > 0
    
    @patch.object(FlexibleBlockManager, '_get_school_config')
    def test_get_school_config_different_types(self, mock_config, db_manager):
        """Test school configuration for different school types"""
        manager = FlexibleBlockManager(db_manager)
        
        # Test İlkokul configuration
        mock_config.return_value = {
            "school_type": "İlkokul",
            "time_slots_count": 7,
            "days_per_week": 5
        }
        
        config = manager._get_school_config()
        assert config["time_slots_count"] == 7
        
        # Test Lise configuration
        mock_config.return_value = {
            "school_type": "Lise",
            "time_slots_count": 8,
            "days_per_week": 5
        }
        
        config = manager._get_school_config()
        assert config["time_slots_count"] == 8