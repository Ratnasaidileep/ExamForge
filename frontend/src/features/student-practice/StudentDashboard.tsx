import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  BookOpen, Clock, CheckCircle2, AlertTriangle, ArrowRight,
  TrendingUp, Award, Layers, Sparkles
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatDate } from '@/lib/formatters';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';

export const StudentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [startingId, setStartingId] = useState<string | null>(null);

  useEffect(() => {
    apiFetch('/dashboard/student')
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleStartExam = async (paperId: string) => {
    setStartingId(paperId);
    try {
      const res = await apiFetch('/attempts', {
        method: 'POST',
        body: JSON.stringify({ paper_id: paperId, mode: 'assessment' })
      });
      navigate(`/student/attempt/${res.attempt_id}`);
    } catch (e: any) {
      alert(`Could not start assessment: ${e.message}`);
    } finally {
      setStartingId(null);
    }
  };

  if (loading) return <Spinner size="lg" className="h-64" />;
  if (!data) return <div>Student dashboard unavailable.</div>;

  const available = data.available_assessments || [];
  const recent = data.recent_attempts || [];
  const recommended = data.recommended_topics || [];
  const topicAcc = data.topic_accuracies || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Top Welcome Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-[#0F766E] to-[#115E59] text-white shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Badge variant="teal" className="bg-teal-800 text-teal-100 border-teal-700 mb-2">
            Student Assessment Portal
          </Badge>
          <h1 className="text-2xl font-bold">Welcome back, {data.user?.name || 'Student'}</h1>
          <p className="text-xs text-teal-100 mt-1 max-w-xl leading-relaxed">
            Prepare for college examinations with timed assessments and topic-grounded practice tests.
          </p>
        </div>

        <Link to="/student/practice">
          <Button variant="secondary" size="md" rightIcon={<ArrowRight className="w-4 h-4" />}>
            Browse Practice Sets
          </Button>
        </Link>
      </div>

      {/* Recommended Topics / Weak Area Alert */}
      {recommended.length > 0 && (
        <Alert
          type="warning"
          title="Recommended Focus Areas"
          action={
            <Link to="/student/practice">
              <Button variant="outline" size="sm">
                Targeted Practice
              </Button>
            </Link>
          }
        >
          Based on your historical quiz attempts, you scored below 60% in:{' '}
          <strong>{recommended.join(', ')}</strong>. Consider reviewing these sections before the final examination.
        </Alert>
      )}

      {/* Grid: Available Assessments + Recent Attempts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 cols): Available Assessments */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Available Examinations & Practice Sets</CardTitle>
                <p className="text-xs text-[#64748B]">Tests currently published by your professors</p>
              </div>
              <Link to="/student/practice">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  View All
                </Button>
              </Link>
            </CardHeader>
            <CardContent className="space-y-3 pt-0">
              {available.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs">
                  No examinations currently published for your section.
                </div>
              ) : (
                available.map((paper: any) => (
                  <div
                    key={paper.id}
                    className="p-4 rounded-xl border border-slate-200 hover:border-teal-300 transition-all bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant={paper.status === 'published' ? 'success' : 'teal'} size="sm">
                          {paper.status === 'published' ? 'Formal Examination' : 'Practice Set'}
                        </Badge>
                        <span className="text-[11px] font-mono text-slate-400">{paper.subject_id}</span>
                      </div>
                      <h3 className="font-bold text-sm text-[#0F172A]">{paper.title}</h3>
                      <div className="text-[11px] text-slate-500 flex items-center gap-3">
                        <span>{paper.question_count} Questions</span>
                        <span>•</span>
                        <span>{paper.total_marks} Marks</span>
                        <span>•</span>
                        <span>{paper.duration_minutes} Mins</span>
                      </div>
                    </div>

                    <Button
                      variant="teal"
                      size="sm"
                      onClick={() => handleStartExam(paper.id)}
                      isLoading={startingId === paper.id}
                      rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                    >
                      Start Assessment
                    </Button>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Recent Attempt History */}
          <Card>
            <CardHeader>
              <CardTitle>Your Recent Assessment Attempts</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {recent.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs">
                  You haven't attempted any assessments yet.
                </div>
              ) : (
                <div className="divide-y divide-[#F1F5F9] overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#F8FAFC] text-[#64748B] font-semibold border-b border-[#E2E8F0]">
                      <tr>
                        <th className="py-2.5 px-4">Exam Title</th>
                        <th className="py-2.5 px-4">Date</th>
                        <th className="py-2.5 px-4">Status</th>
                        <th className="py-2.5 px-4">Score</th>
                        <th className="py-2.5 px-4 text-right">Results</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {recent.map((att: any) => (
                        <tr key={att.id} className="hover:bg-slate-50 transition-colors">
                          <td className="py-3 px-4 font-semibold text-[#0F172A]">{att.title}</td>
                          <td className="py-3 px-4 text-slate-500">{formatDate(att.submitted_at || att.started_at)}</td>
                          <td className="py-3 px-4">
                            <Badge
                              variant={
                                att.status === 'graded'
                                  ? 'success'
                                  : att.status === 'awaiting_grading'
                                  ? 'warning'
                                  : 'info'
                              }
                              size="sm"
                            >
                              {att.status.replace('_', ' ')}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 font-bold text-[#0F172A]">
                            {att.final_score !== null
                              ? `${att.final_score} / ${att.total_possible_marks}`
                              : att.provisional_score !== null
                              ? `${att.provisional_score}* / ${att.total_possible_marks}`
                              : 'In progress'}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Link to={`/student/attempt/${att.id}/results`}>
                              <Button variant="outline" size="sm">
                                View Results
                              </Button>
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column (1 col): Topic Accuracies Widget */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
                Topic Mastery Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 pt-0">
              {topicAcc.length === 0 ? (
                <div className="text-xs text-slate-400 py-4 text-center">
                  Complete assessments to unlock topic performance statistics.
                </div>
              ) : (
                topicAcc.map((t: any, i: number) => (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-semibold text-slate-800 truncate max-w-[180px]">{t.topic_name}</span>
                      <span className="font-bold text-slate-900">{t.accuracy_percentage}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          t.accuracy_percentage >= 70
                            ? 'bg-emerald-600'
                            : t.accuracy_percentage >= 50
                            ? 'bg-amber-500'
                            : 'bg-rose-600'
                        }`}
                        style={{ width: `${Math.min(100, t.accuracy_percentage)}%` }}
                      />
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
