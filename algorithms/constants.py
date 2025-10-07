# -*- coding: utf-8 -*-
"""
Constants for Scheduling Algorithms
Eliminates magic numbers and provides centralized configuration
"""

from typing import Dict

# ============================================================================
# SCHOOL CONFIGURATION
# ============================================================================

SCHOOL_TIME_SLOTS: Dict[str, int] = {
    "İlkokul": 7,
    "Ortaokul": 7,
    "Lise": 8,
    "Anadolu Lisesi": 8,
    "Fen Lisesi": 8,
    "Sosyal Bilimler Lisesi": 8
}

DAYS_PER_WEEK: int = 5
DAY_NAMES: list = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
DAY_NAMES_SHORT: list = ["Pzt", "Sal", "Çar", "Per", "Cum"]
DAY_NAMES_EN: list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# ============================================================================
# TIME SLOT CONFIGURATION
# ============================================================================

# Time slot thresholds
EARLY_SLOT_THRESHOLD: int = 1  # Before 2nd period
LATE_SLOT_THRESHOLD: int = 6   # After 6th period
LUNCH_SLOTS: list = [3, 4]     # Typically 4th and 5th periods

# Morning slots (preferred for difficult lessons)
MORNING_SLOTS: list = [0, 1, 2, 3]

# ============================================================================
# BLOCK DISTRIBUTION
# ============================================================================

# Maximum consecutive same lessons allowed
MAX_CONSECUTIVE_SAME_LESSONS: int = 3

# Block size preferences
PREFERRED_BLOCK_SIZE: int = 2
MIN_BLOCK_SIZE: int = 1
MAX_BLOCK_SIZE: int = 3

# ============================================================================
# SCHEDULING LIMITS
# ============================================================================

# Maximum iterations for iterative schedulers
MAX_ITERATIONS_ULTRA_AGGRESSIVE: int = 1000
MAX_ITERATIONS_SIMPLE_PERFECT: int = 5

# Maximum backtrack attempts
MAX_BACKTRACKS_ULTIMATE: int = 4000
MAX_BACKTRACKS_ENHANCED: int = 5000

# No improvement threshold
MAX_NO_IMPROVEMENT_ITERATIONS: int = 50

# Teacher daily hour limits
MAX_TEACHER_DAILY_HOURS: int = 7

# ============================================================================
# SCORING WEIGHTS (for AdvancedScheduler)
# ============================================================================

DEFAULT_SCHEDULER_WEIGHTS: Dict[str, float] = {
    'same_day_penalty': -30.0,
    'distribution_bonus': 20.0,
    'block_preference_bonus': 15.0,
    'early_slot_penalty': -10.0,
    'late_slot_penalty': -15.0,
    'lunch_break_bonus': 10.0,
    'consecutive_bonus': 5.0,
    'gap_penalty': -25.0,
    'teacher_load_balance': 10.0,
}

# ============================================================================
# SOFT CONSTRAINT WEIGHTS (for HybridOptimalScheduler)
# ============================================================================

SOFT_CONSTRAINT_WEIGHTS: Dict[str, float] = {
    'teacher_time_preference': 10.0,
    'balanced_daily_load': 15.0,
    'lesson_spacing': 12.0,
    'difficult_lessons_morning': 8.0,
    'teacher_load_balance': 10.0,
    'consecutive_block_bonus': 7.0,
    'no_gaps_penalty': 20.0,
    'lunch_break_preference': 5.0,
}

# ============================================================================
# LESSON DIFFICULTY SCORES
# ============================================================================

LESSON_DIFFICULTY_SCORES: Dict[str, int] = {
    "Matematik": 10,
    "Fizik": 9,
    "Kimya": 9,
    "Biyoloji": 8,
    "Türk Dili ve Edebiyatı": 8,
    "Geometri": 9,
    "Analitik Geometri": 9,
    "İngilizce": 7,
    "Tarih": 6,
    "Coğrafya": 6,
    "Felsefe": 7,
    "Din Kültürü": 4,
    "Beden Eğitimi": 2,
    "Beden Eğitimi ve Oyun": 2,
    "Beden Eğitimi ve Spor": 2,
    "Müzik": 2,
    "Görsel Sanatlar": 2,
    "Teknoloji Tasarım": 3,
}

# Difficult lessons (should be scheduled in morning)
DIFFICULT_LESSONS: list = [
    "Matematik",
    "Fizik",
    "Kimya",
    "Biyoloji",
    "Türk Dili ve Edebiyatı",
    "Geometri",
    "Analitik Geometri"
]

# Light lessons (can be scheduled anytime, preferred for lunch)
LIGHT_LESSONS: list = [
    "Beden Eğitimi",
    "Beden Eğitimi ve Oyun",
    "Beden Eğitimi ve Spor",
    "Müzik",
    "Görsel Sanatlar",
    "Teknoloji Tasarım",
    "Seçmeli Ders",
    "Rehberlik"
]

# ============================================================================
# COVERAGE THRESHOLDS
# ============================================================================

EXCELLENT_COVERAGE_THRESHOLD: float = 0.95  # 95%
GOOD_COVERAGE_THRESHOLD: float = 0.85       # 85%
ACCEPTABLE_COVERAGE_THRESHOLD: float = 0.70 # 70%

# ============================================================================
# RELAXATION CONFIGURATION
# ============================================================================

# Iteration threshold for teacher availability relaxation
TEACHER_AVAILABILITY_RELAXATION_THRESHOLD: int = 100

# ============================================================================
# PERFORMANCE CONFIGURATION
# ============================================================================

# Progress reporting interval (iterations)
PROGRESS_REPORT_INTERVAL: int = 10

# Cache refresh interval (seconds)
CACHE_REFRESH_INTERVAL: int = 300  # 5 minutes

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES: Dict[str, str] = {
    'no_teachers': 'Hiç öğretmen bulunamadı',
    'no_classes': 'Hiç sınıf bulunamadı',
    'no_lessons': 'Hiç ders bulunamadı',
    'no_assignments': 'Hiç ders ataması bulunamadı',
    'max_iterations': 'Maksimum iterasyon sayısına ulaşıldı',
    'max_backtracks': 'Maksimum backtrack sayısına ulaşıldı',
    'no_solution': 'Çözüm bulunamadı',
    'conflicts_detected': 'Çakışmalar tespit edildi',
}

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_MESSAGES: Dict[str, str] = {
    'schedule_generated': 'Program başarıyla oluşturuldu',
    'no_conflicts': 'Çakışma tespit edilmedi',
    'excellent_coverage': 'Mükemmel kapsama sağlandı',
    'good_coverage': 'İyi kapsama sağlandı',
}
