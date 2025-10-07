import React, { useState } from 'react';
import EnhancedClassSchedulingRoadmap from './components/EnhancedClassSchedulingRoadmap';
import Dashboard from './components/Dashboard';
import ClassScheduling from './components/ClassScheduling';
import ApprovalWorkflow from './components/ApprovalWorkflow';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import QualityAssuranceDashboard from './components/QualityAssuranceDashboard';
import DeploymentDashboard from './components/DeploymentDashboard';
import { Layout, Map, BookOpen, Calendar, CheckCircle, BarChart3, Shield, Server } from 'lucide-react';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'roadmap' | 'scheduler' | 'approvals' | 'analytics' | 'qa' | 'deployment'>('dashboard');

  return (
    <div className="App">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <BookOpen className="h-8 w-8 text-indigo-600" />
                <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">Ders Dağıtım Sistemi</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentView === 'dashboard'
                      ? 'border-indigo-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  <Layout className="mr-2 h-4 w-4" />
                  Dashboard
                </button>
                <button
                  onClick={() => setCurrentView('scheduler')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentView === 'scheduler'
                      ? 'border-indigo-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  Çizelge
                </button>
                <button
                  onClick={() => setCurrentView('approvals')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentView === 'approvals'
                      ? 'border-indigo-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Onaylar
                </button>
                <button
                  onClick={() => setCurrentView('analytics')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentView === 'analytics'
                      ? 'border-indigo-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  <BarChart3 className="mr-2 h-4 w-4" />
                  Analiz
                </button>
                <button
                  onClick={() => setCurrentView('qa')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentView === 'qa'
                      ? 'border-indigo-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  <Shield className="mr-2 h-4 w-4" />
                  QA
                </button>
                <button
                  onClick={() => setCurrentView('deployment')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentView === 'deployment'
                      ? 'border-indigo-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  <Server className="mr-2 h-4 w-4" />
                  Deployment
                </button>
                <button
                  onClick={() => setCurrentView('roadmap')}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentView === 'roadmap'
                      ? 'border-indigo-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  <Map className="mr-2 h-4 w-4" />
                  Roadmap
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'scheduler' && <ClassScheduling />}
        {currentView === 'approvals' && <ApprovalWorkflow />}
        {currentView === 'analytics' && <AnalyticsDashboard />}
        {currentView === 'qa' && <QualityAssuranceDashboard />}
        {currentView === 'deployment' && <DeploymentDashboard />}
        {currentView === 'roadmap' && <EnhancedClassSchedulingRoadmap />}
      </main>
    </div>
  );
}

export default App;
