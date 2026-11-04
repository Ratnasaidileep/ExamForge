import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Database, Search, Filter, Edit3, Archive, CheckCircle2,
  FileText, ShieldCheck, History, Plus, ChevronLeft, ChevronRight, Copy
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatDate } from '@/lib/formatters';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Spinner } from '@/components/ui/Spinner';
import { MathText } from '@/components/ui/MathText';

export const QuestionBank: React.FC = () => {
  const [data, setData] = useState<any>({ items: [], total: 0, page: 1, total_pages: 1 });
  const [subjects, setSubjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [questionType, setQuestionType] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);

  // Modals
  const [selectedQuestion, setSelectedQuestion] = useState<any | null>(null);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editData, setEditData] = useState<any>({});
  const [savingEdit, setSavingEdit] = useState(false);

  useEffect(() => {
    apiFetch<any[]>('/subjects')
      .then(setSubjects)
      .catch(console.error);
  }, []);

  const loadQuestions = () => {
    setLoading(true);
    const params = new URLSearchParams({
      page: String(page),
      page_size: '10'
    });
    if (search) params.append('search', search);
    if (subjectFilter) params.append('subject_id', subjectFilter);
    if (questionType) params.append('question_type', questionType);
    if (difficulty) params.append('difficulty', difficulty);
    if (status) params.append('status', status);

    apiFetch(`/questions?${params.toString()}`)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQuestions();
  }, [page, search, subjectFilter, questionType, difficulty, status]);

  const handleOpenEdit = (q: any) => {
    const rev = q.current_revision || {};
    setEditData({
      id: q.id,
      question_text: rev.question_text || '',
      difficulty: rev.difficulty || 'medium',
      marks: rev.marks || 2,
      model_answer: rev.model_answer || '',
      correct_answer: rev.correct_answer || '',
      explanation: rev.explanation || ''
    });
    setEditModalOpen(true);
  };

  const handleSaveEdit = async () => {
    setSavingEdit(true);
    try {
      await apiFetch(`/questions/${editData.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          question_text: editData.question_text,
          difficulty: editData.difficulty,
          marks: Number(editData.marks),
          model_answer: editData.model_answer,
          correct_answer: editData.correct_answer,
          explanation: editData.explanation,
          requires_reapproval: true
        })
      });
      setEditModalOpen(false);
      loadQuestions();
    } catch (e: any) {
      alert(`Edit failed: ${e.message}`);
    } finally {
      setSavingEdit(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await apiFetch(`/questions/${id}/approve`, { method: 'POST' });
      loadQuestions();
    } catch (e: any) {
      alert(`Approval failed: ${e.message}`);
    }
  };

  const handleArchive = async (id: string) => {
    if (!confirm('Are you sure you want to archive this question?')) return;
    try {
      await apiFetch(`/questions/${id}/archive`, { method: 'POST' });
      loadQuestions();
    } catch (e: any) {
      alert(`Archive failed: ${e.message}`);
    }
  };

  const handleDuplicate = async (id: string) => {
    try {
      await apiFetch(`/questions/${id}/duplicate`, { method: 'POST' });
      loadQuestions();
    } catch (e: any) {
      alert(`Duplicate failed: ${e.message}`);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-[#0F172A] dark:text-white">Central Question Bank</h1>
            <Badge variant="indigo">{subjects.length > 0 ? `${subjects.length} Subjects Preloaded` : 'Multi-Subject'}</Badge>
          </div>
          <p className="text-xs text-[#64748B] dark:text-slate-400">
            Repository of immutable, approved examination questions with verified curriculum evidence.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link to="/faculty/generate">
            <Button variant="teal" size="sm">
              Generate Questions
            </Button>
          </Link>
          <Link to="/faculty/papers/new">
            <Button variant="primary" size="sm">
              Build Question Paper
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters Toolbar */}
      <div className="bg-white dark:bg-[#1E293B] p-4 rounded-xl border border-[#E2E8F0] dark:border-slate-800 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          <div className="sm:col-span-1">
            <Input
              placeholder="Search question text..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              leftIcon={<Search className="w-4 h-4" />}
            />
          </div>

          <Select
            value={subjectFilter}
            onChange={(e) => {
              setSubjectFilter(e.target.value);
              setPage(1);
            }}
            options={[
              { value: '', label: 'All Subjects' },
              ...subjects.map(s => ({ value: s.id, label: `${s.code}: ${s.name.slice(0, 22)}...` }))
            ]}
          />

          <Select
            value={questionType}
            onChange={(e) => {
              setQuestionType(e.target.value);
              setPage(1);
            }}
            options={[
              { value: '', label: 'All Question Types' },
              { value: 'mcq', label: 'Multiple Choice (MCQ)' },
              { value: 'short_answer', label: 'Short Answer' },
              { value: 'long_answer', label: 'Long Answer' }
            ]}
          />

          <Select
            value={difficulty}
            onChange={(e) => {
              setDifficulty(e.target.value);
              setPage(1);
            }}
            options={[
              { value: '', label: 'All Difficulties' },
              { value: 'easy', label: 'Easy' },
              { value: 'medium', label: 'Medium' },
              { value: 'hard', label: 'Hard' }
            ]}
          />

          <Select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            options={[
              { value: '', label: 'All Statuses' },
              { value: 'approved', label: 'Approved Only' },
              { value: 'draft', label: 'Draft / Awaiting Re-approval' },
              { value: 'archived', label: 'Archived' }
            ]}
          />
        </div>
      </div>

      {/* Questions List */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <Spinner size="lg" className="h-64" />
          ) : data.items.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              No questions found matching your filter criteria.
            </div>
          ) : (
            <div className="divide-y divide-[#F1F5F9]">
              {data.items.map((q: any) => {
                const rev = q.current_revision || {};
                const isApproved = q.status === 'approved';

                return (
                  <div key={q.id} className="p-5 hover:bg-slate-50 transition-colors space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[11px] text-slate-400 font-semibold">{q.id}</span>
                        <Badge variant="indigo" size="sm">{q.subject_id}</Badge>
                        <Badge variant="neutral" size="sm">Rev {rev.revision_number || 1}</Badge>
                        <Badge variant="neutral" size="sm" className="uppercase font-semibold">
                          {rev.question_type?.replace('_', ' ')}
                        </Badge>
                        <Badge
                          variant={
                            rev.difficulty === 'easy'
                              ? 'success'
                              : rev.difficulty === 'hard'
                              ? 'error'
                              : 'warning'
                          }
                          size="sm"
                          className="capitalize"
                        >
                          {rev.difficulty}
                        </Badge>
                        <span className="font-bold text-[#0F172A]">{rev.marks} Marks</span>
                        {rev.topic_name && (
                          <span className="text-slate-500 text-[11px]">
                            • Unit {rev.unit_number}: {rev.topic_name}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <Badge variant={isApproved ? 'success' : 'warning'} size="sm">
                          {isApproved ? 'Approved for Papers' : 'Draft Revision'}
                        </Badge>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Inspect Revision History"
                            onClick={() => setSelectedQuestion(q)}
                          >
                            <History className="w-3.5 h-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Edit (creates new revision)"
                            onClick={() => handleOpenEdit(q)}
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Duplicate Question"
                            onClick={() => handleDuplicate(q.id)}
                          >
                            <Copy className="w-3.5 h-3.5" />
                          </Button>
                          {!isApproved && (
                            <Button
                              variant="teal"
                              size="sm"
                              onClick={() => handleApprove(q.id)}
                            >
                              Approve
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500"
                            onClick={() => handleArchive(q.id)}
                          >
                            <Archive className="w-3.5 h-3.5" />
                          </Button>
                        </div>
                      </div>
                    </div>

                    {/* Question Text */}
                    <div className="text-xs font-semibold text-[#0F172A] leading-relaxed">
                      <MathText text={rev.question_text} />
                    </div>

                    {/* MCQ Options Display */}
                    {rev.question_type === 'mcq' && rev.options_json && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                        {rev.options_json.map((opt: string, optIdx: number) => {
                          const isCorrect = rev.correct_answer === opt || rev.correct_answer === String.fromCharCode(65 + optIdx);
                          return (
                            <div
                              key={optIdx}
                              className={`p-2 rounded-lg border text-xs flex items-center gap-2 ${
                                isCorrect
                                  ? 'bg-emerald-50 border-emerald-300 text-emerald-900 font-medium'
                                  : 'bg-slate-50 border-slate-200 text-slate-700'
                              }`}
                            >
                              <span className="font-bold">{String.fromCharCode(65 + optIdx)}.</span>
                              <span className="truncate"><MathText text={opt} /></span>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Source Evidence Quote */}
                    {rev.supporting_excerpt && (
                      <div className="text-[11px] text-slate-500 italic bg-slate-50 p-2 rounded border border-slate-200 flex items-start gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                        <span>Source Quote: "{rev.supporting_excerpt}"</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination Controls */}
          {data.total_pages > 1 && (
            <div className="p-4 bg-[#F8FAFC] border-t border-[#E2E8F0] flex items-center justify-between text-xs">
              <span className="text-slate-500">
                Page {data.page} of {data.total_pages} ({data.total} total questions)
              </span>
              <div className="flex items-center gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={data.page <= 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={data.page >= data.total_pages}
                  onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Question Modal (Creates New Revision) */}
      <Modal
        isOpen={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Edit Question (Creates New Revision)"
        description="Changes to an approved question create an immutable new revision and require re-approval."
        maxWidth="2xl"
        footer={
          <>
            <Button variant="secondary" onClick={() => setEditModalOpen(false)} disabled={savingEdit}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSaveEdit} isLoading={savingEdit}>
              Save as New Revision
            </Button>
          </>
        }
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="block text-xs font-semibold text-[#1E293B] mb-1">Question Text</label>
            <textarea
              rows={3}
              value={editData.question_text || ''}
              onChange={(e) => setEditData({ ...editData, question_text: e.target.value })}
              className="w-full text-xs rounded-lg border border-slate-300 p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-100"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Difficulty"
              value={editData.difficulty || 'medium'}
              onChange={(e) => setEditData({ ...editData, difficulty: e.target.value })}
              options={[
                { value: 'easy', label: 'Easy' },
                { value: 'medium', label: 'Medium' },
                { value: 'hard', label: 'Hard' }
              ]}
            />
            <Input
              label="Marks"
              type="number"
              value={editData.marks || 2}
              onChange={(e) => setEditData({ ...editData, marks: e.target.value })}
            />
          </div>

          {editData.model_answer !== undefined && (
            <div>
              <label className="block text-xs font-semibold text-[#1E293B] mb-1">Model Answer</label>
              <textarea
                rows={4}
                value={editData.model_answer || ''}
                onChange={(e) => setEditData({ ...editData, model_answer: e.target.value })}
                className="w-full text-xs rounded-lg border border-slate-300 p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-[#1E293B] mb-1">Explanation</label>
            <textarea
              rows={2}
              value={editData.explanation || ''}
              onChange={(e) => setEditData({ ...editData, explanation: e.target.value })}
              className="w-full text-xs rounded-lg border border-slate-300 p-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-100"
            />
          </div>
        </div>
      </Modal>

      {/* Revision History Modal */}
      <Modal
        isOpen={!!selectedQuestion}
        onClose={() => setSelectedQuestion(null)}
        title={`Revision History: ${selectedQuestion?.id}`}
        description="Immutable revision audit log preserving exact historical question snapshots."
        maxWidth="2xl"
        footer={
          <Button variant="secondary" onClick={() => setSelectedQuestion(null)}>
            Close
          </Button>
        }
      >
        <div className="space-y-4 text-xs">
          {selectedQuestion?.current_revision && (
            <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
              <div className="flex items-center justify-between font-bold text-[#3730A3] mb-1">
                <span>Active Revision (Rev {selectedQuestion.current_revision.revision_number})</span>
                <span>{selectedQuestion.status.toUpperCase()}</span>
              </div>
              <p className="text-slate-800 font-medium"><MathText text={selectedQuestion.current_revision.question_text} /></p>
              <div className="text-[11px] text-slate-500 mt-2">
                Created: {formatDate(selectedQuestion.current_revision.created_at)}
              </div>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};
