#!/usr/bin/env python3
"""
Performance Benchmark Script for Scheduling Algorithms
Generates comprehensive performance reports with visualizations
"""

import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Any
import psutil
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Comprehensive performance benchmarking system"""

    def __init__(self):
        self.database = None
        self.results = []
        self.metrics = []

        # Set style for plots
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

    def setup_database(self):
        """Initialize database with test data"""
        try:
            from database.db_manager import DatabaseManager
            self.database = DatabaseManager("benchmark.db")

            # Initialize school type
            self.database.set_school_type("Lise")

            # Create test data
            self._create_test_data()

            logger.info("✅ Database setup completed")
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise

    def _create_test_data(self):
        """Create realistic test data"""
        # Create 12 classes (4 grades × 3 sections)
        classes = []
        grades = [9, 10, 11, 12]
        sections = ['A', 'B', 'C']

        for grade in grades:
            for section in sections:
                class_name = f"{grade}-{section}"
                class_id = self.database.add_class(class_name, grade)
                classes.append(class_id)

        # Create teachers (20 teachers)
        subjects = ["Matematik", "Türkçe", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe", "İngilizce"]
        teachers = []

        for i, subject in enumerate(subjects * 3):
            teacher_id = self.database.add_teacher(f"Öğretmen {i+1}", subject[:3])
            teachers.append(teacher_id)

        # Create lessons based on curriculum
        curriculum_lessons = {
            9: ["Türkçe", "Matematik", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "İngilizce"],
            10: ["Türkçe", "Matematik", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe", "İngilizce"],
            11: ["Türkçe", "Matematik", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe", "İngilizce"],
            12: ["Türkçe", "Matematik", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe", "İngilizce"]
        }

        lesson_ids = {}
        for grade, subjects in curriculum_lessons.items():
            for subject in subjects:
                lesson_name = f"{subject} {grade}.Sınıf"
                # Check if lesson already exists
                existing = self.database.get_lesson_by_name(lesson_name, "Lise")
                if not existing:
                    lesson_id = self.database.add_lesson(lesson_name, weekly_hours=4)  # 4 hours per week
                    lesson_ids[f"{grade}_{subject}"] = lesson_id
                else:
                    lesson_ids[f"{grade}_{subject}"] = existing.lesson_id

                # Set curriculum (weekly hours)
                self.database.add_lesson_weekly_hours(lesson_ids[f"{grade}_{subject}"], grade, "Lise", 4)

        # Create assignments (teacher-lesson-class relationships)
        # Simplified: each class gets assigned teachers based on subject matching
        for class_id in classes:
            class_obj = self.database.get_class_by_id(class_id)
            if not class_obj:
                continue

            grade = class_obj.grade

            # Get required lessons for this grade
            for subject in curriculum_lessons.get(grade, []):
                lesson_id = lesson_ids.get(f"{grade}_{subject}")

                # Find a teacher who teaches this subject
                suitable_teachers = []
                for teacher_id in teachers:
                    teacher = self.database.get_teacher_by_id(teacher_id)
                    if teacher and teacher.subject.lower() in subject.lower():
                        suitable_teachers.append(teacher_id)

                if suitable_teachers:
                    # Assign randomly to one teacher
                    selected_teacher = np.random.choice(suitable_teachers)
                    # Create assignment (not scheduled yet)
                    self.database.add_schedule_entry(class_id, selected_teacher, lesson_id, 1, -1, -1)

        # Create classrooms (4 classrooms)
        for i in range(1, 5):
            self.database.add_classroom(f"Sınıf {i}", 30)

    def run_benchmarks(self):
        """Run comprehensive performance benchmarks"""
        algorithms = self._get_available_algorithms()
        scenarios = ["small", "medium", "large"]  # Different school sizes

        logger.info("🚀 Starting performance benchmarks...")
        logger.info(f"📊 Algorithms to test: {list(algorithms.keys())}")
        logger.info(f"📏 Scenarios: {scenarios}")

        for scenario in scenarios:
            self._run_scenario_benchmarks(scenario, algorithms)

        logger.info("✅ Benchmarking completed!")

    def _get_available_algorithms(self) -> Dict[str, Any]:
        """Get all available scheduling algorithms"""
        algorithms = {}

        # Try to import each algorithm
        try:
            from algorithms.simple_perfect_scheduler import SimplePerfectScheduler
            algorithms["Simple Perfect"] = SimplePerfectScheduler
        except ImportError:
            logger.warning("SimplePerfectScheduler not available")

        try:
            from algorithms.hybrid_optimal_scheduler import HybridOptimalScheduler
            algorithms["Hybrid Optimal"] = HybridOptimalScheduler
        except ImportError:
            logger.warning("HybridOptimalScheduler not available")

        try:
            from algorithms.ultimate_scheduler import UltimateScheduler
            algorithms["Ultimate"] = UltimateScheduler
        except ImportError:
            logger.warning("UltimateScheduler not available")

        try:
            from algorithms.enhanced_strict_scheduler import EnhancedStrictScheduler
            algorithms["Enhanced Strict"] = EnhancedStrictScheduler
        except ImportError:
            logger.warning("EnhancedStrictScheduler not available")

        return algorithms

    def _run_scenario_benchmarks(self, scenario: str, algorithms: Dict[str, Any]):
        """Run benchmarks for a specific scenario"""
        logger.info(f"\n📏 === Running {scenario.upper()} SCENARIO ===")

        # Configuration for different scenarios
        configs = {
            "small": {"classes": 4, "max_time": 30},
            "medium": {"classes": 8, "max_time": 60},
            "large": {"classes": 12, "max_time": 120}
        }

        config = configs[scenario]

        for name, algorithm_class in algorithms.items():
            try:
                logger.info(f"⚡ Testing {name} algorithm...")

                # Warm up run
                self._run_single_test(algorithm_class, config, warm_up=True)

                # Run multiple times for statistical significance
                run_times = []
                for run in range(3):  # 3 runs per algorithm
                    duration, coverage = self._run_single_test(algorithm_class, config)
                    run_times.append((duration, coverage))
                    logger.info(".1f")

                # Calculate statistics
                durations = [rt[0] for rt in run_times]
                coverages = [rt[1] for rt in run_times]

                result = {
                    'scenario': scenario,
                    'algorithm': name,
                    'avg_duration': np.mean(durations),
                    'std_duration': np.std(durations),
                    'min_duration': np.min(durations),
                    'max_duration': np.max(durations),
                    'avg_coverage': np.mean(coverages),
                    'std_coverage': np.std(coverages),
                    'run_count': len(run_times),
                    'timestamp': datetime.now()
                }

                self.results.append(result)

            except Exception as e:
                logger.error(f"❌ Error testing {name}: {e}")
                result = {
                    'scenario': scenario,
                    'algorithm': name,
                    'error': str(e),
                    'timestamp': datetime.now()
                }
                self.results.append(result)

    def _run_single_test(self, algorithm_class, config: Dict, warm_up: bool = False):
        """Run a single algorithm test"""
        try:
            # Create algorithm instance
            algorithm = algorithm_class(self.database)

            # Record start time and memory
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024

            # Generate schedule
            schedule = algorithm.generate_schedule()

            # Record end time and memory
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024

            duration = end_time - start_time
            memory_used = end_memory - start_memory

            # Calculate coverage
            coverage = self._calculate_coverage(schedule)

            if not warm_up:
                # Record metrics
                self._record_metrics({
                    'timestamp': datetime.now(),
                    'algorithm': algorithm_class.__name__,
                    'duration': duration,
                    'memory_used': memory_used,
                    'coverage': coverage,
                    'config': config
                })

            return duration, coverage

        except Exception as e:
            logger.error(f"Single test failed: {e}")
            if not warm_up:
                self._record_metrics({
                    'timestamp': datetime.now(),
                    'algorithm': algorithm_class.__name__,
                    'error': str(e),
                    'config': config
                })
            return 999, 0  # Very slow, no coverage

    def _calculate_coverage(self, schedule: List[Dict]) -> float:
        """Calculate schedule coverage percentage"""
        if not schedule:
            return 0.0

        # Simple coverage calculation
        total_entries = len(schedule)

        # Estimate required slots (rough approximation)
        # For a school with classes, assume average 6-8 slots per class per day × 5 days
        expected_slots = len(self.database.get_all_classes()) * 8 * 5

        coverage = min(100.0, (total_entries / expected_slots) * 100) if expected_slots > 0 else 0

        return coverage

    def _record_metrics(self, metrics: Dict):
        """Record performance metrics"""
        self.metrics.append(metrics)

    def generate_report(self):
        """Generate comprehensive performance report"""
        logger.info("\n📊 Generating performance report...")

        # Create output directory
        os.makedirs("reports", exist_ok=True)

        # Generate summary report
        self._generate_summary_report()

        # Generate visualizations
        self._generate_visualizations()

        # Save raw data
        self._save_raw_data()

        logger.info("✅ Report generation completed!")
        logger.info("📁 Reports saved in 'reports/' directory")

    def _generate_summary_report(self):
        """Generate summary performance report"""
        report_path = "reports/performance_summary.txt"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("🚀 SCHEDULE ALGORITHMS PERFORMANCE BENCHMARK REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Report generated: {datetime.now()}\n\n")

            # Overall summary
            successful_results = [r for r in self.results if 'error' not in r]

            if successful_results:
                f.write("📈 OVERALL SUMMARY\n")
                f.write("-" * 30 + "\n")

                # Best algorithm by average duration
                best_by_speed = min(successful_results, key=lambda x: x.get('avg_duration', 999))
                f.write(".2f\n"                f.write(".2f\n"                f.write(".2f\n\n"                # Best by coverage
                best_by_coverage = max(successful_results, key=lambda x: x.get('avg_coverage', 0))
                f.write(".2f\n"                f.write(".2f\n"                f.write(".2f\n\n"            # Detailed results
            f.write("📊 DETAILED RESULTS\n")
            f.write("-" * 30 + "\n")

            for result in self.results:
                if 'error' in result:
                    f.write(f"❌ {result['scenario'].upper()} - {result['algorithm']}\n")
                    f.write(f"   Error: {result['error']}\n\n")
                else:
                    f.write(f"✅ {result['scenario'].upper()} - {result['algorithm']}\n")
                    f.write(".2f\n"                    f.write(".2f\n"                    f.write(".2f\n")
                    f.write(".2f\n"                    f.write(".2f\n")
                    f.write("   Run count: \n\n")

        logger.info(f"📝 Summary report saved to {report_path}")

    def _generate_visualizations(self):
        """Generate performance visualizations"""
        successful_results = [r for r in self.results if 'error' not in r]

        if not successful_results:
            logger.warning("No successful results to visualize")
            return

        # Create DataFrame for easier plotting
        df = pd.DataFrame(successful_results)

        # Performance comparison by scenario
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Algorithm Performance Comparison', fontsize=16)

        # Duration comparison
        ax1 = sns.barplot(data=df, x='scenario', y='avg_duration', hue='algorithm', ax=axes[0,0])
        ax1.set_title('Average Execution Time by Scenario')
        ax1.set_ylabel('Duration (seconds)')

        # Coverage comparison
        ax2 = sns.barplot(data=df, x='scenario', y='avg_coverage', hue='algorithm', ax=axes[0,1])
        ax2.set_title('Average Coverage by Scenario')
        ax2.set_ylabel('Coverage (%)')

        # Duration vs Coverage scatter plot
        for algorithm in df['algorithm'].unique():
            algo_data = df[df['algorithm'] == algorithm]
            axes[1,0].scatter(algo_data['avg_duration'], algo_data['avg_coverage'],
                             label=algorithm, s=100, alpha=0.7)

        axes[1,0].set_xlabel('Duration (seconds)')
        axes[1,0].set_ylabel('Coverage (%)')
        axes[1,0].set_title('Duration vs Coverage')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)

        # Duration stability (standard deviation)
        ax4 = sns.barplot(data=df, x='algorithm', y='std_duration', ax=axes[1,1])
        ax4.set_title('Algorithm Stability (Duration Std Dev)')
        ax4.set_ylabel('Duration Std Dev (seconds)')
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig('reports/performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Performance metrics over time (if available)
        if self.metrics:
            metrics_df = pd.DataFrame(self.metrics)

            plt.figure(figsize=(12, 8))

            # Filter out failed runs
            success_metrics = metrics_df[metrics_df['duration'] != 999]

            if not success_metrics.empty:
                # Create subplots for metrics
                fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

                # Duration over time
                for algorithm in success_metrics['algorithm'].unique():
                    algo_data = success_metrics[success_metrics['algorithm'] == algorithm]
                    ax1.plot(algo_data['timestamp'], algo_data['duration'], 'o-', label=algorithm)

                ax1.set_title('Execution Time Over Time')
                ax1.set_ylabel('Duration (seconds)')
                ax1.legend()
                ax1.grid(True, alpha=0.3)

                # Coverage over time
                for algorithm in success_metrics['algorithm'].unique():
                    algo_data = success_metrics[success_metrics['algorithm'] == algorithm]
                    ax2.plot(algo_data['timestamp'], algo_data['coverage'], 's-', label=algorithm)

                ax2.set_title('Coverage Over Time')
                ax2.set_ylabel('Coverage (%)')
                ax2.legend()
                ax2.grid(True, alpha=0.3)

                # Memory usage over time
                for algorithm in success_metrics['algorithm'].unique():
                    algo_data = success_metrics[success_metrics['algorithm'] == algorithm]
                    if 'memory_used' in algo_data.columns:
                        ax3.plot(algo_data['timestamp'], algo_data['memory_used'], '^-', label=algorithm)

                ax3.set_title('Memory Usage Over Time')
                ax3.set_ylabel('Memory Used (MB)')
                ax3.legend()
                ax3.grid(True, alpha=0.3)

                plt.tight_layout()
                plt.savefig('reports/performance_over_time.png', dpi=300, bbox_inches='tight')
                plt.close()

        logger.info("📊 Visualizations saved to reports/ directory")

    def _save_raw_data(self):
        """Save raw benchmark data"""
        # Save results as CSV
        if self.results:
            results_df = pd.DataFrame(self.results)
            results_df.to_csv('reports/benchmark_results.csv', index=False)

        # Save metrics as CSV
        if self.metrics:
            metrics_df = pd.DataFrame(self.metrics)
            metrics_df.to_csv('reports/benchmark_metrics.csv', index=False)

        logger.info("💾 Raw data saved to reports/ directory")

def main():
    """Main execution function"""
    print("🚀 Starting Performance Benchmark Suite")
    print("=" * 50)

    benchmark = PerformanceBenchmark()

    try:
        # Setup
        benchmark.setup_database()

        # Run benchmarks
        benchmark.run_benchmarks()

        # Generate reports
        benchmark.generate_report()

        print("\n✅ Performance benchmark completed successfully!")
        print("📁 Check the 'reports/' directory for results")

    except Exception as e:
        logger.error(f"❌ Benchmark failed: {e}")
        raise

    finally:
        # Cleanup
        if benchmark.database:
            benchmark.database.close()

if __name__ == "__main__":
    main()</content>
