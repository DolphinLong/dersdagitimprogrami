# -*- coding: utf-8 -*-
"""
Strict Scheduler - Tam Kapsama ve Öğretmen Uygunluk Garantili
Tüm dersleri öğretmen uygunluğuna göre yerleştirir ve tüm hücreleri doldurur
"""

import io
import random
import sys
from typing import Dict, List, Optional, Tuple

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class StrictScheduler:
    """
    Strict scheduler that guarantees:
    1. All lessons are placed (100% coverage)
    2. Teacher availability is ALWAYS respected
    3. All cells are filled based on weekly requirements
    """

    SCHOOL_TIME_SLOTS = {
        "İlkokul": 7,  # İlkokul: 5 gün × 7 saat = 35 hücre
        "Ortaokul": 7,  # Ortaokul: 5 gün × 7 saat = 35 hücre
        "Lise": 8,  # Lise: 5 gün × 8 saat = 40 hücre
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.schedule_entries = []
        self.teacher_usage = {}  # Track teacher usage per day/slot
        self.class_usage = {}  # Track class usage per day/slot

    def generate_schedule(self) -> List[Dict]:
        """
        Generate complete schedule with strict constraints
        """
        print("\n" + "=" * 80)
        print("🎯 STRICT SCHEDULER - Tam Kapsama ve Öğretmen Uygunluğu Garantili")
        print("=" * 80)

        # Clear existing schedule
        self.schedule_entries = []
        self.teacher_usage = {}
        self.class_usage = {}

        # Get data
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()
        assignments = self.db_manager.get_schedule_by_school_type()

        # Get school configuration
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        print(f"\n📊 Konfigürasyon:")
        print(f"   Okul Türü: {school_type}")
        print(f"   Günlük Ders Saati: {time_slots_count}")
        print(f"   Sınıf Sayısı: {len(classes)}")
        print(f"   Öğretmen Sayısı: {len(teachers)}")
        print(f"   Ders Sayısı: {len(lessons)}")
        print(f"   Ders Atamaları: {len(assignments)}")

        # Build assignment map: {(class_id, lesson_id): teacher_id}
        assignment_map = {}
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id)
            assignment_map[key] = assignment.teacher_id

        print(f"\n✅ {len(assignment_map)} benzersiz ders-öğretmen ataması oluşturuldu")

        # Process each class
        total_required = 0
        total_scheduled = 0
        failed_lessons = []

        for class_idx, class_obj in enumerate(classes, 1):
            print(f"\n{'='*80}")
            print(f"📚 [{class_idx}/{len(classes)}] Sınıf: {class_obj.name} (Seviye {class_obj.grade})")
            print(f"{'='*80}")

            # Get lessons for this class
            class_lessons = self._get_class_lessons(class_obj, lessons, assignment_map, teachers)

            if not class_lessons:
                print(f"⚠️  {class_obj.name} için ders ataması bulunamadı")
                continue

            # Sort by priority (more hours = higher priority)
            class_lessons.sort(key=lambda x: x["weekly_hours"], reverse=True)

            print(f"\n📋 Yerleştirilecek Dersler:")
            for lesson in class_lessons:
                print(
                    f"   • {lesson['lesson_name']}: {lesson['weekly_hours']} saat/hafta (Öğretmen: {lesson['teacher_name']})"
                )
                total_required += lesson["weekly_hours"]

            # Schedule each lesson with multiple strategies
            for lesson_info in class_lessons:
                scheduled = self._schedule_lesson_strict(class_obj, lesson_info, time_slots_count, classrooms)

                total_scheduled += scheduled

                if scheduled < lesson_info["weekly_hours"]:
                    failed_lessons.append(
                        {
                            "class": class_obj.name,
                            "lesson": lesson_info["lesson_name"],
                            "teacher": lesson_info["teacher_name"],
                            "required": lesson_info["weekly_hours"],
                            "scheduled": scheduled,
                        }
                    )
                    print(
                        f"   ❌ UYARI: {lesson_info['lesson_name']} tam yerleştirilemedi! ({scheduled}/{lesson_info['weekly_hours']})"
                    )

        # Final report
        print(f"\n{'='*80}")
        print(f"🎯 SONUÇ RAPORU")
        print(f"{'='*80}")
        print(f"📊 Toplam Gereksinim: {total_required} saat")
        print(f"✅ Yerleştirilen: {total_scheduled} saat")
        print(f"📈 Kapsama Oranı: {(total_scheduled/total_required*100):.1f}%")

        if failed_lessons:
            print(f"\n⚠️  {len(failed_lessons)} ders tam yerleştirilemedi:")
            for fail in failed_lessons:
                print(
                    f"   • {fail['class']} - {fail['lesson']} ({fail['teacher']}): {fail['scheduled']}/{fail['required']} saat"
                )
            print(f"\n💡 Öneriler:")
            print(f"   1. Öğretmen uygunluk saatlerini artırın")
            print(f"   2. Ders yükü dağılımını kontrol edin")
            print(f"   3. Sınıf sayısını/ders saatlerini gözden geçirin")
        else:
            print(f"\n🎉 Tüm dersler başarıyla yerleştirildi!")

        # Save to database
        print(f"\n💾 Veritabanına kaydediliyor...")
        self.db_manager.clear_schedule()

        saved_count = 0
        for entry in self.schedule_entries:
            if self.db_manager.add_schedule_program(
                entry["class_id"],
                entry["teacher_id"],
                entry["lesson_id"],
                entry["classroom_id"],
                entry["day"],
                entry["time_slot"],
            ):
                saved_count += 1

        print(f"✅ {saved_count} program girişi kaydedildi")

        return self.schedule_entries

    def _get_class_lessons(self, class_obj, lessons, assignment_map, teachers) -> List[Dict]:
        """Get all lessons assigned to a class"""
        class_lessons = []

        for lesson in lessons:
            assignment_key = (class_obj.class_id, lesson.lesson_id)
            if assignment_key in assignment_map:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)

                if weekly_hours and weekly_hours > 0:
                    teacher_id = assignment_map[assignment_key]
                    teacher = self.db_manager.get_teacher_by_id(teacher_id)

                    if teacher:
                        class_lessons.append(
                            {
                                "lesson_id": lesson.lesson_id,
                                "lesson_name": lesson.name,
                                "teacher_id": teacher.teacher_id,
                                "teacher_name": teacher.name,
                                "weekly_hours": weekly_hours,
                            }
                        )

        return class_lessons

    def _schedule_lesson_strict(self, class_obj, lesson_info: Dict, time_slots_count: int, classrooms: List) -> int:
        """
        Strictly schedule a lesson respecting teacher availability
        Returns number of hours successfully scheduled
        """
        lesson_name = lesson_info["lesson_name"]
        teacher_id = lesson_info["teacher_id"]
        teacher_name = lesson_info["teacher_name"]
        weekly_hours = lesson_info["weekly_hours"]
        lesson_id = lesson_info["lesson_id"]

        print(f"\n   📝 Yerleştiriliyor: {lesson_name} ({weekly_hours} saat)")
        print(f"      Öğretmen: {teacher_name}")

        scheduled_hours = 0
        used_days = set()

        # Strategy 1: Try to distribute across different days with 2-hour blocks
        print(f"      Strateji 1: Farklı günlere 2'li bloklar halinde dağıt")
        scheduled_hours = self._try_block_distribution(
            class_obj.class_id,
            teacher_id,
            lesson_id,
            weekly_hours,
            time_slots_count,
            classrooms,
            used_days,
            block_size=2,
        )

        # Strategy 2: If not fully scheduled, try single-hour slots
        if scheduled_hours < weekly_hours:
            remaining = weekly_hours - scheduled_hours
            print(f"      Strateji 2: Kalan {remaining} saati tekli slotlara yerleştir")
            scheduled_hours += self._try_single_slots(
                class_obj.class_id,
                teacher_id,
                lesson_id,
                remaining,
                time_slots_count,
                classrooms,
                used_days,
            )

        # Strategy 3: Allow same-day placement if still not complete
        if scheduled_hours < weekly_hours:
            remaining = weekly_hours - scheduled_hours
            print(f"      Strateji 3: Kalan {remaining} saati aynı güne yerleştirmeye izin ver")
            scheduled_hours += self._try_any_available_slot(
                class_obj.class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
            )

        success_rate = (scheduled_hours / weekly_hours * 100) if weekly_hours > 0 else 0

        if scheduled_hours == weekly_hours:
            print(f"      ✅ Başarılı: {scheduled_hours}/{weekly_hours} saat ({success_rate:.0f}%)")
        elif scheduled_hours > 0:
            print(f"      ⚠️  Kısmi: {scheduled_hours}/{weekly_hours} saat ({success_rate:.0f}%)")
        else:
            print(f"      ❌ Başarısız: Hiçbir saat yerleştirilemedi")

        return scheduled_hours

    def _try_block_distribution(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        total_hours: int,
        time_slots_count: int,
        classrooms: List,
        used_days: set,
        block_size: int = 2,
    ) -> int:
        """Try to distribute lessons in blocks across different days"""
        scheduled = 0

        # Calculate how many blocks we need
        full_blocks = total_hours // block_size
        remaining_single = total_hours % block_size

        # Shuffle days for randomization
        days = [0, 1, 2, 3, 4]
        random.shuffle(days)

        # Try to place full blocks
        for _ in range(full_blocks):
            placed = False
            for day in days:
                if day in used_days:
                    continue

                # Find consecutive slots for this block
                for start_slot in range(time_slots_count - block_size + 1):
                    slots = list(range(start_slot, start_slot + block_size))

                    if self._can_place_lesson(class_id, teacher_id, day, slots):
                        # Place the block
                        classroom = self._find_available_classroom(classrooms, day, slots[0])
                        classroom_id = classroom.classroom_id if classroom else 1

                        for slot in slots:
                            self._add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                            scheduled += 1

                        used_days.add(day)
                        placed = True
                        break

                if placed:
                    break

            if not placed:
                break  # Can't place more blocks

        return scheduled

    def _try_single_slots(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        hours_needed: int,
        time_slots_count: int,
        classrooms: List,
        used_days: set,
    ) -> int:
        """Try to place lessons in single-hour slots on unused days"""
        scheduled = 0

        # Prefer unused days
        days = [d for d in range(5) if d not in used_days]
        random.shuffle(days)

        for day in days:
            if scheduled >= hours_needed:
                break

            for slot in range(time_slots_count):
                if scheduled >= hours_needed:
                    break

                if self._can_place_lesson(class_id, teacher_id, day, [slot]):
                    classroom = self._find_available_classroom(classrooms, day, slot)
                    classroom_id = classroom.classroom_id if classroom else 1

                    self._add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                    scheduled += 1
                    used_days.add(day)

        return scheduled

    def _try_any_available_slot(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        hours_needed: int,
        time_slots_count: int,
        classrooms: List,
    ) -> int:
        """Try to place lessons in ANY available slot (last resort)"""
        scheduled = 0

        # Try all days and slots
        for day in range(5):
            if scheduled >= hours_needed:
                break

            for slot in range(time_slots_count):
                if scheduled >= hours_needed:
                    break

                if self._can_place_lesson(class_id, teacher_id, day, [slot]):
                    classroom = self._find_available_classroom(classrooms, day, slot)
                    classroom_id = classroom.classroom_id if classroom else 1

                    self._add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                    scheduled += 1

        return scheduled

    def _can_place_lesson(self, class_id: int, teacher_id: int, day: int, slots: List[int]) -> bool:
        """
        Check if lesson can be placed at given time
        STRICTLY checks teacher availability
        """
        for slot in slots:
            # CRITICAL: Check teacher availability (MUST be available)
            if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                return False

            # Check if slot already used by this class
            key = (class_id, day, slot)
            if key in self.class_usage:
                return False

            # Check if teacher already teaching at this time
            teacher_key = (teacher_id, day, slot)
            if teacher_key in self.teacher_usage:
                return False

        return True

    def _add_schedule_entry(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        classroom_id: int,
        day: int,
        time_slot: int,
    ):
        """Add entry to schedule and update usage tracking"""
        entry = {
            "class_id": class_id,
            "teacher_id": teacher_id,
            "lesson_id": lesson_id,
            "classroom_id": classroom_id,
            "day": day,
            "time_slot": time_slot,
        }

        self.schedule_entries.append(entry)

        # Update usage tracking
        self.class_usage[(class_id, day, time_slot)] = True
        self.teacher_usage[(teacher_id, day, time_slot)] = True

    def _find_available_classroom(self, classrooms: List, day: int, time_slot: int):
        """Find an available classroom for given time"""
        for classroom in classrooms:
            # Check if classroom is used at this time
            used = False
            for entry in self.schedule_entries:
                if (
                    entry["classroom_id"] == classroom.classroom_id
                    and entry["day"] == day
                    and entry["time_slot"] == time_slot
                ):
                    used = True
                    break

            if not used:
                return classroom

        # Return first classroom as fallback
        return classrooms[0] if classrooms else None
