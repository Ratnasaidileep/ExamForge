import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText, Sparkles, Layers, CheckSquare, Plus,
  ArrowRight, Users, Clock, AlertCircle, CheckCircle2, BookOpen
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatDate } from '@/lib/formatters';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';

export const FacultyDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch('/dashboard/faculty')
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner size="lg" className="h-64" />;

  const m = data?.metrics || {};
  const activity = data?.recent_activity || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Header with Title and Prominent Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-[#0F172A]">Faculty Command Dashboard</h1>
            <Badge variant="indigo">Subject: ITS-401</Badge>
          </div>
          <p className="text-xs text-[#64748B]">
            Overview of questions, curriculum documents, examination papers, and pending student grading.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Link to="/faculty/documents">
            <Button variant="secondary" size="sm" leftIcon={<FileText className="w-3.5 h-3.5" />}>
              Upload Notes
            </Button>
          </Link>
          <Link to="/faculty/generate">
            <Button variant="teal" size="sm" leftIcon={<Sparkles className="w-3.5 h-3.5" />}>
              Generate Questions
            </Button>
          </Link>
          <Link to="/faculty/papers/new">
            <Button variant="primary" size="sm" leftIcon={<Plus className="w-3.5 h-3.5" />}>
              Build Question Paper
            </Button>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="hover:border-indigo-300 transition-colors">
          <CardContent className="p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-medium">Uploaded Notes</span>
              <FileText className="w-4 h-4 text-[#3730A3]" />
            </div>
            <div className="text-2xl font-bold text-[#0F172A]">{m.uploaded_documents ?? 0}</div>
            <div className="text-[11px] text-slate-500">Curriculum documents</div>
          </CardContent>
        </Card>

        <Card className="hover:border-indigo-300 transition-colors">
          <CardContent className="p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-medium">Approved Questions</span>
              <CheckCircle2 className="w-4 h-4 text-[#15803D]" />
            </div>
            <div className="text-2xl font-bold text-[#0F172A]">{m.approved_questions ?? 0}</div>
            <div className="text-[11px] text-slate-500">
              {m.questions_awaiting_review ? `${m.questions_awaiting_review} awaiting review` : 'All reviewed'}
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-indigo-300 transition-colors">
          <CardContent className="p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-medium">Published Papers</span>
              <Layers className="w-4 h-4 text-[#0F766E]" />
            </div>
            <div className="text-2xl font-bold text-[#0F172A]">{m.published_papers ?? 0}</div>
            <div className="text-[11px] text-slate-500">{m.draft_papers ?? 0} draft papers</div>
          </CardContent>
        </Card>

        <Card className={`transition-colors ${m.pending_grading_count > 0 ? 'bg-amber-50/50 border-amber-200' : ''}`}>
          <CardContent className="p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-medium">Grading Queue</span>
              <CheckSquare className="w-4 h-4 text-[#B45309]" />
            </div>
            <div className="text-2xl font-bold text-[#B45309]">{m.pending_grading_count ?? 0}</div>
            <div className="text-[11px] text-amber-700 font-medium">
              {m.pending_grading_count > 0 ? 'Submissions require evaluation' : 'Queue is clear'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Banners & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recent Student Submissions & Activity */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Recent Student Submissions</CardTitle>
                <p className="text-xs text-[#64748B]">Latest exam submissions and scoring status</p>
              </div>
              <Link to="/faculty/grading">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  View All in Queue
                </Button>
              </Link>
            </CardHeader>
            <CardContent className="p-0">
              {activity.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">No student attempts recorded yet.</div>
              ) : (
                <div className="divide-y divide-[#F1F5F9] overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#F8FAFC] text-[#64748B] font-semibold border-b border-[#E2E8F0]">
                      <tr>
                        <th className="py-2.5 px-4">Student</th>
                        <th className="py-2.5 px-4">Exam / Paper</th>
                        <th className="py-2.5 px-4">Submitted</th>
                        <th className="py-2.5 px-4">Score</th>
                        <th className="py-2.5 px-4">Status</th>
                        <th className="py-2.5 px-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {activity.map((att: any) => (
                        <tr key={att.id} className="hover:bg-slate-50 transition-colors">
                          <td className="py-3 px-4 font-medium text-[#0F172A]">{att.student_name}</td>
                          <td className="py-3 px-4 text-slate-600 truncate max-w-[200px]">{att.title}</td>
                          <td className="py-3 px-4 text-slate-500">{formatDate(att.submitted_at)}</td>
                          <td className="py-3 px-4 font-semibold text-[#0F172A]">
                            {att.score !== null ? `${att.score} / ${att.max_score}` : 'Pending'}
                          </td>
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
                          <td className="py-3 px-4 text-right">
                            <Link to={`/faculty/grading/${att.id}`}>
                              <Button variant="outline" size="sm">
                                {att.status === 'graded' ? 'Review' : 'Grade'}
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

        {/* Right Column: Workflow Steps & Quick Navigation */}
        <div className="space-y-4">
          <Card className="bg-gradient-to-br from-[#3730A3]/5 to-transparent border-indigo-100">
            <CardHeader>
              <CardTitle className="text-sm text-[#3730A3]">Faculty Exam Creation Workflow</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 pt-0">
              <Link to="/faculty/documents" className="flex items-start gap-3 p-2.5 rounded-lg bg-white border border-slate-200 hover:border-[#3730A3] transition-all">
                <div className="w-6 h-6 rounded-full bg-indigo-50 text-[#3730A3] flex items-center justify-center font-bold text-xs flex-shrink-0">
                  1
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#0F172A]">Upload Course Notes</h4>
                  <p className="text-[11px] text-slate-500">Provide lecture PDFs or DOCX files for topic extraction.</p>
                </div>
              </Link>

              <Link to="/faculty/generate" className="flex items-start gap-3 p-2.5 rounded-lg bg-white border border-slate-200 hover:border-[#3730A3] transition-all">
                <div className="w-6 h-6 rounded-full bg-teal-50 text-[#0F766E] flex items-center justify-center font-bold text-xs flex-shrink-0">
                  2
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#0F172A]">AI Question Studio</h4>
                  <p className="text-[11px] text-slate-500">Generate grounded MCQs and descriptive questions with Gemini.</p>
                </div>
              </Link>

              <Link to="/faculty/questions" className="flex items-start gap-3 p-2.5 rounded-lg bg-white border border-slate-200 hover:border-[#3730A3] transition-all">
                <div className="w-6 h-6 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs flex-shrink-0">
                  3
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#0F172A]">Approve & Manage Bank</h4>
                  <p className="text-[11px] text-slate-500">Review citations, edit model answers, and approve questions.</p>
                </div>
              </Link>

              <Link to="/faculty/papers/new" className="flex items-start gap-3 p-2.5 rounded-lg bg-white border border-slate-200 hover:border-[#3730A3] transition-all">
                <div className="w-6 h-6 rounded-full bg-indigo-50 text-[#3730A3] flex items-center justify-center font-bold text-xs flex-shrink-0">
                  4
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#0F172A]">Assemble & Export Paper</h4>
                  <p className="text-[11px] text-slate-500">Validate blueprints, export official question paper & answer key PDFs.</p>
                </div>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
