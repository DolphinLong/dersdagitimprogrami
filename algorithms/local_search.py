# -*- coding: utf-8 -*-
"""
Local Search Algorithms - Yerel Arama Algoritmaları
Simulated Annealing, Hill Climbing, vb.
"""

import io
import math
import random
import sys
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class SimulatedAnnealing:
    """
    Simulated Annealing - Tavlama Benzetimi
    Kısmi çözümü iyileştirmek için yerel arama
    """

    def __init__(
        self,
        initial_temperature: float = 1000.0,
        cooling_rate: float = 0.95,
        min_temperature: float = 1.0,
        iterations_per_temp: int = 100,
    ):
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.iterations_per_temp = iterations_per_temp

        self.iterations = 0
        self.improvements = 0

    def optimize(
        self, initial_schedule: List[Dict], evaluate_func, neighbor_func, constraints_check=None
    ) -> List[Dict]:
        """
        Simulated annealing ile programı iyileştir

        Args:
            initial_schedule: Başlangıç programı
            evaluate_func: Programı değerlendiren fonksiyon (yüksek = iyi)
            neighbor_func: Komşu çözüm üreten fonksiyon
            constraints_check: Hard constraint kontrolü (opsiyonel)

        Returns:
            İyileştirilmiş program
        """
        print(f"\n🔥 Simulated Annealing başlıyor...")
        print(f"   Başlangıç sıcaklık: {self.initial_temperature}")
        print(f"   Soğutma oranı: {self.cooling_rate}")

        current = deepcopy(initial_schedule)
        current_score = evaluate_func(current)

        best = deepcopy(current)
        best_score = current_score

        temperature = self.initial_temperature
        self.iterations = 0
        self.improvements = 0

        print(f"   Başlangıç skoru: {current_score:.2f}")

        while temperature > self.min_temperature:
            for _ in range(self.iterations_per_temp):
                self.iterations += 1

                # Komşu çözüm üret
                neighbor = neighbor_func(current)

                # Hard constraint kontrolü
                if constraints_check and not constraints_check(neighbor):
                    continue

                # Komşu çözümü değerlendir
                neighbor_score = evaluate_func(neighbor)

                # Skor farkı
                delta = neighbor_score - current_score

                # Kabul et mi?
                if delta > 0:
                    # İyileşme var - kabul et
                    current = neighbor
                    current_score = neighbor_score
                    self.improvements += 1

                    # En iyi çözüm mü?
                    if current_score > best_score:
                        best = deepcopy(current)
                        best_score = current_score
                else:
                    # Kötüleşme var - olasılıkla kabul et
                    acceptance_probability = math.exp(delta / temperature)
                    if random.random() < acceptance_probability:
                        current = neighbor
                        current_score = neighbor_score

            # Sıcaklığı düşür
            temperature *= self.cooling_rate

            # İlerleme raporu (her 10 sıcaklık düşüşünde)
            if self.iterations % (self.iterations_per_temp * 10) == 0:
                print(f"   🌡️  T={temperature:.2f}, En iyi skor: {best_score:.2f}, İyileştirme: {self.improvements}")

        print(f"\n   ✅ Simulated Annealing tamamlandı")
        print(f"      Toplam iterasyon: {self.iterations}")
        print(f"      İyileştirme sayısı: {self.improvements}")
        print(f"      Başlangıç skoru: {current_score:.2f}")
        print(f"      Nihai skor: {best_score:.2f}")

        # Sıfıra bölme kontrolü
        if abs(current_score) > 0.001:
            improvement_pct = (best_score - current_score) / abs(current_score) * 100
            print(f"      İyileşme: {best_score - current_score:.2f} ({improvement_pct:.1f}%)")
        else:
            print(f"      İyileşme: {best_score - current_score:.2f}")

        return best


class HillClimbing:
    """
    Hill Climbing - Tepe Tırmanışı
    Basit yerel arama algoritması
    """

    def __init__(self, max_iterations: int = 1000, max_no_improvement: int = 100):
        self.max_iterations = max_iterations
        self.max_no_improvement = max_no_improvement

    def optimize(
        self, initial_schedule: List[Dict], evaluate_func, neighbor_func, constraints_check=None
    ) -> List[Dict]:
        """Hill climbing ile iyileştirme"""
        print(f"\n⛰️  Hill Climbing başlıyor...")

        current = deepcopy(initial_schedule)
        current_score = evaluate_func(current)

        best = deepcopy(current)
        best_score = current_score

        no_improvement = 0

        for iteration in range(self.max_iterations):
            # Komşu çözüm üret
            neighbor = neighbor_func(current)

            # Hard constraint kontrolü
            if constraints_check and not constraints_check(neighbor):
                continue

            # Değerlendir
            neighbor_score = evaluate_func(neighbor)

            # İyileşme var mı?
            if neighbor_score > current_score:
                current = neighbor
                current_score = neighbor_score
                no_improvement = 0

                # En iyi çözüm mü?
                if current_score > best_score:
                    best = deepcopy(current)
                    best_score = current_score
            else:
                no_improvement += 1

            # Çok uzun süredir iyileşme yoksa dur
            if no_improvement >= self.max_no_improvement:
                print(f"   ⚠️  {self.max_no_improvement} iterasyonda iyileşme yok - durduruluyor")
                break

        print(f"   ✅ Hill Climbing tamamlandı")
        print(f"      İterasyon: {iteration + 1}")
        print(f"      Nihai skor: {best_score:.2f}")

        return best


class ScheduleNeighborGenerator:
    """
    Program için komşu çözüm üretici
    ÖNEMLİ: Blok bütünlüğünü ve hard constraint'leri korur!
    """

    def __init__(self, db_manager, time_slots_count: int = 8):
        self.db_manager = db_manager
        self.time_slots_count = time_slots_count

    def generate_neighbor(self, schedule: List[Dict]) -> List[Dict]:
        """
        Komşu çözüm üret - BLOKLARI KORUYARAK küçük değişiklikler yap

        ÖNEMLİ KURALLAR (HARD CONSTRAINTS):
        1. Blok bütünlüğü korunmalı (2 saatlik dersler ardışık kalmalı)
        2. Her blok farklı günde olmalı
        3. Öğretmen uygunluğu kontrol edilmeli

        Stratejiler:
        1. Aynı dersin tüm bloklarını başka güne taşı (BLOK KORUMA)
        2. İki dersin bloklarını yer değiştir (BLOK KORUMA)
        3. Tek saatlik dersleri taşı
        """
        if not schedule:
            return schedule

        neighbor = deepcopy(schedule)

        # Blok haritası oluştur - hangi dersler bloklarda?
        blocks = self._identify_blocks(neighbor)

        # Stratejiler: BLOK BÜTÜNLÜĞÜNÜ KORUYARAK değişiklik yap
        strategy = random.choice(["swap_blocks", "move_block", "swap_single"])

        if strategy == "swap_blocks":
            # İki dersin BLOKLARINI tamamen yer değiştir
            if len(blocks) >= 2:
                # Rastgele iki ders seç
                lesson_keys = random.sample(list(blocks.keys()), min(2, len(blocks)))
                if len(lesson_keys) == 2:
                    key1, key2 = lesson_keys
                    blocks1 = blocks[key1]
                    blocks2 = blocks[key2]

                    # Blokları yer değiştir (günleri değiştir, slotları koru)
                    for block1 in blocks1:
                        for block2 in blocks2:
                            # Günleri değiştir
                            for idx1 in block1["indices"]:
                                for idx2 in block2["indices"]:
                                    day1 = neighbor[idx1]["day"]
                                    day2 = neighbor[idx2]["day"]
                                    neighbor[idx1]["day"] = day2
                                    neighbor[idx2]["day"] = day1

        elif strategy == "move_block":
            # Bir dersin bir bloğunu başka güne taşı
            if blocks:
                # Rastgele bir ders seç
                lesson_key = random.choice(list(blocks.keys()))
                lesson_blocks = blocks[lesson_key]

                if lesson_blocks:
                    # Rastgele bir blok seç
                    block = random.choice(lesson_blocks)

                    # Kullanılan günleri bul
                    used_days = set(block["day"] for block in lesson_blocks)

                    # Kullanılmayan bir gün seç
                    available_days = [d for d in range(5) if d not in used_days]
                    if available_days:
                        new_day = random.choice(available_days)

                        # Bloktaki tüm dersleri yeni güne taşı
                        for idx in block["indices"]:
                            neighbor[idx]["day"] = new_day

        elif strategy == "swap_single":
            # Tek saatlik (blok olmayan) dersleri değiştir
            single_entries = []
            for idx, entry in enumerate(neighbor):
                # Bu ders bir blok içinde mi kontrol et
                is_in_block = False
                for lesson_blocks in blocks.values():
                    for block in lesson_blocks:
                        if idx in block["indices"]:
                            is_in_block = True
                            break
                    if is_in_block:
                        break

                # Blok içinde değilse tek saatlik ders
                if not is_in_block:
                    single_entries.append(idx)

            # En az 2 tek saatlik ders varsa yer değiştir
            if len(single_entries) >= 2:
                idx1, idx2 = random.sample(single_entries, 2)

                day1, slot1 = neighbor[idx1]["day"], neighbor[idx1]["time_slot"]
                day2, slot2 = neighbor[idx2]["day"], neighbor[idx2]["time_slot"]

                neighbor[idx1]["day"], neighbor[idx1]["time_slot"] = day2, slot2
                neighbor[idx2]["day"], neighbor[idx2]["time_slot"] = day1, slot1

        return neighbor

    def _identify_blocks(self, schedule: List[Dict]) -> Dict:
        """
        Programdaki blokları tanımla
        Returns: {(class_id, lesson_id): [block1, block2, ...]}
        Her block: {'day': day, 'slots': [slots], 'indices': [schedule_indices]}
        """
        from collections import defaultdict

        # Sınıf-ders bazında günlük slotları grupla
        lesson_day_slots = defaultdict(lambda: defaultdict(list))

        for idx, entry in enumerate(schedule):
            key = (entry["class_id"], entry["lesson_id"])
            day = entry["day"]
            slot = entry["time_slot"]
            lesson_day_slots[key][day].append((slot, idx))

        # Blokları tanımla (ardışık slotlar)
        blocks = {}

        for key, day_slots in lesson_day_slots.items():
            lesson_blocks = []

            for day, slot_indices in day_slots.items():
                # Slot'a göre sırala
                slot_indices.sort(key=lambda x: x[0])

                # Ardışık slotları grupla
                current_block = []
                current_slots = []
                current_indices = []

                for i, (slot, idx) in enumerate(slot_indices):
                    if not current_block or slot == current_block[-1] + 1:
                        # Ardışık
                        current_block.append(slot)
                        current_slots.append(slot)
                        current_indices.append(idx)
                    else:
                        # Ardışık değil - önceki blogu kaydet
                        if len(current_block) > 0:
                            lesson_blocks.append({"day": day, "slots": current_slots, "indices": current_indices})

                        # Yeni blok başlat
                        current_block = [slot]
                        current_slots = [slot]
                        current_indices = [idx]

                # Son bloğu kaydet
                if len(current_block) > 0:
                    lesson_blocks.append({"day": day, "slots": current_slots, "indices": current_indices})

            blocks[key] = lesson_blocks

        return blocks


def adaptive_backtrack_limit(num_classes: int, num_teachers: int, avg_lessons_per_class: int) -> int:
    """
    Problem boyutuna göre adaptif backtrack limiti

    Args:
        num_classes: Sınıf sayısı
        num_teachers: Öğretmen sayısı
        avg_lessons_per_class: Sınıf başına ortalama ders sayısı

    Returns:
        Backtrack limiti
    """
    # Temel limit
    base_limit = 2000

    # Problem karmaşıklığı faktörleri
    size_factor = num_classes / 10.0  # Her 10 sınıf için 1x
    teacher_factor = num_teachers / 15.0  # Her 15 öğretmen için 1x
    complexity_factor = avg_lessons_per_class / 8.0  # Her 8 ders için 1x

    # Toplam çarpan
    multiplier = max(1.0, size_factor * teacher_factor * complexity_factor)

    # Nihai limit
    limit = int(base_limit * multiplier)

    # Minimum ve maksimum sınırlar
    limit = max(1000, min(20000, limit))

    return limit
