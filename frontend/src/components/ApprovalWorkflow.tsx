import React, { useState } from 'react';
import { 
  CheckCircle, 
  Clock, 
  User, 
  MessageSquare, 
  FileText, 
  Send, 
  AlertTriangle,
  ThumbsUp,
  ThumbsDown,
  Eye,
  Edit,
  Trash2,
  Download,
  Filter,
  Search
} from 'lucide-react';

// Mock veriler
const mockApprovals = [
  {
    id: 1,
    title: '2023-2024 Güz Dönemi Çizelgesi',
    requester: 'Ahmet Yılmaz',
    department: 'Matematik Bölümü',
    status: 'pending',
    priority: 'high',
    submittedAt: '2023-08-15T10:30:00Z',
    lastUpdated: '2023-08-15T14:22:00Z',
    comments: [
      {
        id: 1,
        author: 'Mehmet Demir',
        role: 'Bölüm Başkanı',
        text: 'Lütfen Salı günkü çakışmaları kontrol edin.',
        timestamp: '2023-08-15T12:15:00Z'
      }
    ]
  },
  {
    id: 2,
    title: 'Özel Sınav Çizelgesi',
    requester: 'Ayşe Kaya',
    department: 'Fizik Bölümü',
    status: 'approved',
    priority: 'medium',
    submittedAt: '2023-08-10T09:15:00Z',
    lastUpdated: '2023-08-12T16:45:00Z',
    comments: [
      {
        id: 2,
        author: 'Elif Çelik',
        role: 'Müdür Yardımcısı',
        text: 'Onaylandı. Teşekkürler.',
        timestamp: '2023-08-12T16:45:00Z'
      }
    ]
  },
  {
    id: 3,
    title: 'Laboratuvar Kullanım Planı',
    requester: 'Mehmet Demir',
    department: 'Kimya Bölümü',
    status: 'rejected',
    priority: 'low',
    submittedAt: '2023-08-05T14:20:00Z',
    lastUpdated: '2023-08-08T11:30:00Z',
    comments: [
      {
        id: 3,
        author: 'Ahmet Yılmaz',
        role: 'Müdür',
        text: 'Yetersiz detay. Lütfen daha fazla bilgi ekleyin.',
        timestamp: '2023-08-08T11:30:00Z'
      }
    ]
  }
];

const ApprovalWorkflow: React.FC = () => {
  const [approvals, setApprovals] = useState(mockApprovals);
  const [selectedApproval, setSelectedApproval] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
  const [comment, setComment] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // Durum filtreleme
  const filteredApprovals = filterStatus === 'all' 
    ? approvals 
    : approvals.filter(approval => approval.status === filterStatus);

  // Onay işlemi
  const handleApprove = (id: number) => {
    setApprovals(prev => 
      prev.map(approval => 
        approval.id === id 
          ? { ...approval, status: 'approved', lastUpdated: new Date().toISOString() } 
          : approval
      )
    );
  };

  // Reddetme işlemi
  const handleReject = (id: number) => {
    setApprovals(prev => 
      prev.map(approval => 
        approval.id === id 
          ? { ...approval, status: 'rejected', lastUpdated: new Date().toISOString() } 
          : approval
      )
    );
  };

  // Yorum ekleme
  const addComment = (approvalId: number) => {
    if (!comment.trim()) return;
    
    setApprovals(prev => 
      prev.map(approval => {
        if (approval.id === approvalId) {
          const newComment = {
            id: Date.now(),
            author: 'Müdür', // Gerçek uygulamada oturum açan kullanıcı
            role: 'Müdür',
            text: comment,
            timestamp: new Date().toISOString()
          };
          
          return {
            ...approval,
            comments: [...approval.comments, newComment],
            lastUpdated: new Date().toISOString()
          };
        }
        return approval;
      })
    );
    
    setComment('');
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
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Öncelik rengi
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Modal işlemleri
  const openModal = (approval: any) => {
    setSelectedApproval(approval);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedApproval(null);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Onay İş Akışları</h1>
          <div className="flex space-x-2">
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
              <option value="all">Tümü</option>
              <option value="pending">Beklemede</option>
              <option value="approved">Onaylandı</option>
              <option value="rejected">Reddedildi</option>
            </select>
            
            <button className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
              <Filter className="w-4 h-4 mr-2" />
              Filtrele
            </button>
          </div>
        </div>
      </div>

      {/* Onay Listesi */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Başlık
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Talep Eden
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Departman
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Durum
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Öncelik
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tarih
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                İşlem
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredApprovals.map((approval) => (
              <tr key={approval.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-gray-400 mr-2" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">{approval.title}</div>
                      <div className="text-sm text-gray-500">
                        {formatDate(approval.submittedAt)}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-semibold text-sm mr-2">
                      {approval.requester.charAt(0)}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">{approval.requester}</div>
                      <div className="text-sm text-gray-500">{approval.requester.includes('Yılmaz') ? 'Müdür' : 'Öğretmen'}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {approval.department}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(approval.status)}`}>
                    {approval.status === 'pending' && 'Beklemede'}
                    {approval.status === 'approved' && 'Onaylandı'}
                    {approval.status === 'rejected' && 'Reddedildi'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(approval.priority)}`}>
                    {approval.priority === 'high' && 'Yüksek'}
                    {approval.priority === 'medium' && 'Orta'}
                    {approval.priority === 'low' && 'Düşük'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(approval.lastUpdated)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => openModal(approval)}
                    className="text-indigo-600 hover:text-indigo-900 mr-3"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  {approval.status === 'pending' && (
                    <>
                      <button
                        onClick={() => handleApprove(approval.id)}
                        className="text-green-600 hover:text-green-900 mr-3"
                      >
                        <ThumbsUp className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleReject(approval.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <ThumbsDown className="w-4 h-4" />
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && selectedApproval && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">
                {selectedApproval.title}
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
                  <h4 className="text-sm font-medium text-gray-500">Talep Eden</h4>
                  <p className="text-sm font-medium">{selectedApproval.requester}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Departman</h4>
                  <p className="text-sm font-medium">{selectedApproval.department}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Durum</h4>
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(selectedApproval.status)}`}>
                    {selectedApproval.status === 'pending' && 'Beklemede'}
                    {selectedApproval.status === 'approved' && 'Onaylandı'}
                    {selectedApproval.status === 'rejected' && 'Reddedildi'}
                  </span>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Öncelik</h4>
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(selectedApproval.priority)}`}>
                    {selectedApproval.priority === 'high' && 'Yüksek'}
                    {selectedApproval.priority === 'medium' && 'Orta'}
                    {selectedApproval.priority === 'low' && 'Düşük'}
                  </span>
                </div>
              </div>
              
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-500 mb-2">Yorumlar</h4>
                <div className="space-y-4">
                  {selectedApproval.comments.map((comment: any) => (
                    <div key={comment.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center">
                          <div className="h-6 w-6 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-semibold text-xs mr-2">
                            {comment.author.charAt(0)}
                          </div>
                          <div>
                            <div className="text-sm font-medium">{comment.author}</div>
                            <div className="text-xs text-gray-500">{comment.role}</div>
                          </div>
                        </div>
                        <span className="text-xs text-gray-500">
                          {formatDate(comment.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{comment.text}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              {selectedApproval.status === 'pending' && (
                <div className="border-t pt-6">
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Yeni Yorum Ekle</h4>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Yorumunuzu yazın..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                    <button
                      onClick={() => addComment(selectedApproval.id)}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <div className="flex justify-end space-x-3 mt-4">
                    <button
                      onClick={() => handleReject(selectedApproval.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center"
                    >
                      <ThumbsDown className="w-4 h-4 mr-2" />
                      Reddet
                    </button>
                    <button
                      onClick={() => handleApprove(selectedApproval.id)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center"
                    >
                      <ThumbsUp className="w-4 h-4 mr-2" />
                      Onayla
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApprovalWorkflow;