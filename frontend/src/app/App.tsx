import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
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

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Welcome Entry Page */}
        <Route path="/" element={<WelcomePage />} />

        {/* Application Layout */}
        <Route element={<AppLayout />}>
          {/* Faculty Routes */}
          <Route path="/faculty/dashboard" element={<FacultyDashboard />} />
          <Route path="/faculty/documents" element={<DocumentLibrary />} />
          <Route path="/faculty/generate" element={<QuestionStudio />} />
          <Route path="/faculty/generation/:generationId" element={<GenerationReview />} />
          <Route path="/faculty/questions" element={<QuestionBank />} />
          <Route path="/faculty/papers" element={<PaperLibrary />} />
          <Route path="/faculty/papers/new" element={<PaperBuilder />} />
          <Route path="/faculty/papers/:paperId" element={<PaperBuilder />} />
          <Route path="/faculty/grading" element={<GradingQueue />} />
          <Route path="/faculty/grading/:attemptId" element={<GradingWorkspace />} />
          <Route path="/faculty/analytics" element={<FacultyAnalytics />} />

          {/* Student Routes */}
          <Route path="/student/dashboard" element={<StudentDashboard />} />
          <Route path="/student/practice" element={<PracticeLibrary />} />
          <Route path="/student/attempt/:attemptId" element={<AssessmentAttempt />} />
          <Route path="/student/attempt/:attemptId/results" element={<AssessmentResults />} />
          <Route path="/student/progress" element={<StudentProgress />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
