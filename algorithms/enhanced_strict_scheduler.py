# -*- coding: utf-8 -*-
"""
Enhanced Strict Scheduler - %100 Doluluk İçin İyileştirilmiş
Backtracking ve akıllı slot önceliklendirme ile
"""

import io
import random
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class EnhancedStrictScheduler:
    """
    Geliştirilmiş scheduler:
    - Backtracking ile geri izleme
    - Dinamik slot önceliklendirme
    - Akıllı çakışma çözme
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
        self.schedule_entries = []
        self.teacher_usage = defaultdict(lambda: defaultdict(set))  # {teacher_id: {day: {slots}}}
        self.class_usage = defaultdict(lambda: defaultdict(set))  # {class_id: {day: {slots}}}
        self.slot_pressure = defaultdict(lambda: defaultdict(int))  # {day: {slot: pressure_count}}

    def generate_schedule(self) -> List[Dict]:
        """Ana program oluşturma fonksiyonu"""
        print("\n" + "=" * 80)
        print("🚀 ENHANCED STRICT SCHEDULER - Backtracking + Akıllı Önceliklendirme")
        print("=" * 80)

        # Başlangıç
        self.schedule_entries = []
        self.teacher_usage.clear()
        self.class_usage.clear()
        self.slot_pressure.clear()

        # Verileri al
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()
        assignments = self.db_manager.get_schedule_by_school_type()

        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        print(f"\n📊 Konfigürasyon:")
        print(f"   • Okul Türü: {school_type}")
        print(f"   • Günlük Saat: {time_slots_count}")
        print(f"   • Sınıf: {len(classes)} | Öğretmen: {len(teachers)} | Ders: {len(lessons)}")
        print(f"   • Atamalar: {len(assignments)}")

        # Atama haritası oluştur
        assignment_map = {}
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id)
            assignment_map[key] = assignment.teacher_id

        # 1. Aşama: Tüm dersleri yerleştirmeyi dene
        total_required = 0
        total_scheduled = 0
        failed_lessons = []

        # Sınıfları önceliklendir (seviye bazlı)
        classes_sorted = sorted(classes, key=lambda c: c.grade, reverse=True)

        for class_idx, class_obj in enumerate(classes_sorted, 1):
            print(f"\n{'='*80}")
            print(f"📚 [{class_idx}/{len(classes)}] {class_obj.name} (Seviye {class_obj.grade})")
            print(f"{'='*80}")

            class_lessons = self._get_class_lessons(class_obj, lessons, assignment_map, teachers)

            if not class_lessons:
                print(f"⚠️  Ders ataması bulunamadı")
                continue

            # Dersleri önceliklendir (saate göre, sonra branşa göre)
            class_lessons.sort(key=lambda x: (-x["weekly_hours"], x["lesson_name"]))

            for lesson_info in class_lessons:
                total_required += lesson_info["weekly_hours"]

                # İlk deneme: Normal yerleştirme
                scheduled = self._schedule_lesson_enhanced(class_obj, lesson_info, time_slots_count, classrooms)

                total_scheduled += scheduled

                # Başarısız ise backtracking dene
                if scheduled < lesson_info["weekly_hours"]:
                    print(f"   🔄 Backtracking deneniyor...")
                    additional = self._schedule_with_backtracking(
                        class_obj,
                        lesson_info,
                        lesson_info["weekly_hours"] - scheduled,
                        time_slots_count,
                        classrooms,
                    )
                    total_scheduled += additional
                    scheduled += additional

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

        # Sonuç raporu
        print(f"\n{'='*80}")
        print(f"🎯 SONUÇ RAPORU")
        print(f"{'='*80}")
        print(f"📊 Toplam Gereksinim: {total_required} saat")
        print(f"✅ Yerleştirilen: {total_scheduled} saat")
        coverage = (total_scheduled / total_required * 100) if total_required > 0 else 0
        print(f"📈 Kapsama Oranı: {coverage:.1f}%")

        if failed_lessons:
            print(f"\n⚠️  {len(failed_lessons)} ders tam yerleştirilemedi:")
            for fail in failed_lessons[:5]:
                print(f"   • {fail['class']} - {fail['lesson']}: {fail['scheduled']}/{fail['required']} saat")
        else:
            print(f"\n🎉 TÜM DERSLER BAŞARIYLA YERLEŞTİRİLDİ!")

        # Veritabanına kaydet
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
        """Sınıfın derslerini al"""
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

    def _schedule_lesson_enhanced(self, class_obj, lesson_info: Dict, time_slots_count: int, classrooms: List) -> int:
        """
        Geliştirilmiş ders yerleştirme - Optimal dağılım stratejisi:
        6 saat: 2+2+2 (3 gün), 5 saat: 2+2+1, 4 saat: 2+2, 3 saat: 2+1
        """
        lesson_name = lesson_info["lesson_name"]
        teacher_id = lesson_info["teacher_id"]
        teacher_name = lesson_info["teacher_name"]
        weekly_hours = lesson_info["weekly_hours"]
        lesson_id = lesson_info["lesson_id"]
        class_id = class_obj.class_id

        print(f"\n   📝 {lesson_name} ({weekly_hours} saat) - {teacher_name}")

        scheduled_hours = 0
        used_days = set()  # Blok yerleştirmede kullanılan günler

        # Haftalık saat sayısına göre optimal dağılım
        if weekly_hours >= 6:
            num_double_blocks = weekly_hours // 2
            scheduled_hours, used_days = self._try_smart_blocks_strict(
                class_id, teacher_id, lesson_id, num_double_blocks, time_slots_count, classrooms, 2
            )
            if scheduled_hours < weekly_hours:
                remaining = weekly_hours - scheduled_hours
                scheduled_hours += self._try_smart_singles(
                    class_id,
                    teacher_id,
                    lesson_id,
                    remaining,
                    time_slots_count,
                    classrooms,
                    exclude_days=used_days,
                )
        elif weekly_hours == 5:
            scheduled_hours, used_days = self._try_smart_blocks_strict(
                class_id, teacher_id, lesson_id, 2, time_slots_count, classrooms, 2
            )
            if scheduled_hours == 4:
                scheduled_hours += self._try_smart_singles(
                    class_id,
                    teacher_id,
                    lesson_id,
                    1,
                    time_slots_count,
                    classrooms,
                    exclude_days=used_days,
                )
            else:
                remaining = weekly_hours - scheduled_hours
                scheduled_hours += self._try_any_slot(
                    class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
                )
        elif weekly_hours == 4:
            scheduled_hours, used_days = self._try_smart_blocks_strict(
                class_id, teacher_id, lesson_id, 2, time_slots_count, classrooms, 2
            )
            if scheduled_hours < weekly_hours:
                remaining = weekly_hours - scheduled_hours
                scheduled_hours += self._try_any_slot(
                    class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
                )
        elif weekly_hours == 3:
            scheduled_hours, used_days = self._try_smart_blocks_strict(
                class_id, teacher_id, lesson_id, 1, time_slots_count, classrooms, 2
            )
            if scheduled_hours == 2:
                scheduled_hours += self._try_smart_singles(
                    class_id,
                    teacher_id,
                    lesson_id,
                    1,
                    time_slots_count,
                    classrooms,
                    exclude_days=used_days,
                )
            else:
                remaining = weekly_hours - scheduled_hours
                scheduled_hours += self._try_any_slot(
                    class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
                )
        elif weekly_hours == 2:
            # 2 saat: MUTLAKA tek blok (ardışık 2 saat) olarak yerleştir
            # Fallback YOK - ya blok olarak yerleşir ya hiç yerleşmez
            scheduled_hours, used_days = self._try_smart_blocks_strict(
                class_id, teacher_id, lesson_id, 1, time_slots_count, classrooms, 2
            )
        elif weekly_hours == 1:
            scheduled_hours += self._try_smart_singles(class_id, teacher_id, lesson_id, 1, time_slots_count, classrooms)

        # Son çare
        # ÖNEMLİ: 2 saatlik dersler için fallback yok (yukarıda zaten blok olarak yerleştirildi)
        if scheduled_hours < weekly_hours and weekly_hours != 2:
            remaining = weekly_hours - scheduled_hours
            scheduled_hours += self._try_any_slot(
                class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
            )

        rate = (scheduled_hours / weekly_hours * 100) if weekly_hours > 0 else 0
        status = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
        print(f"      {status} {scheduled_hours}/{weekly_hours} saat ({rate:.0f}%)")

        return scheduled_hours

    def _schedule_with_backtracking(
        self,
        class_obj,
        lesson_info: Dict,
        hours_needed: int,
        time_slots_count: int,
        classrooms: List,
    ) -> int:
        """Backtracking ile yerleştirme"""
        class_id = class_obj.class_id
        teacher_id = lesson_info["teacher_id"]
        lesson_id = lesson_info["lesson_id"]

        scheduled = 0
        max_attempts = 20

        for attempt in range(max_attempts):
            if scheduled >= hours_needed:
                break

            # Rastgele bir gün ve slot seç
            day = random.randint(0, 4)
            slot = random.randint(0, time_slots_count - 1)

            if self._can_place_lesson(class_id, teacher_id, day, [slot], lesson_id):
                classroom = self._find_available_classroom(classrooms, day, slot)
                classroom_id = classroom.classroom_id if classroom else 1

                self._add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                scheduled += 1

        return scheduled

    def _try_smart_blocks_strict(
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

        # Slot yoğunluğuna göre sırala (az yoğun olanlar önce)
        slot_scores = []
        for day in range(5):
            for start_slot in range(time_slots_count - block_size + 1):
                slots = list(range(start_slot, start_slot + block_size))
                pressure = sum(self.slot_pressure[day][s] for s in slots)
                slot_scores.append((pressure, day, slots))

        slot_scores.sort()  # Az yoğun olanlar önce

        for pressure, day, slots in slot_scores:
            if blocks_placed >= num_blocks:
                break

            if day in used_days:
                continue

            if self._can_place_lesson(class_id, teacher_id, day, slots, lesson_id):
                classroom = self._find_available_classroom(classrooms, day, slots[0])
                classroom_id = classroom.classroom_id if classroom else 1

                for slot in slots:
                    self._add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                    scheduled += 1
                    self.slot_pressure[day][slot] += 1

                used_days.add(day)
                blocks_placed += 1

        return scheduled, used_days

    def _try_smart_blocks(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        total_hours: int,
        time_slots_count: int,
        classrooms: List,
        block_size: int = 2,
    ) -> int:
        """Akıllı blok yerleştirme - az yoğun slotları tercih et (eski yöntem - yedek)"""
        scheduled = 0
        num_blocks = total_hours // block_size

        # Slot yoğunluğuna göre sırala (az yoğun olanlar önce)
        slot_scores = []
        for day in range(5):
            for start_slot in range(time_slots_count - block_size + 1):
                slots = list(range(start_slot, start_slot + block_size))
                pressure = sum(self.slot_pressure[day][s] for s in slots)
                slot_scores.append((pressure, day, slots))

        slot_scores.sort()  # Az yoğun olanlar önce

        used_days = set()
        for pressure, day, slots in slot_scores:
            if scheduled >= num_blocks * block_size:
                break

            if day in used_days:
                continue

            if self._can_place_lesson(class_id, teacher_id, day, slots, lesson_id):
                classroom = self._find_available_classroom(classrooms, day, slots[0])
                classroom_id = classroom.classroom_id if classroom else 1

                for slot in slots:
                    self._add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                    scheduled += 1
                    # Yoğunluğu güncelle
                    self.slot_pressure[day][slot] += 1

                used_days.add(day)

        return scheduled

    def _try_smart_singles(
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
        Akıllı tekli slot yerleştirme
        exclude_days: Bu günlere yerleştirme yapma (aynı güne 2+1 olmasın diye)
        """
        scheduled = 0
        if exclude_days is None:
            exclude_days = set()

        # Tüm slotları yoğunluğa göre sırala
        slot_scores = []
        for day in range(5):
            # ÖNEMLI: Aynı güne yerleştirme yapma
            if day in exclude_days:
                continue

            for slot in range(time_slots_count):
                pressure = self.slot_pressure[day][slot]
                slot_scores.append((pressure, day, slot))

        slot_scores.sort()  # Az yoğun olanlar önce

        for pressure, day, slot in slot_scores:
            if scheduled >= hours_needed:
                break

            if self._can_place_lesson(class_id, teacher_id, day, [slot], lesson_id):
                classroom = self._find_available_classroom(classrooms, day, slot)
                classroom_id = classroom.classroom_id if classroom else 1

                self._add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                scheduled += 1
                self.slot_pressure[day][slot] += 1

        return scheduled

    def _try_any_slot(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        hours_needed: int,
        time_slots_count: int,
        classrooms: List,
    ) -> int:
        """Son çare: herhangi bir boş slot"""
        scheduled = 0

        for day in range(5):
            for slot in range(time_slots_count):
                if scheduled >= hours_needed:
                    break

                if self._can_place_lesson(class_id, teacher_id, day, [slot], lesson_id):
                    classroom = self._find_available_classroom(classrooms, day, slot)
                    classroom_id = classroom.classroom_id if classroom else 1

                    self._add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                    scheduled += 1

        return scheduled

    def _can_place_lesson(
        self, class_id: int, teacher_id: int, day: int, slots: List[int], lesson_id: int = None
    ) -> bool:
        """Ders yerleştirilebilir mi kontrol et"""
        # ÖNEMLİ: Aynı güne aynı dersi BÖLÜNMÜŞ şekilde yerleştirme
        # Eğer bu günde bu sınıfta bu ders zaten varsa, ardışık olmalı
        if lesson_id is not None:
            # Bu günde bu dersin mevcut slotlarını bul
            existing_slots = []
            for entry in self.schedule_entries:
                if entry["class_id"] == class_id and entry["lesson_id"] == lesson_id and entry["day"] == day:
                    existing_slots.append(entry["time_slot"])

            # Eğer bu günde bu ders zaten varsa
            if existing_slots:
                for new_slot in slots:
                    # Yeni slot, mevcut slotlardan en az biriyle ardışık olmalı
                    min_distance = min(abs(new_slot - existing) for existing in existing_slots)
                    if min_distance > 1:
                        # Hiçbir mevcut slotla ardışık değil -> ENGELLE
                        return False

        for slot in slots:
            # Öğretmen uygunluğu (ZORUNLU)
            if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                return False

            # Sınıf çakışması
            if slot in self.class_usage[class_id][day]:
                return False

            # Öğretmen çakışması
            if slot in self.teacher_usage[teacher_id][day]:
                return False

            # ÖNEMLİ: 3 saat üst üste aynı ders kontrolü
            if lesson_id is not None:
                if self._would_create_three_consecutive_lessons(class_id, lesson_id, day, slot):
                    return False

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
            for s, l in class_schedule_today:
                if s == check_slot and l == lesson_id:
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
            for s, l in class_schedule_today:
                if s == check_slot and l == lesson_id:
                    consecutive_after += 1
                    found = True
                    break
            if not found:
                break  # Ardışıklık bozuldu

        # Toplam ardışık ders sayısı (önceki + bu slot + sonraki)
        total_consecutive = consecutive_before + 1 + consecutive_after

        # 3 veya daha fazla ardışık ders olacaksa engelle
        return total_consecutive >= 3

    def _add_schedule_entry(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        classroom_id: int,
        day: int,
        time_slot: int,
    ):
        """Program girişi ekle ve izleme tablolarını güncelle"""
        entry = {
            "class_id": class_id,
            "teacher_id": teacher_id,
            "lesson_id": lesson_id,
            "classroom_id": classroom_id,
            "day": day,
            "time_slot": time_slot,
        }

        self.schedule_entries.append(entry)
        self.class_usage[class_id][day].add(time_slot)
        self.teacher_usage[teacher_id][day].add(time_slot)

    def _find_available_classroom(self, classrooms: List, day: int, slot: int):
        """Uygun sınıf bul"""
        for classroom in classrooms:
            # Basit kontrol - geliştirilmesi gerekebilir
            return classroom
        return None
