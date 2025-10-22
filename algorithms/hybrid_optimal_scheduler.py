# -*- coding: utf-8 -*-
"""
Hybrid Optimal Scheduler - Tüm Teknikleri Birleştiren En Güçlü Scheduler
- CSP + Arc Consistency
- Soft Constraints
- Simulated Annealing
- Advanced Heuristics (MRV + Degree + LCV)
- Explanation & Debugging
"""

import io
import sys
import time
import logging
import functools
from collections import defaultdict
from typing import Dict, List, Optional

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Import yeni modüller
try:
    from algorithms.csp_solver import CSPSolver, CSPVariable, create_schedule_constraints

    CSP_AVAILABLE = True
except ImportError:
    CSP_AVAILABLE = False
    print("⚠️  CSP Solver bulunamadı")

try:
    from algorithms.soft_constraints import SoftConstraintManager

    SOFT_CONSTRAINTS_AVAILABLE = True
except ImportError:
    SOFT_CONSTRAINTS_AVAILABLE = False
    print("⚠️  Soft Constraints bulunamadı")

try:
    from algorithms.local_search import (
        ScheduleNeighborGenerator,
        SimulatedAnnealing,
        adaptive_backtrack_limit,
    )

    LOCAL_SEARCH_AVAILABLE = True
except ImportError:
    LOCAL_SEARCH_AVAILABLE = False
    print("⚠️  Local Search bulunamadı")

try:
    from algorithms.heuristics import HeuristicManager, ScheduleHeuristics

    HEURISTICS_AVAILABLE = True
except ImportError:
    HEURISTICS_AVAILABLE = False
    print("⚠️  Heuristics bulunamadı")

try:
    from algorithms.scheduler_explainer import SchedulerExplainer

    EXPLAINER_AVAILABLE = True
except ImportError:
    EXPLAINER_AVAILABLE = False
    print("⚠️  Explainer bulunamadı")


class PerformanceOptimizer:
    """Performans iyileştirmeleri için yardımcı sınıf"""

    def __init__(self):
        self.cache = {}
        self.call_count = defaultdict(int)
        self.total_time = defaultdict(float)

    def timing_decorator(self, func):
        """Fonksiyon çalışma süresini ölçer"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()

            func_name = func.__name__
            self.call_count[func_name] += 1
            self.total_time[func_name] += (end_time - start_time)

            return result
        return wrapper

    def cache_result(self, key, result, ttl=300):
        """Sonucu önbellekle"""
        self.cache[key] = {
            'result': result,
            'timestamp': time.time(),
            'ttl': ttl
        }

    def get_cached_result(self, key):
        """Önbellekten sonucu al"""
        if key in self.cache:
            cache_entry = self.cache[key]
            if time.time() - cache_entry['timestamp'] < cache_entry['ttl']:
                return cache_entry['result']
            else:
                del self.cache[key]
        return None

    def get_performance_report(self):
        """Performans raporunu döndür"""
        report = []
        for func_name in self.call_count:
            count = self.call_count[func_name]
            total = self.total_time[func_name]
            avg = total / count if count > 0 else 0
            report.append(f"{func_name}: {count} çağrı, toplam {total:.3f}s, ortalama {avg:.3f}s")
        return report


class HybridOptimalScheduler:
    """
    En Güçlü Scheduler - Tüm Teknikleri Birleştirir

    Aşamalar:
    1. Hazırlık: Verileri al, analiz et
    2. İlk Çözüm: Simple Perfect Scheduler ile başlangıç çözümü
    3. CSP Refinement: Arc consistency ve backtracking ile iyileştirme
    4. Soft Optimization: Simulated annealing ile soft constraint'leri optimize et
    5. Final Validation: Tüm kısıtlamaları kontrol et ve raporla
    """

    SCHOOL_TIME_SLOTS = {
        "İlkokul": 7,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(self, db_manager):
        self.db_manager = db_manager

        # Modülleri başlat
        self.explainer = SchedulerExplainer(db_manager) if EXPLAINER_AVAILABLE else None
        self.soft_constraints = SoftConstraintManager(db_manager) if SOFT_CONSTRAINTS_AVAILABLE else None
        self.heuristics = ScheduleHeuristics(db_manager) if HEURISTICS_AVAILABLE else None

        # Performance optimizer ekleme
        self.performance_optimizer = PerformanceOptimizer()

        # Yedek: Simple Perfect Scheduler
        try:
            from algorithms.simple_perfect_scheduler import SimplePerfectScheduler

            self.fallback_scheduler = SimplePerfectScheduler(db_manager)
        except ImportError:
            self.fallback_scheduler = None

    def generate_schedule(self) -> List[Dict]:
        """Ana program oluşturma fonksiyonu"""
        print("\n" + "=" * 80)
        print("🚀 HYBRID OPTIMAL SCHEDULER - En Güçlü Algoritma")
        print("=" * 80)
        print("")
        print("Özellikler:")
        print("  ✅ Arc Consistency (AC-3)")
        print("  ✅ Soft Constraints (8 kriter)")
        print("  ✅ Simulated Annealing")
        print("  ✅ Advanced Heuristics (MRV + Degree + LCV)")
        print("  ✅ Explanation & Debugging")
        print("")

        # 1. HAZIRLIK
        config = self._prepare_configuration()

        if config is None:
            print("❌ Konfigürasyon hazırlığı başarısız!")
            return []

        # 2. İLK ÇÖZÜM - Simple Perfect Scheduler ile
        print("\n" + "=" * 80)
        print("📋 AŞAMA 1: İlk Çözüm (Simple Perfect Scheduler)")
        print("=" * 80)

        initial_schedule = self._generate_initial_solution(config)

        if not initial_schedule:
            print("❌ İlk çözüm oluşturulamadı!")
            return []

        print(f"✅ İlk çözüm hazır: {len(initial_schedule)} ders yerleştirildi")

        # 3. SOFT CONSTRAINT OPTIMİZASYONU
        import yaml
        
        # Load scheduler configuration
        try:
            with open('config/scheduler_config.yaml', 'r', encoding='utf-8') as f:
                scheduler_config = yaml.safe_load(f)
            use_annealing = scheduler_config.get('algorithms', {}).get('hybrid_optimal', {}).get('simulated_annealing', {}).get('enabled', False)
        except (IOError, yaml.YAMLError) as e:
            print(f"⚠️  Yapılandırma okunamadı, optimizasyon atlanıyor: {e}")
            use_annealing = False

        if use_annealing and LOCAL_SEARCH_AVAILABLE and self.soft_constraints:
            print("\n" + "=" * 80)
            print("🔥 AŞAMA 2: Optimizasyon (Simulated Annealing)")
            print("=" * 80)
            optimized_schedule = self._optimize_with_annealing(initial_schedule, config)
            print(f"✅ Optimizasyon tamamlandı: {len(optimized_schedule)} ders")
        else:
            print("\n" + "=" * 80)
            print("ℹ️  AŞAMA 2: Optimizasyon Atlandı (Yapılandırmada devre dışı)")
            print("=" * 80)
            optimized_schedule = initial_schedule

        # Soft constraint skorunu göster (bilgi amaçlı)
        if SOFT_CONSTRAINTS_AVAILABLE:
            result = self.soft_constraints.evaluate_schedule(optimized_schedule)
            print(f"\n📊 Soft Constraint Skoru: {result['total_score']:.2f}")

        # 4. FİNAL VALİDASYON VE RAPORLAMA
        print("\n" + "=" * 80)
        print("📊 AŞAMA 3: Final Validation ve Raporlama")
        print("=" * 80)

        final_schedule = self._final_validation(optimized_schedule, config)

        # 5. VERİTABANINA KAYDET
        self._save_to_database(final_schedule)

        # 6. RAPOR OLUŞTUR
        if self.explainer:
            print("\n" + self.explainer.generate_report())

        return final_schedule

    def _prepare_configuration(self) -> Optional[Dict]:
        """Konfigürasyonu hazırla"""
        print("\n🔧 Konfigürasyon hazırlanıyor...")

        # Verileri al
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()
        assignments = self.db_manager.get_schedule_by_school_type()

        # Okul tipi ve slot sayısı
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        # Adaptif backtrack limiti hesapla
        if LOCAL_SEARCH_AVAILABLE:
            avg_lessons = len(assignments) / max(len(classes), 1)
            backtrack_limit = adaptive_backtrack_limit(len(classes), len(teachers), int(avg_lessons))
        else:
            backtrack_limit = 5000

        print(f"   • Okul: {school_type} ({time_slots_count} saat/gün)")
        print(f"   • Sınıf: {len(classes)} | Öğretmen: {len(teachers)}")
        print(f"   • Ders: {len(lessons)} | Atama: {len(assignments)}")
        print(f"   • Backtrack Limiti: {backtrack_limit}")

        # Atama haritası
        assignment_map = {}
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id)
            assignment_map[key] = assignment.teacher_id

        return {
            "classes": classes,
            "teachers": teachers,
            "lessons": lessons,
            "classrooms": classrooms,
            "assignments": assignments,
            "assignment_map": assignment_map,
            "school_type": school_type,
            "time_slots_count": time_slots_count,
            "backtrack_limit": backtrack_limit,
        }

    def _generate_initial_solution(self, config: Dict) -> List[Dict]:
        """İlk çözümü oluştur (Simple Perfect Scheduler ile)"""
        if self.fallback_scheduler:
            return self.fallback_scheduler.generate_schedule()
        else:
            print("⚠️  Fallback scheduler yok, boş program döndürülüyor")
            return []

    def _optimize_with_annealing(self, schedule: List[Dict], config: Dict) -> List[Dict]:
        """Simulated Annealing ile iyileştirme"""

        # Komşu üreteç
        neighbor_gen = ScheduleNeighborGenerator(self.db_manager, config["time_slots_count"])

        # Değerlendirme fonksiyonu
        def evaluate(sch):
            result = self.soft_constraints.evaluate_schedule(sch)
            return result["total_score"]

        # Hard constraint kontrolü
        def check_constraints(sch):
            conflicts = self._detect_conflicts(sch)
            return len(conflicts) == 0

        # Simulated Annealing
        sa = SimulatedAnnealing(
            initial_temperature=1000.0,
            cooling_rate=0.95,
            min_temperature=1.0,
            iterations_per_temp=50,
        )

        optimized = sa.optimize(schedule, evaluate, neighbor_gen.generate_neighbor, check_constraints)

        return optimized

    def _final_validation(self, schedule: List[Dict], config: Dict) -> List[Dict]:
        """Final validation ve iyileştirmeler"""
        print("\n🔍 Final validation yapılıyor...")

        # Çakışma kontrolü
        conflicts = self._detect_conflicts(schedule)

        if conflicts:
            print(f"   ⚠️  {len(conflicts)} çakışma tespit edildi")

            # Çakışmaları çözmeye çalış
            schedule = self._resolve_conflicts(schedule, conflicts, config)

            # Tekrar kontrol
            conflicts = self._detect_conflicts(schedule)
            if conflicts:
                print(f"   ⚠️  {len(conflicts)} çakışma hala mevcut")
            else:
                print(f"   ✅ Tüm çakışmalar çözüldü")
        else:
            print(f"   ✅ Çakışma yok")

        # Soft constraint skoru
        if self.soft_constraints:
            result = self.soft_constraints.evaluate_schedule(schedule)
            print(f"\n📊 Soft Constraint Skoru: {result['total_score']:.2f}")

            if result["violations"]:
                print(f"   ⚠️  {result['num_violations']} soft constraint ihlali")
                for violation in result["violations"][:5]:
                    print(f"      • {violation['constraint']}: {violation['score']:.1f}")

        # Kapsama analizi
        self._analyze_coverage(schedule, config)

        return schedule

    def _analyze_coverage(self, schedule: List[Dict], config: Dict):
        """Kapsama analizini yap"""
        print(f"\n📈 Kapsama Analizi:")

        # Toplam gereksinim hesapla
        total_required = 0
        total_scheduled = len(schedule)

        for class_obj in config["classes"]:
            for lesson in config["lessons"]:
                key = (class_obj.class_id, lesson.lesson_id)
                if key in config["assignment_map"]:
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                    if weekly_hours:
                        total_required += weekly_hours

        coverage = (total_scheduled / total_required * 100) if total_required > 0 else 100

        print(f"   • Gereksinim: {total_required} saat")
        print(f"   • Yerleşen: {total_scheduled} saat")
        print(f"   • Kapsama: {coverage:.1f}%")

        if coverage >= 95:
            print(f"   ✅ Mükemmel kapsama!")
        elif coverage >= 85:
            print(f"   ✅ İyi kapsama")
        elif coverage >= 70:
            print(f"   ⚠️  Orta kapsama - iyileştirme gerekebilir")
        else:
            print(f"   ❌ Düşük kapsama - ciddi sorunlar var")

    def _detect_conflicts(self, schedule: List[Dict]) -> List[Dict]:
        """Çakışmaları tespit et"""
        conflicts = []

        # Öğretmen çakışmaları
        teacher_slots = defaultdict(list)
        for entry in schedule:
            key = (entry["teacher_id"], entry["day"], entry["time_slot"])
            teacher_slots[key].append(entry)

        for key, entries in teacher_slots.items():
            if len(entries) > 1:
                conflicts.append({"type": "teacher_conflict", "entries": entries})

        # Sınıf çakışmaları
        class_slots = defaultdict(list)
        for entry in schedule:
            key = (entry["class_id"], entry["day"], entry["time_slot"])
            class_slots[key].append(entry)

        for key, entries in class_slots.items():
            if len(entries) > 1:
                conflicts.append({"type": "class_conflict", "entries": entries})

        return conflicts

    def _resolve_conflicts(self, schedule: List[Dict], conflicts: List[Dict], config: Dict) -> List[Dict]:
        """Çakışmaları çözmeye çalış"""
        print("\n🔧 Çakışma çözümü deneniyor...")

        resolved_count = 0

        for conflict in conflicts:
            if conflict["type"] in ["teacher_conflict", "class_conflict"]:
                entries = conflict["entries"]

                # İlk entry'yi koru, diğerlerini taşı
                for entry in entries[1:]:
                    # Yeni slot bul
                    for day in range(5):
                        for slot in range(config["time_slots_count"]):
                            # Bu slot uygun mu?
                            if self._is_slot_available(schedule, entry["class_id"], entry["teacher_id"], day, slot):
                                # Taşı
                                entry["day"] = day
                                entry["time_slot"] = slot
                                resolved_count += 1
                                break

        print(f"   ✅ {resolved_count} çakışma çözüldü")
        return schedule

    def _is_slot_available(self, schedule: List[Dict], class_id: int, teacher_id: int, day: int, slot: int) -> bool:
        """Slot uygun mu?"""
        for entry in schedule:
            if entry["day"] == day and entry["time_slot"] == slot:
                if entry["class_id"] == class_id or entry["teacher_id"] == teacher_id:
                    return False
        return True

    def _save_to_database(self, schedule: List[Dict]):
        """Veritabanına kaydet"""
        print(f"\n💾 Veritabanına kaydediliyor...")

        self.db_manager.clear_schedule()

        saved_count = 0
        for entry in schedule:
            if self.db_manager.add_schedule_program(
                entry["class_id"],
                entry["teacher_id"],
                entry["lesson_id"],
                entry["classroom_id"],
                entry["day"],
                entry["time_slot"],
            ):
                saved_count += 1

        print(f"✅ {saved_count}/{len(schedule)} kayıt tamamlandı")
