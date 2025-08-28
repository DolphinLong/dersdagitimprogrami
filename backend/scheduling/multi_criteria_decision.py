from typing import List, Dict, Any
from dataclasses import dataclass, field
import json

@dataclass
class Criterion:
    """Karar kriteri"""
    name: str
    weight: float  # 0-1 arası ağırlık
    description: str = ""
    unit: str = ""
    
    def __post_init__(self):
        # Ağırlığı 0-1 aralığına sınırla
        self.weight = max(0, min(1, self.weight))

@dataclass
class Alternative:
    """Karar alternatifi"""
    name: str
    values: Dict[str, float]  # Kriter adı: değer
    description: str = ""
    
    def get_normalized_value(self, criterion_name: str, min_val: float, max_val: float) -> float:
        """Değeri 0-1 aralığına normalize eder"""
        if max_val - min_val == 0:
            return 0
        raw_value = self.values.get(criterion_name, 0)
        return (raw_value - min_val) / (max_val - min_val)

class MultiCriteriaDecision:
    """Çok kriterli karar verme sistemi"""
    
    def __init__(self):
        self.criteria: List[Criterion] = []
        self.alternatives: List[Alternative] = []
    
    def add_criterion(self, name: str, weight: float, description: str = "", unit: str = ""):
        """Kriter ekler"""
        criterion = Criterion(name=name, weight=weight, description=description, unit=unit)
        self.criteria.append(criterion)
    
    def add_alternative(self, name: str, values: Dict[str, float], description: str = ""):
        """Alternatif ekler"""
        alternative = Alternative(name=name, values=values, description=description)
        self.alternatives.append(alternative)
    
    def topsis(self) -> List[Dict[str, Any]]:
        """
        TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) yöntemi
        ile alternatifleri sıralar
        """
        if not self.criteria or not self.alternatives:
            return []
        
        # Kriter isimlerini al
        criterion_names = [c.name for c in self.criteria]
        
        # Her kriter için min ve max değerleri bul
        min_max_values = {}
        for criterion_name in criterion_names:
            values = [alt.values.get(criterion_name, 0) for alt in self.alternatives]
            min_max_values[criterion_name] = (min(values), max(values))
        
        # Normalize edilmiş karar matrisi oluştur
        normalized_matrix = []
        for alternative in self.alternatives:
            normalized_values = {}
            for criterion_name in criterion_names:
                min_val, max_val = min_max_values[criterion_name]
                normalized_values[criterion_name] = alternative.get_normalized_value(
                    criterion_name, min_val, max_val
                )
            normalized_matrix.append(normalized_values)
        
        # Ağırlıklı normalize edilmiş karar matrisi
        weighted_matrix = []
        for normalized_values in normalized_matrix:
            weighted_values = {}
            for criterion in self.criteria:
                weighted_values[criterion.name] = (
                    normalized_values[criterion.name] * criterion.weight
                )
            weighted_matrix.append(weighted_values)
        
        # Pozitif ve negatif ideal çözümleri bul
        positive_ideal = {}
        negative_ideal = {}
        
        for criterion in self.criteria:
            if self._is_benefit_criterion(criterion.name):
                # Fayda kriteri (yüksek değerler iyi)
                positive_ideal[criterion.name] = max(
                    [w[criterion.name] for w in weighted_matrix]
                )
                negative_ideal[criterion.name] = min(
                    [w[criterion.name] for w in weighted_matrix]
                )
            else:
                # Maliyet kriteri (düşük değerler iyi)
                positive_ideal[criterion.name] = min(
                    [w[criterion.name] for w in weighted_matrix]
                )
                negative_ideal[criterion.name] = max(
                    [w[criterion.name] for w in weighted_matrix]
                )
        
        # Her alternatif için ideal çözümlere uzaklıkları hesapla
        results = []
        for i, alternative in enumerate(self.alternatives):
            weighted_values = weighted_matrix[i]
            
            # Pozitif ideal çözüme uzaklık
            positive_distance = sum([
                (weighted_values[criterion.name] - positive_ideal[criterion.name]) ** 2
                for criterion in self.criteria
            ]) ** 0.5
            
            # Negatif ideal çözüme uzaklık
            negative_distance = sum([
                (weighted_values[criterion.name] - negative_ideal[criterion.name]) ** 2
                for criterion in self.criteria
            ]) ** 0.5
            
            # Göreli yakınlık (0-1 arası, 1'e yakın olan daha iyi)
            if positive_distance + negative_distance == 0:
                relative_closeness = 0
            else:
                relative_closeness = negative_distance / (positive_distance + negative_distance)
            
            results.append({
                'alternative': alternative,
                'positive_distance': positive_distance,
                'negative_distance': negative_distance,
                'relative_closeness': relative_closeness,
                'score': relative_closeness  # Uyumluluk için score alanı
            })
        
        # Göreli yakınlığa göre sırala (büyükten küçüğe)
        results.sort(key=lambda x: x['relative_closeness'], reverse=True)
        
        return results
    
    def _is_benefit_criterion(self, criterion_name: str) -> bool:
        """
        Kriterin fayda mı maliyet mi olduğunu belirler
        Basit bir yaklaşım: kriter adında "maliyet", "süre", "zaman" gibi kelimeler varsa 
        maliyet kriteri kabul edilir
        """
        cost_keywords = ['maliyet', 'süre', 'zaman', 'hata', 'çakışma', 'ihlal']
        name_lower = criterion_name.lower()
        return not any(keyword in name_lower for keyword in cost_keywords)
    
    def weighted_sum(self) -> List[Dict[str, Any]]:
        """
        Ağırlıklı toplam yöntemi ile alternatifleri sıralar
        """
        if not self.criteria or not self.alternatives:
            return []
        
        results = []
        
        for alternative in self.alternatives:
            # Ağırlıklı toplam skoru hesapla
            score = 0
            total_weight = 0
            
            for criterion in self.criteria:
                criterion_value = alternative.values.get(criterion.name, 0)
                score += criterion_value * criterion.weight
                total_weight += criterion.weight
            
            # Normalize edilmiş skor
            if total_weight > 0:
                normalized_score = score / total_weight
            else:
                normalized_score = 0
            
            results.append({
                'alternative': alternative,
                'score': normalized_score,
                'raw_score': score
            })
        
        # Skora göre sırala (büyükten küçüğe)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def get_criteria_matrix(self) -> Dict[str, List[float]]:
        """Kriter matrisini döndürür"""
        matrix = {}
        for criterion in self.criteria:
            matrix[criterion.name] = [
                alt.values.get(criterion.name, 0) for alt in self.alternatives
            ]
        return matrix
    
    def get_ranking_report(self, method: str = 'topsis') -> Dict[str, Any]:
        """Sıralama raporu oluşturur"""
        if method.lower() == 'topsis':
            results = self.topsis()
        elif method.lower() == 'weighted_sum':
            results = self.weighted_sum()
        else:
            raise ValueError("Geçersiz yöntem. 'topsis' veya 'weighted_sum' kullanın.")
        
        report = {
            'method': method,
            'criteria': [
                {
                    'name': c.name,
                    'weight': c.weight,
                    'description': c.description
                }
                for c in self.criteria
            ],
            'alternatives': [
                {
                    'name': result['alternative'].name,
                    'description': result['alternative'].description,
                    'score': result['score'],
                    'rank': i + 1
                }
                for i, result in enumerate(results)
            ],
            'total_alternatives': len(results)
        }
        
        return report
    
    def sensitivity_analysis(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Duyarlılık analizi yapar - kriter ağırlıklarının değişimi
        sonuçları nasıl etkiler
        """
        base_results = self.topsis()
        base_ranking = [r['alternative'].name for r in base_results]
        
        analysis = {}
        
        # Her kriter için ağırlığı %10 artır ve etkisini ölç
        for criterion in self.criteria:
            # Ağırlığı geçici olarak artır
            original_weight = criterion.weight
            criterion.weight = min(1.0, criterion.weight * 1.1)
            
            # Yeni sonuçları hesapla
            new_results = self.topsis()
            new_ranking = [r['alternative'].name for r in new_results]
            
            # Sıralama değişikliğini ölç
            ranking_changes = []
            for i, (base_alt, new_alt) in enumerate(zip(base_ranking, new_ranking)):
                if base_alt != new_alt:
                    ranking_changes.append({
                        'position': i + 1,
                        'base_alternative': base_alt,
                        'new_alternative': new_alt
                    })
            
            analysis[criterion.name] = {
                'original_weight': original_weight,
                'new_weight': criterion.weight,
                'ranking_changes': ranking_changes,
                'change_count': len(ranking_changes)
            }
            
            # Ağırlığı eski haline getir
            criterion.weight = original_weight
        
        return analysis