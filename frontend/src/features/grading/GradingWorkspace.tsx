import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  CheckSquare, ArrowLeft, CheckCircle2, AlertCircle, ShieldCheck,
  Save, Send, BookOpen, User, HelpCircle
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatDate } from '@/lib/formatters';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';

export const GradingWorkspace: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [grades, setGrades] = useState<{ [responseId: string]: { marks: number | string; feedback: string } }>({});
  const [savingId, setSavingId] = useState<string | null>(null);
  const [finalizing, setFinalizing] = useState(false);

  const loadWorkspace = async () => {
    if (!attemptId) return;
    setLoading(true);
    try {
      const res = await apiFetch(`/grading/attempts/${attemptId}`);
      setData(res);
      // Initialize grades state
      const initial: any = {};
      (res.responses_to_grade || []).forEach((r: any) => {
        initial[r.response_id] = {
          marks: r.marks_awarded !== null ? r.marks_awarded : '',
          feedback: r.faculty_feedback || ''
        };
      });
      setGrades(initial);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkspace();
  }, [attemptId]);

  const handleSaveGrade = async (respId: string, maxMarks: number) => {
    const current = grades[respId];
    if (current.marks === '' || current.marks === null || current.marks === undefined) {
      alert('Please enter a marks value.');
      return;
    }
    const numMarks = Number(current.marks);
    if (isNaN(numMarks) || numMarks < 0 || numMarks > maxMarks) {
      alert(`Awarded marks must be between 0 and maximum possible marks (${maxMarks}).`);
      return;
    }

    setSavingId(respId);
    try {
      await apiFetch(`/grading/responses/${respId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          marks_awarded: numMarks,
          faculty_feedback: current.feedback
        })
      });
      await loadWorkspace();
    } catch (e: any) {
      alert(`Save failed: ${e.message}`);
    } finally {
      setSavingId(null);
    }
  };

  const handleFinalize = async () => {
    if (!confirm('Are you sure you want to finalize grading? This will calculate the final score and notify the student.')) {
      return;
    }

    setFinalizing(true);
    try {
      await apiFetch(`/grading/attempts/${attemptId}/finalize`, {
        method: 'POST',
        body: JSON.stringify({})
      });
      alert('Grading finalized successfully!');
      navigate('/faculty/grading');
    } catch (e: any) {
      alert(`Finalization blocked: ${e.message}`);
    } finally {
      setFinalizing(false);
    }
  };

  if (loading) return <Spinner size="lg" className="h-64" />;
  if (!data) return <div>Grading workspace data unavailable.</div>;

  const responses = data.responses_to_grade || [];
  const pendingCount = responses.filter((r: any) => r.grading_status === 'pending').length;

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <button
            onClick={() => navigate('/faculty/grading')}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-[#3730A3] mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Grading Queue</span>
          </button>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-[#0F172A]">{data.title}</h1>
            <Badge variant="indigo">Student: {data.student_name}</Badge>
            <Badge
              variant={data.status === 'graded' ? 'success' : 'warning'}
            >
              {data.status.replace('_', ' ').toUpperCase()}
            </Badge>
          </div>
          <p className="text-xs text-[#64748B]">
            Submitted on {formatDate(data.submitted_at)} • Student ID: {data.student_id} ({data.student_email})
          </p>
        </div>

        {/* Finalize Button */}
        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            onClick={handleFinalize}
            disabled={!data.can_finalize}
            isLoading={finalizing}
            leftIcon={<CheckCircle2 className="w-4 h-4" />}
          >
            Finalize Evaluation & Release
          </Button>
        </div>
      </div>

      {/* Score Summary Card */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="bg-emerald-50/50 border-emerald-200">
          <CardContent className="p-4">
            <span className="text-xs text-emerald-800 font-semibold block">Auto-Graded MCQs</span>
            <span className="text-2xl font-bold text-emerald-900">{data.objective_score ?? 0} Marks</span>
            <span className="text-[11px] text-emerald-700 block mt-0.5">Objective scoring complete</span>
          </CardContent>
        </Card>

        <Card className="bg-indigo-50/50 border-indigo-200">
          <CardContent className="p-4">
            <span className="text-xs text-[#3730A3] font-semibold block">Provisional Score</span>
            <span className="text-2xl font-bold text-[#3730A3]">{data.provisional_score ?? 0} Marks</span>
            <span className="text-[11px] text-indigo-700 block mt-0.5">Objective + graded descriptive</span>
          </CardContent>
        </Card>

        <Card className="bg-amber-50/50 border-amber-200">
          <CardContent className="p-4">
            <span className="text-xs text-amber-800 font-semibold block">Descriptive Status</span>
            <span className="text-2xl font-bold text-amber-900">{pendingCount} Pending</span>
            <span className="text-[11px] text-amber-700 block mt-0.5">
              {pendingCount === 0 ? 'All graded! Ready to finalize.' : 'Award marks below to proceed.'}
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Descriptive Responses to Grade */}
      <div className="space-y-5">
        {responses.map((resp: any, idx: number) => {
          const maxMarks = resp.marks_allocated;
          const currentInput = grades[resp.response_id] || { marks: '', feedback: '' };
          const isGraded = resp.grading_status === 'manually_graded';

          return (
            <Card
              key={resp.response_id}
              className={`transition-all ${
                isGraded ? 'border-emerald-200 bg-white' : 'border-amber-200 bg-amber-50/10'
              }`}
            >
              <CardContent className="p-5 space-y-4">
                {/* Header */}
                <div className="flex items-center justify-between text-xs pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[#3730A3]">Question {idx + 1}</span>
                    <Badge variant="neutral" size="sm" className="uppercase font-semibold">
                      {resp.question_type.replace('_', ' ')}
                    </Badge>
                    <Badge variant="indigo" size="sm">Max Marks: {maxMarks}M</Badge>
                  </div>
                  <Badge variant={isGraded ? 'success' : 'warning'} size="sm">
                    {isGraded ? `Awarded: ${resp.marks_awarded}M` : 'Pending Grade'}
                  </Badge>
                </div>

                {/* Question Text */}
                <div className="text-xs font-semibold text-[#0F172A] leading-relaxed">
                  {resp.question_text}
                </div>

                {/* Student's Submitted Answer */}
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
                  <span className="font-bold text-slate-700 block">Student's Submitted Answer:</span>
                  <div className="text-slate-800 whitespace-pre-wrap leading-relaxed font-sans">
                    {resp.submitted_answer || <span className="italic text-slate-400">No answer provided.</span>}
                  </div>
                </div>

                {/* Model Answer & Rubric (Faculty Eyes Only) */}
                <div className="p-3 bg-indigo-50/60 rounded-lg border border-indigo-200 text-xs space-y-2">
                  <div className="flex items-center gap-1.5 font-bold text-[#3730A3]">
                    <ShieldCheck className="w-4 h-4 text-[#3730A3]" />
                    <span>Faculty Model Answer & Grading Rubric</span>
                  </div>
                  {resp.model_answer && (
                    <div className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                      <strong>Model Answer:</strong><br />
                      {resp.model_answer}
                    </div>
                  )}
                  {resp.rubric_json && resp.rubric_json.length > 0 && (
                    <div className="pt-2 border-t border-indigo-100">
                      <strong>Rubric Criteria:</strong>
                      <ul className="list-disc pl-4 space-y-0.5 text-slate-600 mt-1">
                        {resp.rubric_json.map((r: any, rI: number) => (
                          <li key={rI}>
                            {r.criteria || r.criterion} — <span className="font-bold">{r.marks}M</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Marks Allocator and Feedback Form */}
                <div className="p-4 bg-slate-50/80 rounded-lg border border-slate-200 space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
                    <div>
                      <label className="block text-xs font-bold text-[#0F172A] mb-1">
                        Award Marks (0 to {maxMarks})
                      </label>
                      <input
                        type="number"
                        step="0.5"
                        min="0"
                        max={maxMarks}
                        value={currentInput.marks}
                        onChange={(e) => {
                          setGrades({
                            ...grades,
                            [resp.response_id]: {
                              ...currentInput,
                              marks: e.target.value
                            }
                          });
                        }}
                        placeholder={`0 - ${maxMarks}`}
                        className="w-full text-xs font-bold font-mono py-1.5 px-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                      />
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-xs font-medium text-slate-600 mb-1">
                        Faculty Feedback / Notes
                      </label>
                      <input
                        type="text"
                        value={currentInput.feedback}
                        onChange={(e) => {
                          setGrades({
                            ...grades,
                            [resp.response_id]: {
                              ...currentInput,
                              feedback: e.target.value
                            }
                          });
                        }}
                        placeholder="e.g. Excellent explanation of DSRC IEEE 802.11p latency."
                        className="w-full text-xs py-1.5 px-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                      />
                    </div>

                    <div>
                      <Button
                        variant={isGraded ? 'secondary' : 'teal'}
                        size="sm"
                        className="w-full justify-center"
                        leftIcon={<Save className="w-3.5 h-3.5" />}
                        onClick={() => handleSaveGrade(resp.response_id, maxMarks)}
                        isLoading={savingId === resp.response_id}
                      >
                        {isGraded ? 'Update Marks' : 'Save Marks'}
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
