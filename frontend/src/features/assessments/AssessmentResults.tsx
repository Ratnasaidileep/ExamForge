import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Award, CheckCircle2, XCircle, Clock, BookOpen,
  ArrowLeft, ShieldCheck, AlertCircle, BarChart3, HelpCircle
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatDate } from '@/lib/formatters';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';

export const AssessmentResults: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [results, setResults] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!attemptId) return;
    setLoading(true);
    apiFetch(`/attempts/${attemptId}/results`)
      .then(setResults)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [attemptId]);

  if (loading) return <Spinner size="lg" className="h-64" />;
  if (!results) return <div>Assessment results unavailable.</div>;

  const isFullyGraded = results.is_fully_graded;
  const questions = results.questions || [];

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <button
            onClick={() => navigate('/student/dashboard')}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-[#0F766E] mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Student Dashboard</span>
          </button>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-[#0F172A]">{results.title}</h1>
            <Badge variant={isFullyGraded ? 'success' : 'warning'}>
              {results.status.replace('_', ' ').toUpperCase()}
            </Badge>
          </div>
          <p className="text-xs text-[#64748B]">
            Submitted on {formatDate(results.submitted_at)}
          </p>
        </div>

        <Link to="/student/practice">
          <Button variant="outline" size="sm">
            Try Another Test
          </Button>
        </Link>
      </div>

      {/* Evaluation Status Banner */}
      {!isFullyGraded ? (
        <Alert
          type="info"
          title="Descriptive Answers Awaiting Evaluation"
        >
          Your objective multiple choice questions have been automatically scored. Short and long descriptive answers have been queued for your professor's review. Your provisional score will update once grading is finalized.
        </Alert>
      ) : (
        <Alert
          type="success"
          title="Grading Finalized"
        >
          Your professor has completed manual grading and feedback evaluation for all descriptive answers.
        </Alert>
      )}

      {/* Scores Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="bg-emerald-50/50 border-emerald-200">
          <CardContent className="p-5 text-center space-y-1">
            <span className="text-xs text-emerald-800 font-semibold uppercase tracking-wider block">
              Objective MCQ Score
            </span>
            <span className="text-3xl font-extrabold text-emerald-950 font-mono block">
              {results.objective_score ?? 0}
            </span>
            <span className="text-[11px] text-emerald-700 block">Auto-graded on submission</span>
          </CardContent>
        </Card>

        <Card className="bg-indigo-50/50 border-indigo-200">
          <CardContent className="p-5 text-center space-y-1">
            <span className="text-xs text-[#3730A3] font-semibold uppercase tracking-wider block">
              {isFullyGraded ? 'Final Total Score' : 'Provisional Score'}
            </span>
            <span className="text-3xl font-extrabold text-[#3730A3] font-mono block">
              {isFullyGraded ? results.final_score : results.provisional_score ?? 0}
              <span className="text-sm font-normal text-slate-500"> / {results.total_possible_marks}</span>
            </span>
            <span className="text-[11px] text-indigo-700 block">
              {isFullyGraded ? 'Evaluation Complete' : '*Pending descriptive answers'}
            </span>
          </CardContent>
        </Card>

        <Card className="bg-slate-50 border-slate-200">
          <CardContent className="p-5 text-center space-y-1">
            <span className="text-xs text-slate-600 font-semibold uppercase tracking-wider block">
              Question Summary
            </span>
            <div className="text-sm font-bold text-slate-800 flex items-center justify-center gap-3 pt-2">
              <span className="text-emerald-700">{results.correct_count} Correct</span>
              <span>•</span>
              <span className="text-rose-700">{results.incorrect_count} Incorrect</span>
              <span>•</span>
              <span className="text-amber-700">{results.pending_grading_count} Pending</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Topic Breakdown */}
      {results.topic_performance && results.topic_performance.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
              Topic-Wise Performance Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#F8FAFC] text-[#64748B] font-semibold border-b border-[#E2E8F0]">
                  <tr>
                    <th className="py-2.5 px-4">Topic</th>
                    <th className="py-2.5 px-4">Questions</th>
                    <th className="py-2.5 px-4">Marks Earned</th>
                    <th className="py-2.5 px-4">Accuracy</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {results.topic_performance.map((tp: any, idx: number) => (
                    <tr key={idx}>
                      <td className="py-3 px-4 font-semibold text-slate-900">{tp.topic_name}</td>
                      <td className="py-3 px-4 text-slate-600">{tp.questions_count}</td>
                      <td className="py-3 px-4 font-bold text-slate-800">
                        {tp.earned_marks} / {tp.total_marks}
                      </td>
                      <td className="py-3 px-4">
                        <Badge
                          variant={tp.accuracy_percentage >= 70 ? 'success' : tp.accuracy_percentage >= 50 ? 'warning' : 'error'}
                          size="sm"
                        >
                          {tp.accuracy_percentage}%
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Per-Question Detailed Review */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-[#0F172A] pt-2">Detailed Question Review & Explanations</h2>

        {questions.map((q: any, idx: number) => {
          const isMcq = q.question_type === 'mcq';
          const isPending = q.grading_status === 'pending';

          return (
            <Card key={idx} className="overflow-hidden">
              <CardContent className="p-5 space-y-3">
                {/* Header */}
                <div className="flex items-center justify-between text-xs pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[#3730A3]">Question {idx + 1}</span>
                    <Badge variant="neutral" size="sm" className="uppercase font-semibold">
                      {q.question_type.replace('_', ' ')}
                    </Badge>
                    <Badge variant="indigo" size="sm">{q.marks_allocated} Marks</Badge>
                  </div>

                  <div>
                    {isPending ? (
                      <Badge variant="warning" size="sm">Awaiting Faculty Grading</Badge>
                    ) : isMcq ? (
                      q.is_correct ? (
                        <Badge variant="success" size="sm">Correct (+{q.marks_awarded}M)</Badge>
                      ) : (
                        <Badge variant="error" size="sm">Incorrect (0M)</Badge>
                      )
                    ) : (
                      <Badge variant="success" size="sm">Awarded: {q.marks_awarded} / {q.marks_allocated}M</Badge>
                    )}
                  </div>
                </div>

                {/* Question Text */}
                <div className="text-xs font-semibold text-[#0F172A] leading-relaxed">
                  {q.question_text}
                </div>

                {/* Submitted Answer Display */}
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
                  <span className="font-bold text-slate-700 block">Your Submitted Answer:</span>
                  <div className="text-slate-800 whitespace-pre-wrap leading-relaxed">
                    {q.submitted_answer || <span className="italic text-slate-400">No answer submitted.</span>}
                  </div>
                </div>

                {/* Released Correct Answer for MCQs */}
                {isMcq && q.correct_answer && (
                  <div className="p-2.5 bg-emerald-50 rounded-lg border border-emerald-200 text-xs text-emerald-900 font-medium">
                    <strong>Correct Answer:</strong> {q.correct_answer}
                  </div>
                )}

                {/* Released Model Answer for Descriptive */}
                {!isMcq && q.model_answer && (
                  <div className="p-3 bg-indigo-50/60 rounded-lg border border-indigo-200 text-xs space-y-1 text-slate-800">
                    <span className="font-bold text-[#3730A3] block">Reference Model Answer:</span>
                    <p className="whitespace-pre-wrap leading-relaxed">{q.model_answer}</p>
                  </div>
                )}

                {/* Explanation */}
                {q.explanation && (
                  <div className="text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded border border-slate-200 leading-relaxed">
                    <strong>Explanation:</strong> {q.explanation}
                  </div>
                )}

                {/* Faculty Feedback */}
                {q.faculty_feedback && (
                  <div className="p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-900">
                    <strong>Faculty Feedback:</strong> {q.faculty_feedback}
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
