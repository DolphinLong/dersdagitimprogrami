# -*- coding: utf-8 -*-
"""
Soft Constraints - Esnek Kısıtlamalar
Tercihler ve optimizasyon hedefleri
"""

import sys
import io
from typing import List, Dict, Tuple, Callable
from collections import defaultdict
import math

# Set encoding for Windows
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class SoftConstraint:
    """Esnek kısıtlama - ihlal edilebilir ama maliyeti var"""
    
    def __init__(self, name: str, weight: float, 
                 evaluate_func: Callable[[Dict], float],
                 description: str = ""):
        self.name = name
        self.weight = weight
        self.evaluate_func = evaluate_func
        self.description = description
        
    def evaluate(self, schedule: List[Dict]) -> float:
        """
        Bu kısıtlama için skoru hesapla
        Yüksek skor = daha iyi (tercihe uygun)
        Düşük skor = daha kötü (tercihe aykırı)
        """
        return self.evaluate_func(schedule)
    
    def weighted_score(self, schedule: List[Dict]) -> float:
        """Ağırlıklı skor"""
        return self.weight * self.evaluate(schedule)


class SoftConstraintManager:
    """Soft constraint'leri yöneten sınıf"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.constraints = []
        self._initialize_constraints()
        
    def _initialize_constraints(self):
        """Tüm soft constraint'leri tanımla"""
        
        # 1. Öğretmen sabah/öğleden sonra tercihi
        self.constraints.append(SoftConstraint(
            name="teacher_time_preference",
            weight=10.0,
            evaluate_func=self._evaluate_teacher_time_preference,
            description="Öğretmenlerin tercih ettikleri saatlere atama"
        ))
        
        # 2. Öğrenci yorgunluğu - günlük ders yükü dengeli olmalı
        self.constraints.append(SoftConstraint(
            name="balanced_daily_load",
            weight=15.0,
            evaluate_func=self._evaluate_balanced_daily_load,
            description="Günlük ders yükü dengeli dağıtım"
        ))
        
        # 3. Ders aralığı - aynı ders için günler arası optimal aralık
        self.constraints.append(SoftConstraint(
            name="lesson_spacing",
            weight=12.0,
            evaluate_func=self._evaluate_lesson_spacing,
            description="Aynı dersin günler arası optimal aralığı (2-3 gün)"
        ))
        
        # 4. Zor dersler sabaha - Matematik, Fen vb. sabah saatlerine
        self.constraints.append(SoftConstraint(
            name="difficult_lessons_morning",
            weight=8.0,
            evaluate_func=self._evaluate_difficult_lessons_morning,
            description="Zor dersler sabah saatlerine yerleştirme"
        ))
        
        # 5. Öğretmen yük dengeleme
        self.constraints.append(SoftConstraint(
            name="teacher_load_balance",
            weight=10.0,
            evaluate_func=self._evaluate_teacher_load_balance,
            description="Öğretmenlerin günlük yükü dengeli olmalı"
        ))
        
        # 6. Ardışık aynı ders bonusu (2 saat bloklar için)
        self.constraints.append(SoftConstraint(
            name="consecutive_block_bonus",
            weight=7.0,
            evaluate_func=self._evaluate_consecutive_blocks,
            description="İki saatlik blokların ardışık olması"
        ))
        
        # 7. Boşluk penaltısı - öğrencilerin programında boşluk olmamalı
        self.constraints.append(SoftConstraint(
            name="no_gaps_penalty",
            weight=20.0,
            evaluate_func=self._evaluate_no_gaps,
            description="Öğrenci programlarında boşluk olmaması"
        ))
        
        # 8. Öğle arası bonusu - öğle saatlerinde hafif dersler
        self.constraints.append(SoftConstraint(
            name="lunch_break_preference",
            weight=5.0,
            evaluate_func=self._evaluate_lunch_break,
            description="Öğle saatlerinde hafif dersler"
        ))
        
    def evaluate_schedule(self, schedule: List[Dict]) -> Dict:
        """
        Tüm programı değerlendir
        Returns: {
            'total_score': float,
            'constraint_scores': {name: score},
            'violations': [...]
        }
        """
        total_score = 0.0
        constraint_scores = {}
        violations = []
        
        for constraint in self.constraints:
            score = constraint.weighted_score(schedule)
            total_score += score
            constraint_scores[constraint.name] = score
            
            # Negatif skor = ihlal
            if score < 0:
                violations.append({
                    'constraint': constraint.name,
                    'description': constraint.description,
                    'score': score
                })
        
        return {
            'total_score': total_score,
            'constraint_scores': constraint_scores,
            'violations': violations,
            'num_violations': len(violations)
        }
    
    def _evaluate_teacher_time_preference(self, schedule: List[Dict]) -> float:
        """Öğretmen saat tercihi değerlendirmesi"""
        score = 0.0
        
        # Her öğretmenin tercih ettiği saatler (sabah: 0-3, öğleden sonra: 4-7)
        # Bu bilgi veritabanından veya öğretmen ayarlarından gelebilir
        # Şimdilik basit bir varsayım: Çoğu öğretmen sabahları tercih eder
        
        for entry in schedule:
            slot = entry['time_slot']
            
            # Sabah saatleri (0-3) için bonus
            if 0 <= slot <= 3:
                score += 2.0
            # Geç saatler (6+) için ceza
            elif slot >= 6:
                score -= 1.0
        
        return score
    
    def _evaluate_balanced_daily_load(self, schedule: List[Dict]) -> float:
        """Günlük ders yükü dengeleme değerlendirmesi"""
        score = 0.0
        
        # Her sınıfın her gündeki ders sayısı
        class_daily_load = defaultdict(lambda: defaultdict(int))
        
        for entry in schedule:
            class_id = entry['class_id']
            day = entry['day']
            class_daily_load[class_id][day] += 1
        
        # Her sınıf için günlük yükün standart sapmasını hesapla
        for class_id, daily_loads in class_daily_load.items():
            loads = list(daily_loads.values())
            if len(loads) > 1:
                mean = sum(loads) / len(loads) if len(loads) > 0 else 0
                variance = sum((x - mean) ** 2 for x in loads) / len(loads) if len(loads) > 0 else 0
                std_dev = math.sqrt(variance) if variance >= 0 else 0
                
                # Düşük standart sapma = dengeli dağılım = yüksek skor
                # Yüksek standart sapma = dengesiz = düşük skor
                score -= std_dev * 5.0
        
        return score
    
    def _evaluate_lesson_spacing(self, schedule: List[Dict]) -> float:
        """Ders aralığı değerlendirmesi - aynı ders 2-3 gün aralıkla olmalı"""
        score = 0.0
        
        # Her sınıf-ders kombinasyonu için günleri bul
        lesson_days = defaultdict(lambda: defaultdict(list))
        
        for entry in schedule:
            class_id = entry['class_id']
            lesson_id = entry['lesson_id']
            day = entry['day']
            lesson_days[class_id][lesson_id].append(day)
        
        # Her ders için günler arası aralığı kontrol et
        for class_id, lessons in lesson_days.items():
            for lesson_id, days in lessons.items():
                days_sorted = sorted(set(days))
                
                # Ardışık günler arasındaki farkları hesapla
                for i in range(len(days_sorted) - 1):
                    gap = days_sorted[i + 1] - days_sorted[i]
                    
                    # Optimal aralık: 2-3 gün
                    if gap == 2 or gap == 3:
                        score += 5.0  # Bonus
                    elif gap == 1:
                        score -= 2.0  # Hafif ceza (çok yakın)
                    elif gap >= 4:
                        score -= 3.0  # Ceza (çok uzak)
        
        return score
    
    def _evaluate_difficult_lessons_morning(self, schedule: List[Dict]) -> float:
        """Zor derslerin sabaha yerleştirilmesi"""
        score = 0.0
        
        # Zor dersler listesi
        difficult_lessons = [
            "Matematik", "Fizik", "Kimya", "Biyoloji",
            "Geometri", "Analitik Geometri", "Türk Dili ve Edebiyatı"
        ]
        
        for entry in schedule:
            lesson_id = entry['lesson_id']
            slot = entry['time_slot']
            
            # Dersin adını al
            lesson = self.db_manager.get_lesson_by_id(lesson_id)
            if lesson and lesson.name in difficult_lessons:
                # Sabah saatleri (0-3)
                if 0 <= slot <= 3:
                    score += 3.0  # Bonus
                # Öğleden sonra (4-5)
                elif 4 <= slot <= 5:
                    score -= 1.0  # Hafif ceza
                # Geç saatler (6+)
                else:
                    score -= 3.0  # Ceza
        
        return score
    
    def _evaluate_teacher_load_balance(self, schedule: List[Dict]) -> float:
        """Öğretmen yük dengeleme"""
        score = 0.0
        
        # Her öğretmenin günlük ders sayısı
        teacher_daily_load = defaultdict(lambda: defaultdict(int))
        
        for entry in schedule:
            teacher_id = entry['teacher_id']
            day = entry['day']
            teacher_daily_load[teacher_id][day] += 1
        
        # Her öğretmen için günlük yükün standart sapmasını hesapla
        for teacher_id, daily_loads in teacher_daily_load.items():
            loads = list(daily_loads.values())
            if len(loads) > 1:
                mean = sum(loads) / len(loads) if len(loads) > 0 else 0
                variance = sum((x - mean) ** 2 for x in loads) / len(loads) if len(loads) > 0 else 0
                std_dev = math.sqrt(variance) if variance >= 0 else 0
                
                # Dengeli dağılım için bonus
                score -= std_dev * 3.0
        
        return score
    
    def _evaluate_consecutive_blocks(self, schedule: List[Dict]) -> float:
        """Ardışık blokların bonusu"""
        score = 0.0
        
        # Her sınıf-gün için dersleri sırala
        class_day_lessons = defaultdict(lambda: defaultdict(list))
        
        for entry in schedule:
            class_id = entry['class_id']
            day = entry['day']
            slot = entry['time_slot']
            lesson_id = entry['lesson_id']
            class_day_lessons[class_id][day].append((slot, lesson_id))
        
        # Ardışık aynı dersleri kontrol et
        for class_id, days in class_day_lessons.items():
            for day, lessons in days.items():
                lessons_sorted = sorted(lessons, key=lambda x: x[0])
                
                for i in range(len(lessons_sorted) - 1):
                    slot1, lesson1 = lessons_sorted[i]
                    slot2, lesson2 = lessons_sorted[i + 1]
                    
                    # Aynı ders ve ardışık slotlar
                    if lesson1 == lesson2 and slot2 == slot1 + 1:
                        score += 5.0  # Bonus
        
        return score
    
    def _evaluate_no_gaps(self, schedule: List[Dict]) -> float:
        """Boşluk penaltısı - öğrenci programlarında boşluk olmamalı"""
        score = 0.0
        
        # Her sınıf-gün için slotları bul
        class_day_slots = defaultdict(lambda: defaultdict(set))
        
        for entry in schedule:
            class_id = entry['class_id']
            day = entry['day']
            slot = entry['time_slot']
            class_day_slots[class_id][day].add(slot)
        
        # Boşlukları kontrol et
        for class_id, days in class_day_slots.items():
            for day, slots in days.items():
                if not slots:
                    continue
                
                min_slot = min(slots)
                max_slot = max(slots)
                expected_slots = max_slot - min_slot + 1
                actual_slots = len(slots)
                
                # Boşluk var mı?
                gaps = expected_slots - actual_slots
                if gaps > 0:
                    score -= gaps * 10.0  # Her boşluk için ceza
        
        return score
    
    def _evaluate_lunch_break(self, schedule: List[Dict]) -> float:
        """Öğle arası tercihi - öğle saatlerinde hafif dersler"""
        score = 0.0
        
        # Öğle saatleri genellikle 3-4. slotlar
        lunch_slots = [3, 4]
        
        # Hafif dersler
        light_lessons = [
            "Beden Eğitimi", "Beden Eğitimi ve Oyun", "Beden Eğitimi ve Spor",
            "Müzik", "Görsel Sanatlar", "Teknoloji Tasarım",
            "Seçmeli Ders", "Rehberlik"
        ]
        
        for entry in schedule:
            slot = entry['time_slot']
            lesson_id = entry['lesson_id']
            
            if slot in lunch_slots:
                lesson = self.db_manager.get_lesson_by_id(lesson_id)
                if lesson:
                    if lesson.name in light_lessons:
                        score += 2.0  # Hafif ders için bonus
                    else:
                        score -= 1.0  # Ağır ders için hafif ceza
        
        return score
    
    def get_constraint_summary(self) -> str:
        """Tüm constraint'lerin özetini döndür"""
        summary = "📋 Soft Constraints Özeti:\n"
        summary += "=" * 60 + "\n"
        
        for constraint in self.constraints:
            summary += f"• {constraint.name} (ağırlık: {constraint.weight})\n"
            summary += f"  {constraint.description}\n\n"
        
        return summary
