"""
Automatic scheduling algorithm for the Class Scheduling Program
"""

import logging
import random

# Import ultra aggressive scheduler (NEWEST - %100 Coverage Goal!)
try:
    from algorithms.ultra_aggressive_scheduler import UltraAggressiveScheduler

    ULTRA_AGGRESSIVE_SCHEDULER_AVAILABLE = True
except ImportError:
    ULTRA_AGGRESSIVE_SCHEDULER_AVAILABLE = False

# Import hybrid optimal scheduler (NEW - Most Powerful!)
try:
    from algorithms.hybrid_optimal_scheduler import HybridOptimalScheduler

    HYBRID_OPTIMAL_SCHEDULER_AVAILABLE = True
except ImportError:
    HYBRID_OPTIMAL_SCHEDULER_AVAILABLE = False

# Import simple perfect scheduler (BEST - Pragmatic and Effective)
try:
    from algorithms.simple_perfect_scheduler import SimplePerfectScheduler

    SIMPLE_PERFECT_SCHEDULER_AVAILABLE = True
except ImportError:
    SIMPLE_PERFECT_SCHEDULER_AVAILABLE = False

# Import ultimate scheduler (ULTIMATE - True backtracking + CSP)
try:
    from algorithms.ultimate_scheduler import UltimateScheduler

    ULTIMATE_SCHEDULER_AVAILABLE = True
except ImportError:
    ULTIMATE_SCHEDULER_AVAILABLE = False

# Import enhanced strict scheduler (BEST - %100 coverage goal)
try:
    from algorithms.enhanced_strict_scheduler import EnhancedStrictScheduler

    ENHANCED_STRICT_SCHEDULER_AVAILABLE = True
except ImportError:
    ENHANCED_STRICT_SCHEDULER_AVAILABLE = False

# Import strict scheduler (new, guaranteed coverage)
try:
    from algorithms.strict_scheduler import StrictScheduler

    STRICT_SCHEDULER_AVAILABLE = True
except ImportError:
    STRICT_SCHEDULER_AVAILABLE = False

# Import advanced scheduler (fallback)
try:
    from algorithms.advanced_scheduler import AdvancedScheduler

    ADVANCED_SCHEDULER_AVAILABLE = True
except ImportError:
    ADVANCED_SCHEDULER_AVAILABLE = False


class Scheduler:
    """Handles automatic schedule generation"""

    # Define time slots for each school type
    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,  # İlkokul: 5 gün × 6 saat = 30 hücre
        "Ortaokul": 7,  # Ortaokul: 5 gün × 7 saat = 35 hücre
        "Lise": 8,  # Lise: 5 gün × 8 saat = 40 hücre
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(
        self, db_manager, use_advanced=True, use_hybrid=True, use_ultra=True, progress_callback=None
    ):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.progress_callback = progress_callback
        self.use_ultra = use_ultra and ULTRA_AGGRESSIVE_SCHEDULER_AVAILABLE
        self.use_hybrid = use_hybrid and HYBRID_OPTIMAL_SCHEDULER_AVAILABLE
        self.use_simple_perfect = SIMPLE_PERFECT_SCHEDULER_AVAILABLE
        self.use_ultimate = ULTIMATE_SCHEDULER_AVAILABLE
        self.use_enhanced_strict = ENHANCED_STRICT_SCHEDULER_AVAILABLE
        self.use_strict = STRICT_SCHEDULER_AVAILABLE
        self.use_advanced = use_advanced and ADVANCED_SCHEDULER_AVAILABLE

        # Initialize ultra aggressive scheduler if available (HIGHEST priority!)
        # NOW FIXED: Güçlendirilmiş çakışma kontrolü + Final validation
        if self.use_ultra:
            self.ultra_scheduler = UltraAggressiveScheduler(
                db_manager, progress_callback
            )
            self.logger.info(
                "💪 ULTRA AGGRESSIVE SCHEDULER Aktif - %100 Doluluk Hedefli!"
            )
            self.logger.info(
                "   ✅ İteratif iyileştirme + Boş hücre kalmayana kadar deneme"
            )
            self.logger.info("   ✅ Güçlendirilmiş çakışma kontrolü + Final validation")
        # Fallback to hybrid optimal scheduler
        elif self.use_hybrid:
            self.hybrid_scheduler = HybridOptimalScheduler(db_manager)
            self.logger.info("🚀 HYBRID OPTIMAL SCHEDULER Aktif - En Güçlü Algoritma!")
            self.logger.info(
                "   ✅ Arc Consistency + Soft Constraints + Simulated Annealing"
            )
        # Fallback to simple perfect scheduler
        elif self.use_simple_perfect:
            self.hybrid_scheduler = None
            self.simple_perfect_scheduler = SimplePerfectScheduler(db_manager)
            self.logger.info(
                "🎯 SIMPLE PERFECT SCHEDULER Aktif - Pragmatik ve %100 Etkili"
            )
        # Fallback to ultimate scheduler
        elif self.use_ultimate:
            self.hybrid_scheduler = None
            self.simple_perfect_scheduler = None
            self.ultimate_scheduler = UltimateScheduler(db_manager)
            self.logger.info(
                "🎯 ULTIMATE SCHEDULER Aktif - Gerçek Backtracking + CSP + Forward Checking"
            )
        # Fallback to enhanced strict scheduler
        elif self.use_enhanced_strict:
            self.hybrid_scheduler = None
            self.ultimate_scheduler = None
            self.enhanced_strict_scheduler = EnhancedStrictScheduler(db_manager)
            self.logger.info(
                "🚀 ENHANCED STRICT SCHEDULER Aktif - Backtracking + %100 Kapsama Hedefi"
            )
        # Fallback to strict scheduler
        elif self.use_strict:
            self.hybrid_scheduler = None
            self.ultimate_scheduler = None
            self.enhanced_strict_scheduler = None
            self.strict_scheduler = StrictScheduler(db_manager)
            self.logger.info(
                "🎯 STRICT SCHEDULER Aktif - Tam Kapsama ve Öğretmen Uygunluğu Garantili"
            )
        else:
            self.hybrid_scheduler = None
            self.ultimate_scheduler = None
            self.enhanced_strict_scheduler = None
            self.strict_scheduler = None

            # Fallback to advanced scheduler
            if self.use_advanced:
                self.advanced_scheduler = AdvancedScheduler(db_manager)
                self.logger.info("✨ Using Advanced Scheduler with smart distribution")
            else:
                self.advanced_scheduler = None
                self.logger.info("📋 Using Standard Scheduler")

    def generate_schedule(self):
        """
        Generate a schedule automatically using lesson assignments
        Returns a list of schedule entries
        """
        # Use ultra aggressive scheduler if available (HIGHEST priority!)
        # NOW FIXED: Güçlendirilmiş çakışma kontrolü
        if self.use_ultra and self.ultra_scheduler:
            return self.ultra_scheduler.generate_schedule()

        # Fallback to hybrid optimal scheduler
        if self.use_hybrid and self.hybrid_scheduler:
            return self.hybrid_scheduler.generate_schedule()

        # Fallback to simple perfect scheduler
        if self.use_simple_perfect and self.simple_perfect_scheduler:
            return self.simple_perfect_scheduler.generate_schedule()

        # Fallback to ultimate scheduler
        if self.use_ultimate and self.ultimate_scheduler:
            return self.ultimate_scheduler.generate_schedule()

        # Fallback to enhanced strict scheduler
        if self.use_enhanced_strict and self.enhanced_strict_scheduler:
            return self.enhanced_strict_scheduler.generate_schedule()

        # Fallback to strict scheduler
        if self.use_strict and self.strict_scheduler:
            return self.strict_scheduler.generate_schedule()

        # Fallback to advanced scheduler
        if self.use_advanced and self.advanced_scheduler:
            return self.advanced_scheduler.generate_schedule()

        # Otherwise use standard scheduler
        return self._generate_schedule_standard()

    def _generate_schedule_standard(self):
        """
        Standard schedule generation (original algorithm)
        """
        # Get all required data
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()

        # Get existing lesson assignments (from schedule table)
        existing_assignments = self.db_manager.get_schedule_by_school_type()

        # Get school type and time slots
        school_type = self.db_manager.get_school_type()
        if not school_type:
            school_type = "İlkokul"  # Default to İlkokul to cover grades 1-8

        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 6)

        # Initialize schedule entries
        schedule_entries = []

        # Time slots based on school type
        time_slots = list(range(time_slots_count))

        self.logger.info(
            f"Starting schedule generation for {len(classes)} classes, "
            f"{len(teachers)} teachers, {len(lessons)} lessons"
        )
        self.logger.info(f"School type: {school_type}, Time slots: {time_slots_count}")
        self.logger.info(f"Found {len(existing_assignments)} existing lesson assignments")

        # Create lesson assignment map from existing assignments
        lesson_assignments = {}  # {(class_id, lesson_id): teacher_id}
        for assignment in existing_assignments:
            key = (assignment.class_id, assignment.lesson_id)
            lesson_assignments[key] = assignment.teacher_id

        self.logger.info(f"Created {len(lesson_assignments)} lesson-teacher assignments")

        # For each class, try to schedule their lessons based on assignments
        for class_obj in classes:
            self.logger.info(
                f"\n=== Scheduling for class: {class_obj.name} (Grade {class_obj.grade}) ==="
            )

            # Get all lessons for this grade that have assignments
            class_lessons = []
            for lesson in lessons:
                # Check if this lesson is assigned to this class
                assignment_key = (class_obj.class_id, lesson.lesson_id)
                if assignment_key in lesson_assignments:
                    # Get weekly hours from curriculum
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                        lesson.lesson_id, class_obj.grade
                    )
                    if weekly_hours and weekly_hours > 0:
                        assigned_teacher_id = lesson_assignments[assignment_key]
                        assigned_teacher = self.db_manager.get_teacher_by_id(
                            assigned_teacher_id
                        )
                        if assigned_teacher:
                            class_lessons.append((lesson, weekly_hours, assigned_teacher))
                            self.logger.info(
                                f"  📋 Found assignment: {lesson.name} -> "
                                f"{assigned_teacher.name} ({weekly_hours} hours)"
                            )

            if not class_lessons:
                self.logger.warning(f"  ⚠️  No lesson assignments found for {class_obj.name}")
                continue

            # Sort lessons by weekly hours (descending) to schedule important lessons first
            class_lessons.sort(key=lambda x: x[1], reverse=True)

            # Schedule assigned lessons
            for lesson, weekly_hours, assigned_teacher in class_lessons:
                self.logger.info(
                    f"Scheduling assigned lesson: {lesson.name} ({weekly_hours} hours) "
                    f"with {assigned_teacher.name}"
                )

                # Try to schedule this lesson with the assigned teacher
                success = self._schedule_lesson_with_assigned_teacher(
                    schedule_entries,
                    class_obj,
                    assigned_teacher,
                    lesson,
                    list(range(5)),
                    time_slots,
                    weekly_hours,
                )

                if not success:
                    self.logger.warning(
                        f"⚠️  Could not fully schedule {lesson.name} for "
                        f"{class_obj.name} with {assigned_teacher.name}"
                    )

            # Print class schedule summary
            class_total = len(
                [e for e in schedule_entries if e["class_id"] == class_obj.class_id]
            )
            self.logger.info(f"✅ Class {class_obj.name} scheduled: {class_total} hours")

        # Final summary
        total_entries = len(schedule_entries)
        self.logger.info(f"\n🎯 Schedule generation completed: {total_entries} total entries")

        # Check for any conflicts
        conflicts = self.detect_conflicts(schedule_entries)
        if conflicts:
            self.logger.warning(
                f"⚠️  {len(conflicts)} conflicts detected - attempting resolution..."
            )
            # Try to resolve conflicts automatically
            from algorithms.conflict_resolver import ConflictResolver

            resolver = ConflictResolver(self.db_manager)
            resolved = resolver.auto_resolve_conflicts(conflicts)
            self.logger.info(f"✅ {resolved} conflicts resolved")

        return schedule_entries

    def _get_eligible_teachers(self, teachers, lesson):
        """Get all teachers eligible to teach a specific lesson"""
        eligible_teachers = [
            teacher for teacher in teachers if teacher.subject == lesson.name
        ]

        # Special handling for specific lessons
        if lesson.name == "T.C. İnkılap Tarihi ve Atatürkçülük":
            sosyal_bilgiler_teachers = [
                teacher for teacher in teachers if teacher.subject == "Sosyal Bilgiler"
            ]
            eligible_teachers.extend(sosyal_bilgiler_teachers)

        # Sort by current workload (ascending)
        teacher_workload = {}
        for teacher in eligible_teachers:
            workload = sum(
                1
                for entry in self.db_manager.get_schedule_for_specific_teacher(
                    teacher.teacher_id
                )
            )
            teacher_workload[teacher.teacher_id] = workload

        eligible_teachers.sort(key=lambda t: teacher_workload.get(t.teacher_id, 0))
        return eligible_teachers

    def _schedule_lesson_with_assigned_teacher(
        self, schedule_entries, class_obj, assigned_teacher, lesson, days, time_slots, weekly_hours
    ):
        """Schedule a lesson with its specifically assigned teacher - AGGRESSIVE MODE"""
        self.logger.info(
            f"  🚀 AGGRESSIVE Scheduling {lesson.name} for {class_obj.name} "
            f"with assigned teacher {assigned_teacher.name}"
        )

        scheduled_hours = 0
        max_attempts = 100  # AGGRESSIVE: Much more attempts for full coverage
        max_daily_hours = 7  # Maximum hours per teacher per day

        # Track teacher daily hours
        teacher_daily_hours = {i: 0 for i in range(5)}
        for entry in schedule_entries:
            if entry["teacher_id"] == assigned_teacher.teacher_id:
                teacher_daily_hours[entry["day"]] += 1

        for attempt in range(max_attempts):
            if scheduled_hours >= weekly_hours:
                break

            # Try different distribution strategies
            remaining_hours = weekly_hours - scheduled_hours

            if attempt < 10:
                # First 10 attempts: try to schedule in blocks of 2, distributed across different days
                block_sizes = self._create_optimal_blocks_distributed(remaining_hours)
            elif attempt < 30:
                # Next 20 attempts: try single hour slots
                block_sizes = [1] * remaining_hours
            elif attempt < 60:
                # Next 30 attempts: try any available slots (more aggressive)
                block_sizes = [1] * remaining_hours
            elif attempt < 80:
                # Next 20 attempts: try larger blocks if possible
                if remaining_hours >= 2:
                    block_sizes = [2] + [1] * (remaining_hours - 2)
                else:
                    block_sizes = [1] * remaining_hours
            else:
                # Final attempts: any available slots
                block_sizes = (
                    [remaining_hours]
                    if remaining_hours <= 3
                    else [2, 1] * (remaining_hours // 2) + [1] * (remaining_hours % 2)
                )

            # Track which days we've used for this lesson to ensure distribution
            used_days = set()

            for block_size in block_sizes:
                if scheduled_hours >= weekly_hours:
                    break

                # Try each day, prioritizing days we haven't used yet
                day_order = list(range(5))
                # Sort days to prioritize unused days
                day_order.sort(key=lambda d: (d in used_days, d))

                for day in day_order:
                    if scheduled_hours >= weekly_hours:
                        break

                    # Check teacher daily limit
                    if teacher_daily_hours[day] + block_size > max_daily_hours:
                        continue

                    # Skip this day if we've already used it and there are unused days available
                    if day in used_days and len(used_days) < min(3, len(block_sizes)):
                        continue

                    # Find available slots for this day - AGGRESSIVE
                    available_slots = self._find_best_slots_aggressive(
                        schedule_entries, class_obj.class_id, day, time_slots, block_size
                    )

                    if available_slots:
                        # Check if assigned teacher is available for all slots - AGGRESSIVE
                        if self._can_teacher_teach_at_slots_aggressive(
                            schedule_entries, assigned_teacher.teacher_id, day, available_slots
                        ):
                            # Schedule the lesson with assigned teacher - but only up to weekly_hours
                            slots_to_schedule = min(
                                len(available_slots), weekly_hours - scheduled_hours
                            )
                            for i in range(slots_to_schedule):
                                time_slot = available_slots[i]
                                new_entry = {
                                    "class_id": class_obj.class_id,
                                    "teacher_id": assigned_teacher.teacher_id,
                                    "lesson_id": lesson.lesson_id,
                                    "classroom_id": 1,
                                    "day": day,
                                    "time_slot": time_slot,
                                }

                                if not self._has_conflict(schedule_entries, new_entry):
                                    schedule_entries.append(new_entry)
                                    scheduled_hours += 1
                                    teacher_daily_hours[day] += 1
                                    self.logger.info(
                                        f"    ✓ AGGRESSIVE: {lesson.name} - Day {day+1}, "
                                        f"Slot {time_slot+1} ({assigned_teacher.name})"
                                    )

                            used_days.add(day)
                            break  # Move to next block
                        else:
                            if attempt < 5:  # Only show warnings for first few attempts
                                self.logger.warning(
                                    f"    ⚠️  Teacher {assigned_teacher.name} not available on "
                                    f"Day {day+1} for {block_size} slots"
                                )

        success_rate = (scheduled_hours / weekly_hours) * 100 if weekly_hours > 0 else 100
        if success_rate < 100:
            self.logger.warning(
                f"    ⚠️  {lesson.name}: {scheduled_hours}/{weekly_hours} hours scheduled ({success_rate:.1f}%)"
            )
        else:
            self.logger.info(
                f"    ✅ {lesson.name}: {scheduled_hours}/{weekly_hours} hours scheduled (100%)"
            )

        return scheduled_hours >= weekly_hours  # AGGRESSIVE: Only accept 100% success

    def _schedule_lesson_improved(
        self,
        schedule_entries,
        class_obj,
        specific_teacher,
        lesson,
        days,
        time_slots,
        weekly_hours,
        eligible_teachers=None,
    ):
        """Improved lesson scheduling with better distribution and conflict handling"""
        if specific_teacher:
            teachers_to_try = [specific_teacher]
        elif eligible_teachers:
            teachers_to_try = eligible_teachers
        else:
            teachers_to_try = self._get_eligible_teachers(
                self.db_manager.get_all_teachers(), lesson
            )

        if not teachers_to_try:
            return False

        scheduled_hours = 0
        max_attempts = 3  # Limit attempts to prevent infinite loops

        for attempt in range(max_attempts):
            if scheduled_hours >= weekly_hours:
                break

            # Try different distribution strategies
            remaining_hours = weekly_hours - scheduled_hours

            if attempt == 0:
                # First attempt: try to schedule in blocks of 2
                block_sizes = self._create_optimal_blocks(remaining_hours)
            elif attempt == 1:
                # Second attempt: try single hour slots
                block_sizes = [1] * remaining_hours
            else:
                # Final attempt: any available slots
                block_sizes = (
                    [remaining_hours]
                    if remaining_hours <= 3
                    else [2, 1] * (remaining_hours // 2) + [1] * (remaining_hours % 2)
                )

            for block_size in block_sizes:
                if scheduled_hours >= weekly_hours:
                    break

                # Try each day
                for day in range(5):
                    if scheduled_hours >= weekly_hours:
                        break

                    # Find available slots for this day
                    available_slots = self._find_best_slots(
                        schedule_entries, class_obj.class_id, day, time_slots, block_size
                    )

                    if available_slots:
                        # Try each eligible teacher
                        for teacher in teachers_to_try:
                            if self._can_teacher_teach_at_slots(
                                schedule_entries, teacher.teacher_id, day, available_slots
                            ):
                                # Schedule the lesson - but only up to weekly_hours
                                slots_to_schedule = min(
                                    len(available_slots), weekly_hours - scheduled_hours
                                )
                                for i in range(slots_to_schedule):
                                    time_slot = available_slots[i]
                                    new_entry = {
                                        "class_id": class_obj.class_id,
                                        "teacher_id": teacher.teacher_id,
                                        "lesson_id": lesson.lesson_id,
                                        "classroom_id": 1,
                                        "day": day,
                                        "time_slot": time_slot,
                                    }

                                    if not self._has_conflict(schedule_entries, new_entry):
                                        schedule_entries.append(new_entry)
                                        scheduled_hours += 1
                                        self.logger.info(
                                            f"  ✓ Scheduled {lesson.name} - Day {day+1}, "
                                            f"Slot {time_slot+1} ({teacher.name})"
                                        )

                                break  # Teacher found, move to next block

                        if scheduled_hours >= weekly_hours:
                            break

        success_rate = (scheduled_hours / weekly_hours) * 100 if weekly_hours > 0 else 100
        if success_rate < 100:
            self.logger.warning(
                f"  ⚠️  {lesson.name}: {scheduled_hours}/{weekly_hours} hours scheduled ({success_rate:.1f}%)"
            )

        return scheduled_hours == weekly_hours

    def _create_optimal_blocks(self, total_hours):
        """Create optimal lesson blocks for better distribution"""
        if total_hours <= 0:
            return []

        blocks = []
        remaining = total_hours

        # Prefer 2-hour blocks for better learning continuity
        while remaining >= 2:
            blocks.append(2)
            remaining -= 2

        # Add remaining single hours
        if remaining > 0:
            blocks.append(remaining)

        return blocks

    def _create_optimal_blocks_distributed(self, total_hours):
        """Create optimal lesson blocks distributed across different days"""
        if total_hours <= 0:
            return []

        blocks = []
        remaining = total_hours

        # Strategy: Create blocks that encourage distribution across days
        if total_hours <= 2:
            # 1-2 hours: single blocks
            blocks = [1] * total_hours
        elif total_hours <= 4:
            # 3-4 hours: prefer 2-hour blocks
            blocks = [2] * (total_hours // 2)
            if total_hours % 2 == 1:
                blocks.append(1)
        else:
            # 5+ hours: mix of 2-hour and 1-hour blocks for better distribution
            # Aim for mostly 2-hour blocks but ensure we can spread across days

            # Calculate optimal distribution
            if total_hours >= 6:
                # For 6+ hours, use 2-hour blocks distributed across 3+ days
                two_hour_blocks = min(total_hours // 2, 3)  # Max 3 blocks of 2 hours
                blocks = [2] * two_hour_blocks
                remaining = total_hours - (two_hour_blocks * 2)
                if remaining > 0:
                    blocks.extend([1] * remaining)
            else:
                # For 5 hours, use 2+2+1 distribution
                blocks = [2, 2, 1]

        # Shuffle to randomize which days get which block sizes
        import random

        random.shuffle(blocks)

        return blocks

    def _find_best_slots(self, schedule_entries, class_id, day, time_slots, hours_needed):
        """Find the best available time slots for a class on a specific day"""
        # First try to find consecutive slots
        for start_slot in range(len(time_slots) - hours_needed + 1):
            consecutive_slots = []
            all_available = True

            for i in range(hours_needed):
                time_slot = time_slots[start_slot + i]
                if not self._is_slot_available_for_class(
                    schedule_entries, class_id, day, time_slot
                ):
                    all_available = False
                    break
                consecutive_slots.append(time_slot)

            if all_available:
                return consecutive_slots

        # If consecutive slots not available, find any available slots
        available_slots = []
        for time_slot in time_slots:
            if self._is_slot_available_for_class(schedule_entries, class_id, day, time_slot):
                available_slots.append(time_slot)
                if len(available_slots) >= hours_needed:
                    return available_slots[:hours_needed]

        return []

    def _find_best_slots_enhanced(self, schedule_entries, class_id, day, time_slots, hours_needed):
        """Enhanced slot finding with better availability checking"""
        # First try to find consecutive slots
        for start_slot in range(len(time_slots) - hours_needed + 1):
            consecutive_slots = []
            all_available = True

            for i in range(hours_needed):
                time_slot = time_slots[start_slot + i]
                if not self._is_slot_available_for_class_enhanced(
                    schedule_entries, class_id, day, time_slot
                ):
                    all_available = False
                    break
                consecutive_slots.append(time_slot)

            if all_available:
                return consecutive_slots

        # If consecutive slots not available, find any available slots
        available_slots = []
        for time_slot in time_slots:
            if self._is_slot_available_for_class_enhanced(
                schedule_entries, class_id, day, time_slot
            ):
                available_slots.append(time_slot)
                if len(available_slots) >= hours_needed:
                    return available_slots[:hours_needed]

        return []

    def _can_teacher_teach_at_slots(self, schedule_entries, teacher_id, day, time_slots):
        """Check if a teacher is available for all specified time slots"""
        for time_slot in time_slots:
            # Check if teacher is already scheduled
            for entry in schedule_entries:
                entry_teacher_id = (
                    entry["teacher_id"] if isinstance(entry, dict) else entry.teacher_id
                )
                entry_day = entry["day"] if isinstance(entry, dict) else entry.day
                entry_time_slot = (
                    entry["time_slot"] if isinstance(entry, dict) else entry.time_slot
                )

                if (
                    entry_teacher_id == teacher_id
                    and entry_day == day
                    and entry_time_slot == time_slot
                ):
                    return False

            # Check explicit availability if exists
            if not self.db_manager.is_teacher_available(teacher_id, day, time_slot):
                return False

        return True

    def _can_teacher_teach_at_slots_enhanced(
        self, schedule_entries, teacher_id, day, time_slots
    ):
        """Enhanced teacher availability checking with better conflict detection"""
        for time_slot in time_slots:
            # Check memory schedule conflicts
            for entry in schedule_entries:
                entry_teacher_id = (
                    entry["teacher_id"] if isinstance(entry, dict) else entry.teacher_id
                )
                entry_day = entry["day"] if isinstance(entry, dict) else entry.day
                entry_time_slot = (
                    entry["time_slot"] if isinstance(entry, dict) else entry.time_slot
                )

                if (
                    entry_teacher_id == teacher_id
                    and entry_day == day
                    and entry_time_slot == time_slot
                ):
                    return False

            # Check database schedule conflicts
            existing_schedule = self.db_manager.get_schedule_program_by_school_type()
            for entry in existing_schedule:
                if (
                    entry.teacher_id == teacher_id
                    and entry.day == day
                    and entry.time_slot == time_slot
                ):
                    return False

            # Check explicit availability (STRICT - respect teacher preferences)
            try:
                if not self.db_manager.is_teacher_available(teacher_id, day, time_slot):
                    return False
            except Exception as e:
                # If check fails, assume teacher is available but log for diagnostics
                self.logger.warning(f"Warning: teacher availability check failed: {e}")
                pass

        return True

    def _find_best_slots_aggressive(
        self, schedule_entries, class_id, day, time_slots, hours_needed
    ):
        """Aggressive slot finding with multiple strategies"""
        # Strategy 1: Try consecutive slots
        for start_slot in range(len(time_slots) - hours_needed + 1):
            consecutive_slots = []
            all_available = True

            for i in range(hours_needed):
                time_slot = time_slots[start_slot + i]
                if not self._is_slot_available_for_class_aggressive(
                    schedule_entries, class_id, day, time_slot
                ):
                    all_available = False
                    break
                consecutive_slots.append(time_slot)

            if all_available:
                return consecutive_slots

        # Strategy 2: Try any available slots
        available_slots = []
        for time_slot in time_slots:
            if self._is_slot_available_for_class_aggressive(
                schedule_entries, class_id, day, time_slot
            ):
                available_slots.append(time_slot)
                if len(available_slots) >= hours_needed:
                    return available_slots[:hours_needed]

        return []

    def _can_teacher_teach_at_slots_aggressive(
        self, schedule_entries, teacher_id, day, time_slots
    ):
        """Aggressive teacher availability checking"""
        for time_slot in time_slots:
            # Check memory schedule conflicts
            for entry in schedule_entries:
                entry_teacher_id = (
                    entry["teacher_id"] if isinstance(entry, dict) else entry.teacher_id
                )
                entry_day = entry["day"] if isinstance(entry, dict) else entry.day
                entry_time_slot = (
                    entry["time_slot"] if isinstance(entry, dict) else entry.time_slot
                )

                if (
                    entry_teacher_id == teacher_id
                    and entry_day == day
                    and entry_time_slot == time_slot
                ):
                    return False

            # Check database schedule conflicts
            existing_schedule = self.db_manager.get_schedule_program_by_school_type()
            for entry in existing_schedule:
                if (
                    entry.teacher_id == teacher_id
                    and entry.day == day
                    and entry.time_slot == time_slot
                ):
                    return False

            # Check explicit availability (AGGRESSIVE - respect teacher preferences)
            try:
                if not self.db_manager.is_teacher_available(teacher_id, day, time_slot):
                    return False
            except Exception as e:
                self.logger.warning(f"Warning: teacher availability check failed: {e}")
                pass

        return True

    def _is_slot_available_for_class_aggressive(
        self, schedule_entries, class_id, day, time_slot
    ):
        """Aggressive slot availability checking"""
        # Check memory schedule
        for entry in schedule_entries:
            entry_class_id = (
                entry["class_id"] if isinstance(entry, dict) else entry.class_id
            )
            entry_day = entry["day"] if isinstance(entry, dict) else entry.day
            entry_time_slot = (
                entry["time_slot"] if isinstance(entry, dict) else entry.time_slot
            )

            if (
                entry_class_id == class_id
                and entry_day == day
                and entry_time_slot == time_slot
            ):
                return False

        # Also check database schedule
        existing_schedule = self.db_manager.get_schedule_program_by_school_type()
        for entry in existing_schedule:
            if (
                entry.class_id == class_id
                and entry.day == day
                and entry.time_slot == time_slot
            ):
                return False

        return True

    def _find_lesson_by_name(self, lessons, subject_name, grade):
        """Find a lesson by name, handling special cases for physical education"""
        for lesson in lessons:
            # Handle special case for physical education subjects
            if (
                (
                    subject_name == "Beden Eğitimi ve Oyun"
                    and lesson.name == "Beden Eğitimi ve Oyun"
                )
                or (
                    subject_name == "Beden Eğitimi ve Spor"
                    and lesson.name == "Beden Eğitimi ve Spor"
                )
                or (lesson.name == subject_name)
            ):
                return lesson
        return None

    def _has_conflict(self, schedule_entries, new_entry):
        """Check if a new entry conflicts with existing entries - improved version"""
        new_class_id = (
            new_entry["class_id"] if isinstance(new_entry, dict) else new_entry.class_id
        )
        new_day = new_entry["day"] if isinstance(new_entry, dict) else new_entry.day
        new_time_slot = (
            new_entry["time_slot"] if isinstance(new_entry, dict) else new_entry.time_slot
        )
        new_teacher_id = (
            new_entry["teacher_id"] if isinstance(new_entry, dict) else new_entry.teacher_id
        )

        for entry in schedule_entries:
            # Extract entry data
            if isinstance(entry, dict):
                entry_class_id = entry["class_id"]
                entry_day = entry["day"]
                entry_time_slot = entry["time_slot"]
                entry_teacher_id = entry["teacher_id"]
            else:
                entry_class_id = entry.class_id
                entry_day = entry.day
                entry_time_slot = entry.time_slot
                entry_teacher_id = entry.teacher_id

            # Same time slot check
            if entry_day == new_day and entry_time_slot == new_time_slot:
                # Class conflict: same class cannot be in two places at once
                if entry_class_id == new_class_id:
                    return True

                # Teacher conflict: same teacher cannot teach two classes at once
                if entry_teacher_id == new_teacher_id:
                    return True

        return False

    def _create_lesson_blocks(self, total_hours, num_days):
        """
        Create lesson blocks (consecutive hours) distributed across days
        Returns a list of block sizes with improved distribution
        """
        if total_hours <= 0:
            return []

        blocks = []

        # Strategy based on total hours
        if total_hours <= 2:
            # 1-2 hours: single blocks
            blocks = [1] * total_hours
        elif total_hours <= 4:
            # 3-4 hours: prefer 2-hour blocks
            blocks = [2] * (total_hours // 2)
            if total_hours % 2 == 1:
                blocks.append(1)
        else:
            # 5+ hours: mix of 2-hour and 1-hour blocks
            # Aim for mostly 2-hour blocks with some singles for flexibility
            two_hour_blocks = min(
                total_hours // 2, num_days - 1
            )  # Leave room for singles
            blocks = [2] * two_hour_blocks
            remaining = total_hours - (two_hour_blocks * 2)
            blocks.extend([1] * remaining)

        # Ensure we don't exceed the number of days
        while len(blocks) > num_days and len(blocks) > 1:
            # Combine the two smallest blocks
            blocks.sort()
            smallest = blocks.pop(0)
            second_smallest = blocks.pop(0)
            blocks.append(smallest + second_smallest)

        # Shuffle for random distribution across days
        random.shuffle(blocks)

        return blocks

    def _find_consecutive_slots(
        self, schedule_entries, class_id, day, time_slots, hours_needed
    ):
        """
        Find consecutive available time slots for a class on a specific day
        Returns a list of consecutive time slots or empty list if not found
        """
        # Try different starting positions
        for start_slot in range(len(time_slots) - hours_needed + 1):
            # Check if we can fit hours_needed consecutive slots starting from start_slot
            consecutive_slots = []
            all_available = True

            for i in range(hours_needed):
                time_slot = time_slots[start_slot + i]
                if not self._is_slot_available_for_class(
                    schedule_entries, class_id, day, time_slot
                ):
                    all_available = False
                    break
                consecutive_slots.append(time_slot)

            if all_available:
                return consecutive_slots

        # If we couldn't find consecutive slots, try to find any available slots
        # This is a fallback approach
        available_slots = []
        for time_slot in time_slots:
            if self._is_slot_available_for_class(
                schedule_entries, class_id, day, time_slot
            ):
                available_slots.append(time_slot)
                if len(available_slots) >= hours_needed:
                    # Return the first hours_needed slots (not necessarily consecutive)
                    return available_slots[:hours_needed]

        return []

    def _find_available_teacher_for_period(
        self, schedule_entries, teachers, lesson, day, start_time, end_time
    ):
        """
        Find an available teacher for a period (consecutive time slots)
        """

        # First, get all teachers who can teach this lesson
        eligible_teachers = [
            teacher for teacher in teachers if teacher.subject == lesson.name
        ]

        # Special handling for T.C. İnkılap Tarihi ve Atatürkçülük lesson in 8th grade
        # Allow Sosyal Bilgiler teachers to also teach this subject
        if lesson.name == "T.C. İnkılap Tarihi ve Atatürkçülük":
            # Add Sosyal Bilgiler teachers as eligible for this lesson
            sosyal_bilgiler_teachers = [
                teacher for teacher in teachers if teacher.subject == "Sosyal Bilgiler"
            ]
            eligible_teachers.extend(sosyal_bilgiler_teachers)

        # If no eligible teachers, return None
        if not eligible_teachers:
            self.logger.info(f"No teachers available for subject: {lesson.name}")
            return None

        # Sort teachers by how many hours they've already been scheduled (ascending)
        # This helps distribute hours more evenly
        teacher_hours = {}
        for teacher in eligible_teachers:
            count = 0
            for entry in schedule_entries:
                # Handle both dictionary and ScheduleEntry object formats
                entry_teacher_id = (
                    entry["teacher_id"] if isinstance(entry, dict) else entry.teacher_id
                )
                if entry_teacher_id == teacher.teacher_id:
                    count += 1
            teacher_hours[teacher.teacher_id] = count

        eligible_teachers.sort(key=lambda t: teacher_hours[t.teacher_id])

        # Try each eligible teacher
        for teacher in eligible_teachers:
            # Check if teacher is available for all time slots in this period
            teacher_available = True
            for time_slot in range(start_time, end_time + 1):
                # Check if teacher is already scheduled at this time
                for entry in schedule_entries:
                    # Handle both dictionary and ScheduleEntry object formats
                    entry_teacher_id = (
                        entry["teacher_id"]
                        if isinstance(entry, dict)
                        else entry.teacher_id
                    )
                    entry_day = entry["day"] if isinstance(entry, dict) else entry.day
                    entry_time_slot = (
                        entry["time_slot"]
                        if isinstance(entry, dict)
                        else entry.time_slot
                    )

                    if (
                        entry_teacher_id == teacher.teacher_id
                        and entry_day == day
                        and entry_time_slot == time_slot
                    ):
                        teacher_available = False
                        break

                if not teacher_available:
                    break

                # Check if teacher is explicitly available for this time slot
                if not self.db_manager.is_teacher_available(
                    teacher.teacher_id, day, time_slot
                ):
                    teacher_available = False
                    break

            if teacher_available:
                return teacher

        # If no teacher with explicit availability is found, try any teacher who is not already scheduled
        # but only if they have the right subject
        for teacher in eligible_teachers:
            teacher_available = True
            for time_slot in range(start_time, end_time + 1):
                for entry in schedule_entries:
                    # Handle both dictionary and ScheduleEntry object formats
                    entry_teacher_id = (
                        entry["teacher_id"]
                        if isinstance(entry, dict)
                        else entry.teacher_id
                    )
                    entry_day = entry["day"] if isinstance(entry, dict) else entry.day
                    entry_time_slot = (
                        entry["time_slot"]
                        if isinstance(entry, dict)
                        else entry.time_slot
                    )

                    if (
                        entry_teacher_id == teacher.teacher_id
                        and entry_day == day
                        and entry_time_slot == time_slot
                    ):
                        teacher_available = False
                        break
                if not teacher_available:
                    break

            if teacher_available:
                return teacher

        return None

    def _is_slot_available_for_class(self, schedule_entries, class_id, day, time_slot):
        """Check if a time slot is available for a class"""
        for entry in schedule_entries:
            # Handle both dictionary and ScheduleEntry object formats
            entry_class_id = (
                entry["class_id"] if isinstance(entry, dict) else entry.class_id
            )
            entry_day = entry["day"] if isinstance(entry, dict) else entry.day
            entry_time_slot = (
                entry["time_slot"] if isinstance(entry, dict) else entry.time_slot
            )

            if (
                entry_class_id == class_id
                and entry_day == day
                and entry_time_slot == time_slot
            ):
                return False
        return True

    def _is_slot_available_for_class_enhanced(
        self, schedule_entries, class_id, day, time_slot
    ):
        """Enhanced slot availability checking with database validation"""
        # Check memory schedule
        for entry in schedule_entries:
            entry_class_id = (
                entry["class_id"] if isinstance(entry, dict) else entry.class_id
            )
            entry_day = entry["day"] if isinstance(entry, dict) else entry.day
            entry_time_slot = (
                entry["time_slot"] if isinstance(entry, dict) else entry.time_slot
            )

            if (
                entry_class_id == class_id
                and entry_day == day
                and entry_time_slot == time_slot
            ):
                return False

        # Also check database schedule
        existing_schedule = self.db_manager.get_schedule_program_by_school_type()
        for entry in existing_schedule:
            if (
                entry.class_id == class_id
                and entry.day == day
                and entry.time_slot == time_slot
            ):
                return False

        return True

    def _distribute_hours_evenly(self, total_hours, num_days):
        """
        Distribute hours evenly across days
        Returns a list with hours per day
        """
        if total_hours <= 0 or num_days <= 0:
            return [0] * num_days

        # Calculate base hours per day
        base_hours = total_hours // num_days
        remainder = total_hours % num_days

        # Create distribution list
        distribution = [base_hours] * num_days

        # Distribute remainder hours
        for i in range(remainder):
            distribution[i] += 1

        return distribution

    def _find_available_teacher(self, schedule_entries, teachers, lesson, day, time_slot):
        """
        Find an available teacher for a lesson at a specific time
        """
        # First, get all teachers who can teach this lesson
        eligible_teachers = [teacher for teacher in teachers if teacher.subject == lesson.name]

        # Special handling for T.C. İnkılap Tarihi ve Atatürkçülük lesson in 8th grade
        # Allow Sosyal Bilgiler teachers to also teach this subject
        if lesson.name == "T.C. İnkılap Tarihi ve Atatürkçülük":
            # Add Sosyal Bilgiler teachers as eligible for this lesson
            sosyal_bilgiler_teachers = [
                teacher for teacher in teachers if teacher.subject == "Sosyal Bilgiler"
            ]
            eligible_teachers.extend(sosyal_bilgiler_teachers)

        # If no eligible teachers, return None
        if not eligible_teachers:
            return None

        # Try each eligible teacher
        for teacher in eligible_teachers:
            # Check if teacher is already scheduled at this time
            teacher_scheduled = False
            for entry in schedule_entries:
                # Handle both dictionary and ScheduleEntry object formats
                entry_teacher_id = (
                    entry["teacher_id"] if isinstance(entry, dict) else entry.teacher_id
                )
                entry_day = entry["day"] if isinstance(entry, dict) else entry.day
                entry_time_slot = entry["time_slot"] if isinstance(entry, dict) else entry.time_slot

                if (
                    entry_teacher_id == teacher.teacher_id
                    and entry_day == day
                    and entry_time_slot == time_slot
                ):
                    teacher_scheduled = True
                    break

            if not teacher_scheduled:
                # Check if teacher is explicitly available for this time slot
                if self.db_manager.is_teacher_available(teacher.teacher_id, day, time_slot):
                    return teacher

        return None

    def _find_available_classroom(self, schedule_entries, classrooms, day, time_slot):
        """
        Find an available classroom at a specific time
        """
        # Try each classroom
        for classroom in classrooms:
            # Check if classroom is already scheduled at this time
            classroom_scheduled = False
            for entry in schedule_entries:
                # Handle both dictionary and ScheduleEntry object formats
                entry_classroom_id = (
                    entry["classroom_id"] if isinstance(entry, dict) else entry.classroom_id
                )
                entry_day = entry["day"] if isinstance(entry, dict) else entry.day
                entry_time_slot = entry["time_slot"] if isinstance(entry, dict) else entry.time_slot

                if (
                    entry_classroom_id == classroom.classroom_id
                    and entry_day == day
                    and entry_time_slot == time_slot
                ):
                    classroom_scheduled = True
                    break

            if not classroom_scheduled:
                return classroom

        return None

    def detect_conflicts(self, schedule_entries):
        """
        Detect conflicts in a schedule
        Returns a list of conflicts
        """
        conflicts = []

        # Check for teacher conflicts (same teacher at same time)
        teacher_slots = {}
        for entry in schedule_entries:
            # Handle both dictionary and ScheduleEntry object formats
            entry_teacher_id = (
                entry["teacher_id"] if isinstance(entry, dict) else entry.teacher_id
            )
            entry_day = entry["day"] if isinstance(entry, dict) else entry.day
            entry_time_slot = (
                entry["time_slot"] if isinstance(entry, dict) else entry.time_slot
            )

            key = (entry_teacher_id, entry_day, entry_time_slot)
            if key in teacher_slots:
                conflicts.append(
                    {
                        "type": "teacher_conflict",
                        "entry1": teacher_slots[key],
                        "entry2": entry,
                    }
                )
            else:
                teacher_slots[key] = entry

        # Check for class conflicts (same class at same time)
        class_slots = {}
        for entry in schedule_entries:
            # Handle both dictionary and ScheduleEntry object formats
            entry_class_id = (
                entry["class_id"] if isinstance(entry, dict) else entry.class_id
            )
            entry_day = entry["day"] if isinstance(entry, dict) else entry.day
            entry_time_slot = (
                entry["time_slot"] if isinstance(entry, dict) else entry.time_slot
            )

            key = (entry_class_id, entry_day, entry_time_slot)
            if key in class_slots:
                conflicts.append(
                    {
                        "type": "class_conflict",
                        "entry1": class_slots[key],
                        "entry2": entry,
                    }
                )
            else:
                class_slots[key] = entry

        return conflicts
