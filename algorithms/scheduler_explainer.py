# -*- coding: utf-8 -*-
"""
Scheduler Explainer - Program Oluşturma Açıklayıcı
Başarısızlık nedenlerini analiz eder ve raporlar
"""

import io
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

# Set encoding for Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class SchedulingFailure:
    """Bir programlama başarısızlığını temsil eder"""

    def __init__(
        self,
        lesson_name: str,
        class_name: str,
        teacher_name: str,
        required_hours: int,
        scheduled_hours: int,
        reason: str,
        context: Dict = None,
    ):
        self.lesson_name = lesson_name
        self.class_name = class_name
        self.teacher_name = teacher_name
        self.required_hours = required_hours
        self.scheduled_hours = scheduled_hours
        self.reason = reason
        self.context = context or {}
        self.timestamp = datetime.now()

    def __repr__(self):
        return (
            f"Failure({self.class_name}-{self.lesson_name}: "
            f"{self.scheduled_hours}/{self.required_hours}h - {self.reason})"
        )


class SchedulerExplainer:
    """Programlama sürecini açıklayan ve analiz eden sınıf"""

    # Başarısızlık nedenleri
    REASON_TEACHER_UNAVAILABLE = "teacher_unavailable"
    REASON_NO_SLOTS = "no_available_slots"
    REASON_TEACHER_CONFLICT = "teacher_conflict"
    REASON_CLASS_CONFLICT = "class_conflict"
    REASON_DOMAIN_EXHAUSTED = "domain_exhausted"
    REASON_CONSTRAINT_VIOLATION = "constraint_violation"
    REASON_BACKTRACK_LIMIT = "backtrack_limit_exceeded"

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.failures = []
        self.warnings = []
        self.stats = defaultdict(int)

    def log_failure(
        self,
        lesson_name: str,
        class_name: str,
        teacher_name: str,
        required_hours: int,
        scheduled_hours: int,
        reason: str,
        context: Dict = None,
    ):
        """Bir başarısızlığı kaydet"""
        failure = SchedulingFailure(
            lesson_name, class_name, teacher_name, required_hours, scheduled_hours, reason, context
        )
        self.failures.append(failure)
        self.stats[reason] += 1

    def log_warning(self, message: str, context: Dict = None):
        """Bir uyarı kaydet"""
        self.warnings.append(
            {"message": message, "context": context or {}, "timestamp": datetime.now()}
        )

    def analyze_failures(self) -> Dict:
        """
        Başarısızlıkları analiz et ve rapor oluştur

        Returns: {
            'total_failures': int,
            'reasons': {reason: count},
            'critical_issues': [...],
            'recommendations': [...]
        }
        """
        if not self.failures:
            return {
                "total_failures": 0,
                "reasons": {},
                "critical_issues": [],
                "recommendations": [],
            }

        # Neden analizi
        reasons = dict(self.stats)

        # Kritik sorunları belirle
        critical_issues = self._identify_critical_issues()

        # Öneriler oluştur
        recommendations = self._generate_recommendations()

        return {
            "total_failures": len(self.failures),
            "reasons": reasons,
            "critical_issues": critical_issues,
            "recommendations": recommendations,
        }

    def _identify_critical_issues(self) -> List[str]:
        """Kritik sorunları belirle"""
        issues = []

        # 1. Öğretmen uygunluğu sorunu
        unavailable_count = self.stats[self.REASON_TEACHER_UNAVAILABLE]
        if unavailable_count > 5:
            issues.append(
                f"🔴 ÖĞRETMEN UYGUNLUĞU: {unavailable_count} ders öğretmen müsaitlik "
                f"sorunu nedeniyle yerleştirilemedi. Öğretmen uygunluk ayarlarını kontrol edin."
            )

        # 2. Slot yetersizliği
        no_slots_count = self.stats[self.REASON_NO_SLOTS]
        if no_slots_count > 5:
            issues.append(
                f"🔴 SLOT YETERSİZLİĞİ: {no_slots_count} ders için uygun slot bulunamadı. "
                f"Haftalık ders saati sayısını artırın veya sınıf sayısını azaltın."
            )

        # 3. Çakışma fazlalığı
        conflict_count = (
            self.stats[self.REASON_TEACHER_CONFLICT] + self.stats[self.REASON_CLASS_CONFLICT]
        )
        if conflict_count > 10:
            issues.append(
                f"🔴 ÇAKIŞMA FAZLALIĞI: {conflict_count} çakışma tespit edildi. "
                f"Öğretmen sayısını artırın veya ders dağılımını gözden geçirin."
            )

        # 4. Backtrack limiti
        backtrack_count = self.stats[self.REASON_BACKTRACK_LIMIT]
        if backtrack_count > 0:
            issues.append(
                f"🔴 BACKTRACK LİMİTİ: Algoritma {backtrack_count} ders için maksimum "
                f"deneme limitine ulaştı. Problem çok karmaşık olabilir."
            )

        # 5. Öğretmen başına düşen ders sayısı kontrolü
        teacher_loads = self._analyze_teacher_loads()
        overloaded_teachers = [t for t, load in teacher_loads.items() if load > 30]
        if overloaded_teachers:
            issues.append(
                f"🔴 ÖĞRETMEN AŞIRI YÜKÜ: {len(overloaded_teachers)} öğretmen haftada "
                f"30+ saat ders yüküne sahip. Öğretmen sayısını artırın."
            )

        return issues

    def _generate_recommendations(self) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []

        # Başarısızlık nedenlerine göre öneriler
        if self.stats[self.REASON_TEACHER_UNAVAILABLE] > 0:
            recommendations.append(
                "💡 Öğretmenlerin uygunluk takvimlerini gözden geçirin ve "
                "müsait oldukları gün/saatleri artırın."
            )

        if self.stats[self.REASON_NO_SLOTS] > 0:
            recommendations.append(
                "💡 Haftalık ders saati sayısını artırmayı düşünün (örn: 7'den 8'e)."
            )

        if self.stats[self.REASON_DOMAIN_EXHAUSTED] > 0:
            recommendations.append("💡 Bazı derslerin haftalık saat sayısını azaltmayı düşünün.")

        # Genel öneriler
        if len(self.failures) > 10:
            recommendations.append(
                "💡 Problem çok karmaşık görünüyor. Daha basit bir algoritma "
                "(Simple Perfect Scheduler) deneyebilirsiniz."
            )

        # Başarı oranına göre öneri
        total_required = sum(f.required_hours for f in self.failures)
        total_scheduled = sum(f.scheduled_hours for f in self.failures)
        success_rate = (total_scheduled / total_required * 100) if total_required > 0 else 100

        if success_rate < 80:
            recommendations.append(
                f"💡 Başarı oranı düşük ({success_rate:.1f}%). "
                f"Sınıf veya ders sayısını azaltmayı düşünün."
            )

        return recommendations

    def _analyze_teacher_loads(self) -> Dict[str, int]:
        """Öğretmen yük analizi"""
        teacher_loads = defaultdict(int)

        for failure in self.failures:
            teacher_loads[failure.teacher_name] += failure.scheduled_hours

        return teacher_loads

    def generate_report(self) -> str:
        """Detaylı rapor oluştur"""
        report = []
        report.append("=" * 80)
        report.append("📊 PROGRAMLAMA SÜREÇ RAPORU")
        report.append("=" * 80)
        report.append("")

        # Özet
        analysis = self.analyze_failures()
        report.append(f"🎯 Özet:")
        report.append(f"   • Toplam Başarısızlık: {analysis['total_failures']}")
        report.append(f"   • Uyarı Sayısı: {len(self.warnings)}")
        report.append("")

        # Neden dağılımı
        if analysis["reasons"]:
            report.append("📋 Başarısızlık Nedenleri:")
            for reason, count in sorted(analysis["reasons"].items(), key=lambda x: -x[1]):
                reason_name = self._get_reason_name(reason)
                report.append(f"   • {reason_name}: {count}")
            report.append("")

        # Kritik sorunlar
        if analysis["critical_issues"]:
            report.append("🔴 Kritik Sorunlar:")
            for issue in analysis["critical_issues"]:
                report.append(f"   {issue}")
            report.append("")

        # Öneriler
        if analysis["recommendations"]:
            report.append("💡 Öneriler:")
            for rec in analysis["recommendations"]:
                report.append(f"   {rec}")
            report.append("")

        # Detaylı başarısızlık listesi (ilk 10)
        if self.failures:
            report.append("📝 Başarısız Dersler (ilk 10):")
            for i, failure in enumerate(self.failures[:10], 1):
                success_rate = (
                    (failure.scheduled_hours / failure.required_hours * 100)
                    if failure.required_hours > 0
                    else 0
                )
                report.append(
                    f"   {i}. {failure.class_name} - {failure.lesson_name} "
                    f"({failure.teacher_name})"
                )
                report.append(
                    f"      Yerleşen: {failure.scheduled_hours}/{failure.required_hours} saat "
                    f"({success_rate:.0f}%)"
                )
                report.append(f"      Neden: {self._get_reason_name(failure.reason)}")
            report.append("")

        # Öğretmen yük analizi
        teacher_loads = self._analyze_teacher_loads()
        if teacher_loads:
            report.append("👨‍🏫 Öğretmen Yük Analizi:")
            sorted_teachers = sorted(teacher_loads.items(), key=lambda x: -x[1])[:10]
            for teacher, load in sorted_teachers:
                status = "⚠️" if load > 25 else "✅"
                report.append(f"   {status} {teacher}: {load} saat/hafta")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def _get_reason_name(self, reason: str) -> str:
        """Neden kodunu insan okunabilir isme çevir"""
        names = {
            self.REASON_TEACHER_UNAVAILABLE: "Öğretmen Müsait Değil",
            self.REASON_NO_SLOTS: "Uygun Slot Yok",
            self.REASON_TEACHER_CONFLICT: "Öğretmen Çakışması",
            self.REASON_CLASS_CONFLICT: "Sınıf Çakışması",
            self.REASON_DOMAIN_EXHAUSTED: "Domain Tükendi",
            self.REASON_CONSTRAINT_VIOLATION: "Kısıtlama İhlali",
            self.REASON_BACKTRACK_LIMIT: "Backtrack Limiti Aşıldı",
        }
        return names.get(reason, reason)

    def clear(self):
        """Tüm kayıtları temizle"""
        self.failures.clear()
        self.warnings.clear()
        self.stats.clear()
