# -*- coding: utf-8 -*-
"""
Ultimate Scheduler - Gerçek Backtracking + Gelişmiş Slot Optimizasyonu
%100 Doluluk için en güçlü algoritma
"""

import sys
import io
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
from copy import deepcopy

# Set encoding for Windows
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class SchedulingState:
    """Scheduling durumunu tutan sınıf (backtracking için)"""
    def __init__(self):
        self.assignments = []  # Yapılan atamalar
        self.teacher_usage = defaultdict(lambda: defaultdict(set))
        self.class_usage = defaultdict(lambda: defaultdict(set))
        self.lesson_progress = {}  # {(class_id, lesson_id): scheduled_hours}
    
    def copy(self):
        """Durumu kopyala"""
        new_state = SchedulingState()
        new_state.assignments = self.assignments.copy()
        new_state.teacher_usage = deepcopy(self.teacher_usage)
        new_state.class_usage = deepcopy(self.class_usage)
        new_state.lesson_progress = self.lesson_progress.copy()
        return new_state


class UltimateScheduler:
    """
    En Güçlü Scheduler:
    - Constraint Satisfaction Problem (CSP) yaklaşımı
    - Gerçek backtracking (geri izleme)
    - Forward checking
    - MRV (Minimum Remaining Values) heuristic
    - LCV (Least Constraining Value) heuristic
    - Arc consistency
    """
    
    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8
    }
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.time_slots_count = 7
        self.state = SchedulingState()
        self.lesson_requirements = []  # [(class_obj, lesson_info, remaining_hours)]
        self.domains = {}  # {(class_id, lesson_id): [valid_slots]}
        self.backtrack_count = 0
        self.max_backtracks = 4000
        
    def generate_schedule(self) -> List[Dict]:
        """Ana program oluşturma fonksiyonu"""
        print("\n" + "="*80)
        print("🎯 ULTIMATE SCHEDULER - Backtracking + CSP + Forward Checking")
        print("="*80)
        
        # Hazırlık
        self.state = SchedulingState()
        self.backtrack_count = 0
        
        # Verileri al
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()
        assignments = self.db_manager.get_schedule_by_school_type()
        
        school_type = self.db_manager.get_school_type() or "Lise"
        self.time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)
        
        print(f"\n📊 Konfigürasyon:")
        print(f"   • Okul: {school_type} | Günlük Saat: {self.time_slots_count}")
        print(f"   • Sınıf: {len(classes)} | Öğretmen: {len(teachers)}")
        print(f"   • Atamalar: {len(assignments)}")
        
        # Atama haritası
        assignment_map = {}
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id)
            assignment_map[key] = assignment.teacher_id
        
        # 1. Ders gereksinimlerini topla
        print(f"\n📝 1. Adım: Ders gereksinimleri toplanıyor...")
        total_hours = 0
        
        for class_obj in classes:
            class_lessons = self._get_class_lessons(class_obj, lessons, assignment_map, teachers)
            for lesson_info in class_lessons:
                weekly_hours = lesson_info['weekly_hours']
                total_hours += weekly_hours
                
                self.lesson_requirements.append({
                    'class_obj': class_obj,
                    'lesson_info': lesson_info,
                    'remaining_hours': weekly_hours
                })
                
                # İlerleme takibi başlat
                key = (class_obj.class_id, lesson_info['lesson_id'])
                self.state.lesson_progress[key] = 0
        
        print(f"   ✅ {len(self.lesson_requirements)} ders gereksinimi ({total_hours} saat)")
        
        # 2. Domain'leri hesapla (her ders için geçerli slotlar)
        print(f"\n🔍 2. Adım: Domain'ler hesaplanıyor...")
        self._initialize_domains(classrooms)
        print(f"   ✅ Domain'ler hazır")
        
        # 3. Dersleri önceliklendir (MRV - Minimum Remaining Values)
        print(f"\n🎯 3. Adım: Dersler önceliklendiriliyor (MRV)...")
        self._prioritize_lessons()
        print(f"   ✅ En kısıtlı dersler önce yerleştirilecek")
        
        # 4. CSP ile çöz (backtracking)
        print(f"\n🚀 4. Adım: CSP çözücü başlatılıyor...")
        success = self._solve_csp(0, classrooms)
        
        # Sonuç
        print(f"\n{'='*80}")
        print(f"🎯 SONUÇ")
        print(f"{'='*80}")
        print(f"📊 Toplam Gereksinim: {total_hours} saat")
        print(f"✅ Yerleştirilen: {len(self.state.assignments)} saat")
        coverage = (len(self.state.assignments) / total_hours * 100) if total_hours > 0 else 0
        print(f"📈 Kapsama: {coverage:.1f}%")
        print(f"🔄 Backtrack Sayısı: {self.backtrack_count}")
        
        if success:
            print(f"\n🎉 BAŞARILI! Tüm dersler yerleştirildi!")
        else:
            print(f"\n⚠️  Bazı dersler yerleştirilemedi (max backtrack limiti)")
        
        # Veritabanına kaydet
        print(f"\n💾 Veritabanına kaydediliyor...")
        self.db_manager.clear_schedule()
        
        saved_count = 0
        for entry in self.state.assignments:
            if self.db_manager.add_schedule_program(
                entry['class_id'], entry['teacher_id'], entry['lesson_id'],
                entry['classroom_id'], entry['day'], entry['time_slot']
            ):
                saved_count += 1
        
        print(f"✅ {saved_count} program girişi kaydedildi")
        
        return self.state.assignments
    
    def _get_class_lessons(self, class_obj, lessons, assignment_map, teachers) -> List[Dict]:
        """Sınıfın derslerini al"""
        class_lessons = []
        
        for lesson in lessons:
            assignment_key = (class_obj.class_id, lesson.lesson_id)
            if assignment_key in assignment_map:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                    lesson.lesson_id, class_obj.grade
                )
                
                if weekly_hours and weekly_hours > 0:
                    teacher_id = assignment_map[assignment_key]
                    teacher = self.db_manager.get_teacher_by_id(teacher_id)
                    
                    if teacher:
                        class_lessons.append({
                            'lesson_id': lesson.lesson_id,
                            'lesson_name': lesson.name,
                            'teacher_id': teacher.teacher_id,
                            'teacher_name': teacher.name,
                            'weekly_hours': weekly_hours,
                        })
        
        return class_lessons
    
    def _initialize_domains(self, classrooms):
        """Her ders için geçerli slot domain'lerini hesapla"""
        for req in self.lesson_requirements:
            class_id = req['class_obj'].class_id
            lesson_id = req['lesson_info']['lesson_id']
            teacher_id = req['lesson_info']['teacher_id']
            
            # Bu ders için geçerli tüm slotları bul
            valid_slots = []
            
            for day in range(5):
                for slot in range(self.time_slots_count):
                    # Öğretmen uygun mu?
                    if self.db_manager.is_teacher_available(teacher_id, day, slot):
                        valid_slots.append((day, slot))
            
            key = (class_id, lesson_id)
            self.domains[key] = valid_slots
    
    def _prioritize_lessons(self):
        """Dersleri MRV heuristic'e göre sırala"""
        # MRV: En az seçeneği olan dersi önce yerleştir
        def mrv_score(req):
            class_id = req['class_obj'].class_id
            lesson_id = req['lesson_info']['lesson_id']
            key = (class_id, lesson_id)
            
            # Domain boyutu (küçük daha öncelikli)
            domain_size = len(self.domains.get(key, []))
            
            # Haftalık saat (fazla daha öncelikli)
            weekly_hours = req['remaining_hours']
            
            # Skor: domain küçük + saat fazla = yüksek öncelik
            return (domain_size, -weekly_hours)
        
        self.lesson_requirements.sort(key=mrv_score)
    
    def _solve_csp(self, index: int, classrooms: List) -> bool:
        """
        CSP çözücü - Backtracking ile
        Returns: True if all lessons scheduled successfully
        """
        # Base case: Tüm dersler işlendi mi?
        if index >= len(self.lesson_requirements):
            # Tüm derslerin tüm saatleri yerleşti mi kontrol et
            for req in self.lesson_requirements:
                class_id = req['class_obj'].class_id
                lesson_id = req['lesson_info']['lesson_id']
                key = (class_id, lesson_id)
                
                if self.state.lesson_progress[key] < req['lesson_info']['weekly_hours']:
                    return False
            return True
        
        # Backtrack limiti kontrolü
        if self.backtrack_count >= self.max_backtracks:
            print(f"   ⚠️  Max backtrack limitine ulaşıldı ({self.max_backtracks})")
            return False
        
        # Mevcut dersi al
        req = self.lesson_requirements[index]
        class_obj = req['class_obj']
        lesson_info = req['lesson_info']
        class_id = class_obj.class_id
        lesson_id = lesson_info['lesson_id']
        teacher_id = lesson_info['teacher_id']
        weekly_hours = lesson_info['weekly_hours']
        
        key = (class_id, lesson_id)
        scheduled = self.state.lesson_progress[key]
        
        # Bu ders zaten tamamlandıysa bir sonrakine geç
        if scheduled >= weekly_hours:
            return self._solve_csp(index + 1, classrooms)
        
        # İlerleme gösterimi
        if index % 5 == 0 and len(self.lesson_requirements) > 0:
            progress = (index / len(self.lesson_requirements) * 100)
            print(f"   📊 İlerleme: {progress:.0f}% ({index}/{len(self.lesson_requirements)} ders)")
        
        # Domain'den slot seç (LCV - Least Constraining Value)
        domain = self._get_current_domain(class_id, lesson_id, teacher_id)
        
        if not domain:
            # Domain boş - backtrack gerekli
            self.backtrack_count += 1
            return False
        
        # LCV sıralaması: diğer dersleri en az kısıtlayan slotları önce dene
        ordered_slots = self._order_domain_lcv(domain, class_id, teacher_id)
        
        # Her slotu dene
        for day, slot in ordered_slots:
            # Forward checking: Bu atama yapılabilir mi?
            if not self._is_consistent(class_id, teacher_id, day, slot, lesson_id):
                continue
            
            # Atamayı yap
            classroom = self._find_available_classroom(classrooms, day, slot)
            classroom_id = classroom.classroom_id if classroom else 1
            
            assignment = {
                'class_id': class_id,
                'teacher_id': teacher_id,
                'lesson_id': lesson_id,
                'classroom_id': classroom_id,
                'day': day,
                'time_slot': slot
            }
            
            # State'i güncelle
            self._make_assignment(assignment)
            
            # Recursive çağrı
            if self._solve_csp(index, classrooms):  # Aynı index (bu dersin devamı)
                return True
            
            # Başarısız - geri al (BACKTRACK)
            self._undo_assignment(assignment)
            self.backtrack_count += 1
        
        # Hiçbir slot çalışmadı - bir sonraki derse geç
        # (Bu ders kısmi yerleşebilir)
        return self._solve_csp(index + 1, classrooms)
    
    def _get_current_domain(self, class_id: int, lesson_id: int, teacher_id: int) -> List[Tuple[int, int]]:
        """Mevcut durumda geçerli domain'i al (forward checking)"""
        key = (class_id, lesson_id)
        original_domain = self.domains.get(key, [])
        
        # Forward checking: Şu anda kullanılabilir slotları filtrele
        valid_slots = []
        for day, slot in original_domain:
            # Sınıf boş mu?
            if slot in self.state.class_usage[class_id][day]:
                continue
            
            # Öğretmen boş mu?
            if slot in self.state.teacher_usage[teacher_id][day]:
                continue
            
            valid_slots.append((day, slot))
        
        return valid_slots
    
    def _order_domain_lcv(self, domain: List[Tuple[int, int]], class_id: int, teacher_id: int) -> List[Tuple[int, int]]:
        """
        LCV (Least Constraining Value) heuristic
        Diğer dersleri en az kısıtlayan slotları önce dene
        """
        slot_scores = []
        
        for day, slot in domain:
            # Bu slotu kullanırsak kaç ders etkilenir?
            constraint_count = 0
            
            # Bu öğretmenin diğer dersleri için bu slot bir seçenek mi?
            for req in self.lesson_requirements:
                other_teacher_id = req['lesson_info']['teacher_id']
                if other_teacher_id == teacher_id:
                    other_key = (req['class_obj'].class_id, req['lesson_info']['lesson_id'])
                    if (day, slot) in self.domains.get(other_key, []):
                        constraint_count += 1
            
            slot_scores.append((constraint_count, day, slot))
        
        # Düşük kısıtlama olanlar önce (LCV)
        slot_scores.sort()
        
        return [(day, slot) for _, day, slot in slot_scores]
    
    def _is_consistent(self, class_id: int, teacher_id: int, day: int, slot: int, lesson_id: int = None) -> bool:
        """Atama tutarlı mı kontrol et"""
        # Sınıf çakışması
        if slot in self.state.class_usage[class_id][day]:
            return False
        
        # Öğretmen çakışması
        if slot in self.state.teacher_usage[teacher_id][day]:
            return False
        
        # Öğretmen uygunluğu
        if not self.db_manager.is_teacher_available(teacher_id, day, slot):
            return False
        
        # ÖNEMLİ: 3 saat üst üste aynı ders kontrolü
        if lesson_id is not None:
            if self._would_create_three_consecutive_lessons(class_id, lesson_id, day, slot):
                return False
        
        return True
    
    def _would_create_three_consecutive_lessons(
        self, class_id: int, lesson_id: int, day: int, slot: int
    ) -> bool:
        """
        Bu slot'a ders yerleştirilirse 3 saat üst üste aynı ders olur mu?
        Returns True if placing would create 3 consecutive same lessons
        """
        # Bu sınıfın bu gündeki tüm derslerini bul
        class_schedule_today = []
        for entry in self.state.assignments:
            if entry['class_id'] == class_id and entry['day'] == day:
                class_schedule_today.append((entry['time_slot'], entry['lesson_id']))
        
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
    
    def _make_assignment(self, assignment: Dict):
        """Atamayı yap ve state'i güncelle"""
        self.state.assignments.append(assignment)
        
        class_id = assignment['class_id']
        teacher_id = assignment['teacher_id']
        lesson_id = assignment['lesson_id']
        day = assignment['day']
        slot = assignment['time_slot']
        
        self.state.class_usage[class_id][day].add(slot)
        self.state.teacher_usage[teacher_id][day].add(slot)
        
        # İlerlemeyi güncelle
        key = (class_id, lesson_id)
        self.state.lesson_progress[key] = self.state.lesson_progress.get(key, 0) + 1
    
    def _undo_assignment(self, assignment: Dict):
        """Atamayı geri al (BACKTRACK)"""
        if assignment in self.state.assignments:
            self.state.assignments.remove(assignment)
        
        class_id = assignment['class_id']
        teacher_id = assignment['teacher_id']
        lesson_id = assignment['lesson_id']
        day = assignment['day']
        slot = assignment['time_slot']
        
        self.state.class_usage[class_id][day].discard(slot)
        self.state.teacher_usage[teacher_id][day].discard(slot)
        
        # İlerlemeyi geri al
        key = (class_id, lesson_id)
        self.state.lesson_progress[key] = max(0, self.state.lesson_progress.get(key, 0) - 1)
    
    def _find_available_classroom(self, classrooms: List, day: int, slot: int):
        """Uygun sınıf bul"""
        for classroom in classrooms:
            return classroom
        return None
