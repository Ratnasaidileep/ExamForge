import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';
import {
  LayoutDashboard, FileText, Sparkles, Database, Layers,
  CheckSquare, BarChart3, Bell, Users, RotateCcw,
  Menu, X, BookOpen, GraduationCap, ChevronRight, AlertTriangle,
  Sun, Moon
} from 'lucide-react';
import { getActiveUser, setActiveUser, apiFetch, DemoProfile } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<DemoProfile>(getActiveUser());
  const [profiles, setProfiles] = useState<DemoProfile[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [isDark, setIsDark] = useState<boolean>(() => {
    return localStorage.getItem('examforge_theme') === 'dark';
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('examforge_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('examforge_theme', 'light');
    }
  }, [isDark]);

  // Load profiles
  useEffect(() => {
    apiFetch<DemoProfile[]>('/demo/profiles')
      .then(setProfiles)
      .catch(console.error);

    const onRoleChanged = () => setCurrentUser(getActiveUser());
    window.addEventListener('examforge_role_changed', onRoleChanged);
    return () => window.removeEventListener('examforge_role_changed', onRoleChanged);
  }, []);

  // Load notifications
  useEffect(() => {
    apiFetch<any[]>('/notifications')
      .then(setNotifications)
      .catch(console.error);
  }, [currentUser]);

  const handleSwitchUser = (user: DemoProfile) => {
    setActiveUser(user);
    setCurrentUser(user);
    if (user.role === 'faculty') {
      navigate('/faculty/dashboard');
    } else {
      navigate('/student/dashboard');
    }
  };

  const handleResetWorkspace = async () => {
    setIsResetting(true);
    try {
      await apiFetch('/demo/reset', {
        method: 'POST',
        body: JSON.stringify({ confirm: true })
      });
      setResetModalOpen(false);
      window.location.reload();
    } catch (e: any) {
      alert(`Reset failed: ${e.message}`);
    } finally {
      setIsResetting(false);
    }
  };

  const facultyNavItems = [
    { label: 'Faculty Dashboard', path: '/faculty/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { label: 'Document Library', path: '/faculty/documents', icon: <FileText className="w-4 h-4" /> },
    { label: 'AI Question Studio', path: '/faculty/generate', icon: <Sparkles className="w-4 h-4" /> },
    { label: 'Question Bank', path: '/faculty/questions', icon: <Database className="w-4 h-4" /> },
    { label: 'Paper Builder & Library', path: '/faculty/papers', icon: <Layers className="w-4 h-4" /> },
    { label: 'Grading Queue', path: '/faculty/grading', icon: <CheckSquare className="w-4 h-4" /> },
    { label: 'Faculty Analytics', path: '/faculty/analytics', icon: <BarChart3 className="w-4 h-4" /> },
  ];

  const studentNavItems = [
    { label: 'Student Dashboard', path: '/student/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { label: 'Practice & Mock Exams', path: '/student/practice', icon: <BookOpen className="w-4 h-4" /> },
    { label: 'Progress & Insights', path: '/student/progress', icon: <BarChart3 className="w-4 h-4" /> },
  ];

  const navItems = currentUser.role === 'faculty' ? facultyNavItems : studentNavItems;
  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col md:flex-row">
      {/* Mobile Drawer Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 z-40 h-screen w-64 bg-[#1E293B] text-white flex flex-col transition-transform duration-200 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-700/60 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-[#3730A3] flex items-center justify-center text-white shadow-md font-bold text-lg">
              EF
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white block">ExamForge</span>
              <span className="text-[10px] text-teal-400 font-semibold tracking-wider uppercase block">AI Assessment Platform</span>
            </div>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Active Demo Role Indicator */}
        <div className="px-4 py-3 bg-slate-800/80 border-b border-slate-700/40">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Active Demo Role</span>
            <Badge variant={currentUser.role === 'faculty' ? 'indigo' : 'teal'} size="sm">
              {currentUser.role === 'faculty' ? 'Faculty Mode' : 'Student Mode'}
            </Badge>
          </div>
          <div className="text-xs text-white font-medium truncate">{currentUser.name}</div>
          <div className="text-[11px] text-slate-400 truncate">{currentUser.email}</div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
          <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            {currentUser.role === 'faculty' ? 'Faculty Portal' : 'Student Portal'}
          </div>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
            const activeBg = currentUser.role === 'faculty' ? 'bg-[#3730A3]' : 'bg-[#0F766E]';
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? `${activeBg} text-white shadow-sm font-semibold`
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Subject & Reset Footer */}
        <div className="p-4 border-t border-slate-700/60 bg-slate-900/50 space-y-2">
          <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-800/60 border border-slate-700/50 text-slate-300">
            <GraduationCap className="w-4 h-4 text-teal-400 flex-shrink-0" />
            <div className="min-w-0 flex-1">
              <div className="text-[11px] font-semibold text-white truncate">ITS-401</div>
              <div className="text-[10px] text-slate-400 truncate">Intelligent Transport Systems</div>
            </div>
          </div>
          <button
            onClick={() => setResetModalOpen(true)}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-slate-700 text-slate-400 hover:text-amber-400 hover:border-amber-400/40 text-xs transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Demo Workspace</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="sticky top-0 z-30 bg-white border-b border-[#E2E8F0] px-4 md:px-8 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="hidden sm:flex items-center gap-2 text-xs text-[#64748B]">
              <Link to="/" className="hover:text-[#3730A3]">ExamForge</Link>
              <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
              <span className="font-medium text-[#0F172A] capitalize">
                {location.pathname.split('/')[2] || 'Home'}
              </span>
            </div>
          </div>

          {/* Right Header Controls */}
          <div className="flex items-center gap-3">
            {/* Theme Toggle */}
            <button
              onClick={() => setIsDark(!isDark)}
              className="p-2 rounded-lg hover:bg-slate-100 text-slate-600 transition-colors"
              title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {isDark ? <Sun className="w-5 h-5 text-amber-500" /> : <Moon className="w-5 h-5 text-slate-600" />}
            </button>

            {/* Notifications Dropdown */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="relative p-2 rounded-lg hover:bg-slate-100 text-slate-600 transition-colors"
                title="Notifications"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#B91C1C]" />
                )}
              </button>

              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-[#E2E8F0] p-3 z-50 animate-fade-in">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100 mb-2">
                    <span className="text-xs font-semibold text-[#0F172A]">Notifications</span>
                    <Badge size="sm" variant="info">{unreadCount} new</Badge>
                  </div>
                  <div className="max-h-64 overflow-y-auto space-y-2">
                    {notifications.length === 0 ? (
                      <p className="text-xs text-slate-400 text-center py-4">No notifications.</p>
                    ) : (
                      notifications.map(n => (
                        <div
                          key={n.id}
                          className={`p-2 rounded-lg text-xs transition-colors cursor-pointer ${
                            n.is_read ? 'bg-slate-50 text-slate-600' : 'bg-indigo-50/60 text-[#1E293B] font-medium'
                          }`}
                          onClick={() => {
                            if (n.link) navigate(n.link);
                            setNotificationsOpen(false);
                          }}
                        >
                          <div className="font-semibold text-[#0F172A]">{n.title}</div>
                          <div className="text-[11px] text-slate-500 mt-0.5">{n.message}</div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Role Switcher Dropdown */}
            <div className="flex items-center bg-slate-100 rounded-lg p-1 border border-slate-200">
              <button
                onClick={() => {
                  const prof = profiles.find(p => p.role === 'faculty');
                  if (prof) handleSwitchUser(prof);
                }}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
                  currentUser.role === 'faculty'
                    ? 'bg-[#3730A3] text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span>Faculty</span>
              </button>
              <button
                onClick={() => {
                  const stud = profiles.find(p => p.role === 'student');
                  if (stud) handleSwitchUser(stud);
                }}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
                  currentUser.role === 'student'
                    ? 'bg-[#0F766E] text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span>Student</span>
              </button>
            </div>
          </div>
        </header>

        {/* Content Outlet */}
        <main className="p-4 md:p-8 flex-1">
          <Outlet />
        </main>
      </div>

      {/* Demo Reset Confirmation Modal */}
      <Modal
        isOpen={resetModalOpen}
        onClose={() => setResetModalOpen(false)}
        title="Reset Demo Workspace?"
        description="This action will restore the initial seeded ITS-401 workspace data."
        footer={
          <>
            <Button variant="secondary" onClick={() => setResetModalOpen(false)} disabled={isResetting}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleResetWorkspace} isLoading={isResetting}>
              Confirm Reset
            </Button>
          </>
        }
      >
        <div className="space-y-3 text-xs text-[#64748B] leading-relaxed">
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2.5 text-amber-900">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <strong>Important Note:</strong>
              <p className="mt-1">
                Resetting restores the sample Intelligent Transport Systems notes, approved questions, sample mid-term paper, and default graded/pending student attempts.
              </p>
            </div>
          </div>
          <p>
            Your Gemini API configuration and uploaded user files will be safely preserved.
          </p>
        </div>
      </Modal>
    </div>
  );
};
