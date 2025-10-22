# -*- coding: utf-8 -*-
"""
ML Scheduler - Machine Learning Integration for Schedule Optimization
Learns from historical schedules to predict optimal placements
"""

import numpy as np
from collections import Counter
import json

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class MLScheduler:
    """
    Machine Learning-based scheduler

    Features:
    - Learn from historical schedules
    - Predict optimal slot placements
    - Feature extraction from schedule context
    - Model training and persistence
    - Adaptive constraint weights

    Note: This is a foundation for ML integration.
    Actual ML models (scikit-learn, TensorFlow) can be added later.
    """

    def __init__(self, db_manager):
        """
        Initialize ML scheduler

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # Historical data storage
        self.historical_schedules: List[Dict] = []
        self.feature_data: List[Dict] = []

        # AI Models (simplified for now)
        self.pattern_recognizer = SchedulePatternRecognizer()
        self.conflict_predictor = ConflictPredictor()
        self.optimization_suggester = OptimizationSuggester()

        # Training data
        self.training_features = []
        self.training_labels = []

        # Model performance tracking
        self.model_accuracy = {
            'pattern_recognition': 0.0,
            'conflict_prediction': 0.0,
            'optimization_suggestions': 0.0
        }

class SchedulePatternRecognizer:
    """Schedule pattern recognition using statistical analysis"""

    def __init__(self):
        self.patterns = defaultdict(Counter)
        self.common_patterns = []

    def analyze_schedule(self, schedule: List[Dict]) -> Dict:
        """Analyze schedule for patterns"""
        patterns = {
            'day_distribution': Counter(),
            'slot_distribution': Counter(),
            'teacher_workload': Counter(),
            'class_workload': Counter(),
            'lesson_patterns': defaultdict(list)
        }

        for entry in schedule:
            day = entry['day']
            slot = entry['time_slot']
            teacher_id = entry['teacher_id']
            class_id = entry['class_id']
            lesson_id = entry['lesson_id']

            patterns['day_distribution'][day] += 1
            patterns['slot_distribution'][slot] += 1
            patterns['teacher_workload'][teacher_id] += 1
            patterns['class_workload'][class_id] += 1

            # Lesson patterns per class
            patterns['lesson_patterns'][f"{class_id}_{lesson_id}"].append((day, slot))

        return patterns

    def find_optimal_patterns(self, patterns: Dict) -> List[str]:
        """Find optimal patterns from historical data"""
        optimal_patterns = []

        # Find most common successful patterns
        if patterns['day_distribution']:
            most_common_day = patterns['day_distribution'].most_common(1)[0][0]
            optimal_patterns.append(f"Most lessons on day {most_common_day}")

        if patterns['slot_distribution']:
            most_common_slots = [slot for slot, count in patterns['slot_distribution'].most_common(3)]
            optimal_patterns.append(f"Popular slots: {most_common_slots}")

        return optimal_patterns


class ConflictPredictor:
    """Predict potential conflicts using historical data"""

    def __init__(self):
        self.conflict_history = []
        self.prediction_accuracy = 0.0

    def predict_conflicts(self, schedule: List[Dict], new_entry: Dict) -> List[Dict]:
        """Predict potential conflicts for a new entry"""
        potential_conflicts = []

        # Simple heuristic-based prediction
        new_day = new_entry['day']
        new_slot = new_entry['time_slot']
        new_teacher = new_entry['teacher_id']
        new_class = new_entry['class_id']

        # Check for teacher conflicts
        teacher_conflicts = [e for e in schedule
                           if e['teacher_id'] == new_teacher
                           and e['day'] == new_day
                           and e['time_slot'] == new_slot]

        if teacher_conflicts:
            potential_conflicts.append({
                'type': 'teacher_conflict',
                'severity': 'high',
                'description': f'Öğretmen {new_teacher} zaten bu saatte başka bir ders veriyor'
            })

        # Check for class conflicts
        class_conflicts = [e for e in schedule
                          if e['class_id'] == new_class
                          and e['day'] == new_day
                          and e['time_slot'] == new_slot]

        if class_conflicts:
            potential_conflicts.append({
                'type': 'class_conflict',
                'severity': 'high',
                'description': f'Sınıf {new_class} zaten bu saatte başka bir ders alıyor'
            })

        # Check for consecutive lessons (might be too many)
        consecutive_count = 0
        for entry in schedule:
            if (entry['class_id'] == new_class and
                entry['day'] == new_day and
                abs(entry['time_slot'] - new_slot) == 1):
                consecutive_count += 1

        if consecutive_count >= 3:
            potential_conflicts.append({
                'type': 'consecutive_warning',
                'severity': 'medium',
                'description': f'Sınıf {new_class} aynı günde çok fazla ardışık ders alacak'
            })

        return potential_conflicts

    def learn_from_conflicts(self, schedule: List[Dict], actual_conflicts: List[Dict]):
        """Learn from actual vs predicted conflicts"""
        # Simple learning - just store patterns
        self.conflict_history.append({
            'schedule_size': len(schedule),
            'conflict_count': len(actual_conflicts),
            'timestamp': time.time()
        })


class OptimizationSuggester:
    """Suggest optimizations based on historical data"""

    def __init__(self):
        self.optimization_history = []
        self.successful_moves = []

    def suggest_optimizations(self, schedule: List[Dict], conflicts: List[Dict]) -> List[Dict]:
        """Suggest specific optimizations"""
        suggestions = []

        if not conflicts:
            return suggestions

        # Suggest moving conflicting entries
        for conflict in conflicts:
            if conflict['type'] == 'teacher_conflict':
                suggestions.append({
                    'type': 'move_teacher',
                    'priority': 'high',
                    'description': 'Öğretmen çakışmasını çözmek için alternatif slot önerisi',
                    'action': 'suggest_alternative_slots'
                })
            elif conflict['type'] == 'class_conflict':
                suggestions.append({
                    'type': 'move_class',
                    'priority': 'high',
                    'description': 'Sınıf çakışmasını çözmek için alternatif slot önerisi',
                    'action': 'suggest_alternative_slots'
                })

        # General optimizations
        suggestions.append({
            'type': 'redistribute',
            'priority': 'medium',
            'description': 'Dersleri haftaya daha dengeli dağıt',
            'action': 'redistribute_lessons'
        })

        return suggestions

    def record_successful_move(self, move_type: str, before_score: float, after_score: float):
        """Record successful optimization moves"""
        self.successful_moves.append({
            'move_type': move_type,
            'improvement': after_score - before_score,
            'timestamp': time.time()
        })

    def extract_features(
        self,
        class_id: int,
        lesson_id: int,
        teacher_id: int,
        day: int,
        slot: int,
        current_schedule: List[Dict],
    ) -> Dict:
        """
        Extract features for ML prediction

        Features include:
        - Time of day (morning/afternoon)
        - Day of week
        - Teacher workload on that day
        - Class schedule density
        - Lesson difficulty
        - Historical success rate for similar placements

        Args:
            class_id: Class ID
            lesson_id: Lesson ID
            teacher_id: Teacher ID
            day: Day (0-4)
            slot: Time slot (0-7)
            current_schedule: Current schedule state

        Returns:
            Dict of features
        """
        features = {}

        # Basic features
        features["day"] = day
        features["slot"] = slot
        features["is_morning"] = 1 if slot < 4 else 0
        features["is_afternoon"] = 1 if slot >= 4 else 0

        # Teacher workload features
        teacher_hours_today = sum(1 for e in current_schedule if e["teacher_id"] == teacher_id and e["day"] == day)
        features["teacher_hours_today"] = teacher_hours_today
        features["teacher_is_busy"] = 1 if teacher_hours_today >= 4 else 0

        # Class schedule density
        class_hours_today = sum(1 for e in current_schedule if e["class_id"] == class_id and e["day"] == day)
        features["class_hours_today"] = class_hours_today
        features["class_has_gap"] = self._check_gap(current_schedule, class_id, day, slot)

        # Lesson features
        lesson = self.db_manager.get_lesson_by_id(lesson_id)
        if lesson:
            features["lesson_name"] = lesson.name
            features["is_difficult_lesson"] = self._is_difficult_lesson(lesson.name)
        else:
            features["lesson_name"] = "Unknown"
            features["is_difficult_lesson"] = 0

        # Historical success rate
        features["historical_success"] = self._get_historical_success_rate(lesson_id, day, slot)

        return features

    def predict_best_slot(
        self,
        class_id: int,
        lesson_id: int,
        teacher_id: int,
        available_slots: List[Tuple[int, int]],
        current_schedule: List[Dict],
    ) -> Optional[Tuple[int, int]]:
        """
        Predict the best slot for a lesson using ML

        Args:
            class_id: Class ID
            lesson_id: Lesson ID
            teacher_id: Teacher ID
            available_slots: List of (day, slot) tuples
            current_schedule: Current schedule state

        Returns:
            Best (day, slot) tuple or None
        """
        if not available_slots:
            return None

        if not self.is_trained:
            # Fallback to heuristic-based selection
            return self._heuristic_selection(class_id, lesson_id, teacher_id, available_slots, current_schedule)

        # Score each available slot
        slot_scores = []

        for day, slot in available_slots:
            features = self.extract_features(class_id, lesson_id, teacher_id, day, slot, current_schedule)

            # Predict score (placeholder - replace with actual ML model)
            score = self._calculate_score_from_features(features)

            slot_scores.append((score, day, slot))

        # Sort by score (descending)
        slot_scores.sort(reverse=True)

        # Return best slot
        best_score, best_day, best_slot = slot_scores[0]

        self.logger.info(f"ML predicted best slot: Day {best_day}, Slot {best_slot} " f"(score: {best_score:.2f})")

        return (best_day, best_slot)

    def learn_from_schedule(self, schedule: List[Dict], quality_metrics: Dict):
        """
        Learn from a completed schedule

        Args:
            schedule: Schedule entries
            quality_metrics: Quality metrics (coverage, conflicts, etc.)
        """
        # Store historical schedule
        historical_entry = {
            "schedule": schedule,
            "metrics": quality_metrics,
            "timestamp": self._get_timestamp(),
        }

        self.historical_schedules.append(historical_entry)

        # Extract features from this schedule
        for entry in schedule:
            features = self.extract_features(
                entry["class_id"],
                entry["lesson_id"],
                entry["teacher_id"],
                entry["day"],
                entry["time_slot"],
                schedule,
            )

            # Add quality label
            features["quality_score"] = quality_metrics.get("coverage", 0)
            features["had_conflicts"] = 1 if quality_metrics.get("conflicts", 0) > 0 else 0

            self.feature_data.append(features)

        self.logger.info(
            f"Learned from schedule: {len(schedule)} entries, " f"coverage: {quality_metrics.get('coverage', 0):.1f}%"
        )

    def train_model(self):
        """
        Train ML model from historical data

        Note: This is a placeholder. Actual implementation would use
        scikit-learn, TensorFlow, or similar ML library.
        """
        if len(self.feature_data) < 10:
            self.logger.warning(
                f"Not enough data to train ({len(self.feature_data)} samples). " "Need at least 10 samples."
            )
            return False

        self.logger.info(f"Training model with {len(self.feature_data)} samples...")

        # Placeholder: Calculate average weights from successful schedules
        successful_features = [
            f for f in self.feature_data if f.get("quality_score", 0) >= 90 and f.get("had_conflicts", 1) == 0
        ]

        if successful_features:
            # Calculate average feature values from successful schedules
            self.learned_weights = {
                "morning_preference": sum(f.get("is_morning", 0) for f in successful_features)
                / len(successful_features),
                "avoid_teacher_overload": 1.0
                - (sum(f.get("teacher_is_busy", 0) for f in successful_features) / len(successful_features)),
                "avoid_gaps": 1.0
                - (sum(f.get("class_has_gap", 0) for f in successful_features) / len(successful_features)),
                "difficult_lesson_morning": sum(
                    f.get("is_difficult_lesson", 0) * f.get("is_morning", 0) for f in successful_features
                )
                / len(successful_features),
            }

            self.is_trained = True
            self.logger.info("Model trained successfully")
            self.logger.info(f"Learned weights: {self.learned_weights}")
            return True
        else:
            self.logger.warning("No successful schedules found for training")
            return False

    def save_model(self, filename: str = "ml_scheduler_model.pkl"):
        """
        Save trained model to file

        Args:
            filename: Output filename
        """
        if not self.is_trained:
            self.logger.warning("Model not trained yet")
            return False

        model_data = {
            "learned_weights": self.learned_weights,
            "feature_data": self.feature_data,
            "historical_schedules": self.historical_schedules,
            "is_trained": self.is_trained,
        }

        try:
            with open(filename, "wb") as f:
                pickle.dump(model_data, f)

            self.logger.info(f"Model saved to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            return False

    def load_model(self, filename: str = "ml_scheduler_model.pkl"):
        """
        Load trained model from file

        Args:
            filename: Input filename
        """
        try:
            with open(filename, "rb") as f:
                model_data = pickle.load(f)

            self.learned_weights = model_data["learned_weights"]
            self.feature_data = model_data["feature_data"]
            self.historical_schedules = model_data["historical_schedules"]
            self.is_trained = model_data["is_trained"]

            self.logger.info(f"Model loaded from {filename}")
            self.logger.info(f"Loaded {len(self.feature_data)} training samples")
            return True
        except FileNotFoundError:
            self.logger.warning(f"Model file not found: {filename}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False

    def _calculate_score_from_features(self, features: Dict) -> float:
        """
        Calculate score from features using learned weights

        Args:
            features: Feature dict

        Returns:
            Score (higher is better)
        """
        if not self.learned_weights:
            return 0.0

        score = 0.0

        # Apply learned weights
        if features.get("is_morning", 0) == 1:
            score += self.learned_weights.get("morning_preference", 0.5) * 10

        if features.get("teacher_is_busy", 0) == 0:
            score += self.learned_weights.get("avoid_teacher_overload", 0.5) * 15

        if features.get("class_has_gap", 0) == 0:
            score += self.learned_weights.get("avoid_gaps", 0.5) * 20

        if features.get("is_difficult_lesson", 0) == 1 and features.get("is_morning", 0) == 1:
            score += self.learned_weights.get("difficult_lesson_morning", 0.5) * 12

        # Historical success bonus
        score += features.get("historical_success", 0) * 5

        return score

    def _heuristic_selection(
        self,
        class_id: int,
        lesson_id: int,
        teacher_id: int,
        available_slots: List[Tuple[int, int]],
        current_schedule: List[Dict],
    ) -> Tuple[int, int]:
        """Fallback heuristic-based selection"""
        # Simple heuristic: prefer morning slots for difficult lessons
        lesson = self.db_manager.get_lesson_by_id(lesson_id)

        if lesson and self._is_difficult_lesson(lesson.name):
            # Prefer morning slots
            morning_slots = [(d, s) for d, s in available_slots if s < 4]
            if morning_slots:
                return morning_slots[0]

        # Default: return first available
        return available_slots[0]

    def _check_gap(self, schedule: List[Dict], class_id: int, day: int, slot: int) -> int:
        """Check if placing at this slot would create a gap"""
        class_slots_today = [e["time_slot"] for e in schedule if e["class_id"] == class_id and e["day"] == day]

        if not class_slots_today:
            return 0

        min_slot = min(class_slots_today)
        max_slot = max(class_slots_today)

        # Check if this slot would create a gap
        if slot < min_slot or slot > max_slot:
            return 0

        # Check if there's a gap between this slot and existing slots
        all_slots = class_slots_today + [slot]
        all_slots.sort()

        for i in range(len(all_slots) - 1):
            if all_slots[i + 1] - all_slots[i] > 1:
                return 1

        return 0

    def _is_difficult_lesson(self, lesson_name: str) -> int:
        """Check if lesson is difficult"""
        difficult_lessons = [
            "Matematik",
            "Fizik",
            "Kimya",
            "Biyoloji",
            "Türk Dili ve Edebiyatı",
            "Geometri",
        ]
        return 1 if lesson_name in difficult_lessons else 0

    def _get_historical_success_rate(self, lesson_id: int, day: int, slot: int) -> float:
        """Get historical success rate for this lesson at this time"""
        if not self.historical_schedules:
            return 0.5  # Neutral

        # Count successful placements
        total = 0
        successful = 0

        for hist in self.historical_schedules:
            for entry in hist["schedule"]:
                if entry["lesson_id"] == lesson_id and entry["day"] == day and entry["time_slot"] == slot:
                    total += 1
                    if hist["metrics"].get("coverage", 0) >= 90:
                        successful += 1

        if total == 0:
            return 0.5  # Neutral

        return successful / total

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()

    def get_statistics(self) -> Dict:
        """Get ML scheduler statistics"""
        return {
            "is_trained": self.is_trained,
            "historical_schedules": len(self.historical_schedules),
            "training_samples": len(self.feature_data),
            "learned_weights": self.learned_weights,
        }
