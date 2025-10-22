# -*- coding: utf-8 -*-
"""
Parallel Scheduler - Run Multiple Algorithms in Parallel
Selects the best result based on coverage and quality metrics
"""

import io
import sys
import multiprocessing
import queue
import time
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import psutil
from typing import Dict, List, Optional, Callable, Any

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Import schedulers
try:
    from algorithms.simple_perfect_scheduler import SimplePerfectScheduler

    SIMPLE_PERFECT_AVAILABLE = True
except ImportError:
    SIMPLE_PERFECT_AVAILABLE = False

try:
    from algorithms.hybrid_approach_scheduler import HybridApproachScheduler

    HYBRID_APPROACH_AVAILABLE = True
except ImportError:
    HYBRID_APPROACH_AVAILABLE = False

try:
    from algorithms.advanced_scheduler import AdvancedScheduler

    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False


class ParallelScheduler:
    """
    Parallel scheduler that runs multiple algorithms simultaneously

    Strategy:
    1. Run 2-3 schedulers in parallel threads
    2. Wait for all to complete (with timeout)
    3. Evaluate each result with scoring function
    4. Select and return the best result

    Benefits:
    - Leverages multi-core CPUs
    - Gets best result from multiple approaches
    - Timeout prevents hanging
    - Fallback if some algorithms fail
    """

    def __init__(
        self,
        db_manager,
        progress_callback: Optional[Callable] = None,
        max_workers: int = 3,
        timeout: int = 120,
        use_multiprocessing: bool = False,
    ):
        """
        Initialize parallel scheduler

        Args:
            db_manager: Database manager instance
            max_workers: Maximum number of parallel workers (default: CPU count)
            use_multiprocessing: Use processes instead of threads (better for CPU-bound tasks)
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # System resource detection
        self.cpu_count = multiprocessing.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)

        # Worker configuration
        if max_workers is None:
            # Adaptive worker count based on system resources
            if self.memory_gb > 8:
                max_workers = min(self.cpu_count, 8)  # More workers for high memory systems
            else:
                max_workers = min(self.cpu_count, 4)  # Conservative for low memory systems

        self.max_workers = max_workers
        self.use_multiprocessing = use_multiprocessing and self.memory_gb > 4  # Only use multiprocessing if enough memory
        self.timeout = timeout
        self.progress_callback = progress_callback

        self.logger.info(f"ParallelScheduler initialized: {max_workers} workers, "
                        f"multiprocessing={use_multiprocessing}, CPU={self.cpu_count}, Memory={self.memory_gb:.1f}GB")

        # Performance tracking
        self.performance_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'best_coverage': 0.0,
            'avg_execution_time': 0.0,
            'total_execution_time': 0.0
        }

        # Available schedulers
        self.available_schedulers = []

        if HYBRID_APPROACH_AVAILABLE:
            self.available_schedulers.append(("HybridApproach", HybridApproachScheduler))

        if SIMPLE_PERFECT_AVAILABLE:
            self.available_schedulers.append(("SimplePerfect", SimplePerfectScheduler))

        if ADVANCED_AVAILABLE:
            self.available_schedulers.append(("Advanced", AdvancedScheduler))

        if not self.available_schedulers:
            raise ImportError("No schedulers available for parallel execution")

        self.logger.info(f"Parallel scheduler initialized with {len(self.available_schedulers)} algorithms")

    def generate_schedule(self) -> List[Dict]:
        """
        Generate schedule using parallel execution

        Returns:
            Best schedule from all algorithms
        """
        print("\n" + "=" * 80)
        print("🚀 PARALLEL SCHEDULER - Multi-Algorithm Execution")
        print("=" * 80)
        print(f"Running {len(self.available_schedulers)} algorithms in parallel:")
        for name, _ in self.available_schedulers:
            print(f"   • {name}")
        print(f"Max workers: {self.max_workers}")
        print(f"Timeout: {self.timeout}s per algorithm")
        print("")

        self._report_progress("Parallel execution başlıyor...", 0)

        start_time = time.time()
        results = []

        # Execute schedulers in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all schedulers
            future_to_scheduler = {}
            for name, scheduler_class in self.available_schedulers:
                future = executor.submit(self._run_scheduler, name, scheduler_class)
                future_to_scheduler[future] = name

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_scheduler, timeout=self.timeout * 2):
                scheduler_name = future_to_scheduler[future]
                completed += 1
                progress = (completed / len(self.available_schedulers)) * 80

                try:
                    result = future.result(timeout=self.timeout)
                    if result:
                        results.append(result)
                        print(f"✅ {scheduler_name}: {result['coverage']:.1f}% coverage in {result['time']:.2f}s")
                    else:
                        print(f"❌ {scheduler_name}: Failed")
                except Exception as e:
                    print(f"❌ {scheduler_name}: Error - {str(e)}")
                    self.logger.error(f"Scheduler {scheduler_name} failed: {e}")

                self._report_progress(f"{completed}/{len(self.available_schedulers)} tamamlandı", progress)

        elapsed = time.time() - start_time

        # Select best result
        if not results:
            print(f"\n❌ All schedulers failed!")
            self._report_progress("Başarısız!", 100)
            return []

        print(f"\n{'='*80}")
        print(f"📊 RESULTS COMPARISON")
        print(f"{'='*80}")

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']}:")
            print(f"   • Coverage: {result['coverage']:.1f}%")
            print(f"   • Entries: {result['entries']}")
            print(f"   • Conflicts: {result['conflicts']}")
            print(f"   • Time: {result['time']:.2f}s")
            print(f"   • Score: {result['score']:.2f}")

        # Select best
        best = results[0]

        print(f"\n{'='*80}")
        print(f"🏆 WINNER: {best['name']}")
        print(f"{'='*80}")
        print(f"📊 Coverage: {best['coverage']:.1f}%")
        print(f"📈 Entries: {best['entries']}")
        print(f"⚡ Time: {best['time']:.2f}s")
        print(f"⏱️  Total Parallel Time: {elapsed:.2f}s")
        print(f"🎯 Score: {best['score']:.2f}")

        self._report_progress("Tamamlandı!", 100)

        # Save best schedule to database
        self._save_to_database(best["schedule"])

        return best["schedule"]

    def _run_scheduler(self, name: str, scheduler_class) -> Optional[Dict]:
        """
        Run a single scheduler

        Args:
            name: Scheduler name
            scheduler_class: Scheduler class

        Returns:
            Result dict or None if failed
        """
        try:
            start = time.time()

            # Create scheduler instance
            scheduler = scheduler_class(self.db_manager)

            # Generate schedule
            schedule = scheduler.generate_schedule()

            elapsed = time.time() - start

            # Analyze result
            coverage = self._calculate_coverage(schedule)
            conflicts = self._count_conflicts(schedule)
            score = self._calculate_score(schedule, coverage, conflicts, elapsed)

            return {
                "name": name,
                "schedule": schedule,
                "coverage": coverage,
                "entries": len(schedule),
                "conflicts": conflicts,
                "time": elapsed,
                "score": score,
            }

        except Exception as e:
            self.logger.error(f"Scheduler {name} failed: {e}")
            return None

    def _calculate_coverage(self, schedule: List[Dict]) -> float:
        """Calculate coverage percentage"""
        classes = self.db_manager.get_all_classes()
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = 8 if "Lise" in school_type else 7

        total_slots = len(classes) * 5 * time_slots_count
        total_scheduled = len(schedule)

        return (total_scheduled / total_slots * 100) if total_slots > 0 else 0

    def _count_conflicts(self, schedule: List[Dict]) -> int:
        """Count conflicts in schedule"""
        conflicts = 0

        # Check class conflicts
        class_slots = set()
        for entry in schedule:
            key = (entry["class_id"], entry["day"], entry["time_slot"])
            if key in class_slots:
                conflicts += 1
            class_slots.add(key)

        # Check teacher conflicts
        teacher_slots = set()
        for entry in schedule:
            key = (entry["teacher_id"], entry["day"], entry["time_slot"])
            if key in teacher_slots:
                conflicts += 1
            teacher_slots.add(key)

        return conflicts

    def _calculate_score(self, schedule: List[Dict], coverage: float, conflicts: int, time_taken: float) -> float:
        """
        Calculate overall score for a schedule

        Scoring formula:
        - Coverage: 0-100 points (most important)
        - Conflicts: -10 points per conflict (critical)
        - Time: Bonus for faster (up to 10 points)
        - Entries: Bonus for more entries (up to 10 points)

        Args:
            schedule: Schedule entries
            coverage: Coverage percentage
            conflicts: Number of conflicts
            time_taken: Time in seconds

        Returns:
            Overall score (higher is better)
        """
        score = 0.0

        # Coverage (0-100 points)
        score += coverage

        # Conflicts penalty (-10 per conflict)
        score -= conflicts * 10

        # Time bonus (faster is better, up to 10 points)
        # 0-10s: +10, 10-30s: +5, 30-60s: +2, 60+s: 0
        if time_taken < 10:
            score += 10
        elif time_taken < 30:
            score += 5
        elif time_taken < 60:
            score += 2

        # Entries bonus (more is better, up to 10 points)
        # Normalized by expected entries
        classes = self.db_manager.get_all_classes()
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = 8 if "Lise" in school_type else 7
        expected_entries = len(classes) * 5 * time_slots_count

        if expected_entries > 0:
            entry_ratio = len(schedule) / expected_entries
            score += min(entry_ratio * 10, 10)

        return score

    def _save_to_database(self, schedule: List[Dict]):
        """Save schedule to database"""
        print(f"\n💾 Veritabanına kaydediliyor...")

        self.db_manager.clear_schedule()

        saved = 0
        for entry in schedule:
            if self.db_manager.add_schedule_program(
                entry["class_id"],
                entry["teacher_id"],
                entry["lesson_id"],
                entry["classroom_id"],
                entry["day"],
                entry["time_slot"],
            ):
                saved += 1

        print(f"✅ {saved}/{len(schedule)} kayıt tamamlandı")

    def _report_progress(self, message: str, percentage: float):
        """Report progress to callback"""
        if self.progress_callback:
            try:
                self.progress_callback(message, percentage)
            except Exception as e:
                self.logger.warning(f"Progress callback raised an exception: {e}")
