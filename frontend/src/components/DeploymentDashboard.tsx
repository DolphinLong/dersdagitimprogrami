import React, { useState } from 'react';
import { 
  Server, 
  Globe, 
  Database, 
  Shield, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Users, 
  Settings,
  Play,
  Pause,
  RotateCcw,
  Download,
  Upload,
  Filter,
  Search,
  Bell,
  Mail,
  Phone,
  Terminal,
  Lock,
  Key,
  Wifi,
  Cpu
} from 'lucide-react';

// Mock production verileri
const mockEnvironments = [
  {
    id: 1,
    name: 'Development',
    status: 'running',
    url: 'https://dev.dersdagitim.local',
    version: '1.0.0-beta.1',
    lastDeploy: '2023-08-15T10:30:00Z',
    uptime: '99.98%',
    cpu: 12,
    memory: 35,
    disk: 42
  },
  {
    id: 2,
    name: 'Staging',
    status: 'running',
    url: 'https://staging.dersdagitim.com',
    version: '1.0.0-rc.3',
    lastDeploy: '2023-08-14T15:45:00Z',
    uptime: '99.95%',
    cpu: 28,
    memory: 52,
    disk: 68
  },
  {
    id: 3,
    name: 'Production',
    status: 'running',
    url: 'https://dersdagitim.com',
    version: '1.0.0',
    lastDeploy: '2023-08-10T09:15:00Z',
    uptime: '99.99%',
    cpu: 45,
    memory: 68,
    disk: 75
  }
];

const mockServices = [
  {
    id: 1,
    name: 'Web Application',
    status: 'healthy',
    instances: 3,
    cpu: 32,
    memory: 58,
    requests: 1247,
    errors: 3
  },
  {
    id: 2,
    name: 'API Gateway',
    status: 'healthy',
    instances: 2,
    cpu: 18,
    memory: 42,
    requests: 9856,
    errors: 12
  },
  {
    id: 3,
    name: 'Database',
    status: 'warning',
    instances: 1,
    cpu: 65,
    memory: 82,
    requests: 15623,
    errors: 0
  },
  {
    id: 4,
    name: 'Redis Cache',
    status: 'healthy',
    instances: 2,
    cpu: 12,
    memory: 28,
    requests: 45689,
    errors: 0
  }
];

const mockIncidents = [
  {
    id: 101,
    title: 'High CPU Usage on Database Server',
    severity: 'high',
    status: 'resolved',
    startTime: '2023-08-15T08:22:00Z',
    endTime: '2023-08-15T09:45:00Z',
    assignedTo: 'Mehmet Demir',
    description: 'Database server CPU usage exceeded 90% threshold due to complex query optimization issues.'
  },
  {
    id: 102,
    title: 'API Gateway Timeout Issues',
    severity: 'medium',
    status: 'investigating',
    startTime: '2023-08-15T11:30:00Z',
    endTime: null,
    assignedTo: 'Ahmet Yılmaz',
    description: 'Intermittent timeout issues affecting 5% of API requests, possibly related to downstream service latency.'
  }
];

const DeploymentDashboard: React.FC = () => {
  const [environments, setEnvironments] = useState(mockEnvironments);
  const [services, setServices] = useState(mockServices);
  const [incidents, setIncidents] = useState(mockIncidents);
  const [selectedEnv, setSelectedEnv] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');

  // Ortam durumu rengi
  const getEnvStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800';
      case 'stopped': return 'bg-red-100 text-red-800';
      case 'maintenance': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Servis durumu rengi
  const getServiceStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Olay önem derecesi rengi
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Olay durumu rengi
  const getIncidentStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-red-100 text-red-800';
      case 'investigating': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'monitoring': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Ortam başlatma
  const startEnvironment = (envId: number) => {
    setEnvironments(prev => 
      prev.map(env => 
        env.id === envId 
          ? { ...env, status: 'running' } 
          : env
      )
    );
  };

  // Ortam durdurma
  const stopEnvironment = (envId: number) => {
    setEnvironments(prev => 
      prev.map(env => 
        env.id === envId 
          ? { ...env, status: 'stopped' } 
          : env
      )
    );
  };

  // Deployment yapma
  const deployEnvironment = (envId: number) => {
    setEnvironments(prev => 
      prev.map(env => {
        if (env.id === envId) {
          return {
            ...env,
            status: 'deploying',
            lastDeploy: new Date().toISOString()
          };
        }
        return env;
      })
    );
    
    // Mock deployment (gerçek uygulamada async olurdu)
    setTimeout(() => {
      setEnvironments(prev => 
        prev.map(env => {
          if (env.id === envId) {
            return {
              ...env,
              status: 'running',
              version: env.version.includes('-beta') 
                ? env.version.replace('-beta', '') 
                : env.version.includes('-rc') 
                  ? env.version.replace('-rc', '') 
                  : env.version + '.1'
            };
          }
          return env;
        })
      );
    }, 3000);
  };

  // Servis yeniden başlatma
  const restartService = (serviceId: number) => {
    setServices(prev => 
      prev.map(service => 
        service.id === serviceId 
          ? { ...service, status: 'restarting' } 
          : service
      )
    );
    
    // Mock restart (gerçek uygulamada async olurdu)
    setTimeout(() => {
      setServices(prev => 
        prev.map(service => {
          if (service.id === serviceId) {
            return {
              ...service,
              status: 'healthy',
              cpu: Math.floor(Math.random() * 20),
              memory: Math.floor(Math.random() * 30) + 30
            };
          }
          return service;
        })
      );
    }, 2000);
  };

  // Olay çözme
  const resolveIncident = (incidentId: number) => {
    setIncidents(prev => 
      prev.map(incident => 
        incident.id === incidentId 
          ? { 
              ...incident, 
              status: 'resolved',
              endTime: new Date().toISOString()
            } 
          : incident
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

  // Süre hesaplama
  const calculateDuration = (start: string, end: string | null) => {
    if (!end) return 'Devam ediyor';
    
    const startDate = new Date(start);
    const endDate = new Date(end);
    const diffMs = endDate.getTime() - startDate.getTime();
    
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours} saat ${minutes} dakika`;
    }
    return `${minutes} dakika`;
  };

  // Modal işlemleri
  const openModal = (env: any) => {
    setSelectedEnv(env);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedEnv(null);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Deployment & Production Dashboard</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => deployEnvironment(2)}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              <Upload className="w-4 h-4 mr-2" />
              Staging'e Deploy Et
            </button>
            
            <button 
              onClick={() => deployEnvironment(3)}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Play className="w-4 h-4 mr-2" />
              Production'a Deploy Et
            </button>
            
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Ara..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            
            <select 
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">Tüm Durumlar</option>
              <option value="running">Çalışıyor</option>
              <option value="stopped">Durduruldu</option>
              <option value="maintenance">Bakımda</option>
            </select>
          </div>
        </div>
      </div>

      {/* Ortam İstatistikleri */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {environments.map(env => (
          <div key={env.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{env.name}</h3>
                <a 
                  href={env.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  {env.url.replace('https://', '')}
                </a>
              </div>
              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getEnvStatusColor(env.status)}`}>
                {env.status === 'running' && 'Çalışıyor'}
                {env.status === 'stopped' && 'Durduruldu'}
                {env.status === 'maintenance' && 'Bakımda'}
                {env.status === 'deploying' && 'Deploy Ediliyor'}
              </span>
            </div>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Versiyon</span>
                  <span className="font-medium">{env.version}</span>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Son Deploy</span>
                  <span className="font-medium">{formatDate(env.lastDeploy)}</span>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Uptime</span>
                  <span className="font-medium">{env.uptime}</span>
                </div>
              </div>
              
              <div>
                <div className="text-sm text-gray-500 mb-1">Kaynak Kullanımı</div>
                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>CPU</span>
                      <span>{env.cpu}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className={`h-1.5 rounded-full ${
                          env.cpu > 80 ? 'bg-red-500' : 
                          env.cpu > 60 ? 'bg-yellow-500' : 'bg-green-500'
                        }`} 
                        style={{ width: `${env.cpu}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Bellek</span>
                      <span>{env.memory}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className={`h-1.5 rounded-full ${
                          env.memory > 80 ? 'bg-red-500' : 
                          env.memory > 60 ? 'bg-yellow-500' : 'bg-green-500'
                        }`} 
                        style={{ width: `${env.memory}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Disk</span>
                      <span>{env.disk}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className={`h-1.5 rounded-full ${
                          env.disk > 80 ? 'bg-red-500' : 
                          env.disk > 60 ? 'bg-yellow-500' : 'bg-green-500'
                        }`} 
                        style={{ width: `${env.disk}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-2 pt-2">
                {env.status === 'running' ? (
                  <button
                    onClick={() => stopEnvironment(env.id)}
                    className="flex-1 flex items-center justify-center px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                  >
                    <Pause className="w-3 h-3 mr-1" />
                    Durdur
                  </button>
                ) : (
                  <button
                    onClick={() => startEnvironment(env.id)}
                    className="flex-1 flex items-center justify-center px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                  >
                    <Play className="w-3 h-3 mr-1" />
                    Başlat
                  </button>
                )}
                
                <button
                  onClick={() => deployEnvironment(env.id)}
                  className="flex-1 flex items-center justify-center px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
                  disabled={env.status === 'deploying'}
                >
                  <Upload className="w-3 h-3 mr-1" />
                  Deploy
                </button>
                
                <button
                  onClick={() => openModal(env)}
                  className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                >
                  <Settings className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Servis Durumu */}
      <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Servis Durumu</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Servis Adı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Durum
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Instance Sayısı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CPU Kullanımı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Bellek Kullanımı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  İstek/Saniye
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hatalar
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  İşlem
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {services.map(service => (
                <tr key={service.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Server className="w-5 h-5 text-gray-400 mr-2" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{service.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getServiceStatusColor(service.status)}`}>
                      {service.status === 'healthy' && 'Sağlıklı'}
                      {service.status === 'warning' && 'Uyarı'}
                      {service.status === 'critical' && 'Kritik'}
                      {service.status === 'restarting' && 'Yeniden Başlatılıyor'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {service.instances}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className={`h-2 rounded-full ${
                            service.cpu > 80 ? 'bg-red-500' : 
                            service.cpu > 60 ? 'bg-yellow-500' : 'bg-green-500'
                          }`} 
                          style={{ width: `${service.cpu}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">{service.cpu}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className={`h-2 rounded-full ${
                            service.memory > 80 ? 'bg-red-500' : 
                            service.memory > 60 ? 'bg-yellow-500' : 'bg-green-500'
                          }`} 
                          style={{ width: `${service.memory}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">{service.memory}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {service.requests}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={service.errors > 0 ? 'text-red-600 font-medium' : 'text-gray-500'}>
                      {service.errors}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => restartService(service.id)}
                      className="text-indigo-600 hover:text-indigo-900"
                      disabled={service.status === 'restarting'}
                    >
                      <RotateCcw className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Olay Yönetimi */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Olay Yönetimi</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Olay Başlığı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Önem Derecesi
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Durum
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Başlangıç Zamanı
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Süre
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
              {incidents.map(incident => (
                <tr key={incident.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{incident.title}</div>
                    <div className="text-sm text-gray-500 mt-1 max-w-md truncate" title={incident.description}>
                      {incident.description}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColor(incident.severity)}`}>
                      {incident.severity === 'high' && 'Yüksek'}
                      {incident.severity === 'medium' && 'Orta'}
                      {incident.severity === 'low' && 'Düşük'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getIncidentStatusColor(incident.status)}`}>
                      {incident.status === 'open' && 'Açık'}
                      {incident.status === 'investigating' && 'İnceleniyor'}
                      {incident.status === 'resolved' && 'Çözüldü'}
                      {incident.status === 'monitoring' && 'İzleniyor'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(incident.startTime)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {calculateDuration(incident.startTime, incident.endTime)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {incident.assignedTo}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {incident.status !== 'resolved' && (
                      <button
                        onClick={() => resolveIncident(incident.id)}
                        className="text-green-600 hover:text-green-900 mr-3"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </button>
                    )}
                    <button className="text-indigo-600 hover:text-indigo-900">
                      <Bell className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && selectedEnv && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">
                {selectedEnv.name} Yapılandırması
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
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Ortam Bilgileri</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Adı</label>
                      <input
                        type="text"
                        value={selectedEnv.name}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">URL</label>
                      <input
                        type="text"
                        value={selectedEnv.url}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Versiyon</label>
                      <input
                        type="text"
                        value={selectedEnv.version}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Kaynak Sınırları</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        CPU Limiti (%)
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={selectedEnv.cpu}
                        className="mt-1 block w-full"
                        onChange={(e) => setSelectedEnv({...selectedEnv, cpu: parseInt(e.target.value)})}
                      />
                      <div className="text-right text-sm text-gray-500">{selectedEnv.cpu}%</div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Bellek Limiti (%)
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={selectedEnv.memory}
                        className="mt-1 block w-full"
                        onChange={(e) => setSelectedEnv({...selectedEnv, memory: parseInt(e.target.value)})}
                      />
                      <div className="text-right text-sm text-gray-500">{selectedEnv.memory}%</div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Disk Limiti (%)
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={selectedEnv.disk}
                        className="mt-1 block w-full"
                        onChange={(e) => setSelectedEnv({...selectedEnv, disk: parseInt(e.target.value)})}
                      />
                      <div className="text-right text-sm text-gray-500">{selectedEnv.disk}%</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  İptal
                </button>
                <button
                  onClick={closeModal}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Kaydet
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DeploymentDashboard;