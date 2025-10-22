# -*- coding: utf-8 -*-
"""
Interactive Scheduler - User-Driven Schedule Editing
Allows users to lock entries, get suggestions, and validate in real-time
"""

import io
import sys
import time
import threading
from collections import defaultdict
from typing import Dict, List, Optional, Callable, Tuple

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class InteractiveScheduler:
    """
    Interactive scheduler for user-driven editing

    Features:
    - Lock specific entries (user-defined)
    - Suggest alternative slots
    - Real-time validation
    - Undo/redo support
    - Conflict detection
    - Quality scoring
    """

    def __init__(self, db_manager):
        """
        Initialize interactive scheduler

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # Current schedule state
        self.schedule: List[Dict] = []

        # Locked entries (cannot be modified by auto-scheduler)
        self.locked_entries: Set[int] = set()  # Set of entry indices

        # History for undo/redo
        self.history: List[List[Dict]] = []
        self.history_index = -1

        # Real-time optimization thread
        self.optimization_thread = None
        self.stop_optimization = threading.Event()

        # Performance monitoring
        self.performance_stats = {
            'total_moves': 0,
            'conflicts_resolved': 0,
            'optimization_time': 0.0,
            'suggestions_generated': 0
        }

        self.max_history: int = 50

        # Conflict tracking
        self.conflicts: List[Dict] = []

    def load_schedule(self, schedule: List[Dict]):
        """
        Load a schedule for editing

        Args:
            schedule: Schedule entries
        """
        self.schedule = schedule.copy()
        self._save_to_history()
        self._detect_conflicts()

        self.logger.info(f"Loaded schedule with {len(schedule)} entries")

    def lock_entry(self, entry_index: int) -> bool:
        """
        Lock an entry to prevent modification

        Args:
            entry_index: Index of entry in schedule

        Returns:
            True if locked successfully
        """
        if 0 <= entry_index < len(self.schedule):
            self.locked_entries.add(entry_index)
            self.logger.info(f"Locked entry {entry_index}")
            return True
        return False

    def unlock_entry(self, entry_index: int) -> bool:
        """
        Unlock an entry

        Args:
            entry_index: Index of entry in schedule

        Returns:
            True if unlocked successfully
        """
        if entry_index in self.locked_entries:
            self.locked_entries.remove(entry_index)
            self.logger.info(f"Unlocked entry {entry_index}")
            return True
        return False

    def is_locked(self, entry_index: int) -> bool:
        """Check if entry is locked"""
        return entry_index in self.locked_entries

    def move_entry(self, entry_index: int, new_day: int, new_slot: int) -> Tuple[bool, Optional[str]]:
        """
        Move an entry to a new time slot

        Args:
            entry_index: Index of entry to move
            new_day: New day (0-4)
            new_slot: New time slot (0-7)

        Returns:
            (success, error_message) tuple
        """
        # Check if entry exists
        if entry_index < 0 or entry_index >= len(self.schedule):
            return False, "Entry index out of range"

        # Check if locked
        if self.is_locked(entry_index):
            return False, "Entry is locked"

        entry = self.schedule[entry_index]
        old_day = entry["day"]
        old_slot = entry["time_slot"]

        # Check if new slot is valid
        can_place, reason = self._can_place_at(
            entry["class_id"], entry["teacher_id"], new_day, new_slot, exclude_index=entry_index
        )

        if not can_place:
            return False, reason

        # Move entry
        entry["day"] = new_day
        entry["time_slot"] = new_slot

        # Save to history before modification
        self._save_to_history()

        # Update conflicts
        self._detect_conflicts()

        self.logger.info(
            f"Moved entry {entry_index} from Day {old_day} Slot {old_slot} " f"to Day {new_day} Slot {new_slot}"
        )

        return True, None

    def suggest_alternatives(self, entry_index: int, max_suggestions: int = 5) -> List[Dict]:
        """
        Suggest alternative slots for an entry

        Args:
            entry_index: Index of entry
            max_suggestions: Maximum number of suggestions

        Returns:
            List of suggestion dicts with 'day', 'slot', 'score', 'reason'
        """
        if entry_index < 0 or entry_index >= len(self.schedule):
            return []

        entry = self.schedule[entry_index]
        suggestions = []

        # Try all possible slots
        for day in range(5):
            for slot in range(8):
                # Skip current slot
                if day == entry["day"] and slot == entry["time_slot"]:
                    continue

                # Check if can place
                can_place, reason = self._can_place_at(
                    entry["class_id"], entry["teacher_id"], day, slot, exclude_index=entry_index
                )

                if can_place:
                    # Calculate score for this slot
                    score = self._score_slot(entry["class_id"], entry["lesson_id"], entry["teacher_id"], day, slot)

                    suggestions.append(
                        {
                            "day": day,
                            "slot": slot,
                            "score": score,
                            "reason": self._get_slot_reason(day, slot, score),
                        }
                    )

        # Sort by score (descending)
        suggestions.sort(key=lambda x: x["score"], reverse=True)

    def start_realtime_optimization(self, interval: float = 1.0):
        """Gerçek zamanlı optimizasyon thread'ini başlat"""
        if self.optimization_thread and self.optimization_thread.is_alive():
            return

        self.stop_optimization.clear()
        self.optimization_thread = threading.Thread(target=self._realtime_optimization_loop, args=(interval,))
        self.optimization_thread.daemon = True
        self.optimization_thread.start()
        self.logger.info("Gerçek zamanlı optimizasyon başlatıldı")

    def stop_realtime_optimization(self):
        """Gerçek zamanlı optimizasyon thread'ini durdur"""
        self.stop_optimization.set()
        if self.optimization_thread:
            self.optimization_thread.join(timeout=2.0)
        self.logger.info("Gerçek zamanlı optimizasyon durduruldu")

    def _realtime_optimization_loop(self, interval: float):
        """Gerçek zamanlı optimizasyon döngüsü"""
        while not self.stop_optimization.is_set():
            try:
                # Performansı kaydet
                start_time = time.time()

                # Çakışmaları tespit et ve otomatik çözmeye çalış
                initial_conflicts = len(self.conflicts)
                if initial_conflicts > 0:
                    self._auto_resolve_conflicts()

                # Performansı güncelle
                end_time = time.time()
                self.performance_stats['optimization_time'] += (end_time - start_time)

                # Kısa bir bekleme
                time.sleep(interval)

            except Exception as e:
                self.logger.error(f"Gerçek zamanlı optimizasyon hatası: {e}")
                time.sleep(interval)

    def _auto_resolve_conflicts(self):
        """Otomatik çakışma çözümü"""
        if not self.conflicts:
            return

        resolved_count = 0

        for conflict in self.conflicts[:]:  # Copy list to avoid modification during iteration
            if self._try_resolve_conflict(conflict):
                self.conflicts.remove(conflict)
                resolved_count += 1

        if resolved_count > 0:
            self.performance_stats['conflicts_resolved'] += resolved_count
            self.logger.info(f"Otomatik olarak {resolved_count} çakışma çözüldü")

    def _try_resolve_conflict(self, conflict: Dict) -> bool:
        """Tek bir çakışmayı çözmeye çalış"""
        try:
            # Basit heuristic: Rastgele bir çakışan entry'i başka bir slot'a taşı
            conflicting_entries = conflict.get('entries', [])

            if len(conflicting_entries) >= 2:
                # İlk entry'i başka bir slot'a taşı
                entry_to_move = conflicting_entries[0]
                entry_index = self._find_entry_index(entry_to_move)

                if entry_index >= 0 and not self.is_locked(entry_index):
                    # Uygun alternatif slotlar bul
                    alternatives = self.suggest_alternatives(entry_index, max_suggestions=3)

                    for alt in alternatives:
                        success, _ = self.move_entry(entry_index, alt['day'], alt['slot'])
                        if success:
                            return True

        except Exception as e:
            self.logger.warning(f"Çakışma çözümü hatası: {e}")

        return False

    def _find_entry_index(self, target_entry: Dict) -> int:
        """Entry'nin schedule'daki index'ini bul"""
        for i, entry in enumerate(self.schedule):
            if (entry['class_id'] == target_entry['class_id'] and
                entry['teacher_id'] == target_entry['teacher_id'] and
                entry['lesson_id'] == target_entry['lesson_id'] and
                entry['day'] == target_entry['day'] and
                entry['time_slot'] == target_entry['time_slot']):
                return i
        return -1

    def _score_slot(self, class_id: int, lesson_id: int, teacher_id: int, day: int, slot: int) -> float:
        """Slot için puan hesapla (yüksek = daha iyi)"""
        score = 50.0  # Base score

        # Gün tercihi (Pazartesi daha iyi)
        score += (4 - day) * 2

        # Slot tercihi (Sabah saatleri daha iyi)
        if slot <= 2:
            score += 10
        elif slot <= 4:
            score += 5
        elif slot >= 6:
            score -= 5

        # Öğretmen uygunluğu kontrolü
        try:
            if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                score -= 20
        except:
            pass

        return score

    def _get_slot_reason(self, day: int, slot: int, score: float) -> str:
        """Slot için neden açıklama"""
        reasons = []

        if score >= 60:
            reasons.append("Mükemmel tercih")
        elif score >= 50:
            reasons.append("İyi tercih")
        elif score >= 40:
            reasons.append("Uygun tercih")
        else:
            reasons.append("Son çare")

        day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        reasons.append(f"{day_names[day]} günü")

        if slot <= 2:
            reasons.append("Sabah saati")
        elif slot >= 6:
            reasons.append("Akşam saati")

        return ", ".join(reasons)

    def get_performance_report(self) -> Dict:
        """Performans istatistiklerini döndür"""
        return self.performance_stats.copy()

    def get_quality_score(self) -> float:
        """Schedule kalite puanını hesapla (0-100)"""
        if not self.schedule:
            return 100.0

        # Çakışma sayısı bazlı puanlama
        conflict_penalty = len(self.conflicts) * 10

        # Kilitli entry bonus
        locked_bonus = len(self.locked_entries) * 2

        # Hareket sayısı bonus
        move_bonus = min(self.performance_stats['total_moves'] * 0.5, 20)

        score = 100.0 - conflict_penalty + locked_bonus + move_bonus

        return max(0.0, min(100.0, score))

    def add_entry(
        self, class_id: int, teacher_id: int, lesson_id: int, classroom_id: int, day: int, slot: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Add a new entry to schedule

        Args:
            class_id: Class ID
            teacher_id: Teacher ID
            lesson_id: Lesson ID
            classroom_id: Classroom ID
            day: Day (0-4)
            slot: Time slot (0-7)

        Returns:
            (success, error_message) tuple
        """
        # Check if can place
        can_place, reason = self._can_place_at(class_id, teacher_id, day, slot)

        if not can_place:
            return False, reason

        # Add entry
        new_entry = {
            "class_id": class_id,
            "teacher_id": teacher_id,
            "lesson_id": lesson_id,
            "classroom_id": classroom_id,
            "day": day,
            "time_slot": slot,
        }

        self.schedule.append(new_entry)

        # Save to history
        self._save_to_history()

        # Update conflicts
        self._detect_conflicts()

        self.logger.info(f"Added new entry: {new_entry}")

        return True, None

    def remove_entry(self, entry_index: int) -> Tuple[bool, Optional[str]]:
        """
        Remove an entry from schedule

        Args:
            entry_index: Index of entry to remove

        Returns:
            (success, error_message) tuple
        """
        if entry_index < 0 or entry_index >= len(self.schedule):
            return False, "Entry index out of range"

        if self.is_locked(entry_index):
            return False, "Entry is locked"

        # Remove entry
        removed = self.schedule.pop(entry_index)

        # Save to history
        self._save_to_history()

        # Update locked entries indices
        self.locked_entries = {i if i < entry_index else i - 1 for i in self.locked_entries if i != entry_index}

        # Update conflicts
        self._detect_conflicts()

        self.logger.info(f"Removed entry {entry_index}: {removed}")

        return True, None

    def undo(self) -> bool:
        """
        Undo last change

        Returns:
            True if undo successful
        """
        if self.history_index > 0:
            self.history_index -= 1
            self.schedule = self.history[self.history_index].copy()
            self._detect_conflicts()
            self.logger.info("Undo successful")
            return True
        return False

    def redo(self) -> bool:
        """
        Redo last undone change

        Returns:
            True if redo successful
        """
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.schedule = self.history[self.history_index].copy()
            self._detect_conflicts()
            self.logger.info("Redo successful")
            return True
        return False

    def validate(self) -> Dict:
        """
        Validate current schedule

        Returns:
            Dict with validation results
        """
        self._detect_conflicts()

        # Calculate coverage
        classes = self.db_manager.get_all_classes()
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = 8 if "Lise" in school_type else 7

        total_slots = len(classes) * 5 * time_slots_count
        coverage = (len(self.schedule) / total_slots * 100) if total_slots > 0 else 0

        # Calculate quality score
        quality_score = self._calculate_quality_score()

        return {
            "is_valid": len(self.conflicts) == 0,
            "conflicts": self.conflicts,
            "conflict_count": len(self.conflicts),
            "coverage": coverage,
            "entry_count": len(self.schedule),
            "locked_count": len(self.locked_entries),
            "quality_score": quality_score,
        }

    def get_schedule(self) -> List[Dict]:
        """Get current schedule"""
        return self.schedule.copy()

    def save_to_database(self) -> bool:
        """Save current schedule to database"""
        try:
            self.db_manager.clear_schedule()

            for entry in self.schedule:
                self.db_manager.add_schedule_program(
                    entry["class_id"],
                    entry["teacher_id"],
                    entry["lesson_id"],
                    entry["classroom_id"],
                    entry["day"],
                    entry["time_slot"],
                )

            self.logger.info(f"Saved {len(self.schedule)} entries to database")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save to database: {e}")
            return False

    def _can_place_at(
        self,
        class_id: int,
        teacher_id: int,
        day: int,
        slot: int,
        exclude_index: Optional[int] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Check if can place at slot"""
        for i, entry in enumerate(self.schedule):
            # Skip excluded entry
            if exclude_index is not None and i == exclude_index:
                continue

            if entry["day"] == day and entry["time_slot"] == slot:
                # Check class conflict
                if entry["class_id"] == class_id:
                    return False, "Class already has a lesson at this time"

                # Check teacher conflict
                if entry["teacher_id"] == teacher_id:
                    return False, "Teacher already teaching at this time"

        # Check teacher availability
        try:
            if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                return False, "Teacher not available at this time"
        except Exception as e:
            self.logger.warning(f"Error while checking teacher availability: {e}")
            # fall back to safe behavior: treat as unknown/unavailable
            return False, "Teacher availability unknown"

        return True, None

    def _detect_conflicts(self):
        """Detect conflicts in current schedule"""
        self.conflicts = []

        # Check class conflicts
        class_slots = defaultdict(list)
        for i, entry in enumerate(self.schedule):
            key = (entry["class_id"], entry["day"], entry["time_slot"])
            class_slots[key].append(i)

        for key, indices in class_slots.items():
            if len(indices) > 1:
                self.conflicts.append(
                    {
                        "type": "class_conflict",
                        "indices": indices,
                        "class_id": key[0],
                        "day": key[1],
                        "slot": key[2],
                    }
                )

        # Check teacher conflicts
        teacher_slots = defaultdict(list)
        for i, entry in enumerate(self.schedule):
            key = (entry["teacher_id"], entry["day"], entry["time_slot"])
            teacher_slots[key].append(i)

        for key, indices in teacher_slots.items():
            if len(indices) > 1:
                self.conflicts.append(
                    {
                        "type": "teacher_conflict",
                        "indices": indices,
                        "teacher_id": key[0],
                        "day": key[1],
                        "slot": key[2],
                    }
                )

    def _score_slot(self, class_id: int, lesson_id: int, teacher_id: int, day: int, slot: int) -> float:
        """Score a slot for quality"""
        score = 50.0  # Base score

        # Morning bonus for difficult lessons
        lesson = self.db_manager.get_lesson_by_id(lesson_id)
        if lesson:
            difficult_lessons = ["Matematik", "Fizik", "Kimya", "Biyoloji"]
            if lesson.name in difficult_lessons and slot < 4:
                score += 15

        # Avoid late slots
        if slot >= 6:
            score -= 10

        # Check for gaps
        class_slots_today = [e["time_slot"] for e in self.schedule if e["class_id"] == class_id and e["day"] == day]

        if class_slots_today:
            min_slot = min(class_slots_today)
            max_slot = max(class_slots_today)

            # Prefer slots that don't create gaps
            if min_slot <= slot <= max_slot:
                # Check if creates gap
                all_slots = sorted(class_slots_today + [slot])
                has_gap = any(all_slots[i + 1] - all_slots[i] > 1 for i in range(len(all_slots) - 1))
                if has_gap:
                    score -= 20
                else:
                    score += 10

        return score

    def _get_slot_reason(self, day: int, slot: int, score: float) -> str:
        """Get reason for slot score"""
        reasons = []

        if slot < 4:
            reasons.append("Morning slot")
        if slot >= 6:
            reasons.append("Late slot")
        if score > 60:
            reasons.append("High quality")
        elif score < 40:
            reasons.append("Low quality")

        return ", ".join(reasons) if reasons else "Neutral"

    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score"""
        if not self.schedule:
            return 0.0

        score = 100.0

        # Penalty for conflicts
        score -= len(self.conflicts) * 10

        # Penalty for gaps
        gap_count = self._count_gaps()
        score -= gap_count * 5

        # Bonus for good distribution
        distribution_score = self._calculate_distribution_score()
        score += distribution_score

        return max(0.0, min(100.0, score))

    def _count_gaps(self) -> int:
        """Count gaps in schedule"""
        gaps = 0

        for class_id in set(e["class_id"] for e in self.schedule):
            for day in range(5):
                slots = sorted([e["time_slot"] for e in self.schedule if e["class_id"] == class_id and e["day"] == day])

                if len(slots) > 1:
                    for i in range(len(slots) - 1):
                        if slots[i + 1] - slots[i] > 1:
                            gaps += 1

        return gaps

    def _calculate_distribution_score(self) -> float:
        """Calculate distribution quality score"""
        # Check if lessons are well distributed across days
        lesson_days = defaultdict(set)

        for entry in self.schedule:
            key = (entry["class_id"], entry["lesson_id"])
            lesson_days[key].add(entry["day"])

        # Prefer lessons spread across multiple days
        distribution_score = 0.0
        for days in lesson_days.values():
            if len(days) >= 3:
                distribution_score += 2
            elif len(days) == 2:
                distribution_score += 1

        return min(distribution_score, 20.0)

    def _save_to_history(self):
        """Save current state to history"""
        # Remove future history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[: self.history_index + 1]

        # Add current state
        self.history.append(self.schedule.copy())
        self.history_index += 1

        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
