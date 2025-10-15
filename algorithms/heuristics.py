# -*- coding: utf-8 -*-
"""
Heuristics - Sezgisel Yöntemler
MRV, Degree, LCV ve diğer heuristic'ler
"""

import io
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class HeuristicManager:
    """Tüm heuristic'leri yöneten sınıf"""

    def __init__(self):
        pass

    def mrv_heuristic(self, variables: List, domains: Dict, assignment: Dict) -> any:
        """
        MRV (Minimum Remaining Values) Heuristic
        En az domain değeri olan değişkeni seç

        Returns: En kısıtlı değişken
        """
        unassigned = [v for v in variables if v not in assignment]

        if not unassigned:
            return None

        # Domain boyutuna göre sırala
        return min(unassigned, key=lambda v: len(domains.get(v, [])))

    def degree_heuristic(self, variables: List, constraints: List, assignment: Dict) -> any:
        """
        Degree Heuristic
        En çok kısıtlamaya sahip değişkeni seç

        Returns: En çok kısıtlamalı değişken
        """
        unassigned = [v for v in variables if v not in assignment]

        if not unassigned:
            return None

        # Her değişken için kısıtlama sayısını hesapla
        degree_map = defaultdict(int)

        for var in unassigned:
            for constraint in constraints:
                if var in constraint.variables:
                    # Atanmamış diğer değişkenlerle kaç kısıtlaması var?
                    for other_var in constraint.variables:
                        if other_var != var and other_var not in assignment:
                            degree_map[var] += 1

        # En yüksek degree'ye sahip olanı seç
        return max(unassigned, key=lambda v: degree_map[v])

    def combined_heuristic(
        self, variables: List, domains: Dict, constraints: List, assignment: Dict
    ) -> any:
        """
        MRV + Degree Kombinasyonu
        Önce MRV, eşitlik durumunda Degree

        Returns: En uygun değişken
        """
        unassigned = [v for v in variables if v not in assignment]

        if not unassigned:
            return None

        # MRV skorları
        mrv_scores = {v: len(domains.get(v, [])) for v in unassigned}

        # En küçük domain boyutunu bul
        min_domain_size = min(mrv_scores.values())

        # Aynı domain boyutuna sahip olanları bul
        mrv_candidates = [v for v in unassigned if mrv_scores[v] == min_domain_size]

        # Tek aday varsa onu döndür
        if len(mrv_candidates) == 1:
            return mrv_candidates[0]

        # Birden fazla aday varsa degree ile ayır
        degree_map = defaultdict(int)

        for var in mrv_candidates:
            for constraint in constraints:
                if var in constraint.variables:
                    for other_var in constraint.variables:
                        if other_var != var and other_var not in assignment:
                            degree_map[var] += 1

        # En yüksek degree'ye sahip olanı seç
        return max(mrv_candidates, key=lambda v: degree_map[v])

    def lcv_heuristic(
        self,
        variable: any,
        domain: Set,
        variables: List,
        domains: Dict,
        constraints: List,
        assignment: Dict,
    ) -> List:
        """
        LCV (Least Constraining Value) Heuristic
        Diğer değişkenleri en az kısıtlayan değeri önce seç

        Returns: Sıralanmış domain değerleri
        """
        if not domain:
            return []

        # Her değer için kısıtlama sayısını hesapla
        value_constraints = []

        for value in domain:
            # Bu değer atanırsa kaç değişkeni etkiler?
            constraint_count = 0

            # Test ataması
            test_assignment = assignment.copy()
            test_assignment[variable] = [value]

            # İlişkili değişkenleri kontrol et
            for constraint in constraints:
                if variable in constraint.variables:
                    for other_var in constraint.variables:
                        if other_var != variable and other_var not in assignment:
                            # Bu değişkenin domain'inde kaç değer kaldı?
                            remaining_values = 0

                            for other_value in domains.get(other_var, []):
                                # Test et
                                test_assignment[other_var] = [other_value]

                                if constraint.is_satisfied(test_assignment):
                                    remaining_values += 1

                                del test_assignment[other_var]

                            # Az değer kaldıysa kısıtlama fazla
                            constraint_count += len(domains.get(other_var, [])) - remaining_values

            value_constraints.append((constraint_count, value))

        # Küçükten büyüğe sırala (az kısıtlayan önce)
        value_constraints.sort()

        return [value for _, value in value_constraints]

    def fail_first_heuristic(
        self, variables: List, domains: Dict, constraints: List, assignment: Dict
    ) -> any:
        """
        Fail-First Principle
        Başarısız olma ihtimali yüksek olan değişkeni önce dene
        (Erken başarısızlık, daha hızlı backtrack)

        Returns: En riskli değişken
        """
        unassigned = [v for v in variables if v not in assignment]

        if not unassigned:
            return None

        # Risk skorları hesapla
        risk_scores = {}

        for var in unassigned:
            # Domain boyutu (küçük = riskli)
            domain_size = len(domains.get(var, []))

            # Kısıtlama sayısı (fazla = riskli)
            constraint_count = sum(1 for c in constraints if var in c.variables)

            # Risk skoru: düşük domain + yüksek constraint = yüksek risk
            risk = constraint_count / (domain_size + 1)
            risk_scores[var] = risk

        # En yüksek risk skoruna sahip olanı seç
        return max(unassigned, key=lambda v: risk_scores[v])


class ScheduleHeuristics:
    """Ders programı için özel heuristic'ler"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.base_heuristics = HeuristicManager()

    def prioritize_lessons(self, class_lessons: List[Dict]) -> List[Dict]:
        """
        Dersleri önceliklendirme stratejisi

        Kriterler:
        1. Haftalık saat sayısı (fazla olan önce)
        2. Zorluk derecesi (zor olan önce)
        3. Öğretmen müsaitlik durumu
        """
        difficulty_scores = {
            "Matematik": 10,
            "Fizik": 9,
            "Kimya": 9,
            "Biyoloji": 8,
            "Türk Dili ve Edebiyatı": 8,
            "Geometri": 9,
            "İngilizce": 7,
            "Tarih": 6,
            "Coğrafya": 6,
            "Felsefe": 7,
            "Din Kültürü": 4,
            "Beden Eğitimi": 2,
            "Müzik": 2,
            "Görsel Sanatlar": 2,
        }

        # Sıralama anahtarı
        def priority_key(lesson_info):
            weekly_hours = lesson_info.get("weekly_hours", 0)
            lesson_name = lesson_info.get("lesson_name", "")
            difficulty = difficulty_scores.get(lesson_name, 5)

            # Öncelik: haftalık saat (yüksek), zorluk (yüksek)
            return (-weekly_hours, -difficulty)

        return sorted(class_lessons, key=priority_key)

    def optimal_block_distribution(self, weekly_hours: int) -> List[int]:
        """
        Haftalık saate göre optimal blok dağılımı

        Örnekler:
        - 6 saat: [2, 2, 2] (3 gün)
        - 5 saat: [2, 2, 1] (3 gün)
        - 4 saat: [2, 2] (2 gün)
        - 3 saat: [2, 1] (2 gün)
        - 2 saat: [2] (1 gün)
        - 1 saat: [1] (1 gün)
        """
        if weekly_hours <= 0:
            return []

        blocks = []
        remaining = weekly_hours

        # 2'li bloklar halinde dağıt
        while remaining >= 2:
            blocks.append(2)
            remaining -= 2

        # Kalan tek saati ekle
        if remaining == 1:
            blocks.append(1)

        return blocks

    def preferred_time_slots(self, lesson_name: str, time_slots_count: int) -> List[int]:
        """
        Ders için tercih edilen slotlar

        Zor dersler: Sabah (0-3)
        Orta dersler: Gün ortası (2-5)
        Hafif dersler: Herhangi (0-7)
        """
        difficult_lessons = [
            "Matematik",
            "Fizik",
            "Kimya",
            "Biyoloji",
            "Türk Dili ve Edebiyatı",
            "Geometri",
        ]

        light_lessons = [
            "Beden Eğitimi",
            "Beden Eğitimi ve Oyun",
            "Beden Eğitimi ve Spor",
            "Müzik",
            "Görsel Sanatlar",
        ]

        if lesson_name in difficult_lessons:
            # Sabah saatleri öncelikli
            return list(range(4)) + list(range(4, time_slots_count))
        elif lesson_name in light_lessons:
            # Tüm saatler eşit
            return list(range(time_slots_count))
        else:
            # Gün ortası öncelikli
            mid_slots = list(range(2, min(6, time_slots_count)))
            other_slots = [s for s in range(time_slots_count) if s not in mid_slots]
            return mid_slots + other_slots
