import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Users, 
  BookOpen, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp, 
  BarChart3, 
  Settings, 
  Moon, 
  Sun,
  Bell,
  Search,
  Filter,
  Download,
  Plus,
  Menu,
  X
} from 'lucide-react';

interface Stat {
  title: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

interface Activity {
  id: number;
  user: string;
  action: string;
  time: string;
}

interface Conflict {
  id: number;
  teacher: string;
  class: string;
  time: string;
  type: string;
}

const Dashboard: React.FC = () => {
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('overview');

  // Tema değişikliğini uygula
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Mock veriler
  const stats: Stat[] = [
    { title: 'Toplam Öğretmen', value: '42', icon: Users, color: 'bg-blue-500' },
    { title: 'Toplam Sınıf', value: '28', icon: BookOpen, color: 'bg-green-500' },
    { title: 'Aktif Çizelge', value: '2', icon: Calendar, color: 'bg-purple-500' },
    { title: 'Çakışma Sayısı', value: '3', icon: AlertTriangle, color: 'bg-red-500' },
  ];

  const recentActivities: Activity[] = [
    { id: 1, user: 'Ahmet Yılmaz', action: 'yeni çizelge oluşturdu', time: '2 dakika önce' },
    { id: 2, user: 'Ayşe Kaya', action: 'çizelge güncelledi', time: '15 dakika önce' },
    { id: 3, user: 'Mehmet Demir', action: 'çakışma çözdü', time: '1 saat önce' },
  ];

  const scheduleConflicts: Conflict[] = [
    { id: 1, teacher: 'Dr. Ali Veli', class: 'A101', time: 'Pazartesi 09:00', type: 'Sınıf Çakışması' },
    { id: 2, teacher: 'Prof. Ayşe Can', class: 'B205', time: 'Salı 10:00', type: 'Öğretmen Çakışması' },
    { id: 3, teacher: 'Doç. Mehmet Öz', class: 'C301', time: 'Çarşamba 11:00', type: 'Zaman Kısıtlaması' },
  ];

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      {/* Header */}
      <header className={`${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b`}>
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden mr-2 p-2 rounded-md text-gray-500 hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-700 dark:hover:text-white"
              >
                {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
              <div className="flex-shrink-0 flex items-center">
                <BookOpen className="h-8 w-8 text-indigo-600" />
                <span className="ml-2 text-xl font-bold">Ders Dağıtımı</span>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className="relative mr-4">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Ara..."
                  className={`pl-10 pr-4 py-2 rounded-lg border ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  } focus:ring-2 focus:ring-indigo-500 focus:border-transparent`}
                />
              </div>
              
              <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 mr-2">
                <Bell className="h-6 w-6 text-gray-500" />
              </button>
              
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {darkMode ? <Sun className="h-6 w-6 text-yellow-400" /> : <Moon className="h-6 w-6 text-gray-700" />}
              </button>
              
              <div className="ml-4 flex items-center">
                <div className="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center text-white font-semibold">
                  A
                </div>
                <span className="ml-2 hidden md:block">Admin</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside 
          className={`${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } md:translate-x-0 fixed md:static inset-y-0 left-0 z-30 w-64 ${
            darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
          } border-r transition-transform duration-300 ease-in-out`}
        >
          <div className="flex flex-col h-full">
            <nav className="flex-1 px-2 py-4 space-y-1">
              {[
                { id: 'overview', name: 'Genel Bakış', icon: BarChart3 },
                { id: 'schedules', name: 'Çizelgeler', icon: Calendar },
                { id: 'teachers', name: 'Öğretmenler', icon: Users },
                { id: 'classes', name: 'Sınıflar', icon: BookOpen },
                { id: 'conflicts', name: 'Çakışmalar', icon: AlertTriangle },
                { id: 'reports', name: 'Raporlar', icon: TrendingUp },
                { id: 'settings', name: 'Ayarlar', icon: Settings },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg w-full ${
                    activeTab === item.id
                      ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-100'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </button>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 pb-8">
          <div className="px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-6">
              <h1 className="text-2xl font-bold">Dashboard</h1>
              <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                Sistem durumu ve son aktiviteler
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat, index) => (
                <div 
                  key={index}
                  className={`rounded-xl shadow ${
                    darkMode ? 'bg-gray-800' : 'bg-white'
                  } p-6`}
                >
                  <div className="flex items-center">
                    <div className={`${stat.color} p-3 rounded-lg`}>
                      <stat.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-4">
                      <p className={`text-sm font-medium ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        {stat.title}
                      </p>
                      <p className="text-2xl font-bold">{stat.value}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Charts and Activities */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Activities */}
              <div className={`rounded-xl shadow ${
                darkMode ? 'bg-gray-800' : 'bg-white'
              } p-6 lg:col-span-1`}>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Son Aktiviteler</h2>
                  <Filter className="h-5 w-5 text-gray-500" />
                </div>
                <div className="space-y-4">
                  {recentActivities.map((activity) => (
                    <div key={activity.id} className="flex items-start">
                      <div className="flex-shrink-0">
                        <div className="h-8 w-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
                          <Users className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                        </div>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium">
                          <span className="font-semibold">{activity.user}</span> {activity.action}
                        </p>
                        <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                          {activity.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Schedule Conflicts */}
              <div className={`rounded-xl shadow ${
                darkMode ? 'bg-gray-800' : 'bg-white'
              } p-6 lg:col-span-2`}>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Aktif Çakışmalar</h2>
                  <div className="flex space-x-2">
                    <Download className="h-5 w-5 text-gray-500" />
                    <Plus className="h-5 w-5 text-gray-500" />
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead>
                      <tr>
                        <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                          darkMode ? 'text-gray-300' : 'text-gray-500'
                        }`}>
                          Öğretmen
                        </th>
                        <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                          darkMode ? 'text-gray-300' : 'text-gray-500'
                        }`}>
                          Sınıf
                        </th>
                        <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                          darkMode ? 'text-gray-300' : 'text-gray-500'
                        }`}>
                          Zaman
                        </th>
                        <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                          darkMode ? 'text-gray-300' : 'text-gray-500'
                        }`}>
                          Tür
                        </th>
                        <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                          darkMode ? 'text-gray-300' : 'text-gray-500'
                        }`}>
                          İşlem
                        </th>
                      </tr>
                    </thead>
                    <tbody className={`divide-y divide-gray-200 dark:divide-gray-700 ${
                      darkMode ? 'bg-gray-800' : 'bg-white'
                    }`}>
                      {scheduleConflicts.map((conflict) => (
                        <tr key={conflict.id}>
                          <td className="px-4 py-4 whitespace-nowrap text-sm font-medium">
                            {conflict.teacher}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm">
                            {conflict.class}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm">
                            {conflict.time}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              conflict.type === 'Sınıf Çakışması' 
                                ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
                                : conflict.type === 'Öğretmen Çakışması'
                                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
                                : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                            }`}>
                              {conflict.type}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm">
                            <button className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">
                              Çöz
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;