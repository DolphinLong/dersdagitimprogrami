# -*- coding: utf-8 -*-
"""
Constraint Priority Manager - User-Configurable Constraint Priorities
Allows users to set priorities for different scheduling constraints
"""

import io
import json
import logging
import sys
from enum import IntEnum
from typing import Dict, List, Optional

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class ConstraintPriority(IntEnum):
    """Constraint priority levels"""

    CRITICAL = 5  # Must be satisfied (hard constraint)
    HIGH = 4  # Very important
    MEDIUM = 3  # Important
    LOW = 2  # Nice to have
    OPTIONAL = 1  # Can be ignored if necessary


class ConstraintPriorityManager:
    """
    Manage constraint priorities for scheduling

    Features:
    - User-configurable priorities
    - Profile management (save/load)
    - Constraint validation
    - Priority-based scoring
    - Conflict resolution strategies
    """

    # Default constraint definitions
    DEFAULT_CONSTRAINTS = {
        # Hard constraints (CRITICAL)
        "no_class_conflicts": {
            "name": "No Class Conflicts",
            "description": "A class cannot have two lessons at the same time",
            "default_priority": ConstraintPriority.CRITICAL,
            "category": "hard",
        },
        "no_teacher_conflicts": {
            "name": "No Teacher Conflicts",
            "description": "A teacher cannot teach two classes at the same time",
            "default_priority": ConstraintPriority.CRITICAL,
            "category": "hard",
        },
        "teacher_availability": {
            "name": "Teacher Availability",
            "description": "Teachers can only teach when they are available",
            "default_priority": ConstraintPriority.HIGH,
            "category": "hard",
        },
        "max_consecutive_same_lesson": {
            "name": "Max Consecutive Same Lesson",
            "description": "No more than 2 hours of the same lesson consecutively",
            "default_priority": ConstraintPriority.HIGH,
            "category": "hard",
        },
        # Soft constraints
        "block_integrity": {
            "name": "Block Integrity",
            "description": "Lessons should be in blocks (2+2+2, 2+2+1, etc.)",
            "default_priority": ConstraintPriority.HIGH,
            "category": "soft",
        },
        "different_days_for_blocks": {
            "name": "Different Days for Blocks",
            "description": "Each block should be on a different day",
            "default_priority": ConstraintPriority.HIGH,
            "category": "soft",
        },
        "no_gaps": {
            "name": "No Gaps",
            "description": "Students should not have gaps in their schedule",
            "default_priority": ConstraintPriority.MEDIUM,
            "category": "soft",
        },
        "difficult_lessons_morning": {
            "name": "Difficult Lessons in Morning",
            "description": "Math, Physics, etc. should be in morning slots",
            "default_priority": ConstraintPriority.MEDIUM,
            "category": "soft",
        },
        "balanced_daily_load": {
            "name": "Balanced Daily Load",
            "description": "Each day should have similar number of lessons",
            "default_priority": ConstraintPriority.MEDIUM,
            "category": "soft",
        },
        "teacher_load_balance": {
            "name": "Teacher Load Balance",
            "description": "Teachers should have balanced daily workload",
            "default_priority": ConstraintPriority.LOW,
            "category": "soft",
        },
        "lesson_spacing": {
            "name": "Lesson Spacing",
            "description": "Same lesson should be 2-3 days apart",
            "default_priority": ConstraintPriority.LOW,
            "category": "soft",
        },
        "lunch_break_preference": {
            "name": "Lunch Break Preference",
            "description": "Light lessons during lunch hours",
            "default_priority": ConstraintPriority.OPTIONAL,
            "category": "soft",
        },
    }

    def __init__(self):
        """Initialize constraint priority manager"""
        self.logger = logging.getLogger(__name__)

        # Current priorities
        self.priorities: Dict[str, ConstraintPriority] = {}

        # Load defaults
        self.load_defaults()

    def load_defaults(self):
        """Load default priorities"""
        for constraint_id, constraint_info in self.DEFAULT_CONSTRAINTS.items():
            self.priorities[constraint_id] = constraint_info["default_priority"]

        self.logger.info("Loaded default constraint priorities")

    def set_priority(self, constraint_id: str, priority: ConstraintPriority) -> bool:
        """
        Set priority for a constraint

        Args:
            constraint_id: Constraint identifier
            priority: Priority level

        Returns:
            True if set successfully
        """
        if constraint_id not in self.DEFAULT_CONSTRAINTS:
            self.logger.warning(f"Unknown constraint: {constraint_id}")
            return False

        self.priorities[constraint_id] = priority
        self.logger.info(f"Set {constraint_id} priority to {priority.name}")
        return True

    def get_priority(self, constraint_id: str) -> Optional[ConstraintPriority]:
        """
        Get priority for a constraint

        Args:
            constraint_id: Constraint identifier

        Returns:
            Priority level or None
        """
        return self.priorities.get(constraint_id)

    def get_all_priorities(self) -> Dict[str, Dict]:
        """
        Get all constraints with their priorities

        Returns:
            Dict of constraint info with current priorities
        """
        result = {}

        for constraint_id, constraint_info in self.DEFAULT_CONSTRAINTS.items():
            result[constraint_id] = {
                "name": constraint_info["name"],
                "description": constraint_info["description"],
                "category": constraint_info["category"],
                "default_priority": constraint_info["default_priority"].name,
                "current_priority": self.priorities.get(
                    constraint_id, constraint_info["default_priority"]
                ).name,
            }

        return result

    def get_constraints_by_category(self, category: str) -> Dict:
        """
        Get constraints by category

        Args:
            category: 'hard' or 'soft'

        Returns:
            Dict of constraints in that category
        """
        return {
            cid: info
            for cid, info in self.DEFAULT_CONSTRAINTS.items()
            if info["category"] == category
        }

    def get_constraints_by_priority(self, priority: ConstraintPriority) -> List[str]:
        """
        Get constraints with specific priority

        Args:
            priority: Priority level

        Returns:
            List of constraint IDs
        """
        return [cid for cid, p in self.priorities.items() if p == priority]

    def calculate_violation_penalty(self, constraint_id: str) -> float:
        """
        Calculate penalty for violating a constraint

        Args:
            constraint_id: Constraint identifier

        Returns:
            Penalty value (higher priority = higher penalty)
        """
        priority = self.get_priority(constraint_id)

        if priority is None:
            return 0.0

        # Map priority to penalty
        penalty_map = {
            ConstraintPriority.CRITICAL: 1000.0,
            ConstraintPriority.HIGH: 100.0,
            ConstraintPriority.MEDIUM: 10.0,
            ConstraintPriority.LOW: 1.0,
            ConstraintPriority.OPTIONAL: 0.1,
        }

        return penalty_map.get(priority, 0.0)

    def should_enforce(self, constraint_id: str, strict_mode: bool = False) -> bool:
        """
        Check if constraint should be enforced

        Args:
            constraint_id: Constraint identifier
            strict_mode: If True, enforce HIGH and above; if False, enforce CRITICAL only

        Returns:
            True if should be enforced
        """
        priority = self.get_priority(constraint_id)

        if priority is None:
            return False

        if strict_mode:
            return priority >= ConstraintPriority.HIGH
        else:
            return priority == ConstraintPriority.CRITICAL

    def save_profile(self, filename: str, profile_name: str = "Default") -> bool:
        """
        Save current priorities to a profile file

        Args:
            filename: Output filename
            profile_name: Name of the profile

        Returns:
            True if saved successfully
        """
        profile_data = {
            "profile_name": profile_name,
            "priorities": {cid: priority.name for cid, priority in self.priorities.items()},
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved profile '{profile_name}' to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save profile: {e}")
            return False

    def load_profile(self, filename: str) -> bool:
        """
        Load priorities from a profile file

        Args:
            filename: Input filename

        Returns:
            True if loaded successfully
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                profile_data = json.load(f)

            profile_name = profile_data.get("profile_name", "Unknown")
            priorities_data = profile_data.get("priorities", {})

            # Load priorities
            for cid, priority_name in priorities_data.items():
                if cid in self.DEFAULT_CONSTRAINTS:
                    try:
                        priority = ConstraintPriority[priority_name]
                        self.priorities[cid] = priority
                    except KeyError:
                        self.logger.warning(f"Invalid priority '{priority_name}' for {cid}")

            self.logger.info(f"Loaded profile '{profile_name}' from {filename}")
            return True
        except FileNotFoundError:
            self.logger.error(f"Profile file not found: {filename}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load profile: {e}")
            return False

    def create_preset_profile(self, preset_name: str) -> bool:
        """
        Create a preset profile

        Available presets:
        - 'strict': All constraints HIGH or CRITICAL
        - 'balanced': Mix of priorities (default)
        - 'flexible': Most constraints LOW or OPTIONAL
        - 'speed': Only CRITICAL constraints enforced

        Args:
            preset_name: Name of preset

        Returns:
            True if created successfully
        """
        if preset_name == "strict":
            # Strict mode: enforce everything
            for cid in self.priorities:
                if self.DEFAULT_CONSTRAINTS[cid]["category"] == "hard":
                    self.priorities[cid] = ConstraintPriority.CRITICAL
                else:
                    self.priorities[cid] = ConstraintPriority.HIGH

        elif preset_name == "balanced":
            # Balanced mode: use defaults
            self.load_defaults()

        elif preset_name == "flexible":
            # Flexible mode: relax soft constraints
            for cid in self.priorities:
                if self.DEFAULT_CONSTRAINTS[cid]["category"] == "hard":
                    self.priorities[cid] = ConstraintPriority.HIGH
                else:
                    self.priorities[cid] = ConstraintPriority.LOW

        elif preset_name == "speed":
            # Speed mode: only critical constraints
            for cid in self.priorities:
                if self.DEFAULT_CONSTRAINTS[cid]["category"] == "hard":
                    if cid in ["no_class_conflicts", "no_teacher_conflicts"]:
                        self.priorities[cid] = ConstraintPriority.CRITICAL
                    else:
                        self.priorities[cid] = ConstraintPriority.HIGH
                else:
                    self.priorities[cid] = ConstraintPriority.OPTIONAL

        else:
            self.logger.error(f"Unknown preset: {preset_name}")
            return False

        self.logger.info(f"Created preset profile: {preset_name}")
        return True

    def get_scoring_weights(self) -> Dict[str, float]:
        """
        Get scoring weights based on priorities

        Returns:
            Dict of constraint weights for scoring
        """
        weights = {}

        for cid, priority in self.priorities.items():
            # Map priority to weight
            weight_map = {
                ConstraintPriority.CRITICAL: 100.0,
                ConstraintPriority.HIGH: 50.0,
                ConstraintPriority.MEDIUM: 20.0,
                ConstraintPriority.LOW: 5.0,
                ConstraintPriority.OPTIONAL: 1.0,
            }

            weights[cid] = weight_map.get(priority, 0.0)

        return weights

    def validate_priorities(self) -> List[str]:
        """
        Validate current priorities

        Returns:
            List of warning messages
        """
        warnings = []

        # Check if critical constraints are set
        critical_constraints = ["no_class_conflicts", "no_teacher_conflicts"]
        for cid in critical_constraints:
            if self.priorities.get(cid) != ConstraintPriority.CRITICAL:
                warnings.append(f"Warning: {cid} should be CRITICAL for valid schedules")

        # Check if too many constraints are OPTIONAL
        optional_count = sum(
            1 for p in self.priorities.values() if p == ConstraintPriority.OPTIONAL
        )

        if optional_count > len(self.priorities) * 0.5:
            warnings.append(
                "Warning: More than 50% of constraints are OPTIONAL. "
                "Schedule quality may be low."
            )

        return warnings

    def get_summary(self) -> str:
        """
        Get summary of current priorities

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("CONSTRAINT PRIORITY SUMMARY")
        lines.append("=" * 60)

        # Group by priority
        by_priority = defaultdict(list)
        for cid, priority in self.priorities.items():
            by_priority[priority].append(cid)

        # Display by priority (high to low)
        for priority in sorted(by_priority.keys(), reverse=True):
            lines.append(f"\n{priority.name} ({priority.value}):")
            for cid in by_priority[priority]:
                name = self.DEFAULT_CONSTRAINTS[cid]["name"]
                lines.append(f"  • {name}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)


# Import for defaultdict
from collections import defaultdict
