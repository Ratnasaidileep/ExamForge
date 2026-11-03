import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { BarChart3, TrendingUp, Award, BookOpen, AlertCircle, CheckCircle2 } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';

export const StudentProgress: React.FC = () => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch('/analytics/student')
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner size="lg" className="h-64" />;
  if (!data) return <div>Student progress data unavailable.</div>;

  const trends = data.trends || [];
  const topicAcc = data.topic_accuracies || [];
  const recommended = data.recommended_topics || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="pb-2 border-b border-[#E2E8F0]">
        <div className="flex items-center gap-2 mb-1">
          <h1 className="text-2xl font-bold text-[#0F172A]">Student Progress & Analytics</h1>
          <Badge variant="teal">{data.student_name}</Badge>
        </div>
        <p className="text-xs text-[#64748B]">
          Performance trajectory, topic mastery metrics, and evidence-grounded study recommendations.
        </p>
      </div>

      {/* Top Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 space-y-1">
            <span className="text-xs text-slate-500 font-medium">Total Assessments Attempted</span>
            <div className="text-2xl font-bold text-[#0F172A]">{data.total_attempts}</div>
            <div className="text-[11px] text-teal-700 font-medium">{data.completed_attempts} completed & scored</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 space-y-1">
            <span className="text-xs text-slate-500 font-medium">Average Score</span>
            <div className="text-2xl font-bold text-[#0F766E]">{data.average_score_percentage}%</div>
            <div className="text-[11px] text-slate-500">Across graded tests</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 space-y-1">
            <span className="text-xs text-slate-500 font-medium">Prioritized Focus Topics</span>
            <div className="text-2xl font-bold text-[#B45309]">{recommended.length}</div>
            <div className="text-[11px] text-amber-700 font-medium">Based on statistical rule</div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendation Transparency Alert */}
      <Alert
        type="info"
        title="Recommendation Logic Transparency"
      >
        {data.recommendation_rationale}
      </Alert>

      {/* Score Trajectory Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
            Assessment Score Trajectory (%)
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {trends.length === 0 ? (
            <div className="h-64 flex items-center justify-center text-xs text-slate-400">
              No completed tests yet to display performance trajectory.
            </div>
          ) : (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends} margin={{ top: 10, right: 20, left: -20, bottom: 20 }}>
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="score_percentage"
                    stroke="#0F766E"
                    strokeWidth={3}
                    dot={{ r: 5, fill: '#0F766E' }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Topic Accuracy & Strength Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Curriculum Topic Accuracy & Status</CardTitle>
          <p className="text-xs text-slate-500">
            Confidence indicators reflect sample depth. Topics with under 5 questions attempted are labelled for further practice.
          </p>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F8FAFC] text-[#64748B] font-semibold border-b border-[#E2E8F0]">
                <tr>
                  <th className="py-2.5 px-4">Topic Name</th>
                  <th className="py-2.5 px-4">Questions Answered</th>
                  <th className="py-2.5 px-4">Correct</th>
                  <th className="py-2.5 px-4">Accuracy</th>
                  <th className="py-2.5 px-4">Evaluation Rule Assessment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {topicAcc.map((t: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-semibold text-[#0F172A]">{t.topic_name}</td>
                    <td className="py-3 px-4 text-slate-600">{t.total_questions} questions</td>
                    <td className="py-3 px-4 text-slate-600">{t.correct_count}</td>
                    <td className="py-3 px-4 font-bold text-slate-900">{t.accuracy_percentage}%</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={
                            t.is_weak_area
                              ? 'warning'
                              : t.total_questions < 5
                              ? 'neutral'
                              : 'success'
                          }
                          size="sm"
                        >
                          {t.is_weak_area
                            ? 'Needs Practice'
                            : t.total_questions < 5
                            ? 'Low Sample Size'
                            : 'Proficient'}
                        </Badge>
                        <span className="text-[11px] text-slate-500">{t.rule_note}</span>
                      </div>
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
