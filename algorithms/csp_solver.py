# -*- coding: utf-8 -*-
"""
CSP Solver - Constraint Satisfaction Problem Çözücü
Arc Consistency (AC-3) ve Constraint Propagation ile
"""

import sys
import io
from typing import List, Dict, Tuple, Set, Optional, Callable
from collections import defaultdict, deque
from copy import deepcopy

# Set encoding for Windows
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class CSPVariable:
    """CSP değişkeni (bir sınıf-ders kombinasyonu)"""
    def __init__(self, class_id: int, lesson_id: int, hours_needed: int):
        self.class_id = class_id
        self.lesson_id = lesson_id
        self.hours_needed = hours_needed
        self.assigned_slots = []  # [(day, slot), ...]
        
    def __repr__(self):
        return f"Var(C{self.class_id}_L{self.lesson_id}:{self.hours_needed}h)"
    
    def __hash__(self):
        return hash((self.class_id, self.lesson_id))
    
    def __eq__(self, other):
        return (self.class_id == other.class_id and 
                self.lesson_id == other.lesson_id)


class CSPConstraint:
    """CSP kısıtlaması"""
    def __init__(self, variables: List[CSPVariable], check_func: Callable, name: str = ""):
        self.variables = variables
        self.check_func = check_func
        self.name = name
        
    def is_satisfied(self, assignment: Dict) -> bool:
        """Kısıtlama sağlanıyor mu?"""
        return self.check_func(assignment, self.variables)


class ArcConsistency:
    """
    AC-3 (Arc Consistency 3) Algoritması
    Domain'leri tutarlı hale getirir
    """
    
    def __init__(self):
        self.revisions = 0
        
    def ac3(self, variables: List[CSPVariable], 
            domains: Dict[CSPVariable, Set[Tuple[int, int]]],
            constraints: List[CSPConstraint]) -> bool:
        """
        AC-3 algoritması ile arc consistency sağla
        Returns: True if consistent, False if unsolvable
        """
        print(f"   🔍 AC-3: Domain tutarlılığı kontrolü başlıyor...")
        self.revisions = 0
        
        # Kısıtlama haritası oluştur (her değişken için hangi kısıtlamalar var)
        constraint_map = self._build_constraint_map(variables, constraints)
        
        # Kuyruk: tüm kısıtlamaları (arc'ları) içerir
        queue = deque()
        for constraint in constraints:
            if len(constraint.variables) == 2:
                var1, var2 = constraint.variables
                queue.append((var1, var2, constraint))
                queue.append((var2, var1, constraint))
        
        # AC-3 ana döngüsü
        while queue:
            var_i, var_j, constraint = queue.popleft()
            
            if self._revise(var_i, var_j, domains, constraint):
                self.revisions += 1
                
                # Domain boş kaldıysa çözüm yok
                if not domains[var_i]:
                    print(f"   ❌ AC-3: {var_i} için domain boş kaldı - çözüm yok!")
                    return False
                
                # İlişkili tüm kısıtlamaları kuyruğa ekle
                for other_constraint in constraint_map.get(var_i, []):
                    if other_constraint == constraint:
                        continue
                    for other_var in other_constraint.variables:
                        if other_var != var_i:
                            queue.append((other_var, var_i, other_constraint))
        
        print(f"   ✅ AC-3 tamamlandı: {self.revisions} revizyon yapıldı")
        return True
    
    def _revise(self, var_i: CSPVariable, var_j: CSPVariable,
                domains: Dict[CSPVariable, Set[Tuple[int, int]]],
                constraint: CSPConstraint) -> bool:
        """
        var_i'nin domain'ini revize et (var_j'ye göre)
        Returns: True if domain was revised
        """
        revised = False
        domain_i = domains[var_i].copy()
        
        for value_i in domain_i:
            # Bu değer için var_j'de uyumlu bir değer var mı?
            satisfiable = False
            
            for value_j in domains[var_j]:
                # Test ataması yap
                test_assignment = {
                    var_i: [value_i],
                    var_j: [value_j]
                }
                
                if constraint.is_satisfied(test_assignment):
                    satisfiable = True
                    break
            
            # Uyumlu değer yoksa bu değeri sil
            if not satisfiable:
                domains[var_i].discard(value_i)
                revised = True
        
        return revised
    
    def _build_constraint_map(self, variables: List[CSPVariable],
                              constraints: List[CSPConstraint]) -> Dict:
        """Her değişken için hangi kısıtlamalar var?"""
        constraint_map = defaultdict(list)
        for constraint in constraints:
            for var in constraint.variables:
                constraint_map[var].append(constraint)
        return constraint_map


class MaintainedArcConsistency:
    """
    MAC (Maintained Arc Consistency)
    Her atamadan sonra arc consistency'yi koru
    """
    
    def __init__(self):
        self.ac3 = ArcConsistency()
        
    def maintain_consistency(self, variable: CSPVariable, value: Tuple[int, int],
                            variables: List[CSPVariable],
                            domains: Dict[CSPVariable, Set[Tuple[int, int]]],
                            constraints: List[CSPConstraint]) -> Optional[Dict]:
        """
        Bir atama yaptıktan sonra consistency'yi koru
        Returns: Yeni domain'ler veya None (inconsistent ise)
        """
        # Domain'lerin kopyasını al
        new_domains = {var: domain.copy() for var, domain in domains.items()}
        
        # Atanan değişkenin domain'ini tek değere indir
        new_domains[variable] = {value}
        
        # İlişkili değişkenler için AC-3 çalıştır
        related_vars = self._get_related_variables(variable, variables, constraints)
        
        if related_vars:
            # Sadece ilişkili kısıtlamaları kontrol et (daha hızlı)
            related_constraints = [c for c in constraints 
                                 if variable in c.variables]
            
            if not self.ac3.ac3(related_vars, new_domains, related_constraints):
                return None  # Inconsistent
        
        return new_domains
    
    def _get_related_variables(self, variable: CSPVariable,
                               variables: List[CSPVariable],
                               constraints: List[CSPConstraint]) -> List[CSPVariable]:
        """Bir değişkenle ilişkili diğer değişkenler"""
        related = set()
        for constraint in constraints:
            if variable in constraint.variables:
                for var in constraint.variables:
                    if var != variable:
                        related.add(var)
        return list(related)


class CSPSolver:
    """
    Gelişmiş CSP Çözücü
    - AC-3 ile domain filtreleme
    - MAC ile consistency koruma
    - Backtracking
    - Forward checking
    """
    
    def __init__(self):
        self.ac3 = ArcConsistency()
        self.mac = MaintainedArcConsistency()
        self.backtrack_count = 0
        self.node_count = 0
        
    def solve(self, variables: List[CSPVariable],
              domains: Dict[CSPVariable, Set[Tuple[int, int]]],
              constraints: List[CSPConstraint],
              max_backtracks: int = 10000) -> Optional[Dict]:
        """
        CSP problemini çöz
        Returns: Assignment veya None
        """
        print(f"\n🔧 CSP Solver başlıyor...")
        print(f"   Değişkenler: {len(variables)}")
        print(f"   Kısıtlamalar: {len(constraints)}")
        
        self.backtrack_count = 0
        self.node_count = 0
        
        # İlk AC-3 ile domain'leri filtrele
        if not self.ac3.ac3(variables, domains, constraints):
            print(f"   ❌ İlk AC-3 başarısız - çözüm yok!")
            return None
        
        # Backtracking ile çöz
        assignment = {}
        result = self._backtrack(assignment, variables, domains, 
                                constraints, max_backtracks)
        
        print(f"\n   📊 CSP Sonuç:")
        print(f"      Backtrack: {self.backtrack_count}")
        print(f"      Node: {self.node_count}")
        
        if result:
            print(f"      ✅ Çözüm bulundu!")
        else:
            print(f"      ❌ Çözüm bulunamadı")
        
        return result
    
    def _backtrack(self, assignment: Dict, 
                   variables: List[CSPVariable],
                   domains: Dict[CSPVariable, Set[Tuple[int, int]]],
                   constraints: List[CSPConstraint],
                   max_backtracks: int) -> Optional[Dict]:
        """Backtracking ile çöz"""
        
        self.node_count += 1
        
        # Backtrack limiti kontrolü
        if self.backtrack_count >= max_backtracks:
            return None
        
        # Tüm değişkenler atandı mı?
        if len(assignment) == len(variables):
            # Tüm kısıtlamalar sağlanıyor mu?
            if all(c.is_satisfied(assignment) for c in constraints):
                return assignment
            return None
        
        # Sonraki değişkeni seç (MRV heuristic)
        var = self._select_unassigned_variable(assignment, variables, domains)
        
        # Domain'den değerleri dene (LCV heuristic)
        ordered_values = self._order_domain_values(var, domains[var], 
                                                   assignment, constraints)
        
        for value in ordered_values:
            # Atamayı dene
            assignment[var] = [value]
            
            # MAC ile consistency kontrolü
            new_domains = self.mac.maintain_consistency(
                var, value, variables, domains, constraints
            )
            
            if new_domains is not None:
                # Consistency korunuyor - devam et
                result = self._backtrack(assignment, variables, new_domains,
                                       constraints, max_backtracks)
                if result is not None:
                    return result
            
            # Başarısız - geri al
            del assignment[var]
            self.backtrack_count += 1
        
        return None
    
    def _select_unassigned_variable(self, assignment: Dict,
                                    variables: List[CSPVariable],
                                    domains: Dict) -> CSPVariable:
        """MRV heuristic - en az domain'i olan değişkeni seç"""
        unassigned = [v for v in variables if v not in assignment]
        
        # Domain boyutuna göre sırala (küçükten büyüğe)
        return min(unassigned, key=lambda v: len(domains[v]))
    
    def _order_domain_values(self, variable: CSPVariable,
                            domain: Set[Tuple[int, int]],
                            assignment: Dict,
                            constraints: List[CSPConstraint]) -> List:
        """LCV heuristic - en az kısıtlayan değeri önce seç"""
        # Basit versiyon: domain'i olduğu gibi döndür
        # Geliştirilmiş versiyon: her değerin ne kadar kısıtlama yarattığını hesapla
        return list(domain)


def create_schedule_constraints(db_manager, time_slots_count: int) -> List[CSPConstraint]:
    """
    Ders programı için CSP kısıtlamalarını oluştur
    """
    constraints = []
    
    # 1. Öğretmen çakışma kısıtlaması
    def teacher_conflict_check(assignment, variables):
        """Aynı öğretmen aynı anda iki yerde olamaz"""
        teacher_slots = defaultdict(list)
        for var, values in assignment.items():
            for day, slot in values:
                teacher_id = var.teacher_id if hasattr(var, 'teacher_id') else None
                if teacher_id:
                    teacher_slots[(teacher_id, day, slot)].append(var)
        
        # Çakışma var mı?
        for key, vars_list in teacher_slots.items():
            if len(vars_list) > 1:
                return False
        return True
    
    # 2. Sınıf çakışma kısıtlaması
    def class_conflict_check(assignment, variables):
        """Aynı sınıf aynı anda iki derste olamaz"""
        class_slots = defaultdict(list)
        for var, values in assignment.items():
            for day, slot in values:
                class_slots[(var.class_id, day, slot)].append(var)
        
        # Çakışma var mı?
        for key, vars_list in class_slots.items():
            if len(vars_list) > 1:
                return False
        return True
    
    # Kısıtlamaları ekle
    # Not: variables parametresi çalışma zamanında verilecek
    # Bu yüzden boş liste ile oluşturuyoruz
    constraints.append(CSPConstraint([], teacher_conflict_check, "teacher_no_conflict"))
    constraints.append(CSPConstraint([], class_conflict_check, "class_no_conflict"))
    
    return constraints
