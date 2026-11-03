import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles, GraduationCap, ShieldCheck, FileText,
  Layers, CheckSquare, ArrowRight, BookOpen, Clock, BarChart3,
  Sun, Moon
} from 'lucide-react';
import { setActiveUser, getActiveUser, apiFetch, DemoProfile } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export const WelcomePage: React.FC = () => {
  const navigate = useNavigate();

  const handleSelectFaculty = async () => {
    try {
      const profiles = await apiFetch<DemoProfile[]>('/demo/profiles');
      const prof = profiles.find(p => p.role === 'faculty') || {
        id: 'prof_sharma',
        name: 'Dr. R. Sharma',
        role: 'faculty',
        email: 'r.sharma@college.edu'
      };
      setActiveUser(prof);
      navigate('/faculty/dashboard');
    } catch {
      navigate('/faculty/dashboard');
    }
  };

  const handleSelectStudent = async () => {
    try {
      const profiles = await apiFetch<DemoProfile[]>('/demo/profiles');
      const stud = profiles.find(p => p.role === 'student') || {
        id: 'student_aditi',
        name: 'Aditi Rao',
        role: 'student',
        email: 'aditi.cs21@college.edu'
      };
      setActiveUser(stud);
      navigate('/student/dashboard');
    } catch {
      navigate('/student/dashboard');
    }
  };

  const [isDark, setIsDark] = useState<boolean>(() => {
    return localStorage.getItem('examforge_theme') === 'dark';
  });

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (nextDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('examforge_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('examforge_theme', 'light');
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 animate-fade-in space-y-10">
      {/* Top Floating Controls */}
      <div className="flex justify-end">
        <button
          onClick={toggleTheme}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#111827] text-slate-700 dark:text-slate-200 shadow-xs hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-medium transition-colors"
          title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          <span>{isDark ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
      </div>

      {/* Top Banner */}
      <div className="text-center space-y-3">
        <Badge variant="indigo" size="md">
          Academic SaaS Demonstration
        </Badge>
        <h1 className="text-3xl md:text-4xl font-extrabold text-[#0F172A] dark:text-white tracking-tight">
          ExamForge Assessment Platform
        </h1>
        <p className="text-sm md:text-base text-[#64748B] dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
          AI-powered, source-grounded question paper generator and college examination workflow system built for rigorous academic evaluation.
        </p>
      </div>

      {/* Two Entry Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Faculty Portal Card */}
        <Card className="border-2 border-indigo-100 hover:border-[#3730A3] transition-all shadow-md group">
          <CardContent className="p-8 space-y-5">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-[#3730A3]">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-[#0F172A]">Faculty Demo</h2>
                <Badge variant="indigo">Educator Mode</Badge>
              </div>
              <p className="text-xs text-[#64748B] mt-1.5 leading-relaxed">
                Experience end-to-end question paper creation: upload syllabus notes, generate source-grounded questions with Gemini, assemble blueprint-validated exams, export official PDFs, and grade student submissions.
              </p>
            </div>

            <div className="space-y-2 py-2">
              <div className="flex items-center gap-2.5 text-xs text-[#1E293B]">
                <FileText className="w-4 h-4 text-[#3730A3]" />
                <span>Upload PDF/DOCX notes & inspect extracted text</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1E293B]">
                <ShieldCheck className="w-4 h-4 text-[#15803D]" />
                <span>Strict grounding verification with source quotes</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1E293B]">
                <Layers className="w-4 h-4 text-[#0F766E]" />
                <span>Interactive paper builder & dual PDF export</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1E293B]">
                <CheckSquare className="w-4 h-4 text-[#B45309]" />
                <span>Manual descriptive grading queue & rubrics</span>
              </div>
            </div>

            <Button
              variant="primary"
              size="lg"
              className="w-full justify-between mt-4"
              onClick={handleSelectFaculty}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Enter Faculty Workspace
            </Button>
          </CardContent>
        </Card>

        {/* Student Portal Card */}
        <Card className="border-2 border-teal-100 hover:border-[#0F766E] transition-all shadow-md group">
          <CardContent className="p-8 space-y-5">
            <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center text-[#0F766E]">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-[#0F172A]">Student Demo</h2>
                <Badge variant="teal">Examinee Mode</Badge>
              </div>
              <p className="text-xs text-[#64748B] mt-1.5 leading-relaxed">
                Take timed assessments or self-paced practice sets in a distraction-free exam environment. Submit answers with instant objective scoring and track topic-wise proficiency.
              </p>
            </div>

            <div className="space-y-2 py-2">
              <div className="flex items-center gap-2.5 text-xs text-[#1E293B]">
                <Clock className="w-4 h-4 text-[#0F766E]" />
                <span>Timed assessment environment with server-enforced deadline</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1E293B]">
                <ShieldCheck className="w-4 h-4 text-[#15803D]" />
                <span>Zero answer leaks during active test taking</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1E293B]">
                <BookOpen className="w-4 h-4 text-[#3730A3]" />
                <span>Instant MCQ grading & descriptive evaluation status</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1E293B]">
                <BarChart3 className="w-4 h-4 text-[#1D4ED8]" />
                <span>Evidence-based topic accuracy & weak area recommendations</span>
              </div>
            </div>

            <Button
              variant="teal"
              size="lg"
              className="w-full justify-between mt-4"
              onClick={handleSelectStudent}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Enter Student Assessment
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Course Context & Architecture Overview */}
      <Card className="bg-[#1E293B] text-white border-slate-700">
        <CardContent className="p-6 md:p-8 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-teal-400 text-xs font-semibold uppercase tracking-wider">
              <BookOpen className="w-4 h-4" />
              <span>Seeded College Subject</span>
            </div>
            <Badge variant="indigo">SQLite Database Grounded</Badge>
          </div>
          <h3 className="text-lg font-bold text-white">
            ITS-401: Intelligent Transport Systems
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
            Pre-loaded with 4 academic units covering ITS Architecture, Inductive Loops and Radar Surveillance, SCATS/SCOOT Adaptive Traffic Optimization, FASTag RFID Toll Collection, DSRC vs Cellular-V2X (C-V2X), and Cooperative Adaptive Cruise Control (CACC) Platooning.
          </p>
          <div className="pt-2 flex flex-wrap gap-2 text-[11px] text-slate-400">
            <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">Unit 1: Fundamentals & Sensors</span>
            <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">Unit 2: ATMS & Ramp Metering</span>
            <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">Unit 3: ATIS & RFID Toll Collection</span>
            <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">Unit 4: V2X & Autonomous Platooning</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
