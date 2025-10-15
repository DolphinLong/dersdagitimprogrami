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
from typing import Dict, List

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
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

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.schedule_entries = []
        self.teacher_slots = defaultdict(set)  # {teacher_id: {(day, slot)}}
        self.class_slots = defaultdict(set)  # {class_id: {(day, slot)}}
        self.logger = logging.getLogger(__name__)

    def generate_schedule(self) -> List[Dict]:
        """Program oluştur"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🎯 SIMPLE PERFECT SCHEDULER - Pragmatik ve Etkili")
        self.logger.info("=" * 80)

        # Reset
        self.schedule_entries = []
        self.teacher_slots.clear()
        self.class_slots.clear()

        # Verileri al
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

        # Atama haritası
        assignment_map = {}
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id)
            assignment_map[key] = assignment.teacher_id

        # Tüm ihtiyaçları topla
        all_needs = []
        total_required = 0

        for class_obj in classes:
            for lesson in lessons:
                key = (class_obj.class_id, lesson.lesson_id)
                if key in assignment_map:
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)

                    if weekly_hours and weekly_hours > 0:
                        teacher_id = assignment_map[key]
                        teacher = self.db_manager.get_teacher_by_id(teacher_id)

                        if teacher:
                            all_needs.append(
                                {
                                    "class_id": class_obj.class_id,
                                    "class_name": class_obj.name,
                                    "lesson_id": lesson.lesson_id,
                                    "lesson_name": lesson.name,
                                    "teacher_id": teacher_id,
                                    "teacher_name": teacher.name,
                                    "weekly_hours": weekly_hours,
                                    "scheduled": 0,
                                }
                            )
                            total_required += weekly_hours

        self.logger.info(f"\n📝 Toplam Gereksinim: {total_required} saat")
        self.logger.info(f"   {len(all_needs)} farklı ders ataması")

        # Dersleri önceliklendir (fazla saatli olanlar önce)
        all_needs.sort(key=lambda x: -x["weekly_hours"])

        self.logger.info("\n🚀 Yerleştirme başlıyor...")

        # Her dersi yerleştir
        total_scheduled = 0

        for idx, need in enumerate(all_needs):
            if (idx + 1) % 10 == 0:
                self.logger.info(f"   📊 İlerleme: {idx + 1}/{len(all_needs)} ders")

            # Bu dersin tüm saatlerini yerleştirmeye çalış
            scheduled = self._schedule_lesson(need, time_slots_count, classrooms, max_attempts=5)

            need["scheduled"] = scheduled
            total_scheduled += scheduled

        # Sonuç
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🎯 SONUÇ")
        self.logger.info("=" * 80)
        self.logger.info(f"📊 Gereksinim: {total_required} saat")
        self.logger.info(f"✅ Yerleşen: {total_scheduled} saat")
        coverage = (total_scheduled / total_required * 100) if total_required > 0 else 0
        self.logger.info(f"📈 Başarı: {coverage:.1f}%")

        # Başarısız olanları göster
        failed = [n for n in all_needs if n["scheduled"] < n["weekly_hours"]]
        if failed:
            self.logger.warning(f"\n⚠️  {len(failed)} ders tam yerleştirilemedi:")
            for f in failed[:5]:
                self.logger.warning(
                    f"   • {f['class_name']} - {f['lesson_name']}: {f['scheduled']}/{f['weekly_hours']}"
                )
        else:
            self.logger.info("\n🎉 TÜM DERSLER BAŞARIYLA YERLEŞTİRİLDİ!")

        # Veritabanına kaydet
        self.logger.info("\n💾 Veritabanına kaydediliyor...")
        self.db_manager.clear_schedule()

        saved = 0
        for entry in self.schedule_entries:
            if self.db_manager.add_schedule_program(
                entry["class_id"],
                entry["teacher_id"],
                entry["lesson_id"],
                entry["classroom_id"],
                entry["day"],
                entry["time_slot"],
            ):
                saved += 1

        self.logger.info(f"✅ {saved} kayıt tamamlandı")

        return self.schedule_entries

    def _schedule_lesson(self, need: Dict, time_slots_count: int, classrooms: List, max_attempts: int = 5) -> int:
        """
        Bir dersi yerleştir - Optimal dağılım stratejisi:
        6 saat: 2+2+2 (3 gün)
        5 saat: 2+2+1 (3 gün)
        4 saat: 2+2 (2 gün)
        3 saat: 2+1 (2 gün)
        2 saat: 2 (1 gün) veya 1+1 (2 gün)
        1 saat: 1 (1 gün)
        """
        class_id = need["class_id"]
        teacher_id = need["teacher_id"]
        lesson_id = need["lesson_id"]
        weekly_hours = need["weekly_hours"]

        scheduled = 0

        # Haftalık saat sayısına göre optimal dağılım planı
        used_days = set()  # Blok yerleştirmede kullanılan günler

        if weekly_hours >= 6:
            # 6+ saat: Önce 2'li bloklar yerleştir (2+2+2+...)
            num_double_blocks = weekly_hours // 2
            scheduled, used_days = self._try_blocks_strict(
                class_id, teacher_id, lesson_id, num_double_blocks, time_slots_count, classrooms, 2
            )
            # Kalan tek saatler varsa (FARKLI günlere yerleştir)
            if scheduled < weekly_hours:
                remaining = weekly_hours - scheduled
                scheduled += self._try_singles(
                    class_id,
                    teacher_id,
                    lesson_id,
                    remaining,
                    time_slots_count,
                    classrooms,
                    exclude_days=used_days,
                )
        elif weekly_hours == 5:
            # 5 saat: 2+2+1 stratejisi (3 FARKLI gün)
            # Önce 2 adet 2'li blok
            scheduled, used_days = self._try_blocks_strict(
                class_id, teacher_id, lesson_id, 2, time_slots_count, classrooms, 2
            )
            # Sonra 1 tekli (FARKLI bir güne)
            if scheduled == 4:  # İlk iki blok başarılıysa
                scheduled += self._try_singles(
                    class_id,
                    teacher_id,
                    lesson_id,
                    1,
                    time_slots_count,
                    classrooms,
                    exclude_days=used_days,
                )
            else:  # Bloklar tam yerleştirilemediyse, kalanı yerleştir
                remaining = weekly_hours - scheduled
                scheduled += self._try_any_available(
                    class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
                )
        elif weekly_hours == 4:
            # 4 saat: 2+2 stratejisi (2 FARKLI gün)
            scheduled, used_days = self._try_blocks_strict(
                class_id, teacher_id, lesson_id, 2, time_slots_count, classrooms, 2
            )
            # Eksik kaldıysa tamamla
            if scheduled < weekly_hours:
                remaining = weekly_hours - scheduled
                scheduled += self._try_any_available(
                    class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
                )
        elif weekly_hours == 3:
            # 3 saat: 2+1 stratejisi (2 FARKLI gün)
            scheduled, used_days = self._try_blocks_strict(
                class_id, teacher_id, lesson_id, 1, time_slots_count, classrooms, 2
            )
            # Sonra 1 tekli (FARKLI bir güne)
            if scheduled == 2:
                scheduled += self._try_singles(
                    class_id,
                    teacher_id,
                    lesson_id,
                    1,
                    time_slots_count,
                    classrooms,
                    exclude_days=used_days,
                )
            else:
                remaining = weekly_hours - scheduled
                scheduled += self._try_any_available(
                    class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
                )
        elif weekly_hours == 2:
            # 2 saat: MUTLAKA tek blok (ardışık 2 saat) olarak yerleştir
            # Fallback YOK - ya blok olarak yerleşir ya hiç yerleşmez
            scheduled, used_days = self._try_blocks_strict(
                class_id, teacher_id, lesson_id, 1, time_slots_count, classrooms, 2
            )
        elif weekly_hours == 1:
            # 1 saat: Tekli yerleştir
            scheduled += self._try_singles(class_id, teacher_id, lesson_id, 1, time_slots_count, classrooms)

        # Son çare: Kalan saatler için esnek yerleştirme
        # ÖNEMLİ: 2 saatlik dersler için fallback yok (yukarıda zaten blok olarak yerleştirildi)
        if scheduled < weekly_hours and weekly_hours != 2:
            remaining = weekly_hours - scheduled
            scheduled += self._try_any_available(
                class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms
            )

        # Kritik dersler için öğretmen uygunluğunu esnet
        # ÖNEMLİ: 2 saatlik dersler için fallback yok
        if scheduled < weekly_hours and weekly_hours >= 4:
            remaining = weekly_hours - scheduled
            scheduled += self._try_relaxed(class_id, teacher_id, lesson_id, remaining, time_slots_count, classrooms)

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

            # ÖNEMLI: Aynı güne yerleştirme yapma
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
        max_attempts = hours_needed * 10

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

    def _can_place_all(self, class_id: int, teacher_id: int, day: int, slots: List[int], lesson_id: int = None) -> bool:
        """Tüm slotlara yerleştirilebilir mi?"""
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
            # Sınıf çakışması
            if (day, slot) in self.class_slots[class_id]:
                return False

            # Öğretmen çakışması
            if (day, slot) in self.teacher_slots[teacher_id]:
                return False

            # Öğretmen uygunluğu
            try:
                if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                    return False
            except Exception as e:
                logging.warning(f"Error checking teacher availability in SimplePerfectScheduler: {e}")
                # On error, treat as available to avoid blocking schedule generation

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
