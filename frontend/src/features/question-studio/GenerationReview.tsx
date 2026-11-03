import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Sparkles, CheckCircle2, XCircle, Edit3, ShieldCheck,
  AlertTriangle, BookOpen, Layers, ArrowLeft, Check,
  Copy, Trash2, RotateCw
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';
import { MathText } from '@/components/ui/MathText';

export const GenerationReview: React.FC = () => {
  const { generationId } = useParams<{ generationId: string }>();
  const navigate = useNavigate();

  const [job, setJob] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [editQuestion, setEditQuestion] = useState<any | null>(null);
  const [isApproving, setIsApproving] = useState<string | null>(null);
  const [isBatchApproving, setIsBatchApproving] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState<string | null>(null);

  const handleDuplicate = async (qId: string) => {
    try {
      await apiFetch(`/generations/questions/${qId}/duplicate`, { method: 'POST' });
      loadJob();
    } catch (e: any) {
      alert(`Duplicate failed: ${e.message}`);
    }
  };

  const handleDiscard = async (qId: string) => {
    if (!confirm('Discard this draft question?')) return;
    try {
      await apiFetch(`/generations/questions/${qId}`, { method: 'DELETE' });
      loadJob();
    } catch (e: any) {
      alert(`Discard failed: ${e.message}`);
    }
  };

  const handleRegenerate = async (qId: string) => {
    setIsRegenerating(qId);
    try {
      await apiFetch(`/generations/questions/${qId}/regenerate`, { method: 'POST' });
      loadJob();
    } catch (e: any) {
      alert(`Regeneration failed: ${e.message}`);
    } finally {
      setIsRegenerating(null);
    }
  };

  const loadJob = () => {
    if (!generationId) return;
    setLoading(true);
    apiFetch(`/generations/${generationId}`)
      .then(setJob)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadJob();
  }, [generationId]);

  const handleApproveSingle = async (qId: string) => {
    setIsApproving(qId);
    try {
      await apiFetch(`/generations/questions/${qId}/approve`, { method: 'POST' });
      loadJob();
    } catch (e: any) {
      alert(`Approval failed: ${e.message}`);
    } finally {
      setIsApproving(null);
    }
  };

  const handleBatchApprove = async () => {
    if (!job?.generated_questions) return;
    const pendingIds = job.generated_questions
      .filter((q: any) => q.review_status !== 'approved')
      .map((q: any) => q.id);

    if (pendingIds.length === 0) return;

    setIsBatchApproving(true);
    try {
      await apiFetch('/generations/batch-approve', {
        method: 'POST',
        body: JSON.stringify({ question_ids: pendingIds })
      });
      loadJob();
    } catch (e: any) {
      alert(`Batch approval failed: ${e.message}`);
    } finally {
      setIsBatchApproving(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editQuestion) return;
    try {
      await apiFetch(`/generations/questions/${editQuestion.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          question_text: editQuestion.question_text,
          difficulty: editQuestion.difficulty,
          marks: Number(editQuestion.marks),
          correct_answer: editQuestion.correct_answer,
          model_answer: editQuestion.model_answer,
          explanation: editQuestion.explanation
        })
      });
      setEditQuestion(null);
      loadJob();
    } catch (e: any) {
      alert(`Update failed: ${e.message}`);
    }
  };

  if (loading) return <Spinner size="lg" className="h-64" />;

  const questions = job?.generated_questions || [];
  const pendingCount = questions.filter((q: any) => q.review_status !== 'approved').length;

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <button
            onClick={() => navigate('/faculty/generate')}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-[#3730A3] mb-1 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Question Studio</span>
          </button>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-[#0F172A]">Generation Review & Question Editor</h1>
            <Badge variant="indigo">{questions.length} Generated</Badge>
          </div>
          <p className="text-xs text-[#64748B]">
            Inspect AI grounding citations, edit model answers, and approve questions into the Central Question Bank.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {pendingCount > 0 && (
            <Button
              variant="teal"
              leftIcon={<Check className="w-4 h-4" />}
              onClick={handleBatchApprove}
              isLoading={isBatchApproving}
            >
              Approve All ({pendingCount})
            </Button>
          )}
          <Button
            variant="outline"
            leftIcon={<Layers className="w-4 h-4" />}
            onClick={() => navigate('/faculty/questions')}
          >
            Go to Question Bank
          </Button>
        </div>
      </div>

      {/* Questions Review List */}
      <div className="space-y-4">
        {questions.map((q: any, idx: number) => {
          const isApproved = q.review_status === 'approved';

          return (
            <Card
              key={q.id}
              className={`transition-all ${
                isApproved ? 'border-emerald-200 bg-emerald-50/20' : 'hover:border-indigo-300'
              }`}
            >
              <CardContent className="p-5 space-y-4">
                {/* Meta row */}
                <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[#3730A3]">Q{idx + 1}.</span>
                    <Badge variant="neutral" size="sm" className="uppercase font-semibold">
                      {q.question_type.replace('_', ' ')}
                    </Badge>
                    <Badge
                      variant={
                        q.difficulty === 'easy'
                          ? 'success'
                          : q.difficulty === 'hard'
                          ? 'error'
                          : 'warning'
                      }
                      size="sm"
                      className="capitalize"
                    >
                      {q.difficulty}
                    </Badge>
                    <Badge variant="indigo" size="sm">{q.marks} Marks</Badge>
                    {q.topic_name && (
                      <span className="text-slate-500 text-[11px] font-medium truncate max-w-[200px]">
                        • {q.topic_name}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        q.confidence_flag === 'grounded'
                          ? 'success'
                          : q.confidence_flag === 'partially_grounded'
                          ? 'warning'
                          : 'error'
                      }
                      size="sm"
                    >
                      {q.confidence_flag === 'grounded' ? 'Verified Grounded' : q.confidence_flag}
                    </Badge>
                    {isApproved ? (
                      <Badge variant="success" size="sm">Approved</Badge>
                    ) : (
                      <Badge variant="warning" size="sm">Draft Review</Badge>
                    )}
                  </div>
                </div>

                {/* Question Text */}
                <div className="text-sm font-semibold text-[#0F172A] leading-relaxed">
                  <MathText text={q.question_text} />
                </div>

                {/* MCQ Options */}
                {q.question_type === 'mcq' && q.options_json && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {q.options_json.map((opt: string, optIdx: number) => {
                      const isCorrect = q.correct_answer === opt || q.correct_answer === String.fromCharCode(65 + optIdx);
                      return (
                        <div
                          key={optIdx}
                          className={`p-2.5 rounded-lg border text-xs flex items-start gap-2 ${
                            isCorrect
                              ? 'bg-emerald-50 border-emerald-300 text-emerald-900 font-medium'
                              : 'bg-slate-50 border-slate-200 text-slate-700'
                          }`}
                        >
                          <span className="font-bold">{String.fromCharCode(65 + optIdx)}.</span>
                          <span><MathText text={opt} /></span>
                          {isCorrect && (
                            <span className="ml-auto text-[10px] text-emerald-700 font-bold uppercase">Correct</span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Descriptive Model Answer & Rubric */}
                {q.question_type !== 'mcq' && (
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-2 text-xs">
                    {q.model_answer && (
                      <div>
                        <span className="font-bold text-[#1E293B] block mb-1">Model Answer:</span>
                        <MathText text={q.model_answer} className="text-slate-700 leading-relaxed whitespace-pre-wrap block" />
                      </div>
                    )}
                    {q.rubric_json && q.rubric_json.length > 0 && (
                      <div className="pt-2 border-t border-slate-200">
                        <span className="font-bold text-[#1E293B] block mb-1">Grading Rubric:</span>
                        <ul className="list-disc pl-4 space-y-1 text-slate-600">
                          {q.rubric_json.map((r: any, rIdx: number) => (
                            <li key={rIdx}>
                              {r.criteria || r.criterion} — <span className="font-semibold">{r.marks}M</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Grounding Source Evidence Excerpt */}
                {q.supporting_excerpt && (
                  <div className="p-3 bg-amber-50/50 border border-amber-200/80 rounded-lg text-xs space-y-1">
                    <div className="flex items-center gap-1.5 font-bold text-amber-900">
                      <ShieldCheck className="w-4 h-4 text-amber-700" />
                      <span>Supporting Curriculum Excerpt:</span>
                    </div>
                    <blockquote className="italic text-slate-700 border-l-2 border-amber-400 pl-2 py-0.5 text-[11px] leading-relaxed">
                      "{q.supporting_excerpt}"
                    </blockquote>
                  </div>
                )}

                {/* Question Actions Footer */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100">
                  <div className="flex items-center gap-1.5">
                    {!isApproved && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        leftIcon={<Trash2 className="w-3.5 h-3.5" />}
                        onClick={() => handleDiscard(q.id)}
                      >
                        Discard
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      leftIcon={<Copy className="w-3.5 h-3.5" />}
                      onClick={() => handleDuplicate(q.id)}
                    >
                      Duplicate
                    </Button>
                    {!isApproved && (
                      <Button
                        variant="ghost"
                        size="sm"
                        leftIcon={<RotateCw className="w-3.5 h-3.5" />}
                        onClick={() => handleRegenerate(q.id)}
                        isLoading={isRegenerating === q.id}
                      >
                        Regenerate
                      </Button>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      leftIcon={<Edit3 className="w-3.5 h-3.5" />}
                      onClick={() => setEditQuestion({ ...q })}
                    >
                      Edit Question
                    </Button>
                    {!isApproved && (
                      <Button
                        variant="teal"
                        size="sm"
                        leftIcon={<CheckCircle2 className="w-3.5 h-3.5" />}
                        onClick={() => handleApproveSingle(q.id)}
                        isLoading={isApproving === q.id}
                      >
                        Approve Question
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Edit Question Modal */}
      <Modal
        isOpen={!!editQuestion}
        onClose={() => setEditQuestion(null)}
        title="Edit Generated Question"
        maxWidth="2xl"
        footer={
          <>
            <Button variant="secondary" onClick={() => setEditQuestion(null)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSaveEdit}>
              Save Changes
            </Button>
          </>
        }
      >
        {editQuestion && (
          <div className="space-y-4 text-xs">
            <div>
              <label className="block text-xs font-semibold text-[#1E293B] mb-1">Question Text</label>
              <textarea
                rows={3}
                value={editQuestion.question_text || ''}
                onChange={(e) => setEditQuestion({ ...editQuestion, question_text: e.target.value })}
                className="w-full text-xs rounded-lg border border-slate-300 p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Select
                label="Difficulty"
                value={editQuestion.difficulty || 'medium'}
                onChange={(e) => setEditQuestion({ ...editQuestion, difficulty: e.target.value })}
                options={[
                  { value: 'easy', label: 'Easy' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'hard', label: 'Hard' }
                ]}
              />
              <Input
                label="Marks"
                type="number"
                value={editQuestion.marks || 2}
                onChange={(e) => setEditQuestion({ ...editQuestion, marks: e.target.value })}
              />
            </div>

            {editQuestion.question_type === 'mcq' ? (
              <Input
                label="Correct Answer (Exact text or letter)"
                value={editQuestion.correct_answer || ''}
                onChange={(e) => setEditQuestion({ ...editQuestion, correct_answer: e.target.value })}
              />
            ) : (
              <div>
                <label className="block text-xs font-semibold text-[#1E293B] mb-1">Model Answer</label>
                <textarea
                  rows={4}
                  value={editQuestion.model_answer || ''}
                  onChange={(e) => setEditQuestion({ ...editQuestion, model_answer: e.target.value })}
                  className="w-full text-xs rounded-lg border border-slate-300 p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-[#1E293B] mb-1">Explanation</label>
              <textarea
                rows={2}
                value={editQuestion.explanation || ''}
                onChange={(e) => setEditQuestion({ ...editQuestion, explanation: e.target.value })}
                className="w-full text-xs rounded-lg border border-slate-300 p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
