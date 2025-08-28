import React, { useState } from 'react';
import { CheckCircle, Circle, Clock, Users, Palette, Cog, Database, Layout, Zap, Brain, BarChart3, Shield, Workflow } from 'lucide-react';

interface Task {
  id: string;
  text: string;
}

interface Phase {
  id: string;
  title: string;
  duration: string;
  icon: React.ReactNode;
  color: string;
  focus: string;
  priority: string;
  tasks: Task[];
}

const EnhancedClassSchedulingRoadmap = () => {
  const [completedPhases, setCompletedPhases] = useState<Set<string>>(new Set());
  const [completedTasks, setCompletedTasks] = useState<Set<string>>(new Set());

  const togglePhase = (phaseId: string) => {
    const newCompleted = new Set(completedPhases);
    if (newCompleted.has(phaseId)) {
      newCompleted.delete(phaseId);
    } else {
      newCompleted.add(phaseId);
    }
    setCompletedPhases(newCompleted);
  };

  const toggleTask = (taskId: string) => {
    const newCompleted = new Set(completedTasks);
    if (newCompleted.has(taskId)) {
      newCompleted.delete(taskId);
    } else {
      newCompleted.add(taskId);
    }
    setCompletedTasks(newCompleted);
  };

  const phases: Phase[] = [
    {
      id: 'phase1',
      title: 'Faz 1: Temel Altyapı & Planlama',
      duration: '2-3 hafta',
      icon: <Database className="w-6 h-6" />,
      color: 'bg-blue-100 border-blue-300',
      focus: 'Sağlam temel oluşturma',
      priority: 'Kritik',
      tasks: [
        { id: 't1-1', text: 'Proje kurulumu ve Git repository oluşturma' },
        { id: 't1-2', text: 'Django projesi kurulumu ve temel yapılandırma' },
        { id: 't1-3', text: 'PostgreSQL veritabanı kurulumu' },
        { id: 't1-4', text: 'Gelişmiş modeller: Öğretmen, Sınıf, Ders, Zaman Dilimi, Kısıtlamalar' },
        { id: 't1-5', text: 'Django Admin arayüzü kurulumu' },
        { id: 't1-6', text: 'React projesi kurulumu ve Tailwind CSS entegrasyonu' },
        { id: 't1-7', text: 'Veritabanı ilişkileri ve indexleme stratejisi' }
      ]
    },
    {
      id: 'phase2',
      title: 'Faz 2: Temel Algoritma & Kısıtlama Motoru',
      duration: '3-4 hafta',
      icon: <Cog className="w-6 h-6" />,
      color: 'bg-green-100 border-green-300',
      focus: 'Çekirdek çizelgeleme mantığı',
      priority: 'Kritik',
      tasks: [
        { id: 't2-1', text: 'Çoklu kısıtlama analizi ve tasarım dokümantasyonu' },
        { id: 't2-2', text: 'Temel ders dağıtım algoritması implementasyonu' },
        { id: 't2-3', text: 'Çakışma kontrolü ve hata yönetimi sistemi' },
        { id: 't2-4', text: 'Öğretmen müsaitlik ve tercih sistemi' },
        { id: 't2-5', text: 'Sınıf kapasite ve özellik kontrolü' },
        { id: 't2-6', text: 'Çakışma matrisi algoritması' },
        { id: 't2-7', text: 'Yedek plan sistemi ve alternatif çözümler' },
        { id: 't2-8', text: 'API endpoints (REST) oluşturma' }
      ]
    },
    {
      id: 'phase25',
      title: 'Faz 2.5: Akıllı Optimizasyon Sistemi',
      duration: '2-3 hafta',
      icon: <Brain className="w-6 h-6" />,
      color: 'bg-indigo-100 border-indigo-300',
      focus: 'İleri seviye optimizasyon algoritmaları',
      priority: 'Yüksek',
      tasks: [
        { id: 't25-1', text: 'Genetik algoritma implementasyonu' },
        { id: 't25-2', text: 'Çok kriterli karar verme sistemi' },
        { id: 't25-3', text: 'Machine Learning veri toplama altyapısı' },
        { id: 't25-4', text: 'Performans metriklerini ölçme sistemi' },
        { id: 't25-5', text: 'Optimizasyon sonuçları karşılaştırma aracı' },
        { id: 't25-6', text: 'Adaptive learning: Sistem kendini geliştirme' }
      ]
    },
    {
      id: 'phase3',
      title: 'Faz 3: Kullanıcı Arayüzü & Workflow',
      duration: '3-4 hafta',
      icon: <Layout className="w-6 h-6" />,
      color: 'bg-purple-100 border-purple-300',
      focus: 'Kullanışlı ve güçlü arayüz',
      priority: 'Kritik',
      tasks: [
        { id: 't3-1', text: 'Gelişmiş component yapısı (Header, Sidebar, Layout)' },
        { id: 't3-2', text: 'İnteraktif ders çizelgesi görünümü (grid layout)' },
        { id: 't3-3', text: 'Öğretmen ve sınıf yönetim sayfaları' },
        { id: 't3-4', text: 'Çizelge karşılaştırma ve senaryo analiz aracı' },
        { id: 't3-5', text: 'Bulk editing: Toplu değişiklik yapma arayüzü' },
        { id: 't3-6', text: 'Form componentları ve gelişmiş validasyonlar' },
        { id: 't3-7', text: 'Real-time çakışma uyarıları' },
        { id: 't3-8', text: 'Loading states ve error handling UI' }
      ]
    },
    {
      id: 'phase4',
      title: 'Faz 4: Şık Tasarım & UX İyileştirmeleri',
      duration: '2-3 hafta',
      icon: <Palette className="w-6 h-6" />,
      color: 'bg-pink-100 border-pink-300',
      focus: 'Modern ve profesyonel görünüm',
      priority: 'Orta',
      tasks: [
        { id: 't4-1', text: 'Tutarlı renk paleti ve typography sistemi' },
        { id: 't4-2', text: 'Modern ikon seti ve görsel hiyerarşi' },
        { id: 't4-3', text: 'Smooth animasyonlar ve micro-interactions' },
        { id: 't4-4', text: 'Responsive design (mobil ve tablet uyumlu)' },
        { id: 't4-5', text: 'Dark mode desteği ve tema yönetimi' },
        { id: 't4-6', text: 'Accessibility (WCAG 2.1) uyumluluğu' },
        { id: 't4-7', text: 'Kullanıcı onboarding ve tooltips' }
      ]
    },
    {
      id: 'phase5',
      title: 'Faz 5: Gelişmiş Özellikler & Entegrasyonlar',
      duration: '3-4 hafta',
      icon: <Zap className="w-6 h-6" />,
      color: 'bg-yellow-100 border-yellow-300',
      focus: 'İleri seviye kullanıcı deneyimi',
      priority: 'Yüksek',
      tasks: [
        { id: 't5-1', text: 'Drag & drop ile ders taşıma ve düzenleme' },
        { id: 't5-2', text: 'Otomatik çizelge oluşturma ve öneriler' },
        { id: 't5-3', text: 'Excel/PDF export ve import özellikleri' },
        { id: 't5-4', text: 'Şablon sistemi: Hızlı kurulum için hazır şablonlar' },
        { id: 't5-5', text: 'WhatsApp/Email bildirim entegrasyonu' },
        { id: 't5-6', text: 'Real-time collaboration (çoklu kullanıcı)' },
        { id: 't5-7', text: 'Performance optimization ve caching stratejileri' },
        { id: 't5-8', text: 'Bulk operations ve batch processing' }
      ]
    },
    {
      id: 'phase55',
      title: 'Faz 5.5: Onay Süreci & Workflow Yönetimi',
      duration: '2 hafta',
      icon: <Workflow className="w-6 h-6" />,
      color: 'bg-teal-100 border-teal-300',
      focus: 'Kurumsal süreç yönetimi',
      priority: 'Yüksek',
      tasks: [
        { id: 't55-1', text: 'Approval workflow sistemi (Müdür onayı)' },
        { id: 't55-2', text: 'Öğretmen feedback ve değişiklik talep sistemi' },
        { id: 't55-3', text: 'Değişiklik geçmişi (audit trail)' },
        { id: 't55-4', text: 'Rol bazlı yetki yönetimi' },
        { id: 't55-5', text: 'Otomatik bildirim sistemi' },
        { id: 't55-6', text: 'Conflict resolution protokolleri' }
      ]
    },
    {
      id: 'phase6',
      title: 'Faz 6: Veri Analizi & Raporlama',
      duration: '2-3 hafta',
      icon: <BarChart3 className="w-6 h-6" />,
      color: 'bg-emerald-100 border-emerald-300',
      focus: 'İş zekası ve analitik',
      priority: 'Orta',
      tasks: [
        { id: 't6-1', text: 'Çizelge verimliliği analiz dashboard\'u' },
        { id: 't6-2', text: 'Öğretmen iş yükü dengesi raporları' },
        { id: 't6-3', text: 'Sınıf kullanım oranı ve optimizasyon önerileri' },
        { id: 't6-4', text: 'Historical data tracking ve trend analizi' },
        { id: 't6-5', text: 'Dönemler arası karşılaştırma raporları' },
        { id: 't6-6', text: 'Custom report builder' },
        { id: 't6-7', text: 'KPI tracking ve performance metrics' }
      ]
    },
    {
      id: 'phase7',
      title: 'Faz 7: Test & Kalite Güvence',
      duration: '2-3 hafta',
      icon: <Shield className="w-6 h-6" />,
      color: 'bg-orange-100 border-orange-300',
      focus: 'Güvenilirlik ve kalite',
      priority: 'Kritik',
      tasks: [
        { id: 't7-1', text: 'Comprehensive unit ve integration testleri' },
        { id: 't7-2', text: 'Algorithm stress testing ve edge cases' },
        { id: 't7-3', text: 'End-to-end testing ve user journey testleri' },
        { id: 't7-4', text: 'Performance ve load testing' },
        { id: 't7-5', text: 'Security testing ve vulnerability assessment' },
        { id: 't7-6', text: 'User acceptance testing (UAT)' },
        { id: 't7-7', text: 'Data migration ve backup testing' }
      ]
    },
    {
      id: 'phase8',
      title: 'Faz 8: Deployment & Production',
      duration: '2 hafta',
      icon: <Users className="w-6 h-6" />,
      color: 'bg-red-100 border-red-300',
      focus: 'Canlıya alma ve sürdürülebilirlik',
      priority: 'Kritik',
      tasks: [
        { id: 't8-1', text: 'Production environment kurulumu ve hardening' },
        { id: 't8-2', text: 'CI/CD pipeline kurulumu ve automation' },
        { id: 't8-3', text: 'Monitoring ve alerting sistemi' },
        { id: 't8-4', text: 'Backup ve disaster recovery planı' },
        { id: 't8-5', text: 'Comprehensive documentation ve API docs' },
        { id: 't8-6', text: 'Kullanıcı eğitimi ve rehber materyalleri' },
        { id: 't8-7', text: 'Go-live support ve hotfix planları' }
      ]
    }
  ];

  const totalTasks = phases.reduce((sum, phase) => sum + phase.tasks.length, 0);
  const completedTaskCount = completedTasks.size;
  const progressPercentage = Math.round((completedTaskCount / totalTasks) * 100);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Kritik': return 'bg-red-100 text-red-800 border-red-200';
      case 'Yüksek': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Orta': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">🎓 İleri Seviye Ders Dağıtım Sistemi</h1>
        <p className="text-gray-600 mb-4">AI Destekli Akıllı Çizelgeleme - Geliştirme Yol Haritası</p>
        
        <div className="bg-gradient-to-r from-indigo-500 via-purple-600 to-pink-600 rounded-lg p-6 text-white mb-6">
          <div className="flex justify-between items-center mb-3">
            <span className="text-xl font-semibold">🚀 Genel İlerleme</span>
            <span className="text-3xl font-bold">{progressPercentage}%</span>
          </div>
          <div className="w-full bg-white/30 rounded-full h-4 mb-3">
            <div 
              className="bg-white rounded-full h-4 transition-all duration-500 ease-out shadow-lg"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <div className="flex justify-between text-sm opacity-90">
            <span>{completedTaskCount} / {totalTasks} görev tamamlandı</span>
            <span>⏱️ Tahmini Süre: 18-25 hafta</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-4 rounded-lg text-white">
            <h3 className="font-semibold mb-2">🎯 Kullanışlılık</h3>
            <p className="text-sm opacity-90">Sezgisel arayüz ve akıllı workflow</p>
          </div>
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-4 rounded-lg text-white">
            <h3 className="font-semibold mb-2">🎨 Estetik</h3>
            <p className="text-sm opacity-90">Modern ve profesyonel tasarım</p>
          </div>
          <div className="bg-gradient-to-r from-green-500 to-green-600 p-4 rounded-lg text-white">
            <h3 className="font-semibold mb-2">⚙️ İşlevsellik</h3>
            <p className="text-sm opacity-90">AI destekli akıllı algoritma</p>
          </div>
          <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 p-4 rounded-lg text-white">
            <h3 className="font-semibold mb-2">🧠 Zeka</h3>
            <p className="text-sm opacity-90">ML ve optimizasyon teknolojileri</p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {phases.map((phase) => {
          const phaseCompleted = completedPhases.has(phase.id);
          const phaseTasksCompleted = phase.tasks.filter(task => completedTasks.has(task.id)).length;
          const phaseProgress = Math.round((phaseTasksCompleted / phase.tasks.length) * 100);

          return (
            <div key={phase.id} className={`bg-white rounded-lg shadow-md border-l-4 ${phase.color} overflow-hidden transition-all duration-200 hover:shadow-lg`}>
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <button 
                      onClick={() => togglePhase(phase.id)}
                      className="flex items-center space-x-3 hover:bg-gray-50 p-2 rounded-lg transition-colors"
                    >
                      {phaseCompleted ? (
                        <CheckCircle className="w-6 h-6 text-green-500" />
                      ) : (
                        <Circle className="w-6 h-6 text-gray-400" />
                      )}
                      <div className="flex items-center space-x-3">
                        {phase.icon}
                        <div>
                          <h3 className="text-xl font-bold text-gray-800">{phase.title}</h3>
                          <p className="text-sm text-gray-600">{phase.focus}</p>
                        </div>
                      </div>
                    </button>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getPriorityColor(phase.priority)}`}>
                      {phase.priority}
                    </span>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-700">{phaseProgress}% tamamlandı</p>
                      <p className="text-xs text-gray-500 flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {phase.duration}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                  <div 
                    className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full h-2 transition-all duration-300"
                    style={{ width: `${phaseProgress}%` }}
                  />
                </div>

                <div className="space-y-2">
                  {phase.tasks.map((task) => {
                    const taskCompleted = completedTasks.has(task.id);
                    return (
                      <div key={task.id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                        <button 
                          onClick={() => toggleTask(task.id)}
                          className="flex items-center space-x-3 flex-1 text-left"
                        >
                          {taskCompleted ? (
                            <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                          ) : (
                            <Circle className="w-5 h-5 text-gray-400 flex-shrink-0" />
                          )}
                          <span className={`text-sm ${taskCompleted ? 'line-through text-gray-500' : 'text-gray-700'} transition-all`}>
                            {task.text}
                          </span>
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">🏗️ Teknoloji Yığını & Özellikler</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-700 border-b pb-2">Core Technologies</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Backend:</span><span className="font-medium">Python + Django + DRF</span></div>
              <div className="flex justify-between"><span>Frontend:</span><span className="font-medium">React + TypeScript</span></div>
              <div className="flex justify-between"><span>Database:</span><span className="font-medium">PostgreSQL + Redis</span></div>
              <div className="flex justify-between"><span>Styling:</span><span className="font-medium">Tailwind CSS</span></div>
            </div>
          </div>
          
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-700 border-b pb-2">AI & Optimization</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Algorithm:</span><span className="font-medium">Genetic Algorithm</span></div>
              <div className="flex justify-between"><span>ML Framework:</span><span className="font-medium">Scikit-learn</span></div>
              <div className="flex justify-between"><span>Optimization:</span><span className="font-medium">Multi-criteria Decision</span></div>
              <div className="flex justify-between"><span>Analytics:</span><span className="font-medium">Pandas + NumPy</span></div>
            </div>
          </div>
          
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-700 border-b pb-2">DevOps & Production</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Containerization:</span><span className="font-medium">Docker + K8s</span></div>
              <div className="flex justify-between"><span>CI/CD:</span><span className="font-medium">GitHub Actions</span></div>
              <div className="flex justify-between"><span>Monitoring:</span><span className="font-medium">Grafana + Prometheus</span></div>
              <div className="flex justify-between"><span>Cloud:</span><span className="font-medium">AWS/Azure</span></div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-emerald-50 to-blue-50 p-4 rounded-lg">
          <h4 className="font-bold text-gray-800 mb-3">🚀 Yeni Eklenen Özellikler</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong className="text-emerald-700">• AI-Powered Optimization:</strong> Genetik algoritma ile en iyi çizelge kombinasyonları
            </div>
            <div>
              <strong className="text-blue-700">• Workflow Management:</strong> Onay süreçleri ve otomatik bildirimler
            </div>
            <div>
              <strong className="text-purple-700">• Advanced Analytics:</strong> Veri analizi ve performance raporları
            </div>
            <div>
              <strong className="text-orange-700">• Template System:</strong> Hızlı kurulum için hazır şablonlar
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center space-x-2 text-yellow-800">
            <Clock className="w-5 h-5" />
            <span className="font-semibold">Toplam Tahmini Süre: 18-25 hafta (4.5-6 ay)</span>
          </div>
          <p className="text-sm text-yellow-700 mt-2">
            Bu roadmap gerçek dünya ihtiyaçlarına göre optimize edilmiştir ve endüstri standartlarında bir ders dağıtım sistemi geliştirecektir.
          </p>
        </div>
      </div>
    </div>
  );
};

export default EnhancedClassSchedulingRoadmap;