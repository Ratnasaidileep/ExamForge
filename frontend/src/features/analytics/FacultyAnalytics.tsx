import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { BarChart3, Database, Layers, CheckSquare, Users } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';

const COLORS = ['#3730A3', '#0F766E', '#B45309', '#1D4ED8', '#64748B'];

export const FacultyAnalytics: React.FC = () => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch('/analytics/faculty')
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner size="lg" className="h-64" />;
  if (!data) return <div>Analytics data unavailable.</div>;

  // Format type distribution data
  const typeData = Object.entries(data.questions_by_type || {}).map(([name, value]) => ({
    name: name.replace('_', ' ').toUpperCase(),
    count: value
  }));

  // Format difficulty distribution data
  const diffData = Object.entries(data.questions_by_difficulty || {}).map(([name, value]) => ({
    name: name.toUpperCase(),
    count: value
  }));

  // Format score distribution data
  const scoreData = (data.score_distribution || []).map((b: any) => ({
    name: b.range_label,
    count: b.count
  }));

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="pb-2 border-b border-[#E2E8F0]">
        <div className="flex items-center gap-2 mb-1">
          <h1 className="text-2xl font-bold text-[#0F172A]">Faculty Curriculum Analytics</h1>
          <Badge variant="indigo">Demo Data Label</Badge>
        </div>
        <p className="text-xs text-[#64748B]">
          Database-grounded insights on question bank distribution, assessment scores, and topic mastery.
        </p>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 space-y-1">
            <span className="text-xs text-slate-500 font-medium">Total Questions in Bank</span>
            <div className="text-2xl font-bold text-[#0F172A]">{data.total_questions}</div>
            <div className="text-[11px] text-emerald-700 font-medium">{data.approved_questions} approved</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 space-y-1">
            <span className="text-xs text-slate-500 font-medium">Published Exams</span>
            <div className="text-2xl font-bold text-[#0F766E]">{data.published_papers}</div>
            <div className="text-[11px] text-slate-500">of {data.total_papers} total papers</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 space-y-1">
            <span className="text-xs text-slate-500 font-medium">Student Attempts</span>
            <div className="text-2xl font-bold text-[#3730A3]">{data.total_attempts}</div>
            <div className="text-[11px] text-slate-500">Completed & in progress</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 space-y-1">
            <span className="text-xs text-slate-500 font-medium">Pending Descriptive Workload</span>
            <div className="text-2xl font-bold text-[#B45309]">{data.pending_grading_count}</div>
            <div className="text-[11px] text-amber-700 font-medium">Answers awaiting grading</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Question Type Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
              Question Bank Breakdown by Type
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={typeData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3730A3" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Difficulty Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
              Difficulty Distribution
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={diffData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#0F766E" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Exam Score Distribution */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
              Student Assessment Score Distribution (Historical Attempts)
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scoreData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#1D4ED8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Topic Accuracy Across Students Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Curriculum Topic Accuracies</CardTitle>
          <p className="text-xs text-slate-500">Aggregate accuracy across student responses per topic.</p>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F8FAFC] text-[#64748B] font-semibold border-b border-[#E2E8F0]">
                <tr>
                  <th className="py-2.5 px-4">Topic Name</th>
                  <th className="py-2.5 px-4">Questions Answered</th>
                  <th className="py-2.5 px-4">Correct / High-Score</th>
                  <th className="py-2.5 px-4">Accuracy</th>
                  <th className="py-2.5 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(data.topic_accuracies || []).map((t: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-semibold text-[#0F172A]">{t.topic_name}</td>
                    <td className="py-3 px-4 text-slate-600">{t.total_questions}</td>
                    <td className="py-3 px-4 text-slate-600">{t.correct_count}</td>
                    <td className="py-3 px-4 font-bold text-slate-900">{t.accuracy_percentage}%</td>
                    <td className="py-3 px-4">
                      <Badge
                        variant={t.is_weak_area ? 'warning' : 'success'}
                        size="sm"
                      >
                        {t.is_weak_area ? 'Flagged Topic' : 'Healthy Mastery'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
