import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  PieChart, 
  TrendingUp, 
  Users, 
  BookOpen, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  Download,
  Filter,
  Calendar,
  User,
  Building
} from 'lucide-react';

// Mock veriler
const mockScheduleData = {
  utilizationRates: [
    { classroom: 'A101', rate: 85, capacity: 30 },
    { classroom: 'B205', rate: 92, capacity: 50 },
    { classroom: 'C301', rate: 78, capacity: 25 },
    { classroom: 'D102', rate: 95, capacity: 40 },
    { classroom: 'E201', rate: 68, capacity: 35 },
  ],
  teacherWorkload: [
    { teacher: 'Ahmet Yılmaz', workload: 28, maxHours: 40 },
    { teacher: 'Ayşe Kaya', workload: 35, maxHours: 40 },
    { teacher: 'Mehmet Demir', workload: 22, maxHours: 30 },
    { teacher: 'Elif Çelik', workload: 38, maxHours: 40 },
    { teacher: 'Fatma Şahin', workload: 15, maxHours: 25 },
  ],
  conflictsByDay: [
    { day: 'Pazartesi', conflicts: 3 },
    { day: 'Salı', conflicts: 1 },
    { day: 'Çarşamba', conflicts: 2 },
    { day: 'Perşembe', conflicts: 0 },
    { day: 'Cuma', conflicts: 4 },
  ],
  courseDistribution: [
    { course: 'Matematik', count: 15 },
    { course: 'Fizik', count: 12 },
    { course: 'Kimya', count: 10 },
    { course: 'Biyoloji', count: 8 },
    { course: 'İngilizce', count: 6 },
  ]
};

const AnalyticsDashboard: React.FC = () => {
  const [dateRange, setDateRange] = useState({ start: '2023-09-01', end: '2023-09-30' });
  const [department, setDepartment] = useState('all');
  const [activeTab, setActiveTab] = useState('overview');

  // Veri hesaplama fonksiyonları
  const calculateAverageUtilization = () => {
    const rates = mockScheduleData.utilizationRates.map(item => item.rate);
    return rates.reduce((sum, rate) => sum + rate, 0) / rates.length;
  };

  const calculateTotalConflicts = () => {
    return mockScheduleData.conflictsByDay.reduce((sum, day) => sum + day.conflicts, 0);
  };

  const calculateTeacherSatisfaction = () => {
    const workloads = mockScheduleData.teacherWorkload.map(teacher => 
      (teacher.workload / teacher.maxHours) * 100
    );
    
    // Memnuniyet skoru: %70-%100 arası iyi, %40-%70 arası orta, %0-%40 arası düşük
    const satisfactionScores = workloads.map(workload => {
      if (workload <= 40) return 85; // Düşük iş yükü = yüksek memnuniyet
      if (workload <= 70) return 75; // Orta iş yükü = orta memnuniyet
      if (workload <= 100) return 60; // Yüksek iş yükü = düşük memnuniyet
      return 40; // Çok yüksek iş yükü = çok düşük memnuniyet
    });
    
    return satisfactionScores.reduce((sum, score) => sum + score, 0) / satisfactionScores.length;
  };

  // Grafik bileşenleri
  const BarChartComponent = ({ data, xAxis, yAxis }: any) => (
    <div className="h-64">
      <svg viewBox="0 0 400 200" className="w-full h-full">
        {data.map((item: any, index: number) => {
          const barHeight = (item[yAxis] / Math.max(...data.map((d: any) => d[yAxis]))) * 150;
          const x = (index * 350) / data.length + 25;
          
          return (
            <g key={index}>
              <rect
                x={x}
                y={180 - barHeight}
                width={20}
                height={barHeight}
                fill="#4F46E5"
                rx="2"
              />
              <text
                x={x + 10}
                y={195}
                textAnchor="middle"
                fontSize="10"
                fill="#6B7280"
              >
                {item[xAxis]}
              </text>
              <text
                x={x + 10}
                y={175 - barHeight}
                textAnchor="middle"
                fontSize="10"
                fill="#4F46E5"
              >
                {item[yAxis]}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );

  const PieChartComponent = ({ data, labelKey, valueKey }: any) => {
    const total = data.reduce((sum: number, item: any) => sum + item[valueKey], 0);
    let startAngle = 0;
    
    const colors = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
    
    return (
      <div className="h-64">
        <svg viewBox="0 0 200 200" className="w-full h-full">
          {data.map((item: any, index: number) => {
            const percentage = (item[valueKey] / total) * 100;
            const angle = (percentage / 100) * 360;
            const endAngle = startAngle + angle;
            
            // SVG arc path hesaplama
            const startX = 100 + 80 * Math.cos((Math.PI / 180) * (startAngle - 90));
            const startY = 100 + 80 * Math.sin((Math.PI / 180) * (startAngle - 90));
            const endX = 100 + 80 * Math.cos((Math.PI / 180) * (endAngle - 90));
            const endY = 100 + 80 * Math.sin((Math.PI / 180) * (endAngle - 90));
            
            const largeArcFlag = angle > 180 ? 1 : 0;
            
            const pathData = [
              `M 100 100`,
              `L ${startX} ${startY}`,
              `A 80 80 0 ${largeArcFlag} 1 ${endX} ${endY}`,
              'Z'
            ].join(' ');
            
            const color = colors[index % colors.length];
            startAngle = endAngle;
            
            return (
              <g key={index}>
                <path
                  d={pathData}
                  fill={color}
                  stroke="#FFFFFF"
                  strokeWidth="2"
                />
                <text
                  x={100 + 60 * Math.cos((Math.PI / 180) * (startAngle - angle/2 - 90))}
                  y={100 + 60 * Math.sin((Math.PI / 180) * (startAngle - angle/2 - 90))}
                  textAnchor="middle"
                  fontSize="8"
                  fill="#FFFFFF"
                  fontWeight="bold"
                >
                  {Math.round(percentage)}%
                </text>
              </g>
            );
          })}
          {data.map((item: any, index: number) => (
            <text
              key={`label-${index}`}
              x={10}
              y={20 + index * 15}
              fontSize="10"
              fill="#6B7280"
            >
              <tspan fontWeight="bold" fill={colors[index % colors.length]}>
                ■
              </tspan> {item[labelKey]} ({item[valueKey]})
            </text>
          ))}
        </svg>
      </div>
    );
  };

  // Rapor dışa aktarma
  const exportReport = (format: 'pdf' | 'excel') => {
    alert(`${format.toUpperCase()} formatında rapor dışa aktarılıyor...`);
    // Gerçek uygulamada burada dışa aktarma işlemi yapılacak
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Analiz Dashboard'u</h1>
          <div className="flex space-x-2">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm"
              />
              <span>-</span>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm"
              />
            </div>
            
            <select 
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">Tüm Departmanlar</option>
              <option value="math">Matematik</option>
              <option value="physics">Fizik</option>
              <option value="chemistry">Kimya</option>
              <option value="biology">Biyoloji</option>
            </select>
            
            <button 
              onClick={() => exportReport('pdf')}
              className="flex items-center px-3 py-1 bg-red-600 text-white rounded-md text-sm hover:bg-red-700"
            >
              <Download className="w-4 h-4 mr-1" />
              PDF
            </button>
            
            <button 
              onClick={() => exportReport('excel')}
              className="flex items-center px-3 py-1 bg-green-600 text-white rounded-md text-sm hover:bg-green-700"
            >
              <Download className="w-4 h-4 mr-1" />
              Excel
            </button>
          </div>
        </div>
      </div>

      {/* KPI Kartları */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <Building className="w-6 h-6 text-indigo-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Ort. Sınıf Kullanımı</p>
              <p className="text-2xl font-bold">{calculateAverageUtilization().toFixed(1)}%</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Öğretmen Memnuniyeti</p>
              <p className="text-2xl font-bold">{calculateTeacherSatisfaction().toFixed(1)}%</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Toplam Çakışma</p>
              <p className="text-2xl font-bold">{calculateTotalConflicts()}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Verimlilik Oranı</p>
              <p className="text-2xl font-bold">92%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sekmeler */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Genel Bakış', icon: BarChart },
              { id: 'classrooms', name: 'Sınıf Kullanımı', icon: Building },
              { id: 'teachers', name: 'Öğretmen Yükü', icon: Users },
              { id: 'courses', name: 'Ders Dağılımı', icon: BookOpen },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Grafikler */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {activeTab === 'overview' && (
          <>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Sınıf Kullanım Oranları</h3>
              <BarChartComponent 
                data={mockScheduleData.utilizationRates} 
                xAxis="classroom" 
                yAxis="rate" 
              />
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Ders Dağılımı</h3>
              <PieChartComponent 
                data={mockScheduleData.courseDistribution} 
                labelKey="course" 
                valueKey="count" 
              />
            </div>
            
            <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Günlük Çakışma Sayıları</h3>
              <BarChartComponent 
                data={mockScheduleData.conflictsByDay} 
                xAxis="day" 
                yAxis="conflicts" 
              />
            </div>
          </>
        )}
        
        {activeTab === 'classrooms' && (
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Detaylı Sınıf Kullanımı</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sınıf
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Kapasite
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Kullanım (%)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Kullanım (Saat)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Boşluk
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {mockScheduleData.utilizationRates.map((classroom, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {classroom.classroom}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {classroom.capacity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className="bg-indigo-600 h-2 rounded-full" 
                              style={{ width: `${classroom.rate}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-900">{classroom.rate}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {Math.round((classroom.rate / 100) * 40)} saat
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {Math.round(((100 - classroom.rate) / 100) * 40)} saat
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
        
        {activeTab === 'teachers' && (
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Öğretmen İş Yükü Analizi</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Öğretmen
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Atanan Saat
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Maksimum Saat
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Yük (%)</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Memnuniyet Tahmini
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {mockScheduleData.teacherWorkload.map((teacher, index) => {
                    const workloadPercentage = (teacher.workload / teacher.maxHours) * 100;
                    const satisfaction = workloadPercentage <= 40 ? 'Yüksek' : 
                                          workloadPercentage <= 70 ? 'Orta' : 'Düşük';
                    
                    return (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {teacher.teacher}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {teacher.workload} saat
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {teacher.maxHours} saat
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  workloadPercentage <= 40 ? 'bg-green-600' : 
                                  workloadPercentage <= 70 ? 'bg-yellow-500' : 'bg-red-600'
                                }`} 
                                style={{ width: `${workloadPercentage}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-900">{workloadPercentage.toFixed(1)}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            workloadPercentage <= 40 ? 'bg-green-100 text-green-800' : 
                            workloadPercentage <= 70 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {satisfaction}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
        
        {activeTab === 'courses' && (
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ders Dağılımı ve Talep Analizi</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ders
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Atanan Grup Sayısı
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ortalama Öğrenci Sayısı
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Talep Doygunluğu
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {mockScheduleData.courseDistribution.map((course, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {course.course}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {course.count} grup
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {Math.round(course.count * 25)} öğrenci
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${(course.count / 20) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-900">
                            {Math.round((course.count / 20) * 100)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;