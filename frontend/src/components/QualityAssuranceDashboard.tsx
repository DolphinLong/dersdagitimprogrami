import React, { useState } from 'react';
import { 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Users, 
  Cpu, 
  Database,
  Wifi,
  Lock,
  Key,
  Settings,
  Play,
  Pause,
  RotateCcw,
  Download,
  Filter,
  Search
} from 'lucide-react';

// Mock test verileri
const mockTestResults = [
  {
    id: 1,
    name: 'Unit Test Suite',
    category: 'unit',
    status: 'passed',
    passed: 1247,
    failed: 0,
    skipped: 23,
    duration: '12.4s',
    lastRun: '2023-08-15T10:30:00Z',
    coverage: 92.5
  },
  {
    id: 2,
    name: 'Integration Tests',
    category: 'integration',
    status: 'failed',
    passed: 89,
    failed: 3,
    skipped: 2,
    duration: '45.2s',
    lastRun: '2023-08-15T11:15:00Z',
    coverage: 78.3
  },
  {
    id: 3,
    name: 'End-to-End Tests',
    category: 'e2e',
    status: 'running',
    passed: 15,
    failed: 0,
    skipped: 0,
    duration: '8.7s',
    lastRun: '2023-08-15T12:00:00Z',
    coverage: 0
  },
  {
    id: 4,
    name: 'Performance Tests',
    category: 'performance',
    status: 'passed',
    passed: 23,
    failed: 0,
    skipped: 0,
    duration: '18.3s',
    lastRun: '2023-08-15T09:45:00Z',
    coverage: 0
  },
  {
    id: 5,
    name: 'Security Tests',
    category: 'security',
    status: 'passed',
    passed: 45,
    failed: 0,
    skipped: 5,
    duration: '32.1s',
    lastRun: '2023-08-15T10:00:00Z',
    coverage: 0
  }
];

const mockFailedTests = [
  {
    id: 101,
    testName: 'TeacherAvailabilityTest',
    testSuite: 'Integration Tests',
    errorMessage: 'Teacher availability check failed for overlapping schedules',
    filePath: 'tests/integration/teacher.test.ts',
    lineNumber: 142,
    failureType: 'logic',
    severity: 'high',
    assignedTo: 'Ahmet Yılmaz'
  },
  {
    id: 102,
    testName: 'ClassroomCapacityValidation',
    testSuite: 'Integration Tests',
    errorMessage: 'Classroom capacity exceeded in schedule assignment',
    filePath: 'tests/integration/classroom.test.ts',
    lineNumber: 87,
    failureType: 'validation',
    severity: 'medium',
    assignedTo: 'Ayşe Kaya'
  }
];

const QualityAssuranceDashboard: React.FC = () => {
  const [testResults, setTestResults] = useState(mockTestResults);
  const [failedTests, setFailedTests] = useState(mockFailedTests);
  const [selectedTest, setSelectedTest] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  // Filtrelenmiş test sonuçları
  const filteredTestResults = testResults.filter(test => {
    const categoryMatch = filterCategory === 'all' || test.category === filterCategory;
    const statusMatch = filterStatus === 'all' || test.status === filterStatus;
    return categoryMatch && statusMatch;
  });

  // Test istatistikleri
  const testStats = {
    total: testResults.length,
    passed: testResults.filter(t => t.status === 'passed').length,
    failed: testResults.filter(t => t.status === 'failed').length,
    running: testResults.filter(t => t.status === 'running').length,
    coverage: testResults.reduce((sum, test) => sum + test.coverage, 0) / testResults.length
  };

  // Test çalıştırma
  const runTest = (testId: number) => {
    setTestResults(prev => 
      prev.map(test => 
        test.id === testId 
          ? { ...test, status: 'running', duration: '0.0s' } 
          : test
      )
    );
    
    // Mock test çalıştırma (gerçek uygulamada async olurdu)
    setTimeout(() => {
      setTestResults(prev => 
        prev.map(test => {
          if (test.id === testId) {
            // Mock sonuç
            const isSuccess = Math.random() > 0.3;
            return {
              ...test,
              status: isSuccess ? 'passed' : 'failed',
              duration: (Math.random() * 10).toFixed(1) + 's',
              lastRun: new Date().toISOString()
            };
          }
          return test;
        })
      );
    }, 2000);
  };

  // Tüm testleri çalıştır
  const runAllTests = () => {
    testResults.forEach(test => runTest(test.id));
  };

  // Testi yeniden çalıştır
  const rerunTest = (testId: number) => {
    runTest(testId);
  };

  // Test atama
  const assignTest = (testId: number, assignee: string) => {
    setFailedTests(prev => 
      prev.map(test => 
        test.id === testId 
          ? { ...test, assignedTo: assignee } 
          : test
      )
    );
  };

  // Tarih formatlama
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR') + ' ' + date.toLocaleTimeString('tr-TR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Durum rengi
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'running': return 'bg-yellow-100 text-yellow-800';
      case 'pending': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Kategori rengi
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'unit': return 'bg-blue-100 text-blue-800';
      case 'integration': return 'bg-purple-100 text-purple-800';
      case 'e2e': return 'bg-indigo-100 text-indigo-800';
      case 'performance': return 'bg-orange-100 text-orange-800';
      case 'security': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Modal işlemleri
  const openModal = (test: any) => {
    setSelectedTest(test);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedTest(null);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Kalite Güvence Dashboard'u</h1>
          <div className="flex space-x-2">
            <button 
              onClick={runAllTests}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Play className="w-4 h-4 mr-2" />
              Tüm Testleri Çalıştır
            </button>
            
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Test ara..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            
            <select 
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">Tüm Kategoriler</option>
              <option value="unit">Unit Test</option>
              <option value="integration">Integration</option>
              <option value="e2e">End-to-End</option>
              <option value="performance">Performance</option>
              <option value="security">Security</option>
            </select>
            
            <select 
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">Tüm Durumlar</option>
              <option value="passed">Geçti</option>
              <option value="failed">Başarısız</option>
              <option value="running">Çalışıyor</option>
            </select>
          </div>
        </div>
      </div>

      {/* Test İstatistikleri */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <Shield className="w-6 h-6 text-indigo-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Toplam Test</p>
              <p className="text-2xl font-bold">{testStats.total}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Geçen Test</p>
              <p className="text-2xl font-bold">{testStats.passed}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-red-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Başarısız Test</p>
              <p className="text-2xl font-bold">{testStats.failed}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Çalışan Test</p>
              <p className="text-2xl font-bold">{testStats.running}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Kod Kapsamı</p>
              <p className="text-2xl font-bold">{testStats.coverage.toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Test Sonuçları Tablosu */}
      <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Test Sonuçları</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Test Adı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Kategori
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Durum
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Geçen/Toplam
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Süre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Kod Kapsamı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Son Çalıştırma
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  İşlem
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTestResults.map((test) => (
                <tr key={test.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{test.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getCategoryColor(test.category)}`}>
                      {test.category === 'unit' && 'Unit Test'}
                      {test.category === 'integration' && 'Integration'}
                      {test.category === 'e2e' && 'End-to-End'}
                      {test.category === 'performance' && 'Performance'}
                      {test.category === 'security' && 'Security'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(test.status)}`}>
                      {test.status === 'passed' && 'Geçti'}
                      {test.status === 'failed' && 'Başarısız'}
                      {test.status === 'running' && 'Çalışıyor'}
                      {test.status === 'pending' && 'Beklemede'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                      <span>{test.passed}</span>
                      <span className="mx-1">/</span>
                      <span>{test.passed + test.failed + test.skipped}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.duration}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {test.coverage > 0 && (
                      <div className="flex items-center">
                        <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${test.coverage}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-900">{test.coverage.toFixed(1)}%</span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(test.lastRun)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => runTest(test.id)}
                      className="text-indigo-600 hover:text-indigo-900 mr-3"
                      disabled={test.status === 'running'}
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => rerunTest(test.id)}
                      className="text-green-600 hover:text-green-900 mr-3"
                      disabled={test.status === 'running'}
                    >
                      <RotateCcw className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => openModal(test)}
                      className="text-gray-600 hover:text-gray-900"
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Başarısız Testler */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Başarısız Testler</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Test Adı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Test Suite
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hata Mesajı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dosya
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Satır
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Atanan Kişi
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  İşlem
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {failedTests.map((test) => (
                <tr key={test.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{test.testName}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.testSuite}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate" title={test.errorMessage}>
                      {test.errorMessage}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.filePath}:{test.lineNumber}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.lineNumber}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.assignedTo}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => assignTest(test.id, 'Mehmet Demir')}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Ata
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && selectedTest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">
                {selectedTest.name} Detayları
              </h3>
              <button 
                onClick={closeModal}
                className="p-2 rounded-full hover:bg-gray-100"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Kategori</h4>
                  <p className="text-sm font-medium">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getCategoryColor(selectedTest.category)}`}>
                      {selectedTest.category}
                    </span>
                  </p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Durum</h4>
                  <p className="text-sm font-medium">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(selectedTest.status)}`}>
                      {selectedTest.status}
                    </span>
                  </p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Süre</h4>
                  <p className="text-sm font-medium">{selectedTest.duration}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Son Çalıştırma</h4>
                  <p className="text-sm font-medium">{formatDate(selectedTest.lastRun)}</p>
                </div>
              </div>
              
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-500 mb-2">Test İstatistikleri</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-green-50 p-3 rounded-lg">
                    <div className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                      <span className="text-sm font-medium">Geçen</span>
                    </div>
                    <p className="text-xl font-bold mt-1">{selectedTest.passed}</p>
                  </div>
                  <div className="bg-red-50 p-3 rounded-lg">
                    <div className="flex items-center">
                      <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
                      <span className="text-sm font-medium">Başarısız</span>
                    </div>
                    <p className="text-xl font-bold mt-1">{selectedTest.failed}</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="flex items-center">
                      <Pause className="w-5 h-5 text-gray-500 mr-2" />
                      <span className="text-sm font-medium">Atlandı</span>
                    </div>
                    <p className="text-xl font-bold mt-1">{selectedTest.skipped}</p>
                  </div>
                </div>
              </div>
              
              {selectedTest.coverage > 0 && (
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Kod Kapsamı</h4>
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-blue-600 h-3 rounded-full" 
                        style={{ width: `${selectedTest.coverage}%` }}
                      ></div>
                    </div>
                    <span className="ml-3 text-sm font-medium">{selectedTest.coverage.toFixed(1)}%</span>
                  </div>
                </div>
              )}
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Kapat
                </button>
                <button
                  onClick={() => runTest(selectedTest.id)}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center"
                  disabled={selectedTest.status === 'running'}
                >
                  {selectedTest.status === 'running' ? (
                    <Clock className="w-4 h-4 mr-2" />
                  ) : (
                    <Play className="w-4 h-4 mr-2" />
                  )}
                  {selectedTest.status === 'running' ? 'Çalışıyor...' : 'Testi Çalıştır'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QualityAssuranceDashboard;