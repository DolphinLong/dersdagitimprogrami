# -*- coding: utf-8 -*-
"""
Simple Perfect Scheduler - Basit ama %100 Etkili
Karmaşık CSP yerine pragmatik yaklaşım
"""

import io
import logging
import random
import sys
from collections import defaultdict
from typing import Any, Dict, List

# Set encoding for Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class SimplePerfectScheduler:
    """
    Basit ama etkili scheduler:
    - Öğretmen uygunluğunu kontrol eder
    - Çakışmaları önler
    - Tüm slotları doldurmaya çalışır
    - Gerçek backtracking (basit versiyon)
    """

    SCHOOL_TIME_SLOTS = {
        "İlkokul": 7,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(self, db_manager, heuristics=None, relaxed_mode=False):
        self.db_manager = db_manager
        self.schedule_entries = []
        self.teacher_slots = defaultdict(set)  # {teacher_id: {(day, slot)}}
        self.class_slots = defaultdict(set)  # {class_id: {(day, slot)}}
        self.logger = logging.getLogger(__name__)
        self.heuristics = heuristics  # Heuristics manager for smart slot selection
        self.relaxed_mode = relaxed_mode  # Relaxed mode: skip teacher availability checks for better coverage

    def generate_schedule(self) -> List[Dict]:
        """Program oluştur"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🎯 SIMPLE PERFECT SCHEDULER - Akıllı Sıralama ile")
        self.logger.info("=" * 80)

        self.schedule_entries = []
        self.teacher_slots.clear()
        self.class_slots.clear()

        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()
        assignments = self.db_manager.get_schedule_by_school_type()

        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        self.logger.info("\n📊 Konfigürasyon:")
        self.logger.info(f"   • Okul: {school_type} ({time_slots_count} saat/gün)")
        self.logger.info(f"   • Sınıf: {len(classes)} | Öğretmen: {len(teachers)}")
        self.logger.info(f"   • Atamalar: {len(assignments)}")

        assignment_map = { (a.class_id, a.lesson_id): a.teacher_id for a in assignments }

        all_needs = []
        total_required = 0
        teacher_workload = defaultdict(int)
        class_workload = defaultdict(int)

        for class_obj in classes:
            for lesson in lessons:
                key = (class_obj.class_id, lesson.lesson_id)
                if key in assignment_map:
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                    if weekly_hours and weekly_hours > 0:
                        teacher_id = assignment_map[key]
                        teacher = self.db_manager.get_teacher_by_id(teacher_id)
                        if teacher:
                            need = {
                                "class_id": class_obj.class_id, "class_name": class_obj.name,
                                "lesson_id": lesson.lesson_id, "lesson_name": lesson.name,
                                "teacher_id": teacher_id, "teacher_name": teacher.name,
                                "weekly_hours": weekly_hours, "scheduled": 0,
                            }
                            all_needs.append(need)
                            total_required += weekly_hours
                            teacher_workload[teacher_id] += weekly_hours
                            class_workload[class_obj.class_id] += weekly_hours

        self.logger.info(f"\n📝 Toplam Gereksinim: {total_required} saat")
        self.logger.info(f"   {len(all_needs)} farklı ders ataması")

        def calculate_difficulty_score(need):
            score = (
                need['weekly_hours'] * 10 + 
                teacher_workload.get(need['teacher_id'], 0) * 5 + 
                class_workload.get(need['class_id'], 0) * 3
            )
            return score

        all_needs.sort(key=calculate_difficulty_score, reverse=True)
        self.logger.info("\n🧠 Akıllı sıralama tamamlandı. En zor dersler önce yerleştirilecek.")

        self.logger.info("\n🚀 Yerleştirme başlıyor...")
        total_scheduled = 0
        for idx, need in enumerate(all_needs):
            if (idx + 1) % 10 == 0:
                self.logger.info(f"   📊 İlerleme: {idx + 1}/{len(all_needs)} ders")
            
            scheduled = self._schedule_lesson(need, time_slots_count, classrooms, max_attempts=5)
            need["scheduled"] = scheduled
            total_scheduled += scheduled

        self.logger.info("\n" + "=" * 80)
        self.logger.info("🎯 SONUÇ")
        self.logger.info("=" * 80)
        self.logger.info(f"📊 Gereksinim: {total_required} saat")
        self.logger.info(f"✅ Yerleşen: {total_scheduled} saat")
        coverage = (total_scheduled / total_required * 100) if total_required > 0 else 0
        self.logger.info(f"📈 Başarı: {coverage:.1f}%")

        failed = [n for n in all_needs if n["scheduled"] < n["weekly_hours"]]
        if failed:
            self.logger.warning(f"\n⚠️  {len(failed)} ders tam yerleştirilemedi:")
            for f in failed[:5]:
                self.logger.warning(f"   • {f['class_name']} - {f['lesson_name']}: {f['scheduled']}/{f['weekly_hours']}")
        else:
            self.logger.info("\n🎉 TÜM DERSLER BAŞARIYLA YERLEŞTİRİLDİ!")

        self.logger.info("\n💾 Veritabanına kaydediliyor...")
        self.db_manager.clear_schedule()
        saved = 0
        for entry in self.schedule_entries:
            if self.db_manager.add_schedule_program(
                entry["class_id"], entry["teacher_id"], entry["lesson_id"],
                entry["classroom_id"], entry["day"], entry["time_slot"],
            ):
                saved += 1
        self.logger.info(f"✅ {saved} kayıt tamamlandı")
        
        # GAP FILLING - DEVRE DIŞI (Strict mode - blok kurallarını bozuyor)
        if self.relaxed_mode:
            # Sadece relaxed mode'da gap filling yap
            self.logger.info("\n🔧 RELAXED MODE: Gap filling aktif")
            self.logger.info("\n🔧 FULL CURRICULUM SCHEDULING:")
            curriculum_filled = self._schedule_full_curriculum(classes, teachers, lessons, assignments, time_slots_count)
            self.logger.info(f"   • {curriculum_filled} saat tam müfredat programı oluşturuldu")
            
            if curriculum_filled > 0:
                self.logger.info("   • Gelişmiş boşluk doldurma stratejisi uygulanıyor...")
                gap_filled = self._advanced_gap_filling()
                self.logger.info(f"   • {gap_filled} ek saat dolduruldu")
        else:
            # Strict mode - gap filling devre dışı
            self.logger.info("\n🔒 STRICT MODE: Gap filling devre dışı (blok kuralları korunur)")

        return self.schedule_entries

    def _schedule_full_curriculum(self, classes, teachers, lessons, assignments, time_slots_count: int) -> int:
        """
        Schedule full curriculum based on weekly hours requirements
        This addresses the core issue of only scheduling 112 assignments instead of 280 hours
        """
        scheduled_hours = 0
        
        self.logger.info(f"   📚 Tam müfredat programlaması başlatılıyor...")
        self.logger.info(f"      • Toplam sınıf: {len(classes)}")
        self.logger.info(f"      • Toplam öğretmen: {len(teachers)}")
        self.logger.info(f"      • Toplam ders: {len(lessons)}")
        
        # Get assignment map from existing assignments
        assignment_map = {}
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id)
            assignment_map[key] = assignment.teacher_id
        
        # For each class, schedule all required lessons based on curriculum
        for class_obj in classes:
            self.logger.info(f"   📖 {class_obj.name} için müfredat planlaması...")
            
            # Get all lessons required for this class grade
            class_lessons = []
            for lesson in lessons:
                assignment_key = (class_obj.class_id, lesson.lesson_id)
                if assignment_key in assignment_map:
                    # Get weekly hours from curriculum
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                    if weekly_hours and weekly_hours > 0:
                        teacher_id = assignment_map[assignment_key]
                        teacher = self.db_manager.get_teacher_by_id(teacher_id)
                        if teacher:
                            class_lessons.append({
                                "lesson": lesson,
                                "weekly_hours": weekly_hours,
                                "teacher": teacher,
                                "teacher_id": teacher_id
                            })
                            self.logger.info(f"      📋 {lesson.name}: {weekly_hours} saat ({teacher.name})")
            
            # Schedule each required lesson for this class
            for lesson_info in class_lessons:
                lesson = lesson_info["lesson"]
                weekly_hours = lesson_info["weekly_hours"]
                teacher = lesson_info["teacher"]
                teacher_id = lesson_info["teacher_id"]
                
                self.logger.info(f"   🎯 {class_obj.name} - {lesson.name} ({weekly_hours} saat) yerleştiriliyor...")
                
                # Try to schedule all required hours
                scheduled_for_this_lesson = self._schedule_lesson_full_curriculum(
                    class_obj.class_id,
                    lesson.lesson_id,
                    teacher_id,
                    weekly_hours,
                    time_slots_count
                )
                
                scheduled_hours += scheduled_for_this_lesson
                self.logger.info(f"      ✅ {scheduled_for_this_lesson}/{weekly_hours} saat yerleştirildi")
        
        self.logger.info(f"   📊 Tam müfredat planlaması tamamlandı: {scheduled_hours} saat")
        return scheduled_hours

    def _schedule_lesson_full_curriculum(self, class_id: int, lesson_id: int, teacher_id: int, 
                                       weekly_hours: int, time_slots_count: int) -> int:
        """
        Schedule a lesson for its full weekly hours requirement
        """
        scheduled_count = 0
        max_attempts = weekly_hours * 20  # More attempts for better coverage
        attempts = 0
        
        # Try to schedule all required hours
        while scheduled_count < weekly_hours and attempts < max_attempts:
            attempts += 1
            
            # Try different strategies for placement
            for day in range(5):  # 5 days per week
                if scheduled_count >= weekly_hours:
                    break
                    
                for time_slot in range(time_slots_count):
                    if scheduled_count >= weekly_hours:
                        break
                        
                    # Check if we can place this lesson here (relaxed constraints)
                    can_place = self._can_place_relaxed(class_id, teacher_id, day, time_slot)
                    
                    if can_place:
                        # Place the lesson
                        classroom_id = 1  # Default classroom
                        self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                        scheduled_count += 1
                        self.logger.debug(f"         ✓ Yerleştirildi: Gün {day+1}, Slot {time_slot+1}")
                        break  # Move to next hour needed
        
        # If we couldn't place all hours, try aggressive placement
        if scheduled_count < weekly_hours:
            remaining = weekly_hours - scheduled_count
            self.logger.warning(f"      ⚠️  {remaining} saat eksik kaldı, agresif yerleştirme denemesi...")
            aggressive_placed = self._aggressive_placement_for_remaining_hours(
                class_id, lesson_id, teacher_id, remaining, time_slots_count
            )
            scheduled_count += aggressive_placed
            
        return scheduled_count

    def _aggressive_placement_for_remaining_hours(self, class_id: int, lesson_id: int, teacher_id: int, 
                                               remaining_hours: int, time_slots_count: int) -> int:
        """
        Aggressively place remaining hours with relaxed constraints
        """
        placed_count = 0
        
        # Try each day and time slot with very relaxed constraints
        for day in range(5):
            if placed_count >= remaining_hours:
                break
                
            for time_slot in range(time_slots_count):
                if placed_count >= remaining_hours:
                    break
                    
                # Very relaxed check - only hard constraints (class/teacher conflicts)
                class_conflict = (day, time_slot) in self.class_slots[class_id]
                teacher_conflict = (day, time_slot) in self.teacher_slots[teacher_id]
                
                if not class_conflict and not teacher_conflict:
                    # Place the lesson
                    classroom_id = 1  # Default classroom
                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                    placed_count += 1
                    self.logger.debug(f"         ⚡ Agresif yerleştirme: Gün {day+1}, Slot {time_slot+1}")
        
        return placed_count

    def _get_school_config(self) -> dict:
        """Get school configuration"""
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)
        return {
            "school_type": school_type,
            "time_slots_count": time_slots_count
        }
    
    def _advanced_gap_filling(self) -> int:
        """
        Advanced gap filling strategy to improve coverage
        """
        gap_filled_count = 0
        
        # Try to fill any remaining empty slots in the schedule
        classes = self.db_manager.get_all_classes()
        time_slots_count = self._get_school_config()["time_slots_count"]
        
        # For each class, check each day for gaps
        for class_obj in classes:
            for day in range(5):
                # Check which slots are occupied
                occupied_slots = {entry["time_slot"] for entry in self.schedule_entries 
                                if entry["class_id"] == class_obj.class_id and entry["day"] == day}
                
                # Check unoccupied slots
                for time_slot in range(time_slots_count):
                    if time_slot not in occupied_slots:
                        # This slot is empty, try to place something here
                        filled = self._try_fill_empty_slot(class_obj.class_id, day, time_slot)
                        if filled:
                            gap_filled_count += 1
        
        return gap_filled_count

    def _try_fill_empty_slot(self, class_id: int, day: int, time_slot: int) -> bool:
        """
        Try to fill an empty slot with a needed assignment
        """
        # Get all assignments for this class
        assignments = self.db_manager.get_schedule_by_school_type()
        class_assignments = [a for a in assignments if a.class_id == class_id]
        
        # Try each assignment
        for assignment in class_assignments:
            # Check if this assignment still needs placement
            current_count = sum(1 for entry in self.schedule_entries 
                              if entry["class_id"] == class_id and entry["lesson_id"] == assignment.lesson_id)
            
            class_obj = next((c for c in self.db_manager.get_all_classes() if c.class_id == class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                
                if weekly_hours and current_count < weekly_hours:
                    # Try to place this assignment in the empty slot
                    teacher_id = assignment.teacher_id
                    lesson_id = assignment.lesson_id
                    
                    # Relaxed check
                    can_place = self._can_place_relaxed(class_id, teacher_id, day, time_slot)
                    
                    if can_place:
                        # Place the assignment
                        classroom_id = 1  # Default classroom
                        self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                        self.logger.debug(f"         ✨ Boş slot dolduruldu: {class_id} - Gün {day+1}, Slot {time_slot+1}")
                        return True
        
        return False

    def _enhanced_gap_filling(self, all_needs: List[Dict]) -> int:
        """
        Enhanced gap filling strategy to improve coverage
        """
        gap_filled_count = 0
        
        # Try to fill gaps for each need that wasn't fully scheduled
        for need in all_needs:
            scheduled = need.get("scheduled", 0)
            weekly_hours = need.get("weekly_hours", 0)
            
            if scheduled < weekly_hours:
                remaining = weekly_hours - scheduled
                self.logger.info(f"     Gap filling for {need.get('class_name', 'Unknown')} - "
                               f"{need.get('lesson_name', 'Unknown')}: {remaining} hours")
                
                # Try aggressive placement for remaining hours
                filled = self._aggressive_placement_for_need(need, remaining)
                gap_filled_count += filled
                
        return gap_filled_count

    def _aggressive_placement_for_need(self, need: Dict, remaining_hours: int) -> int:
        """
        Aggressively place remaining hours for a specific need
        """
        filled_count = 0
        
        class_id = need.get("class_id")
        teacher_id = need.get("teacher_id")
        lesson_id = need.get("lesson_id")
        
        if not class_id or not teacher_id or not lesson_id:
            return filled_count
        
        # Try placement with relaxed constraints
        for day in range(5):  # 5 days
            if filled_count >= remaining_hours:
                break
                
            for time_slot in range(8):  # Try up to 8 time slots
                if filled_count >= remaining_hours:
                    break
                    
                # Try to place with relaxed constraints
                can_place = self._can_place_relaxed(
                    class_id, teacher_id, day, time_slot
                )
                
                if can_place:
                    # Place the lesson
                    classroom_id = 1  # Default classroom
                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                    filled_count += 1
                    need["scheduled"] = need.get("scheduled", 0) + 1
                    
                    self.logger.info(f"       ✓ Aggressively placed: Day {day+1}, Slot {time_slot+1}")
        
        return filled_count

    def _aggressive_placement_for_remaining(self, all_needs: List[Dict]) -> int:
        """
        Aggressively place remaining difficult assignments by relaxing some constraints
        """
        filled_count = 0
        
        # Get assignments that still need placement
        remaining_needs = self._get_remaining_assignments()
        
        # Try to place each remaining assignment
        for need in remaining_needs:
            class_id = need.get("class_id")
            lesson_id = need.get("lesson_id")
            teacher_id = need.get("teacher_id")
            remaining_hours = need.get("remaining_hours", 0)
            
            if not class_id or not teacher_id or not lesson_id:
                continue
            
            # Try each day and time slot
            for day in range(5):
                for time_slot in range(8):
                    # Try aggressive placement (even with relaxed constraints)
                    if self._try_aggressive_placement(class_id, lesson_id, teacher_id, day, time_slot):
                        filled_count += 1
                        remaining_hours -= 1
                        if remaining_hours <= 0:
                            break
                if remaining_hours <= 0:
                    break
        
        return filled_count

    def _get_remaining_assignments(self) -> List[Dict[str, Any]]:
        """
        Get list of assignments that still need placement
        """
        # Get all assignments from database
        all_assignments = self.db_manager.get_schedule_by_school_type()
        remaining_needs = []
        
        # Check each assignment
        for assignment in all_assignments:
            class_id = assignment.class_id
            lesson_id = assignment.lesson_id
            teacher_id = assignment.teacher_id
            
            # Count how many are already placed
            current_count = sum(1 for entry in self.schedule_entries 
                               if entry["class_id"] == class_id and entry["lesson_id"] == lesson_id)
            
            class_obj = next((c for c in self.db_manager.get_all_classes() if c.class_id == class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(lesson_id, class_obj.grade)
                
                if weekly_hours and current_count < weekly_hours:
                    remaining_needs.append({
                        "class_id": class_id,
                        "lesson_id": lesson_id,
                        "teacher_id": teacher_id,
                        "remaining_hours": weekly_hours - current_count,
                        "weekly_hours": weekly_hours
                    })
        
        return remaining_needs

    def _decompose_into_blocks(self, weekly_hours: int) -> List[int]:
        """Haftalık saati bloklara ayır: 6→[2,2,2], 5→[2,2,1], vb."""
        blocks = []
        while weekly_hours >= 2:
            blocks.append(2)
            weekly_hours -= 2
        if weekly_hours == 1:
            blocks.append(1)
        return blocks
    
    def _find_consecutive_windows(self, class_id: int, teacher_id: int, lesson_id: int,
                                  day: int, length: int, time_slots_count: int) -> List[int]:
        """Belirli bir günde ardışık 'length' uzunluğunda uygun pencereleri bul"""
        windows = []
        for start_slot in range(time_slots_count - length + 1):
            slots = list(range(start_slot, start_slot + length))
            if self._can_place_all(class_id, teacher_id, day, slots, lesson_id):
                # 3 ardışık aynı ders oluşmasın kontrolü
                ok = True
                for s in slots:
                    if self._would_create_three_consecutive_lessons(class_id, lesson_id, day, s):
                        ok = False
                        break
                if ok:
                    windows.append(start_slot)
        return windows
    
    def _remove_entry(self, class_id: int, teacher_id: int, lesson_id: int, day: int, slot: int):
        """Bir kaydı geri al (rollback için)"""
        for i in range(len(self.schedule_entries) - 1, -1, -1):
            e = self.schedule_entries[i]
            if (e["class_id"] == class_id and e["teacher_id"] == teacher_id and
                e["lesson_id"] == lesson_id and e["day"] == day and e["time_slot"] == slot):
                self.schedule_entries.pop(i)
                self.class_slots[class_id].discard((day, slot))
                self.teacher_slots[teacher_id].discard((day, slot))
                return
    
    def _schedule_lesson(self, need: Dict, time_slots_count: int, classrooms: List, max_attempts: int = 5) -> int:
        """
        BLOK SISTEMİ (KATI - BACKTRACKING): Blokları AYRI günlerde ve ARDIŞIK slotlarda yerleştir.
        Fallback olarak tekli yerleştirme YOK (strict mode).
        Örnek: 5 saat → [2+2+1] üç ayrı günde, her blok ardışık
        """
        class_id = need["class_id"]
        teacher_id = need["teacher_id"]
        lesson_id = need["lesson_id"]
        weekly_hours = need["weekly_hours"]

        # Bloklara ayır ve büyükten küçüğe sırala
        blocks = self._decompose_into_blocks(weekly_hours)
        blocks.sort(reverse=True)  # 2'ler önce
        
        classroom = classrooms[0] if classrooms else None
        classroom_id = classroom.classroom_id if classroom else 1
        
        used_days = set()
        
        def backtrack(i: int) -> bool:
            """Backtracking ile blokları yerleştir"""
            if i == len(blocks):
                return True  # Tüm bloklar yerleşti
            
            size = blocks[i]
            
            # Günleri, o gün için mevcut pencere sayısına göre sırala (az pencere önce)
            day_candidates = []
            for day in range(5):
                if day in used_days:
                    continue
                wins = self._find_consecutive_windows(class_id, teacher_id, lesson_id, day, size, time_slots_count)
                if wins:
                    day_candidates.append((day, wins))
            
            # En az penceresi olan günler önce (zorları önce çöz)
            day_candidates.sort(key=lambda x: len(x[1]))
            
            # Her uygun günü dene
            for day, windows in day_candidates:
                for start in windows:
                    slots = list(range(start, start + size))
                    
                    # Yerleştir
                    for s in slots:
                        self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, s)
                    used_days.add(day)
                    
                    # Recursive - sonraki bloğu yerleştir
                    if backtrack(i + 1):
                        return True
                    
                    # Başarısız - geri al (rollback)
                    for s in slots:
                        self._remove_entry(class_id, teacher_id, lesson_id, day, s)
                    used_days.remove(day)
            
            return False  # Bu blok yerleştirilemedi
        
        # Backtracking başlat
        success = backtrack(0)
        
        if success:
            self.logger.debug(f"        ✓ {need['class_name']} - {need['lesson_name']}: {weekly_hours} saat blok olarak yerleştirildi")
            return weekly_hours
        
        # Tam yerleşemedi - kısmi başarı için sadece 2'li blokları dene
        two_blocks = [b for b in blocks if b == 2]
        if len(two_blocks) > 0 and len(two_blocks) != len(blocks):
            used_days.clear()
            
            def backtrack_twos(i: int) -> bool:
                if i == len(two_blocks):
                    return True
                size = 2
                day_candidates = []
                for day in range(5):
                    if day in used_days:
                        continue
                    wins = self._find_consecutive_windows(class_id, teacher_id, lesson_id, day, size, time_slots_count)
                    if wins:
                        day_candidates.append((day, wins))
                day_candidates.sort(key=lambda x: len(x[1]))
                
                for day, windows in day_candidates:
                    for start in windows:
                        slots = [start, start + 1]
                        for s in slots:
                            self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, s)
                        used_days.add(day)
                        
                        if backtrack_twos(i + 1):
                            return True
                        
                        for s in slots:
                            self._remove_entry(class_id, teacher_id, lesson_id, day, s)
                        used_days.remove(day)
                return False
            
            if backtrack_twos(0):
                partial = len(two_blocks) * 2
                self.logger.warning(f"        ⚠️  {need['class_name']} - {need['lesson_name']}: Kısmi yerleştirme {partial}/{weekly_hours}")
                return partial
        
        # Hiçbir şey yerleştirilemedi
        self.logger.error(f"        ❌ {need['class_name']} - {need['lesson_name']}: Yerleştirilemedi!")
        return 0
    
    def _schedule_lesson_OLD_BROKEN(self, need: Dict, time_slots_count: int, classrooms: List, max_attempts: int = 5) -> int:
        """
        ESKİ VE BOZUK VERSİYON - KULLANMAYIN!
        BLOK SISTEMİ - TÜM DERSLER İÇİN 2+2+1 HAFTALIK DAĞILIM
        Her ders haftalık olarak belirlenen günlere bloklar halinde dağıtılır
        Hafta içi günlerde denge sağlanır
        """
        class_id = need["class_id"]
        teacher_id = need["teacher_id"]
        lesson_id = need["lesson_id"]
        weekly_hours = need["weekly_hours"]

        scheduled = 0

        # BLOK SISTEMİ: Tüm dersler için haftalık 3 gün kullanılır
        # Gün seçimi: Pazartesi, Salı, Perşembe (2+2+1 dağılım için)
        block_days = self._select_block_days(weekly_hours)

        if len(block_days) >= 1:
            # Her gün için blok boyutu hesapla
            block_sizes = self._calculate_block_sizes_for_days(weekly_hours, block_days)

            self.logger.info(
                f"    📅 BLOK SISTEMİ: {weekly_hours} saat -> {len(block_days)} güne dağıtım: {block_sizes}"
            )

            # Her gün için blok yerleştir (ardışık saatler)
            for block_size in block_sizes:
                placed = False
                for day in block_days:
                    block_scheduled = self._try_single_block_on_day(
                        class_id, teacher_id, lesson_id, day, block_size, time_slots_count, classrooms
                    )
                    if block_scheduled:
                        scheduled += block_size
                        placed = True
                        break
                if not placed:
                    break
        else:
            # Blok sistem başarısız, esnek yerleştirme
            scheduled, used_days = self._try_blocks_strict(
                class_id, teacher_id, lesson_id, weekly_hours // 2 or 1, time_slots_count, classrooms, 2
            )

        # KALAN SAATLER İÇİN BLOK SISTEMİ DEVAM
        if scheduled < weekly_hours:
            remaining = weekly_hours - scheduled
            # Kalan saatleri küçük bloklar olarak dağıt
            while remaining > 0 and remaining >= 1:
                block_size = min(remaining, 2)  # Maksimum 2 saat blok
                block_placed = self._try_place_remaining_block(
                    class_id, teacher_id, lesson_id, block_size, time_slots_count, classrooms, set(block_days) if 'block_days' in locals() else set()
                )
                if block_placed:
                    scheduled += block_size
                    remaining -= block_size
                else:
                    remaining -= 1  # Azaltarak dene

        # ESKİ UYARILAR
        if scheduled < weekly_hours:
            remaining = weekly_hours - scheduled
            scheduled += self._try_any_available(
                class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
            )

        return scheduled

    def _try_blocks_strict(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        num_blocks: int,
        time_slots_count: int,
        classrooms: List,
        block_size: int,
    ) -> tuple:
        """
        Belirli sayıda blok yerleştir - Her blok FARKLI bir güne
        Örn: 2+2+2 için num_blocks=3, block_size=2
        Returns: (scheduled_count, used_days_set)
        """
        scheduled = 0
        used_days = set()
        blocks_placed = 0

        for _ in range(num_blocks):
            placed = False

            # Kullanılmamış günleri dene
            for day in range(5):
                if day in used_days:
                    continue

                # Ardışık slotlar bul
                for start_slot in range(time_slots_count - block_size + 1):
                    slots = list(range(start_slot, start_slot + block_size))

                    # Tüm slotlar uygun mu?
                    if self._can_place_all(class_id, teacher_id, day, slots, lesson_id):
                        # Yerleştir
                        classroom = classrooms[0] if classrooms else None
                        classroom_id = classroom.classroom_id if classroom else 1

                        for slot in slots:
                            self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                            scheduled += 1

                        used_days.add(day)
                        blocks_placed += 1
                        placed = True
                        break

                if placed:
                    break

            if not placed:
                break

        return scheduled, used_days

    def _try_blocks(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        total_hours: int,
        time_slots_count: int,
        classrooms: List,
        block_size: int,
    ) -> int:
        """2'li veya 3'lü bloklar halinde yerleştir (eski yöntem - yedek)"""
        scheduled = 0
        num_blocks = total_hours // block_size
        used_days = set()

        for _ in range(num_blocks):
            placed = False

            # Kullanılmamış günleri dene
            for day in range(5):
                if day in used_days:
                    continue

                # Ardışık slotlar bul
                for start_slot in range(time_slots_count - block_size + 1):
                    slots = list(range(start_slot, start_slot + block_size))

                    # Tüm slotlar uygun mu?
                    if self._can_place_all(class_id, teacher_id, day, slots, lesson_id):
                        # Yerleştir
                        classroom = classrooms[0] if classrooms else None
                        classroom_id = classroom.classroom_id if classroom else 1

                        for slot in slots:
                            self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                            scheduled += 1

                        used_days.add(day)
                        placed = True
                        break

                if placed:
                    break

            if not placed:
                break

        return scheduled

    def _try_singles(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        hours_needed: int,
        time_slots_count: int,
        classrooms: List,
        exclude_days: set = None,
    ) -> int:
        """
        Tekli slotlar halinde yerleştir
        exclude_days: Bu günlere yerleştirme yapma (aynı güne 2+1 olmasın diye)
        """
        scheduled = 0
        if exclude_days is None:
            exclude_days = set()

        # Tüm slotları dene
        for day in range(5):
            if scheduled >= hours_needed:
                break

            # ÖNEMLİ: Aynı güne yerleştirme yapma
            if day in exclude_days:
                continue

            for slot in range(time_slots_count):
                if scheduled >= hours_needed:
                    break

                if self._can_place_all(class_id, teacher_id, day, [slot], lesson_id):
                    classroom = classrooms[0] if classrooms else None
                    classroom_id = classroom.classroom_id if classroom else 1

                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                    scheduled += 1

        return scheduled

    def _try_any_available(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        hours_needed: int,
        time_slots_count: int,
        classrooms: List,
    ) -> int:
        """Herhangi bir boş slotu doldur"""
        scheduled = 0
        attempts = 0
        max_attempts = hours_needed * 100  # Artırıldı: 10 -> 100

        while scheduled < hours_needed and attempts < max_attempts:
            attempts += 1

            # Rastgele slot seç
            day = random.randint(0, 4)
            slot = random.randint(0, time_slots_count - 1)

            if self._can_place_all(class_id, teacher_id, day, [slot], lesson_id):
                classroom = classrooms[0] if classrooms else None
                classroom_id = classroom.classroom_id if classroom else 1

                self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                scheduled += 1

        return scheduled

    def _try_relaxed(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        hours_needed: int,
        time_slots_count: int,
        classrooms: List,
    ) -> int:
        """Öğretmen uygunluğunu esnetilmiş kontrol (son çare)"""
        scheduled = 0

        for day in range(5):
            if scheduled >= hours_needed:
                break

            for slot in range(time_slots_count):
                if scheduled >= hours_needed:
                    break

                # Sadece çakışma kontrolü (uygunluk kontrolü YOK)
                if self._can_place_relaxed(class_id, teacher_id, day, slot):
                    classroom = classrooms[0] if classrooms else None
                    classroom_id = classroom.classroom_id if classroom else 1

                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                    scheduled += 1

        return scheduled
    
    def _ultra_aggressive_gap_filling(self) -> int:
        """
        ULTRA AGRESİF BOŞLUK DOLDURMA
        Son çare: Tüm eksiklikleri yerleştir
        Öğretmen uygunluk kontrolü YAPILMAZ (sadece çakışma kontrolü)
        """
        filled_count = 0
        
        classes = self.db_manager.get_all_classes()
        lessons = self.db_manager.get_all_lessons()
        assignments = self.db_manager.get_schedule_by_school_type()
        
        assignment_map = {(a.class_id, a.lesson_id): a.teacher_id for a in assignments}
        
        for class_obj in classes:
            for lesson in lessons:
                key = (class_obj.class_id, lesson.lesson_id)
                if key in assignment_map:
                    # Haftalık gereksinim
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                        lesson.lesson_id, class_obj.grade
                    )
                    
                    if not weekly_hours:
                        continue
                    
                    # Mevcut yerleşme
                    current_count = sum(
                        1 for entry in self.schedule_entries 
                        if entry["class_id"] == class_obj.class_id 
                        and entry["lesson_id"] == lesson.lesson_id
                    )
                    
                    # Eksik varsa
                    if current_count < weekly_hours:
                        remaining = weekly_hours - current_count
                        teacher_id = assignment_map[key]
                        
                        self.logger.info(f"   📌 {class_obj.name} - {lesson.name}: {remaining} saat eksik")
                        
                        # Her gün, her slotu dene (öğretmen uygunluk kontrolü YOK)
                        for day in range(5):
                            if remaining <= 0:
                                break
                            for slot in range(7):
                                if remaining <= 0:
                                    break
                                    
                                # SADECE çakışma kontrolü (availability kontrolü yok)
                                class_free = (day, slot) not in self.class_slots[class_obj.class_id]
                                teacher_free = (day, slot) not in self.teacher_slots[teacher_id]
                                
                                if class_free and teacher_free:
                                    # Yerleştir
                                    self._add_entry(
                                        class_obj.class_id,
                                        teacher_id,
                                        lesson.lesson_id,
                                        1,  # classroom_id
                                        day,
                                        slot
                                    )
                                    remaining -= 1
                                    filled_count += 1
                                    self.logger.debug(f"      ✅ Yerleştirildi: Gün {day+1}, Slot {slot+1}")
        
        return filled_count
    
    def _can_place_all(self, class_id: int, teacher_id: int, day: int, slots: List[int], lesson_id: int = None) -> bool:
        """Tüm slotlara yerleştirilebilir mi? - BLOK SISTEMİ için güncellenmiş"""

        for slot in slots:
            # Sınıf çakışması
            if (day, slot) in self.class_slots[class_id]:
                return False

            # Öğretmen çakışması
            if (day, slot) in self.teacher_slots[teacher_id]:
                return False

            # Öğretmen uygunluğu kontrolü - Relaxed mode'da atlanır
            if not self.relaxed_mode:
                try:
                    if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                        return False
                except Exception:
                    pass  # Uygunluk kontrolü başarısız olursa devam

        return True

    def _would_create_three_consecutive_lessons(self, class_id: int, lesson_id: int, day: int, slot: int) -> bool:
        """
        Bu slot'a ders yerleştirilirse 3 saat üst üste aynı ders olur mu?
        Returns True if placing would create 3 consecutive same lessons
        """
        # Bu sınıfın bu gündeki tüm derslerini bul
        class_schedule_today = []
        for entry in self.schedule_entries:
            if entry["class_id"] == class_id and entry["day"] == day:
                class_schedule_today.append((entry["time_slot"], entry["lesson_id"]))

        # Slot'a göre sırala
        class_schedule_today.sort(key=lambda x: x[0])

        # Şimdi bu yeni slot'u ekleyip kontrol edelim
        # Önceki 2 slot'a bak
        consecutive_before = 0
        for check_slot in range(slot - 1, slot - 3, -1):
            if check_slot < 0:
                break
            # Bu slot'ta aynı ders var mı?
            found = False
            for s, l_id in class_schedule_today:
                if s == check_slot and l_id == lesson_id:
                    consecutive_before += 1
                    found = True
                    break
            if not found:
                break  # Ardışıklık bozuldu

        # Sonraki 2 slot'a bak
        consecutive_after = 0
        for check_slot in range(slot + 1, slot + 3):
            # Bu slot'ta aynı ders var mı?
            found = False
            for s, l_id in class_schedule_today:
                if s == check_slot and l_id == lesson_id:
                    consecutive_after += 1
                    found = True
                    break
            if not found:
                break  # Ardışıklık bozuldu

        # Toplam ardışık ders sayısı (önceki + bu slot + sonraki)
        total_consecutive = consecutive_before + 1 + consecutive_after

        # 3 veya daha fazla ardışık ders olacaksa engelle
        return total_consecutive >= 3

    def _can_place_relaxed(self, class_id: int, teacher_id: int, day: int, slot: int) -> bool:
        """Esnek kontrol (sadece çakışma)"""
        # Sınıf çakışması
        if (day, slot) in self.class_slots[class_id]:
            return False

        # Öğretmen çakışması
        if (day, slot) in self.teacher_slots[teacher_id]:
            return False

        return True

    def _select_block_days(self, weekly_hours: int) -> List[int]:
        """
        Blok sistemi için gerek günleri seç - 2+2+1 dağılımı
        """
        if weekly_hours <= 1:
            return [0]  # Sadece Pazartesi
        elif weekly_hours <= 2:
            return [0]  # Pazartesi (2 saat blok)
        elif weekly_hours <= 3:
            return [0, 1]  # Pazartesi+Salı
        elif weekly_hours <= 5:
            return [0, 1, 3]  # Pazartesi+Salı+Perşembe (2+2+1)
        else:
            # Daha fazla saat için tüm günleri kullan
            return [0, 1, 2, 3, 4]  # Pazartesi-Cuma

    def _calculate_block_sizes_for_days(self, weekly_hours: int, block_days: List[int]) -> List[int]:
        """
        Haftalık saati günlere göre blok boyutlarına böl - 2+2+1 sistemi
        """
        num_days = len(block_days)

        if weekly_hours <= 2:
            return [weekly_hours]
        elif weekly_hours <= 4:
            if num_days >= 2:
                return [2] * (weekly_hours // 2) + [weekly_hours % 2]
            else:
                return [weekly_hours]
        else:  # 5+ saat
            if num_days >= 3:
                # 2+2+1 şeklinde dağıt
                if weekly_hours >= 5:
                    remaining = weekly_hours - 4  # İlk günlerin 2+2'si
                    return [2, 2] + [remaining if remaining >= 1 else 1]
                else:
                    return [2] * (weekly_hours // 2) + [weekly_hours % 2]
            else:
                return [2] * (weekly_hours // 2) + [weekly_hours % 2]

    def _try_single_block_on_day(self, class_id: int, teacher_id: int, lesson_id: int,
                                day: int, block_size: int, time_slots_count: int, classrooms: List) -> bool:
        """
        Belirli bir güne ardışık blok yerleştir
        """
        for start_slot in range(time_slots_count - block_size + 1):
            slots = list(range(start_slot, start_slot + block_size))

            if self._can_place_all(class_id, teacher_id, day, slots, lesson_id):
                classroom = classrooms[0] if classrooms else None
                classroom_id = classroom.classroom_id if classroom else 1

                for slot in slots:
                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)

                self.logger.debug(f"        ✓ BLOK yerleştirildi: Gün {day+1}, Saat {start_slot+1}-{start_slot+

block_size}")
                return True

        return False

    def _try_place_remaining_block(self, class_id: int, teacher_id: int, lesson_id: int, block_size: int,
                                  time_slots_count: int, classrooms: List, used_days: set) -> bool:
        """
        Kalan blok için kullanılmamış bir gün bul
        """
        for day in range(5):
            if day in used_days:
                continue

            if self._try_single_block_on_day(class_id, teacher_id, lesson_id, day, block_size, time_slots_count, classrooms):
                return True

        return False

    def _add_entry(self, class_id: int, teacher_id: int, lesson_id: int, classroom_id: int, day: int, slot: int):
        """Kayıt ekle"""
        entry = {
            "class_id": class_id,
            "teacher_id": teacher_id,
            "lesson_id": lesson_id,
            "classroom_id": classroom_id,
            "day": day,
            "time_slot": slot,
        }

        self.schedule_entries.append(entry)
        self.class_slots[class_id].add((day, slot))
        self.teacher_slots[teacher_id].add((day, slot))
        
    def _fill_remaining_gaps(self, assignments, time_slots_count: int) -> int:
        """
        Fill remaining gaps in the schedule using available slots
        """
        filled_count = 0
        
        # Get all classes
        classes = self.db_manager.get_all_classes()
        
        # For each class, check each day for empty slots
        for class_obj in classes:
            for day in range(5):  # 5 days per week
                # Check for empty slots in this day for this class
                occupied_slots = set()
                for entry in self.schedule_entries:
                    if entry["class_id"] == class_obj.class_id and entry["day"] == day:
                        occupied_slots.add(entry["time_slot"])
                
                # Try to fill empty slots
                for time_slot in range(time_slots_count):
                    if time_slot not in occupied_slots:
                        # This slot is empty, try to place a needed assignment
                        filled = self._try_place_in_empty_slot(class_obj.class_id, day, time_slot, assignments)
                        if filled:
                            filled_count += 1
        
        return filled_count
    
    def _try_place_in_empty_slot(self, class_id: int, day: int, time_slot: int, assignments) -> bool:
        """
        Try to place a needed assignment in an empty slot
        """
        # Get all assignments for this class
        class_assignments = [a for a in assignments if a.class_id == class_id]
        
        # Try each assignment that might still need placement
        for assignment in class_assignments:
            # Check if this assignment still needs more hours
            current_count = sum(1 for entry in self.schedule_entries 
                              if entry["class_id"] == class_id and entry["lesson_id"] == assignment.lesson_id)
            
            class_obj = next((c for c in self.db_manager.get_all_classes() if c.class_id == class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                
                if weekly_hours and current_count < weekly_hours:
                    # Try to place this assignment in the empty slot
                    teacher_id = assignment.teacher_id
                    lesson_id = assignment.lesson_id
                    
                    # Check if we can place (relaxed constraints)
                    if self._can_place_relaxed(class_id, teacher_id, day, time_slot):
                        # Place the assignment
                        classroom_id = 1  # Default classroom
                        self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                        return True
        
        return False
    
    def _aggressive_placement_for_remaining(self, assignments, time_slots_count: int) -> int:
        """
        Aggressively place remaining difficult assignments by relaxing some constraints
        """
        filled_count = 0
        
        # Get assignments that still need placement
        remaining_needs = self._get_remaining_assignments()
        
        # Try to place each remaining assignment
        for need in remaining_needs:
            class_id = need["class_id"]
            lesson_id = need["lesson_id"]
            teacher_id = need["teacher_id"]
            remaining_hours = need["remaining_hours"]
            
            # Try each day and time slot
            for day in range(5):
                for time_slot in range(time_slots_count):
                    # Try aggressive placement (even with relaxed constraints)
                    if self._try_aggressive_placement(class_id, lesson_id, teacher_id, day, time_slot):
                        filled_count += 1
                        remaining_hours -= 1
                        if remaining_hours <= 0:
                            break
                if remaining_hours <= 0:
                    break
        
        return filled_count
    
    def _get_remaining_assignments(self) -> List[Dict[str, Any]]:
        """
        Get list of assignments that still need placement
        """
        # Get all assignments from database
        all_assignments = self.db_manager.get_schedule_by_school_type()
        remaining_needs = []
        
        # Check each assignment
        for assignment in all_assignments:
            class_id = assignment.class_id
            lesson_id = assignment.lesson_id
            teacher_id = assignment.teacher_id
            
            # Count how many are already placed
            current_count = sum(1 for entry in self.schedule_entries 
                               if entry["class_id"] == class_id and entry["lesson_id"] == lesson_id)
            
            # Get required hours
            class_obj = next((c for c in self.db_manager.get_all_classes() if c.class_id == class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(lesson_id, class_obj.grade)
                
                if weekly_hours and current_count < weekly_hours:
                    remaining_needs.append({
                        "class_id": class_id,
                        "lesson_id": lesson_id,
                        "teacher_id": teacher_id,
                        "remaining_hours": weekly_hours - current_count,
                        "weekly_hours": weekly_hours
                    })
        
        return remaining_needs
    
    def _try_aggressive_placement(self, class_id: int, lesson_id: int, teacher_id: int, day: int, time_slot: int) -> bool:
        """
        Try aggressive placement with relaxed constraints
        """
        # Check basic hard constraints (no class/teacher conflicts)
        class_conflict = (day, time_slot) in self.class_slots[class_id]
        teacher_conflict = (day, time_slot) in self.teacher_slots[teacher_id]
        
        if not class_conflict and not teacher_conflict:
            # Place the assignment (ignoring some soft constraints)
            classroom_id = 1  # Default classroom
            self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
            return True
        
        return False

    def _schedule_full_curriculum(self, classes, teachers, lessons, assignments, time_slots_count: int) -> int:
        """
        Schedule full curriculum based on weekly hours requirements
        This addresses the core issue of only scheduling 112 assignments instead of 280 hours
        """
        scheduled_hours = 0
        
        self.logger.info(f"   📚 Tam müfredat programlaması başlatılıyor...")
        self.logger.info(f"      • Toplam sınıf: {len(classes)}")
        self.logger.info(f"      • Toplam öğretmen: {len(teachers)}")
        self.logger.info(f"      • Toplam ders: {len(lessons)}")
        
        # Get assignment map from existing assignments
        assignment_map = {}
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id)
            assignment_map[key] = assignment.teacher_id
        
        # For each class, schedule all required lessons based on curriculum
        for class_obj in classes:
            self.logger.info(f"   📖 {class_obj.name} için müfredat planlaması...")
            
            # Get all lessons required for this class grade
            class_lessons = []
            for lesson in lessons:
                assignment_key = (class_obj.class_id, lesson.lesson_id)
                if assignment_key in assignment_map:
                    # Get weekly hours from curriculum
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                    if weekly_hours and weekly_hours > 0:
                        teacher_id = assignment_map[assignment_key]
                        teacher = self.db_manager.get_teacher_by_id(teacher_id)
                        if teacher:
                            class_lessons.append({
                                "lesson": lesson,
                                "weekly_hours": weekly_hours,
                                "teacher": teacher,
                                "teacher_id": teacher_id
                            })
                            self.logger.info(f"      📋 {lesson.name}: {weekly_hours} saat ({teacher.name})")
            
            # Schedule each required lesson for this class
            for lesson_info in class_lessons:
                lesson = lesson_info["lesson"]
                weekly_hours = lesson_info["weekly_hours"]
                teacher = lesson_info["teacher"]
                teacher_id = lesson_info["teacher_id"]
                
                self.logger.info(f"   🎯 {class_obj.name} - {lesson.name} ({weekly_hours} saat) yerleştiriliyor...")
                
                # Try to schedule all required hours
                scheduled_for_this_lesson = self._schedule_lesson_full_curriculum(
                    class_obj.class_id,
                    lesson.lesson_id,
                    teacher_id,
                    weekly_hours,
                    time_slots_count
                )
                
                scheduled_hours += scheduled_for_this_lesson
                self.logger.info(f"      ✅ {scheduled_for_this_lesson}/{weekly_hours} saat yerleştirildi")
        
        self.logger.info(f"   📊 Tam müfredat planlaması tamamlandı: {scheduled_hours} saat")
        return scheduled_hours

    def _schedule_lesson_full_curriculum(self, class_id: int, lesson_id: int, teacher_id: int, 
                                       weekly_hours: int, time_slots_count: int) -> int:
        """
        Schedule a lesson for its full weekly hours requirement
        """
        scheduled_count = 0
        max_attempts = weekly_hours * 20  # More attempts for better coverage
        attempts = 0
        
        # Try to schedule all required hours
        while scheduled_count < weekly_hours and attempts < max_attempts:
            attempts += 1
            
            # Try different strategies for placement
            for day in range(5):  # 5 days per week
                if scheduled_count >= weekly_hours:
                    break
                    
                for time_slot in range(time_slots_count):
                    if scheduled_count >= weekly_hours:
                        break
                        
                    # Check if we can place this lesson here (relaxed constraints)
                    can_place = self._can_place_relaxed(class_id, teacher_id, day, time_slot)
                    
                    if can_place:
                        # Place the lesson
                        classroom_id = 1  # Default classroom
                        self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                        scheduled_count += 1
                        self.logger.debug(f"         ✓ Yerleştirildi: Gün {day+1}, Slot {time_slot+1}")
                        break  # Move to next hour needed
        
        # If we couldn't place all hours, try aggressive placement
        if scheduled_count < weekly_hours:
            remaining = weekly_hours - scheduled_count
            self.logger.warning(f"      ⚠️  {remaining} saat eksik kaldı, agresif yerleştirme denemesi...")
            aggressive_placed = self._aggressive_placement_for_remaining_hours(
                class_id, lesson_id, teacher_id, remaining, time_slots_count
            )
            scheduled_count += aggressive_placed
            
        return scheduled_count

    def _aggressive_placement_for_remaining_hours(self, class_id: int, lesson_id: int, teacher_id: int, 
                                               remaining_hours: int, time_slots_count: int) -> int:
        """
        Aggressively place remaining hours with relaxed constraints
        """
        placed_count = 0
        
        # Try each day and time slot with very relaxed constraints
        for day in range(5):
            if placed_count >= remaining_hours:
                break
                
            for time_slot in range(time_slots_count):
                if placed_count >= remaining_hours:
                    break
                    
                # Very relaxed check - only hard constraints (class/teacher conflicts)
                class_conflict = (day, time_slot) in self.class_slots[class_id]
                teacher_conflict = (day, time_slot) in self.teacher_slots[teacher_id]
                
                if not class_conflict and not teacher_conflict:
                    # Place the lesson
                    classroom_id = 1  # Default classroom
                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                    placed_count += 1
                    self.logger.debug(f"         ⚡ Agresif yerleştirme: Gün {day+1}, Slot {time_slot+1}")
        
        return placed_count
        return placed_count

    def _enhanced_gap_filling(self, all_needs: List[Dict]) -> int:
        """
        Enhanced gap filling strategy to improve coverage
        """
        gap_filled_count = 0
        
        # Try to fill gaps for each need that wasn't fully scheduled
        for need in all_needs:
            scheduled = need.get("scheduled", 0)
            weekly_hours = need.get("weekly_hours", 0)
            
            if scheduled < weekly_hours:
                remaining = weekly_hours - scheduled
                self.logger.info(f"     Gap filling for {need.get('class_name', 'Unknown')} - "
                               f"{need.get('lesson_name', 'Unknown')}: {remaining} hours")
                
                # Try aggressive placement for remaining hours
                filled = self._aggressive_placement_for_need(need, remaining)
                gap_filled_count += filled
                
        return gap_filled_count

    def _aggressive_placement_for_need(self, need: Dict, remaining_hours: int) -> int:
        """
        Aggressively place remaining hours for a specific need
        """
        filled_count = 0
        class_id = need["class_id"]
        teacher_id = need["teacher_id"]
        lesson_id = need["lesson_id"]
        
        # Try placement with relaxed constraints
        for day in range(5):  # 5 days
            if filled_count >= remaining_hours:
                break
                
            for time_slot in range(8):  # Try up to 8 time slots
                if filled_count >= remaining_hours:
                    break
                    
                # Try to place with relaxed constraints
                can_place = self._can_place_relaxed(
                    class_id, teacher_id, day, time_slot
                )
                
                if can_place:
                    # Place the lesson
                    classroom_id = 1  # Default classroom
                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                    filled_count += 1
                    need["scheduled"] = need.get("scheduled", 0) + 1
                    
                    self.logger.info(f"       ✓ Aggressively placed: Day {day+1}, Slot {time_slot+1}")
        
        return filled_count
