import React, { useState, useCallback } from 'react';
import { 
  Calendar, 
  Clock, 
  Users, 
  BookOpen, 
  Plus, 
  Edit, 
  Trash2, 
  Download, 
  Upload, 
  Move, 
  Copy, 
  AlertTriangle,
  CheckCircle,
  X
} from 'lucide-react';

// Mock veriler
const mockTeachers = [
  { id: 1, name: 'Ahmet Yılmaz', subject: 'Matematik' },
  { id: 2, name: 'Ayşe Kaya', subject: 'Fizik' },
  { id: 3, name: 'Mehmet Demir', subject: 'Kimya' },
  { id: 4, name: 'Elif Çelik', subject: 'Biyoloji' },
];

const mockClasses = [
  { id: 1, name: 'A101', capacity: 30, hasProjector: true },
  { id: 2, name: 'B205', capacity: 50, hasProjector: true },
  { id: 3, name: 'C301', capacity: 25, hasProjector: false },
];

const mockCourses = [
  { id: 1, code: 'MAT101', name: 'Matematik I' },
  { id: 2, code: 'FIZ101', name: 'Fizik I' },
  { id: 3, code: 'KIM101', name: 'Kimya I' },
  { id: 4, code: 'BIY101', name: 'Biyoloji I' },
];

const mockTimeSlots = [
  { id: 1, day: 'Pazartesi', startTime: '09:00', endTime: '11:00' },
  { id: 2, day: 'Pazartesi', startTime: '11:00', endTime: '13:00' },
  { id: 3, day: 'Salı', startTime: '09:00', endTime: '11:00' },
  { id: 4, day: 'Salı', startTime: '11:00', endTime: '13:00' },
  { id: 5, day: 'Çarşamba', startTime: '09:00', endTime: '11:00' },
  { id: 6, day: 'Çarşamba', startTime: '11:00', endTime: '13:00' },
];

// Ders tipi
interface ScheduleItem {
  id: number;
  courseId: number;
  teacherId: number;
  classId: number;
  timeSlotId: number;
  date: string;
}

const ClassScheduling: React.FC = () => {
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [draggedItem, setDraggedItem] = useState<ScheduleItem | null>(null);
  const [selectedItem, setSelectedItem] = useState<ScheduleItem | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [conflicts, setConflicts] = useState<string[]>([]);

  // Ders ekleme
  const addScheduleItem = useCallback((item: Omit<ScheduleItem, 'id'>) => {
    const newItem = { ...item, id: Date.now() };
    setSchedule(prev => [...prev, newItem]);
    
    // Çakışma kontrolü
    checkForConflicts([...schedule, newItem]);
  }, [schedule]);

  // Ders silme
  const removeScheduleItem = useCallback((id: number) => {
    setSchedule(prev => prev.filter(item => item.id !== id));
    if (selectedItem?.id === id) {
      setSelectedItem(null);
    }
    
    // Çakışma kontrolü
    const newSchedule = schedule.filter(item => item.id !== id);
    checkForConflicts(newSchedule);
  }, [schedule, selectedItem]);

  // Drag & drop işlemleri
  const handleDragStart = (item: ScheduleItem) => {
    setDraggedItem(item);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (timeSlotId: number, classId: number) => {
    if (draggedItem) {
      // Yeni konuma taşı
      const updatedSchedule = schedule.map(item => 
        item.id === draggedItem.id 
          ? { ...item, timeSlotId, classId } 
          : item
      );
      
      setSchedule(updatedSchedule);
      setDraggedItem(null);
      
      // Çakışma kontrolü
      checkForConflicts(updatedSchedule);
    }
  };

  // Çakışma kontrolü
  const checkForConflicts = (currentSchedule: ScheduleItem[]) => {
    const newConflicts: string[] = [];
    
    // Öğretmen çakışmalarını kontrol et
    const teacherConflicts = new Map<string, ScheduleItem[]>();
    currentSchedule.forEach(item => {
      const key = `${item.teacherId}-${item.timeSlotId}-${item.date}`;
      if (!teacherConflicts.has(key)) {
        teacherConflicts.set(key, []);
      }
      teacherConflicts.get(key)?.push(item);
    });
    
    teacherConflicts.forEach((items, key) => {
      if (items.length > 1) {
        const teacher = mockTeachers.find(t => t.id === items[0].teacherId);
        const timeSlot = mockTimeSlots.find(t => t.id === items[0].timeSlotId);
        newConflicts.push(
          `${teacher?.name} öğretmeni ${timeSlot?.day} ${timeSlot?.startTime}-${timeSlot?.endTime} zaman diliminde çakışma var`
        );
      }
    });
    
    // Sınıf çakışmalarını kontrol et
    const classConflicts = new Map<string, ScheduleItem[]>();
    currentSchedule.forEach(item => {
      const key = `${item.classId}-${item.timeSlotId}-${item.date}`;
      if (!classConflicts.has(key)) {
        classConflicts.set(key, []);
      }
      classConflicts.get(key)?.push(item);
    });
    
    classConflicts.forEach((items, key) => {
      if (items.length > 1) {
        const classroom = mockClasses.find(c => c.id === items[0].classId);
        const timeSlot = mockTimeSlots.find(t => t.id === items[0].timeSlotId);
        newConflicts.push(
          `${classroom?.name} sınıfı ${timeSlot?.day} ${timeSlot?.startTime}-${timeSlot?.endTime} zaman diliminde çakışma var`
        );
      }
    });
    
    setConflicts(newConflicts);
  };

  // Ders detaylarını al
  const getItemDetails = (item: ScheduleItem) => {
    const course = mockCourses.find(c => c.id === item.courseId);
    const teacher = mockTeachers.find(t => t.id === item.teacherId);
    const classroom = mockClasses.find(c => c.id === item.classId);
    const timeSlot = mockTimeSlots.find(t => t.id === item.timeSlotId);
    
    return { course, teacher, classroom, timeSlot };
  };

  // Modal işlemleri
  const openModal = (item: ScheduleItem | null = null) => {
    setSelectedItem(item);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedItem(null);
  };

  // Excel/PDF export
  const exportSchedule = (format: 'excel' | 'pdf') => {
    alert(`${format.toUpperCase()} formatında dışa aktarma işlemi başlatıldı`);
    // Gerçek uygulamada burada dışa aktarma işlemi yapılacak
  };

  // Excel/PDF import
  const importSchedule = (format: 'excel' | 'pdf') => {
    alert(`${format.toUpperCase()} formatında içe aktarma işlemi başlatıldı`);
    // Gerçek uygulamada burada içe aktarma işlemi yapılacak
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Ders Çizelgesi</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => importSchedule('excel')}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Upload className="w-4 h-4 mr-2" />
              Excel İçe Aktar
            </button>
            <button 
              onClick={() => exportSchedule('excel')}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Download className="w-4 h-4 mr-2" />
              Excel Dışa Aktar
            </button>
            <button 
              onClick={() => exportSchedule('pdf')}
              className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              <Download className="w-4 h-4 mr-2" />
              PDF Dışa Aktar
            </button>
            <button 
              onClick={() => openModal()}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Yeni Ders Ekle
            </button>
          </div>
        </div>
        
        {conflicts.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
              <h3 className="font-semibold text-red-800">Çakışmalar Tespit Edildi</h3>
            </div>
            <ul className="mt-2 space-y-1">
              {conflicts.map((conflict, index) => (
                <li key={index} className="text-red-700 text-sm">{conflict}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Çizelge */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Gün başlıkları */}
        <div className="grid grid-cols-7 border-b">
          <div className="p-4 font-semibold bg-gray-50"></div>
          {mockTimeSlots.slice(0, 2).map(slot => (
            <div key={slot.id} className="p-4 font-semibold bg-gray-50 border-l text-center">
              {slot.startTime} - {slot.endTime}
            </div>
          ))}
        </div>
        
        {/* Sınıf satırları */}
        {mockClasses.map(classroom => (
          <div key={classroom.id} className="grid grid-cols-7 border-b">
            {/* Sınıf adı */}
            <div className="p-4 font-semibold bg-gray-50 border-r flex items-center">
              <div>
                <div>{classroom.name}</div>
                <div className="text-sm font-normal text-gray-600">
                  {classroom.capacity} kişi
                  {classroom.hasProjector && ' | Projektörlü'}
                </div>
              </div>
            </div>
            
            {/* Zaman dilimleri */}
            {mockTimeSlots.slice(0, 2).map(timeSlot => {
              const scheduleItem = schedule.find(
                item => item.classId === classroom.id && item.timeSlotId === timeSlot.id
              );
              
              return (
                <div 
                  key={`${classroom.id}-${timeSlot.id}`}
                  className="p-2 border-l min-h-24 relative"
                  onDragOver={handleDragOver}
                  onDrop={() => handleDrop(timeSlot.id, classroom.id)}
                >
                  {scheduleItem ? (
                    <div 
                      draggable
                      onDragStart={() => handleDragStart(scheduleItem)}
                      className="p-2 bg-indigo-100 rounded border border-indigo-300 cursor-move hover:bg-indigo-200"
                      onClick={() => openModal(scheduleItem)}
                    >
                      <div className="font-semibold text-sm">
                        {mockCourses.find(c => c.id === scheduleItem.courseId)?.code}
                      </div>
                      <div className="text-xs text-gray-600">
                        {mockTeachers.find(t => t.id === scheduleItem.teacherId)?.name}
                      </div>
                      <div className="absolute top-1 right-1 flex space-x-1">
                        <button 
                          onClick={(e) => {
                            e.stopPropagation();
                            openModal(scheduleItem);
                          }}
                          className="p-1 rounded hover:bg-indigo-200"
                        >
                          <Edit className="w-3 h-3 text-indigo-600" />
                        </button>
                        <button 
                          onClick={(e) => {
                            e.stopPropagation();
                            removeScheduleItem(scheduleItem.id);
                          }}
                          className="p-1 rounded hover:bg-red-200"
                        >
                          <Trash2 className="w-3 h-3 text-red-600" />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div 
                          className="h-full flex items-center justify-center text-gray-400 cursor-pointer hover:bg-gray-50 rounded"
                          onClick={() => openModal({
                            id: 0,
                            courseId: 0,
                            teacherId: 0,
                            classId: classroom.id,
                            timeSlotId: timeSlot.id,
                            date: '2023-09-04'
                          })}
                        >
                          <Plus className="w-4 h-4" />
                        </div>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">
                {selectedItem ? 'Ders Düzenle' : 'Yeni Ders Ekle'}
              </h3>
              <button 
                onClick={closeModal}
                className="p-2 rounded-full hover:bg-gray-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ders
                </label>
                <select className="w-full p-2 border border-gray-300 rounded-lg">
                  <option value="">Ders seçin</option>
                  {mockCourses.map(course => (
                    <option key={course.id} value={course.id}>
                      {course.code} - {course.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Öğretmen
                </label>
                <select className="w-full p-2 border border-gray-300 rounded-lg">
                  <option value="">Öğretmen seçin</option>
                  {mockTeachers.map(teacher => (
                    <option key={teacher.id} value={teacher.id}>
                      {teacher.name} ({teacher.subject})
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tarih
                </label>
                <input 
                  type="date" 
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  defaultValue="2023-09-04"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Gün
                  </label>
                  <select className="w-full p-2 border border-gray-300 rounded-lg">
                    <option>Pazartesi</option>
                    <option>Salı</option>
                    <option>Çarşamba</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Saat
                  </label>
                  <select className="w-full p-2 border border-gray-300 rounded-lg">
                    <option>09:00 - 11:00</option>
                    <option>11:00 - 13:00</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 p-6 border-t">
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
                {selectedItem ? 'Güncelle' : 'Ekle'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClassScheduling;