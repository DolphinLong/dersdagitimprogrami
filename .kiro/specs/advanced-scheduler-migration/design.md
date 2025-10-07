# Design Document

## Overview

This design outlines the migration of AdvancedScheduler to inherit from BaseScheduler, eliminating code duplication while preserving advanced scheduling capabilities. The migration will consolidate common functionality into BaseScheduler and create a clean inheritance hierarchy that allows for better code reuse and maintainability.

## Architecture

### Current State Analysis

**AdvancedScheduler (600+ lines):**
- Contains duplicate methods that exist in BaseScheduler
- Has advanced-specific features: smart blocks, scoring system, conflict resolution
- Uses different internal state management
- Has hardcoded school time slots and configuration

**BaseScheduler (400+ lines):**
- Provides common scheduling infrastructure
- Has abstract methods for subclass implementation
- Uses proper state management with class_slots and teacher_slots
- Includes validation and conflict detection

### Target Architecture

```
BaseScheduler (Abstract)
├── Common scheduling infrastructure
├── State management (class_slots, teacher_slots)
├── Validation and conflict detection
├── Template methods for extensibility
└── Abstract generate_schedule() method

AdvancedScheduler (Inherits from BaseScheduler)
├── Advanced-specific logic only
├── Smart block distribution
├── Scoring system with weights
├── Advanced conflict resolution
└── Implements generate_schedule()
```

## Components and Interfaces

### 1. Enhanced BaseScheduler

**New Methods to Add:**
- `_load_scheduler_weights()` - Template method for weight loading
- `_get_class_lessons()` - Common lesson retrieval logic
- `_find_available_classroom()` - Classroom availability checking
- `_create_lesson_blocks()` - Enhanced version of existing method
- `_is_placement_valid_advanced()` - Extended validation with multiple slots

**Enhanced Existing Methods:**
- `_detect_conflicts()` - Enhanced to return List[Dict] format
- `_get_lesson_blocks()` - Support for advanced block strategies
- `__init__()` - Support for scheduler-specific initialization

### 2. Refactored AdvancedScheduler

**Methods to Keep (Advanced-Specific):**
- `_schedule_lesson_smart()` - Core advanced scheduling logic
- `_calculate_placement_score()` - Scoring algorithm
- `_create_smart_blocks()` - Advanced block distribution
- `_attempt_conflict_resolution()` - Advanced conflict resolution

**Methods to Remove (Duplicates):**
- `_is_placement_valid()` - Use BaseScheduler version
- `_detect_conflicts()` - Use enhanced BaseScheduler version
- `_find_available_classroom()` - Move to BaseScheduler
- `_get_class_lessons()` - Move to BaseScheduler

### 3. Method Mapping Strategy

| AdvancedScheduler Method | Action | BaseScheduler Method |
|-------------------------|--------|---------------------|
| `_is_placement_valid()` | Remove | `_can_place_lesson()` (enhanced) |
| `_detect_conflicts()` | Remove | `_detect_conflicts()` (enhanced) |
| `_find_available_classroom()` | Move | New method |
| `_get_class_lessons()` | Move | New method |
| `_create_smart_blocks()` | Keep | Override `_get_lesson_blocks()` |
| `_schedule_lesson_smart()` | Keep | Advanced-specific |
| `_calculate_placement_score()` | Keep | Advanced-specific |

## Data Models

### Scheduler State Management

```python
# BaseScheduler state (existing)
self.schedule_entries: List[Dict]
self.teacher_slots: defaultdict(set)  # {teacher_id: {(day, slot)}}
self.class_slots: defaultdict(set)    # {class_id: {(day, slot)}}

# AdvancedScheduler additional state
self.weights: Dict[str, float]  # Scoring weights
```

### Schedule Entry Format (Standardized)

```python
{
    'class_id': int,
    'lesson_id': int,
    'teacher_id': int,
    'day': int,           # 0-4 (Monday-Friday)
    'time_slot': int,     # 0-7 (depending on school type)
    'classroom_id': Optional[int]
}
```

### Conflict Detection Format (Enhanced)

```python
# BaseScheduler enhanced format
{
    'class_conflicts': List[Dict],
    'teacher_conflicts': List[Dict],
    'total_conflicts': int
}

# Individual conflict format
{
    'type': str,          # 'class_conflict' or 'teacher_conflict'
    'entry1': Dict,       # First conflicting entry
    'entry2': Dict,       # Second conflicting entry
    'day': int,
    'slot': int
}
```

## Error Handling

### Exception Hierarchy Integration

The migration will integrate with the existing exception hierarchy:

```python
# Use existing exceptions from exceptions.py
- ConflictError: For scheduling conflicts
- TeacherConflictError: For teacher-specific conflicts  
- ClassConflictError: For class-specific conflicts
- AvailabilityError: For availability issues
- ScheduleGenerationError: For general generation failures
```

### Error Handling Strategy

1. **Validation Errors**: Use BaseScheduler's `_validate_schedule()` method
2. **Conflict Resolution**: Enhanced error reporting in AdvancedScheduler
3. **Fallback Mechanisms**: Preserve existing fallback logic in advanced scheduler
4. **Logging**: Maintain detailed logging for debugging

## Testing Strategy

### Unit Tests

1. **BaseScheduler Tests**:
   - Test new common methods
   - Test enhanced existing methods
   - Test abstract method contracts

2. **AdvancedScheduler Tests**:
   - Test inheritance behavior
   - Test advanced-specific methods
   - Test integration with BaseScheduler

3. **Integration Tests**:
   - Test complete schedule generation
   - Test conflict resolution
   - Test scoring system

### Migration Validation Tests

1. **Regression Tests**:
   - Compare pre/post migration schedule outputs
   - Verify identical results for same inputs
   - Test performance characteristics

2. **Compatibility Tests**:
   - Test with existing database schemas
   - Test with existing configuration
   - Test with existing teacher availability data

### Test Data Strategy

- Use existing test fixtures from `tests/conftest.py`
- Create specific migration test scenarios
- Test edge cases (empty schedules, full conflicts, etc.)

## Implementation Phases

### Phase 1: BaseScheduler Enhancement
- Add new common methods
- Enhance existing methods
- Maintain backward compatibility

### Phase 2: AdvancedScheduler Refactoring  
- Update inheritance
- Remove duplicate methods
- Update method calls to use super()

### Phase 3: Integration and Testing
- Run comprehensive tests
- Fix any integration issues
- Performance validation

### Phase 4: Cleanup and Documentation
- Remove dead code
- Update documentation
- Code review and optimization

## Performance Considerations

### Memory Usage
- Reduced memory footprint due to eliminated duplication
- Shared state management in BaseScheduler
- Optimized conflict detection algorithms

### Execution Speed
- Faster method resolution through proper inheritance
- Reduced code paths for common operations
- Maintained performance for advanced features

### Scalability
- Better code organization for future scheduler types
- Easier maintenance and bug fixes
- Cleaner extension points for new features