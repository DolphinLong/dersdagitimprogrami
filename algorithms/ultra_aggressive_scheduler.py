# -*- coding: utf-8 -*-
"""
Ultra Aggressive Scheduler - %100 Doluluk Hedefli
Boş hücre KALMAYANA kadar sürekli iyileştirme yapar!
"""

import io
import logging
import random
import sys
import time
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Tuple

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class UltraAggressiveScheduler:
    """
    %100 Doluluk Hedefli Ultra Agresif Scheduler

    Strateji:
    1. İlk tur: Simple Perfect Scheduler ile başla
    2. Boş hücre analizi: Hangi sınıfta kaç saat eksik?
    3. İteratif iyileştirme: Boş hücreleri doldurmaya çalış
    4. Relaxation: Gerekirse kuralları esnet (kontrollü)
    5. Sürekli deneme: Tablo dolana kadar dur!
    """

    SCHOOL_TIME_SLOTS = {
        "İlkokul": 7,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(self, db_manager, progress_callback: Optional[Callable] = None):
        self.db_manager = db_manager
        self.progress_callback = progress_callback  # UI için callback
        self.schedule_entries = []
        self.iteration = 0
        self.max_iterations = 5000  # Maksimum deneme sayısı
        self.logger = logging.getLogger(__name__)

    def generate_schedule(self) -> List[Dict]:
        """Ana program oluşturma - %100 doluluk hedefli"""
        print("\n" + "=" * 80)
        print("🚀 ULTRA AGGRESSIVE SCHEDULER - %100 DOLULUK HEDEFLİ")
        print("=" * 80)
        print("💪 Boş hücre KALMAYANA kadar sürekli iyileştirme yapılacak!")
        print("")

        # Başlangıç zamanı
        start_time = time.time()

        # Konfigürasyon
        config = self._prepare_configuration()
        if not config:
            return []

        # 1. AŞAMA: Simple Perfect Scheduler ile başla
        print("\n📋 AŞAMA 1: İlk çözüm oluşturuluyor...")
        self._report_progress("İlk çözüm oluşturuluyor...", 0)

        initial_schedule = self._generate_initial_solution(config)
        self.schedule_entries = initial_schedule

        # 2. AŞAMA: Kapsama analizi
        print("\n📊 AŞAMA 2: Kapsama analizi yapılıyor...")
        coverage_report = self._analyze_coverage(config)

        initial_coverage = coverage_report["overall_percentage"]
        print(f"\n   ✅ İlk kapsama: {initial_coverage:.1f}%")
        print(
            f"   📊 Yerleşen: {coverage_report['total_scheduled']} / {coverage_report['total_required']} saat"
        )

        # 3. AŞAMA: İteratif iyileştirme - %100 dolana kadar!
        if initial_coverage < 100:
            print("\n💪 AŞAMA 3: İTERATİF İYİLEŞTİRME BAŞLIYOR...")
            print(f"   🎯 Hedef: %100 doluluk")
            print(f"   ⚡ Maksimum deneme: {self.max_iterations}")
            print("")

            self.schedule_entries = self._iterative_improvement(
                self.schedule_entries, coverage_report, config
            )

        # 4. AŞAMA: Final analiz
        print("\n📊 AŞAMA 4: Final kapsama analizi...")
        final_coverage = self._analyze_coverage(config)

        elapsed_time = time.time() - start_time

        # Sonuç raporu
        self._print_final_report(initial_coverage, final_coverage, elapsed_time)

        # 5. AŞAMA: Final Validation - Çakışma Kontrolü
        print("\n🔍 AŞAMA 5: Final çakışma kontrolü...")
        conflicts = self._validate_no_conflicts()

        if conflicts:
            print(f"   ⚠️  {len(conflicts)} çakışma tespit edildi!")
            for conflict in conflicts[:5]:  # İlk 5'ini göster
                print(f"      • {conflict}")

            # Çakışmaları temizle
            print("   🔧 Çakışmalar temizleniyor...")
            self.schedule_entries = self._remove_conflicts(self.schedule_entries)

            # Tekrar kontrol et
            conflicts_after = self._validate_no_conflicts()
            if conflicts_after:
                print(f"   ⚠️  Hala {len(conflicts_after)} çakışma var (temizlenemedi)")
            else:
                print("   ✅ Tüm çakışmalar temizlendi!")
        else:
            print("   ✅ Çakışma yok!")

        # 6. AŞAMA: Veritabanına kaydet
        self._save_to_database()

        self._report_progress("Tamamlandı!", 100)

        return self.schedule_entries

    def _prepare_configuration(self) -> Optional[Dict]:
        """Konfigürasyon hazırla"""
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()
        assignments = self.db_manager.get_schedule_by_school_type()

        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        print(f"📊 Konfigürasyon:")
        print(f"   • Okul: {school_type} ({time_slots_count} saat/gün)")
        print(f"   • Sınıf: {len(classes)} | Öğretmen: {len(teachers)}")
        print(f"   • Ders: {len(lessons)} | Atama: {len(assignments)}")

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
        }

    def _generate_initial_solution(self, config: Dict) -> List[Dict]:
        """İlk çözümü oluştur - Simple Perfect Scheduler kullan"""
        try:
            from algorithms.simple_perfect_scheduler import SimplePerfectScheduler

            scheduler = SimplePerfectScheduler(self.db_manager)
            return scheduler.generate_schedule()
        except Exception as e:
            logging.warning(f"SimplePerfectScheduler unavailable or failed: {e}")
            print("⚠️  Simple Perfect Scheduler bulunamadı, boş döndürülüyor")
            return []

    def _analyze_coverage(self, config: Dict) -> Dict:
        """
        Detaylı kapsama analizi

        ÖNEMLI:
        - GERÇEK DOLULUK = Yerleşen / TOPLAM SLOT SAYISI (5 gün × N saat)
        - DERS GEREKSİNİMİ = Haftalık ders saati (MEB müfredatı)

        Kullanıcı GERÇEK DOLULUK istiyor (UI'de boş hücre görünmemeli!)
        """
        # GERÇEK DOLULUK hesabı (UI bazlı)
        total_slots = len(config["classes"]) * 5 * config["time_slots_count"]
        total_scheduled = len(self.schedule_entries)

        # Ders gereksinim hesabı (MEB müfredatı - backward compatibility)
        total_required = 0

        # Sınıf bazlı analiz
        class_coverage = {}

        for class_obj in config["classes"]:
            # Bu sınıfın TOPLAM SLOT SAYISI (5 gün × N saat)
            class_total_slots = 5 * config["time_slots_count"]

            # Bu sınıfın ders gereksinimleri (MEB müfredatı)
            class_required = 0
            for lesson in config["lessons"]:
                key = (class_obj.class_id, lesson.lesson_id)
                if key in config["assignment_map"]:
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                        lesson.lesson_id, class_obj.grade
                    )
                    if weekly_hours:
                        class_required += weekly_hours
                        total_required += weekly_hours

            # Bu sınıfa yerleşen saatler
            class_scheduled = 0
            for entry in self.schedule_entries:
                if entry["class_id"] == class_obj.class_id:
                    class_scheduled += 1

            # Boş slotları bul
            occupied_slots = set()
            for entry in self.schedule_entries:
                if entry["class_id"] == class_obj.class_id:
                    occupied_slots.add((entry["day"], entry["time_slot"]))

            # Tüm olası slotlar
            empty_slots = []
            for day in range(5):
                for slot in range(config["time_slots_count"]):
                    if (day, slot) not in occupied_slots:
                        empty_slots.append((day, slot))

            # GERÇEK doluluk yüzdesi (UI bazlı)
            class_percentage = (
                (class_scheduled / class_total_slots * 100) if class_total_slots > 0 else 100
            )

            class_coverage[class_obj.class_id] = {
                "class_name": class_obj.name,
                "total_slots": class_total_slots,  # GERÇEK slot sayısı
                "required": class_required,  # MEB müfredatı (backward compatibility)
                "scheduled": class_scheduled,
                "empty_slots": empty_slots,
                "percentage": class_percentage,  # GERÇEK doluluk!
            }

        # GERÇEK genel doluluk (UI bazlı)
        overall_percentage = (total_scheduled / total_slots * 100) if total_slots > 0 else 100

        return {
            "total_slots": total_slots,  # GERÇEK slot sayısı
            "total_required": total_required,  # MEB müfredatı (backward compatibility)
            "total_scheduled": total_scheduled,
            "overall_percentage": overall_percentage,  # GERÇEK doluluk!
            "class_coverage": class_coverage,
        }

    def _iterative_improvement(
        self, schedule: List[Dict], coverage: Dict, config: Dict
    ) -> List[Dict]:
        """İteratif iyileştirme - boş hücreleri doldur"""

        current_schedule = schedule[:]
        best_schedule = schedule[:]
        best_coverage = coverage["overall_percentage"]

        self.iteration = 0
        no_improvement_count = 0
        max_no_improvement = 50  # 50 denemede iyileşme yoksa dur

        while self.iteration < self.max_iterations and best_coverage < 100:
            self.iteration += 1

            # Progress raporu
            if self.iteration % 10 == 0:
                print(f"   🔄 İterasyon {self.iteration}: Kapsama %{best_coverage:.1f}")
                progress = min(best_coverage, 99)
                self._report_progress(
                    f"İterasyon {self.iteration} - %{best_coverage:.1f} dolu", progress
                )

            # Boş hücreleri doldurmaya çalış
            new_schedule = self._fill_empty_cells(current_schedule[:], coverage, config)

            # Yeni kapsama hesapla
            self.schedule_entries = new_schedule
            new_coverage_report = self._analyze_coverage(config)
            new_coverage = new_coverage_report["overall_percentage"]

            # İyileşme var mı?
            if new_coverage > best_coverage:
                best_schedule = new_schedule[:]
                best_coverage = new_coverage
                current_schedule = new_schedule[:]
                coverage = new_coverage_report
                no_improvement_count = 0

                print(f"   ✅ İyileşme! Yeni kapsama: %{best_coverage:.1f}")

                if best_coverage >= 100:
                    print(f"\n   🎉 %100 DOLULUK SAĞLANDI!")
                    break
            else:
                no_improvement_count += 1

                # Küçük rastgele değişiklik yap (local search)
                current_schedule = self._random_perturbation(best_schedule[:], config)

            # Çok uzun süredir iyileşme yoksa stratejiler değiştir
            if no_improvement_count >= max_no_improvement:
                print(f"\n   ⚠️  {max_no_improvement} iterasyonda iyileşme yok")
                print(f"   💪 Relaxation stratejileri devreye giriyor...")

                # Daha agresif stratejiler dene
                current_schedule = self._aggressive_filling(best_schedule[:], coverage, config)
                no_improvement_count = 0

        # Final mesaj
        if best_coverage >= 100:
            print(f"\n   🎉 BAŞARILI! %100 doluluk sağlandı ({self.iteration} iterasyon)")
        elif self.iteration >= self.max_iterations:
            print(f"\n   ⚠️  Maksimum iterasyon limitine ulaşıldı")
            print(f"   📊 Elde edilen kapsama: %{best_coverage:.1f}")

        return best_schedule

    def _fill_empty_cells(self, schedule: List[Dict], coverage: Dict, config: Dict) -> List[Dict]:
        """
        Boş hücreleri doldurmaya çalış

        GÜÇLENDIRILMIŞ: Çakışma kontrolü ile
        """

        # Rastgele bir sınıf seç (kapsama düşük olanları tercih et)
        class_priorities = sorted(
            coverage["class_coverage"].items(), key=lambda x: x[1]["percentage"]
        )

        for class_id, class_info in class_priorities:
            if class_info["percentage"] >= 100:
                continue

            empty_slots = class_info["empty_slots"]
            if not empty_slots:
                continue

            # Rastgele bir boş slot seç
            day, slot = random.choice(empty_slots)

            # ÇAKIŞMA KONTROLÜ: Bu slot gerçekten boş mu?
            is_occupied = False
            for entry in schedule:
                if (
                    entry["class_id"] == class_id
                    and entry["day"] == day
                    and entry["time_slot"] == slot
                ):
                    is_occupied = True
                    break

            if is_occupied:
                # Bu slot zaten dolu, atlayalım
                continue

            # Bu slota ders yerleştirmeye çalış
            success = self._try_place_lesson_in_slot(schedule, class_id, day, slot, config)

            if success:
                break

        return schedule

    def _try_place_lesson_in_slot(
        self, schedule: List[Dict], class_id: int, day: int, slot: int, config: Dict
    ) -> bool:
        """Belirli bir slota ders yerleştirmeye çalış"""

        # Bu sınıfın henüz yerleşmemiş dersleri var mı?
        class_obj = next((c for c in config["classes"] if c.class_id == class_id), None)
        if not class_obj:
            return False

        # Tüm dersleri dene (rastgele sırada)
        lessons_to_try = list(config["lessons"])
        random.shuffle(lessons_to_try)

        for lesson in lessons_to_try:
            key = (class_id, lesson.lesson_id)
            if key not in config["assignment_map"]:
                continue

            teacher_id = config["assignment_map"][key]

            # Bu dersten ne kadar yerleşti?
            weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                lesson.lesson_id, class_obj.grade
            )
            if not weekly_hours:
                continue

            scheduled_hours = sum(
                1
                for e in schedule
                if e["class_id"] == class_id and e["lesson_id"] == lesson.lesson_id
            )

            if scheduled_hours >= weekly_hours:
                continue  # Bu ders zaten tam

            # Bu slota yerleştir
            if self._can_place_at_slot(
                schedule, class_id, teacher_id, day, slot, lesson_name=lesson.name
            ):
                classroom = config["classrooms"][0] if config["classrooms"] else None
                classroom_id = classroom.classroom_id if classroom else 1

                schedule.append(
                    {
                        "class_id": class_id,
                        "teacher_id": teacher_id,
                        "lesson_id": lesson.lesson_id,
                        "classroom_id": classroom_id,
                        "day": day,
                        "time_slot": slot,
                    }
                )
                self.logger.info(
                    f"[BAŞARILI YERLEŞTİRME] Slot: (Sınıf: {class_id}, Gün: {day}, Saat: {slot}) | "
                    f"Ders: {lesson.name} yerleştirildi."
                )
                return True

        self.logger.warning(
            f"[BOŞLUK DOLDURULAMADI] Slot: (Sınıf: {class_id}, Gün: {day}, Saat: {slot}) | "
            f"Neden: Bu boşluğa yerleştirilebilecek uygun bir ders bulunamadı."
        )
        return False

    def _can_place_at_slot_detailed(
        self,
        schedule: List[Dict],
        class_id: int,
        teacher_id: int,
        day: int,
        slot: int,
        lesson_name: str = "",
    ) -> Tuple[bool, str]:
        """
        Bu slota yerleştirme yapılabilir mi?

        GÜÇLENDIRILMIŞ ÇAKIŞMA KONTROLÜ VE DETAYLI LOGLAMA:
        1. Sınıf çakışması (ZORUNLU)
        2. Öğretmen çakışması (ZORUNLU)
        3. Öğretmen uygunluğu (İlk 100 iterasyon ZORUNLU)
        """

        # 1. SINIF ÇAKIŞMASI KONTROLÜ (ZORUNLU - ASLA ESNETILMEZ!)
        for entry in schedule:
            if entry["class_id"] == class_id and entry["day"] == day and entry["time_slot"] == slot:
                self.logger.debug(
                    f"[DENEME BAŞARISIZ] Slot: (Sınıf: {class_id}, Gün: {day}, Saat: {slot}) | "
                    f"Neden: SINIF ÇAKIŞMASI. Bu slot zaten dolu."
                )
                return False, "SINIF_CAKISMASI"

        # 2. ÖĞRETMEN ÇAKIŞMASI KONTROLÜ (ZORUNLU - ASLA ESNETILMEZ!)
        for entry in schedule:
            if (
                entry["teacher_id"] == teacher_id
                and entry["day"] == day
                and entry["time_slot"] == slot
            ):
                self.logger.debug(
                    f"[DENEME BAŞARISIZ] Slot: (Sınıf: {class_id}, Gün: {day}, Saat: {slot}) | "
                    f"Ders: {lesson_name}, Öğretmen ID: {teacher_id} | "
                    f"Neden: ÖĞRETMEN ÇAKIŞMASI. Öğretmen bu saatte başka bir derste."
                )
                return False, "OGRETMEN_CAKISMASI"

        # 3. ÖĞRETMEN UYGUNLUĞU KONTROLÜ (İlk turda zorunlu)
        try:
            if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                # İlk 100 iterasyonda uygunluk ZORUNLU
                if self.iteration < 100:
                    self.logger.debug(
                        f"[DENEME BAŞARISIZ] Slot: (Sınıf: {class_id}, Gün: {day}, Saat: {slot}) | "
                        f"Ders: {lesson_name}, Öğretmen ID: {teacher_id} | "
                        f"Neden: ÖĞRETMEN UYGUN DEĞİL (İterasyon {self.iteration} < 100, Kural Esnetilmedi)."
                    )
                    return False, "OGRETMEN_UYGUN_DEGIL"
                else:
                    self.logger.warning(
                        f"[KURAL ESNETİLDİ] Slot: (Sınıf: {class_id}, Gün: {day}, Saat: {slot}) | "
                        f"Ders: {lesson_name}, Öğretmen ID: {teacher_id} | "
                        f"Neden: Öğretmen normalde uygun değil ancak kural esnetildi (İterasyon {self.iteration} >= 100)."
                    )
        except Exception as e:
            self.logger.error(f"Öğretmen uygunluk kontrolü sırasında hata: {e}")
            pass

        return True, "BASARILI"

    def _can_place_at_slot(
        self,
        schedule: List[Dict],
        class_id: int,
        teacher_id: int,
        day: int,
        slot: int,
        lesson_name: str = "",
    ) -> bool:
        """Basit çakışma kontrolü, sadece evet/hayır döndürür."""
        can_place, _ = self._can_place_at_slot_detailed(
            schedule, class_id, teacher_id, day, slot, lesson_name
        )
        return can_place

    def _random_perturbation(self, schedule: List[Dict], config: Dict) -> List[Dict]:
        """Rastgele küçük değişiklik yap (local search) - ÇAKIŞMA KONTROLLÜ"""

        if not schedule or len(schedule) < 2:
            return schedule

        # 10 deneme hakkı ver
        for _ in range(10):
            new_schedule = [s.copy() for s in schedule]

            # Strateji: Bir dersi başka bir boş slota taşı
            # En az yerleşmiş sınıflardan birini seç
            coverage_report = self._analyze_coverage(config)
            class_priorities = sorted(
                coverage_report["class_coverage"].items(), key=lambda x: x[1]["percentage"]
            )

            if not class_priorities:
                continue

            class_id_to_move = class_priorities[0][0]

            # Bu sınıfa ait bir dersi ve boş bir slotu seç
            entries_to_move = [e for e in new_schedule if e["class_id"] == class_id_to_move]
            empty_slots = coverage_report["class_coverage"][class_id_to_move]["empty_slots"]

            if not entries_to_move or not empty_slots:
                continue

            entry_to_move_idx = new_schedule.index(random.choice(entries_to_move))
            original_entry = new_schedule[entry_to_move_idx].copy()

            day, slot = random.choice(empty_slots)

            # Değişikliği uygula
            new_schedule[entry_to_move_idx]["day"] = day
            new_schedule[entry_to_move_idx]["time_slot"] = slot

            # Çakışma kontrolü yap
            # Geçici olarak dersi çıkarıp o slotun boş olup olmadığını kontrol et
            temp_schedule = new_schedule[:entry_to_move_idx] + new_schedule[entry_to_move_idx + 1 :]

            can_place, reason = self._can_place_at_slot_detailed(
                temp_schedule, original_entry["class_id"], original_entry["teacher_id"], day, slot
            )

            if can_place:
                self.logger.info(
                    f"[PERTURBATION] Ders (ID: {original_entry['lesson_id']}) yeni slota taşındı: Sınıf {original_entry['class_id']} -> Gün {day}, Saat {slot}"
                )
                return new_schedule  # Çakışma yok, yeni programı döndür

        # 10 denemede de başarılı olamazsa, orijinal programı döndür
        self.logger.warning(
            "[PERTURBATION] Rastgele taşıma denemeleri başarısız, çakışma riski nedeniyle değişiklik yapılmadı."
        )
        return schedule

    def _aggressive_filling(self, schedule: List[Dict], coverage: Dict, config: Dict) -> List[Dict]:
        """Agresif doldurma - kuralları esnet"""

        new_schedule = schedule[:]

        # Tüm boş hücreleri bul
        all_empty_cells = []
        for class_id, class_info in coverage["class_coverage"].items():
            for day, slot in class_info["empty_slots"]:
                all_empty_cells.append((class_id, day, slot))

        # Her boş hücreyi doldurmaya çalış (öğretmen uygunluğu esnetilmiş)
        for class_id, day, slot in all_empty_cells:
            self._try_place_lesson_in_slot(new_schedule, class_id, day, slot, config)

        return new_schedule

    def _print_final_report(
        self, initial_coverage: float, final_coverage: Dict, elapsed_time: float
    ):
        """Final rapor yazdır"""
        print("\n" + "=" * 80)
        print("📊 FİNAL RAPOR")
        print("=" * 80)

        print(f"\n⏱️  Süre: {elapsed_time:.2f} saniye")
        print(f"🔄 İterasyon: {self.iteration}")

        print(f"\n📈 KAPSAMA ANALİZİ:")
        print(f"   • Başlangıç: %{initial_coverage:.1f}")
        print(f"   • Bitiş: %{final_coverage['overall_percentage']:.1f}")
        improvement = final_coverage["overall_percentage"] - initial_coverage
        print(f"   • İyileşme: +%{improvement:.1f}")

        print(f"\n📊 DETAY:")
        print(f"   • Toplam slot sayısı: {final_coverage['total_slots']} slot")
        print(f"   • Yerleşen: {final_coverage['total_scheduled']} slot")
        missing = final_coverage["total_slots"] - final_coverage["total_scheduled"]
        print(f"   • Boş: {missing} slot")

        # Sınıf bazlı rapor
        print(f"\n🏫 SINIF BAZLI KAPSAMA:")
        for class_id, class_info in final_coverage["class_coverage"].items():
            status = "✅" if class_info["percentage"] >= 100 else "⚠️"
            print(
                f"   {status} {class_info['class_name']}: "
                f"{class_info['scheduled']}/{class_info['total_slots']} slot "
                f"(%{class_info['percentage']:.1f})"
            )
            if class_info["empty_slots"]:
                print(f"      Boş slot: {len(class_info['empty_slots'])} adet")

        # Başarı durumu
        if final_coverage["overall_percentage"] >= 100:
            print(f"\n🎉 MÜKEMMEL! %100 DOLULUK SAĞLANDI!")
        elif final_coverage["overall_percentage"] >= 95:
            print(f"\n✅ ÇOK İYİ! %{final_coverage['overall_percentage']:.1f} doluluk")
        elif final_coverage["overall_percentage"] >= 85:
            print(f"\n👍 İYİ! %{final_coverage['overall_percentage']:.1f} doluluk")
        else:
            print(f"\n⚠️  DİKKAT! Sadece %{final_coverage['overall_percentage']:.1f} doluluk")
            print(f"   Öğretmen uygunluğunu veya ders atamalarını kontrol edin")

    def _save_to_database(self):
        """Veritabanına kaydet"""
        print(f"\n💾 Veritabanına kaydediliyor...")

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

        print(f"✅ {saved}/{len(self.schedule_entries)} kayıt tamamlandı")

    def _validate_no_conflicts(self) -> List[str]:
        """
        Çakışma kontrolü yap

        Returns:
            List[str]: Çakışma mesajları (boş liste = çakışma yok)
        """
        conflicts = []

        # Sınıf bazlı çakışma kontrolü
        class_slots = {}
        for entry in self.schedule_entries:
            key = (entry["class_id"], entry["day"], entry["time_slot"])
            if key in class_slots:
                class_slots[key].append(entry)
            else:
                class_slots[key] = [entry]

        for key, entries in class_slots.items():
            if len(entries) > 1:
                class_id, day, slot = key
                days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
                day_name = days_tr[day] if day < 5 else f"Gün {day}"

                lessons = []
                for entry in entries:
                    lesson = self.db_manager.get_lesson_by_id(entry["lesson_id"])
                    lesson_name = lesson.name if lesson else "?"
                    lessons.append(lesson_name)

                conflict_msg = (
                    f"Sınıf ID {class_id} - {day_name} {slot+1}. saat: {', '.join(lessons)}"
                )
                conflicts.append(conflict_msg)

        # Öğretmen bazlı çakışma kontrolü
        teacher_slots = {}
        for entry in self.schedule_entries:
            key = (entry["teacher_id"], entry["day"], entry["time_slot"])
            if key in teacher_slots:
                teacher_slots[key].append(entry)
            else:
                teacher_slots[key] = [entry]

        for key, entries in teacher_slots.items():
            if len(entries) > 1:
                teacher_id, day, slot = key
                days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
                day_name = days_tr[day] if day < 5 else f"Gün {day}"

                teacher = self.db_manager.get_teacher_by_id(teacher_id)
                teacher_name = teacher.name if teacher else "?"

                lessons = []
                for entry in entries:
                    lesson = self.db_manager.get_lesson_by_id(entry["lesson_id"])
                    lesson_name = lesson.name if lesson else "?"
                    lessons.append(lesson_name)

                conflict_msg = (
                    f"Öğretmen {teacher_name} - {day_name} {slot+1}. saat: {', '.join(lessons)}"
                )
                conflicts.append(conflict_msg)

        return conflicts

    def _remove_conflicts(self, schedule: List[Dict]) -> List[Dict]:
        """
        Çakışmaları temizle

        Strateji: Aynı slotta birden fazla ders varsa, sadece BİRİNİ tut
        """
        # Sınıf bazlı deduplicate
        seen_slots = set()
        cleaned_schedule = []

        for entry in schedule:
            key = (entry["class_id"], entry["day"], entry["time_slot"])
            if key not in seen_slots:
                cleaned_schedule.append(entry)
                seen_slots.add(key)

        # Öğretmen bazlı deduplicate
        teacher_seen_slots = set()
        final_schedule = []

        for entry in cleaned_schedule:
            key = (entry["teacher_id"], entry["day"], entry["time_slot"])
            if key not in teacher_seen_slots:
                final_schedule.append(entry)
                teacher_seen_slots.add(key)

        return final_schedule

    def _report_progress(self, message: str, percentage: float):
        """Progress callback'e bildir"""
        if self.progress_callback:
            try:
                self.progress_callback(message, percentage)
            except Exception as e:
                logging.warning(
                    f"Progress callback raised an exception in UltraAggressiveScheduler: {e}"
                )
