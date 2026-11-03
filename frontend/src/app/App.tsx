import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ShieldAlert } from 'lucide-react';
import { getActiveUser, setActiveUser } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { AppLayout } from '@/components/layout/AppLayout';
import { WelcomePage } from '@/features/demo/WelcomePage';
import { FacultyDashboard } from '@/features/faculty-dashboard/FacultyDashboard';
import { DocumentLibrary } from '@/features/documents/DocumentLibrary';
import { QuestionStudio } from '@/features/question-studio/QuestionStudio';
import { GenerationReview } from '@/features/question-studio/GenerationReview';
import { QuestionBank } from '@/features/question-bank/QuestionBank';
import { PaperLibrary } from '@/features/paper-builder/PaperLibrary';
import { PaperBuilder } from '@/features/paper-builder/PaperBuilder';
import { GradingQueue } from '@/features/grading/GradingQueue';
import { GradingWorkspace } from '@/features/grading/GradingWorkspace';
import { FacultyAnalytics } from '@/features/analytics/FacultyAnalytics';
import { StudentDashboard } from '@/features/student-practice/StudentDashboard';
import { PracticeLibrary } from '@/features/student-practice/PracticeLibrary';
import { AssessmentAttempt } from '@/features/assessments/AssessmentAttempt';
import { AssessmentResults } from '@/features/assessments/AssessmentResults';
import { StudentProgress } from '@/features/analytics/StudentProgress';

const RoleGuard: React.FC<{ allowedRole: 'faculty' | 'student'; children: React.ReactNode }> = ({ allowedRole, children }) => {
  const [user, setUser] = useState(getActiveUser());

  useEffect(() => {
    const handleRoleChanged = () => setUser(getActiveUser());
    window.addEventListener('examforge_role_changed', handleRoleChanged);
    return () => window.removeEventListener('examforge_role_changed', handleRoleChanged);
  }, []);

  if (user.role !== allowedRole) {
    return (
      <div className="p-8 max-w-md mx-auto my-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="w-12 h-12 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center mx-auto">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-slate-800">Role-Restricted Area</h2>
        <p className="text-xs text-slate-500 leading-relaxed">
          This workspace requires <span className="font-semibold text-slate-700 uppercase">{allowedRole}</span> privileges. You are currently in <span className="font-semibold text-slate-700 capitalize">{user.role} mode</span>.
        </p>
        <div className="pt-2">
          <Button
            variant={allowedRole === 'faculty' ? 'primary' : 'teal'}
            size="sm"
            onClick={() => {
              if (allowedRole === 'faculty') {
                setActiveUser({
                  id: 'prof_sharma',
                  name: 'Dr. R. Sharma',
                  role: 'faculty',
                  email: 'r.sharma@college.edu',
                  department: 'Computer Science & Engineering',
                  avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'
                });
              } else {
                setActiveUser({
                  id: 'student_aditi',
                  name: 'Aditi Rao',
                  role: 'student',
                  email: 'aditi.cs21@college.edu',
                  department: 'Computer Science & Engineering',
                  avatar_url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150'
                });
              }
            }}
          >
            Switch to {allowedRole.toUpperCase()} View
          </Button>
        </div>
      </div>
    );
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Welcome Entry Page */}
        <Route path="/" element={<WelcomePage />} />

        {/* Application Layout */}
        <Route element={<AppLayout />}>
          {/* Faculty Routes */}
          <Route path="/faculty/dashboard" element={<RoleGuard allowedRole="faculty"><FacultyDashboard /></RoleGuard>} />
          <Route path="/faculty/documents" element={<RoleGuard allowedRole="faculty"><DocumentLibrary /></RoleGuard>} />
          <Route path="/faculty/generate" element={<RoleGuard allowedRole="faculty"><QuestionStudio /></RoleGuard>} />
          <Route path="/faculty/generation/:generationId" element={<RoleGuard allowedRole="faculty"><GenerationReview /></RoleGuard>} />
          <Route path="/faculty/questions" element={<RoleGuard allowedRole="faculty"><QuestionBank /></RoleGuard>} />
          <Route path="/faculty/papers" element={<RoleGuard allowedRole="faculty"><PaperLibrary /></RoleGuard>} />
          <Route path="/faculty/papers/new" element={<RoleGuard allowedRole="faculty"><PaperBuilder /></RoleGuard>} />
          <Route path="/faculty/papers/:paperId" element={<RoleGuard allowedRole="faculty"><PaperBuilder /></RoleGuard>} />
          <Route path="/faculty/grading" element={<RoleGuard allowedRole="faculty"><GradingQueue /></RoleGuard>} />
          <Route path="/faculty/grading/:attemptId" element={<RoleGuard allowedRole="faculty"><GradingWorkspace /></RoleGuard>} />
          <Route path="/faculty/analytics" element={<RoleGuard allowedRole="faculty"><FacultyAnalytics /></RoleGuard>} />

          {/* Student Routes */}
          <Route path="/student/dashboard" element={<RoleGuard allowedRole="student"><StudentDashboard /></RoleGuard>} />
          <Route path="/student/practice" element={<RoleGuard allowedRole="student"><PracticeLibrary /></RoleGuard>} />
          <Route path="/student/attempt/:attemptId" element={<RoleGuard allowedRole="student"><AssessmentAttempt /></RoleGuard>} />
          <Route path="/student/attempt/:attemptId/results" element={<RoleGuard allowedRole="student"><AssessmentResults /></RoleGuard>} />
          <Route path="/student/progress" element={<RoleGuard allowedRole="student"><StudentProgress /></RoleGuard>} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
