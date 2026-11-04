import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Layers, Plus, Trash2, CheckCircle2, AlertTriangle, FileDown,
  Sparkles, ShieldCheck, Printer, Save, ArrowLeft, Eye, RefreshCw, Edit3,
  Calendar, Clock
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';
import { MathText } from '@/components/ui/MathText';

export const PaperBuilder: React.FC = () => {
  const { paperId } = useParams<{ paperId: string }>();
  const navigate = useNavigate();

  const [paper, setPaper] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [availableQuestions, setAvailableQuestions] = useState<any[]>([]);
  const [validation, setValidation] = useState<any | null>(null);
  const [validating, setValidating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [windowStart, setWindowStart] = useState<string>('');
  const [windowEnd, setWindowEnd] = useState<string>('');
  const [savingSchedule, setSavingSchedule] = useState(false);

  // Helper to format ISO to datetime-local
  const toLocalInput = (isoStr: string | null) => {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      if (isNaN(d.getTime())) return '';
      const pad = (n: number) => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
    } catch {
      return '';
    }
  };

  // Load paper and question bank
  const loadPaper = async () => {
    if (!paperId || paperId === 'new') {
      // Create new draft paper
      try {
        const newPaper = await apiFetch('/papers', {
          method: 'POST',
          body: JSON.stringify({
            title: 'ITS-401 Examination Paper (Draft)',
            total_marks: 30.0,
            duration_minutes: 60
          })
        });
        navigate(`/faculty/papers/${newPaper.id}`, { replace: true });
      } catch (e: any) {
        alert(`Failed to create paper draft: ${e.message}`);
      }
      return;
    }

    setLoading(true);
    try {
      const p = await apiFetch(`/papers/${paperId}`);
      setPaper(p);
      setWindowStart(toLocalInput(p.window_start));
      setWindowEnd(toLocalInput(p.window_end));
      // Run validation
      const val = await apiFetch(`/papers/${paperId}/validate`, { method: 'POST' });
      setValidation(val);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSchedule = async () => {
    if (!paper) return;
    setSavingSchedule(true);
    try {
      const payload: any = {
        window_start: windowStart ? new Date(windowStart).toISOString() : null,
        window_end: windowEnd ? new Date(windowEnd).toISOString() : null
      };
      await apiFetch(`/papers/${paper.id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      });
      alert('Examination window schedule saved successfully!');
      loadPaper();
    } catch (e: any) {
      alert(`Failed to update exam window: ${e.message}`);
    } finally {
      setSavingSchedule(false);
    }
  };

  useEffect(() => {
    loadPaper();
    // Load approved questions
    apiFetch('/questions?status=approved&page_size=50')
      .then((res) => setAvailableQuestions(res.items || []))
      .catch(console.error);
  }, [paperId]);

  const handleAutoAssemble = async () => {
    if (!paper) return;
    setValidating(true);
    try {
      const res = await apiFetch(`/papers/${paper.id}/assemble`, {
        method: 'POST',
        body: JSON.stringify({
          blueprint: {
            target_marks: paper.total_marks || 30.0,
            duration_minutes: paper.duration_minutes || 60,
            difficulty_target: { easy: 40, medium: 40, hard: 20 },
            type_target: { mcq: 5, short_answer: 2, long_answer: 1 },
            required_units: [1, 2, 3, 4]
          }
        })
      });
      setValidation(res.validation);
      await loadPaper();
    } catch (e: any) {
      alert(`Auto-assembly failed: ${e.message}`);
    } finally {
      setValidating(false);
    }
  };

  const handleAddQuestionToSection = async (sectionId: string, qItem: any) => {
    if (!paper) return;
    const rev = qItem.current_revision;
    const currentSections = [...(paper.sections || [])];
    const sec = currentSections.find(s => s.id === sectionId);
    if (!sec) return;

    sec.items = sec.items || [];
    sec.items.push({
      question_revision_id: rev.id,
      marks: rev.marks || 2.0,
      revision: rev
    });

    try {
      await apiFetch(`/papers/${paper.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ sections: currentSections })
      });
      loadPaper();
    } catch (e: any) {
      alert(`Failed to add question: ${e.message}`);
    }
  };

  const handleRemoveItem = async (sectionId: string, itemIdx: number) => {
    if (!paper) return;
    const currentSections = [...(paper.sections || [])];
    const sec = currentSections.find(s => s.id === sectionId);
    if (!sec || !sec.items) return;

    sec.items.splice(itemIdx, 1);
    try {
      await apiFetch(`/papers/${paper.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ sections: currentSections })
      });
      loadPaper();
    } catch (e: any) {
      alert(`Failed to remove item: ${e.message}`);
    }
  };

  const handleAddSection = async () => {
    if (!paper) return;
    const currentSections = [...(paper.sections || [])];
    const nextLetter = String.fromCharCode(65 + currentSections.length);
    const newSec = {
      id: `sec_${Date.now()}`,
      name: `Section ${nextLetter}: Applied Case Analysis`,
      description: 'Custom examination section',
      section_order: currentSections.length + 1,
      total_marks: 10.0,
      instructions: 'Answer all questions in this section.',
      items: []
    };
    currentSections.push(newSec);
    try {
      await apiFetch(`/papers/${paper.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ sections: currentSections })
      });
      loadPaper();
    } catch (e: any) {
      alert(`Failed to add section: ${e.message}`);
    }
  };

  const handleRemoveSection = async (secId: string) => {
    if (!paper) return;
    if (!confirm('Are you sure you want to remove this section and its items?')) return;
    const currentSections = (paper.sections || []).filter((s: any) => s.id !== secId);
    try {
      await apiFetch(`/papers/${paper.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ sections: currentSections })
      });
      loadPaper();
    } catch (e: any) {
      alert(`Failed to delete section: ${e.message}`);
    }
  };

  const handleEditSectionName = async (secId: string, currentName: string) => {
    const newName = prompt('Enter section title:', currentName);
    if (!newName || newName === currentName) return;
    const currentSections = (paper.sections || []).map((s: any) =>
      s.id === secId ? { ...s, name: newName } : s
    );
    try {
      await apiFetch(`/papers/${paper.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ sections: currentSections })
      });
      loadPaper();
    } catch (e: any) {
      alert(`Failed to rename section: ${e.message}`);
    }
  };

  const handleToggleAcknowledgeWarnings = async () => {
    if (!paper) return;
    try {
      await apiFetch(`/papers/${paper.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ warnings_acknowledged: !paper.warnings_acknowledged })
      });
      loadPaper();
    } catch (e: any) {
      alert(`Failed to update warnings acknowledgment: ${e.message}`);
    }
  };

  const handlePublish = async () => {
    if (!paper) return;
    setPublishing(true);
    try {
      await apiFetch(`/papers/${paper.id}/publish`, { method: 'POST' });
      alert('Examination paper published successfully!');
      loadPaper();
    } catch (e: any) {
      alert(`Publication blocked: ${e.message}`);
    } finally {
      setPublishing(false);
    }
  };

  const handleMakePractice = async () => {
    if (!paper) return;
    try {
      await apiFetch(`/papers/${paper.id}/make-practice`, { method: 'POST' });
      alert('Paper made available for student practice!');
      loadPaper();
    } catch (e: any) {
      alert(`Action failed: ${e.message}`);
    }
  };

  const handleExportPDF = (type: 'paper' | 'key') => {
    if (!paper) return;
    const endpoint = type === 'paper' ? `/papers/${paper.id}/export` : `/papers/${paper.id}/answer-key`;
    window.open(`/api/v1${endpoint}`, '_blank');
  };

  if (loading) return <Spinner size="lg" className="h-64" />;
  if (!paper) return <div>Paper not found.</div>;

  const sections = paper.sections || [];
  const allItems = paper.items || [];
  const actualMarks = sections.reduce((acc: number, s: any) => {
    return acc + (s.items || []).reduce((iAcc: number, it: any) => iAcc + (it.marks || 0), 0);
  }, 0);

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <button
            onClick={() => navigate('/faculty/papers')}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-[#3730A3] mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Paper Library</span>
          </button>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-[#0F172A]">{paper.title}</h1>
            <Badge
              variant={
                paper.status === 'published'
                  ? 'success'
                  : paper.status === 'practice'
                  ? 'teal'
                  : 'warning'
              }
            >
              {paper.status.toUpperCase()}
            </Badge>
          </div>
          <p className="text-xs text-[#64748B]">
            Interactive blueprint assembler, section editor, and live printable paper preview.
          </p>
        </div>

        {/* Global Paper Actions */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Printer className="w-3.5 h-3.5" />}
            onClick={() => handleExportPDF('paper')}
          >
            Export Paper PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<FileDown className="w-3.5 h-3.5 text-red-600" />}
            onClick={() => handleExportPDF('key')}
          >
            Export Answer Key
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleMakePractice}
          >
            Make Available for Practice
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handlePublish}
            isLoading={publishing}
            leftIcon={<CheckCircle2 className="w-3.5 h-3.5" />}
          >
            Publish Formal Exam
          </Button>
        </div>
      </div>

      {/* 3-Column Coordinated Area */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Left Column (3 cols): Metadata, Blueprint Rules, Add Question */}
        <div className="xl:col-span-3 space-y-4">
          {/* Blueprint & Assembly Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
                1. Blueprint & Assembly
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 pt-0 text-xs">
              <Button
                variant="teal"
                size="sm"
                className="w-full justify-center"
                leftIcon={<Sparkles className="w-4 h-4" />}
                onClick={handleAutoAssemble}
                isLoading={validating}
              >
                Auto-Assemble from Blueprint
              </Button>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Picks approved questions deterministically to satisfy target marks, question types, and topic units.
              </p>

              <div className="p-3 bg-slate-50 rounded-lg space-y-2 border border-slate-200">
                <div className="flex justify-between">
                  <span className="text-slate-500">Target Marks:</span>
                  <span className="font-bold text-[#0F172A]">{paper.total_marks} Marks</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Allocated Marks:</span>
                  <span className={`font-bold ${actualMarks === paper.total_marks ? 'text-emerald-700' : 'text-amber-700'}`}>
                    {actualMarks} Marks
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Duration:</span>
                  <span className="font-bold text-[#0F172A]">{paper.duration_minutes} Mins</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Exam Window Schedule Card */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs uppercase tracking-wider text-slate-500 flex items-center justify-between">
                <span>2. Scheduled Window</span>
                <Clock className="w-3.5 h-3.5 text-indigo-600" />
              </CardTitle>
              <p className="text-[11px] text-slate-400">Lock exam access strictly to an examination time window.</p>
            </CardHeader>
            <CardContent className="space-y-3 pt-0 text-xs">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Window Opens (Start)
                </label>
                <input
                  type="datetime-local"
                  value={windowStart}
                  onChange={(e) => setWindowStart(e.target.value)}
                  className="w-full text-xs rounded-lg border border-slate-300 p-2 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Window Closes (End)
                </label>
                <input
                  type="datetime-local"
                  value={windowEnd}
                  onChange={(e) => setWindowEnd(e.target.value)}
                  className="w-full text-xs rounded-lg border border-slate-300 p-2 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
              </div>

              <div className="flex items-center gap-2 pt-1">
                <Button
                  variant="primary"
                  size="sm"
                  className="w-full justify-center"
                  leftIcon={<Save className="w-3.5 h-3.5" />}
                  onClick={handleSaveSchedule}
                  isLoading={savingSchedule}
                >
                  Save Schedule
                </Button>
                {(windowStart || windowEnd) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-500"
                    onClick={() => {
                      setWindowStart('');
                      setWindowEnd('');
                    }}
                    title="Clear window inputs"
                  >
                    Clear
                  </Button>
                )}
              </div>

              {paper.window_start || paper.window_end ? (
                <div className="p-2 rounded bg-indigo-50/70 border border-indigo-200 text-[10px] text-indigo-900 leading-relaxed">
                  <strong>Active Schedule:</strong><br />
                  Opens: {paper.window_start ? new Date(paper.window_start).toLocaleString() : 'Anytime'}<br />
                  Closes: {paper.window_end ? new Date(paper.window_end).toLocaleString() : 'No close date'}
                </div>
              ) : (
                <span className="text-[10px] text-slate-400 italic block">
                  No window set — open anytime after publication.
                </span>
              )}
            </CardContent>
          </Card>

          {/* Question Bank Selector */}
          <Card className="flex flex-col max-h-[500px]">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
                3. Approved Questions Bank
              </CardTitle>
              <p className="text-[11px] text-slate-400">Click (+) to add to Section</p>
            </CardHeader>
            <CardContent className="space-y-2 overflow-y-auto flex-1 pt-0">
              {availableQuestions.map((q) => {
                const rev = q.current_revision || {};
                return (
                  <div key={q.id} className="p-2.5 rounded-lg border border-slate-200 bg-white hover:border-indigo-300 transition-colors text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <Badge variant="neutral" size="sm">{rev.question_type}</Badge>
                      <span className="font-bold text-slate-700">{rev.marks}M</span>
                    </div>
                    <div className="text-[11px] font-medium text-slate-800 line-clamp-2">
                      <MathText text={rev.question_text} />
                    </div>
                    <div className="flex items-center justify-between pt-1 border-t border-slate-100">
                      <span className="text-[10px] text-slate-400">Unit {rev.unit_number}</span>
                      {sections.length > 0 && (
                        <select
                          className="text-[10px] border border-slate-200 rounded px-1.5 py-0.5 bg-slate-50"
                          onChange={(e) => {
                            if (e.target.value) {
                              handleAddQuestionToSection(e.target.value, q);
                              e.target.value = '';
                            }
                          }}
                        >
                          <option value="">+ Add to Section</option>
                          {sections.map((s: any) => (
                            <option key={s.id} value={s.id}>
                              {s.name}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>

        {/* Center Column (5 cols): Sections & Selected Questions */}
        <div className="xl:col-span-5 space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
                  2. Paper Sections & Structure
                </CardTitle>
                <p className="text-[11px] text-slate-400 mt-0.5">Organize questions into categorized exam sections</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Plus className="w-3.5 h-3.5" />}
                onClick={handleAddSection}
              >
                Add Section
              </Button>
            </CardHeader>
            <CardContent className="space-y-4 pt-0">
              {sections.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No sections added yet. Click &quot;Add Section&quot; or use &quot;Auto-Assemble&quot;.
                </div>
              ) : (
                sections.map((sec: any) => {
                  const items = sec.items || [];
                  const secMarks = items.reduce((acc: number, it: any) => acc + (it.marks || 0), 0);

                  return (
                    <div key={sec.id} className="border border-slate-200 rounded-xl overflow-hidden bg-slate-50/50">
                      <div className="p-3 bg-white border-b border-slate-200 flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-xs text-[#0F172A]">{sec.name}</h4>
                            <button
                              onClick={() => handleEditSectionName(sec.id, sec.name)}
                              className="text-slate-400 hover:text-indigo-600 p-0.5"
                              title="Rename Section"
                            >
                              <Edit3 className="w-3 h-3" />
                            </button>
                          </div>
                          <span className="text-[11px] text-slate-500">
                            {items.length} Questions • {secMarks} Marks
                          </span>
                        </div>
                        <button
                          onClick={() => handleRemoveSection(sec.id)}
                          className="text-slate-400 hover:text-red-600 p-1 rounded"
                          title="Delete Section"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div className="p-3 space-y-2">
                        {items.length === 0 ? (
                          <div className="p-4 text-center text-slate-400 text-xs border border-dashed border-slate-200 rounded-lg">
                            Section is empty. Add questions from the left panel.
                          </div>
                        ) : (
                          items.map((it: any, itIdx: number) => {
                            const rev = it.revision || {};
                            return (
                              <div
                                key={itIdx}
                                className="p-3 rounded-lg bg-white border border-slate-200 flex items-start gap-3 shadow-xs"
                              >
                                <span className="font-bold text-xs text-[#3730A3] mt-0.5">
                                  Q{itIdx + 1}.
                                </span>
                                <div className="flex-1 min-w-0">
                                  <div className="text-xs text-slate-800 line-clamp-2 leading-relaxed">
                                    <MathText text={rev.question_text || it.question_text} />
                                  </div>
                                  <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                                    <span className="uppercase">{rev.question_type}</span>
                                    <span>•</span>
                                    <span>{it.marks} Marks</span>
                                  </div>
                                </div>
                                <button
                                  onClick={() => handleRemoveItem(sec.id, itIdx)}
                                  className="text-slate-400 hover:text-red-600 p-1 rounded"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            );
                          })
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column (4 cols): Live Printable Preview & Validation */}
        <div className="xl:col-span-4 space-y-4">
          {/* Validation Status Box */}
          {validation && (
            <Card className={validation.can_publish ? 'border-emerald-200 bg-emerald-50/20' : 'border-amber-200 bg-amber-50/20'}>
              <CardContent className="p-4 space-y-2 text-xs">
                <div className="flex items-center justify-between font-bold">
                  <span className="flex items-center gap-1.5">
                    {validation.can_publish ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                    )}
                    <span>{validation.can_publish ? 'Blueprint Validated' : 'Validation Issues'}</span>
                  </span>
                  <Badge variant={validation.can_publish ? 'success' : 'warning'}>
                    {validation.can_publish ? 'Ready to Publish' : 'Draft Only'}
                  </Badge>
                </div>

                {validation.errors?.length > 0 && (
                  <div className="space-y-1 text-red-700">
                    <span className="font-bold">Errors (Blocks Publication):</span>
                    <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
                      {validation.errors.map((err: string, i: number) => (
                        <li key={i}>{err}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {validation.warnings?.length > 0 && (
                  <div className="p-2.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg space-y-2 text-amber-900 dark:text-amber-200">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[11px]">Blueprint Warnings ({validation.warnings.length}):</span>
                      <button
                        onClick={handleToggleAcknowledgeWarnings}
                        className={`text-[10px] px-2 py-0.5 rounded font-semibold transition-colors ${
                          paper.warnings_acknowledged
                            ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                            : 'bg-amber-200 hover:bg-amber-300 text-amber-900'
                        }`}
                      >
                        {paper.warnings_acknowledged ? '✓ Warnings Acknowledged' : 'Acknowledge Warnings'}
                      </button>
                    </div>
                    <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
                      {validation.warnings.map((warn: string, i: number) => (
                        <li key={i}>{warn}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Live Academic Paper Preview */}
          <Card className="shadow-md border-[#CBD5E1]">
            <CardHeader className="bg-[#1E293B] text-white p-3">
              <CardTitle className="text-xs uppercase tracking-wider text-slate-300 flex items-center justify-between">
                <span>3. Official Paper Preview</span>
                <span className="text-[10px] text-teal-400 font-normal">A4 Format</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 bg-white space-y-4 max-h-[600px] overflow-y-auto text-xs font-serif leading-relaxed">
              <div className="text-center space-y-1 pb-3 border-b border-black">
                <div className="font-bold text-[13px] uppercase tracking-wide">
                  College of Engineering & Technology
                </div>
                <div className="text-[11px] text-slate-700 uppercase">
                  Department of Computer Science & Engineering
                </div>
                <div className="font-bold text-[14px] uppercase pt-1 text-indigo-950">
                  {paper.title}
                </div>
                <div className="flex justify-between text-[11px] pt-2 font-sans font-semibold">
                  <span>Subject: {paper.subject_id}</span>
                  <span>Time: {paper.duration_minutes} Mins</span>
                  <span>Max Marks: {paper.total_marks}</span>
                </div>
              </div>

              {/* Instructions */}
              <div className="p-2 bg-slate-50 border border-slate-200 text-[10px] font-sans rounded">
                <strong>General Instructions:</strong> All questions are compulsory. Figures to the right indicate full marks.
              </div>

              {/* Live Rendered Sections */}
              {sections.map((sec: any, sIdx: number) => (
                <div key={sec.id} className="space-y-3 pt-2">
                  <div className="font-sans font-bold text-xs uppercase border-b border-slate-300 pb-1 text-[#1E1B4B]">
                    {sec.name} ({sec.items?.reduce((a: number, b: any) => a + (b.marks || 0), 0) || 0} Marks)
                  </div>

                  {sec.items?.map((it: any, iIdx: number) => {
                    const rev = it.revision || {};
                    return (
                      <div key={iIdx} className="space-y-1.5 pl-1">
                        <div className="flex justify-between font-sans text-xs">
                          <span className="font-semibold text-slate-900">
                            Q{iIdx + 1}. <MathText text={rev.question_text || it.question_text} />
                          </span>
                          <span className="font-bold text-indigo-900 font-mono ml-2">
                            [{it.marks}]
                          </span>
                        </div>

                        {rev.question_type === 'mcq' && rev.options_json && (
                          <div className="grid grid-cols-2 gap-x-4 gap-y-1 font-sans text-[11px] pl-4 text-slate-800">
                            {rev.options_json.map((opt: string, optI: number) => (
                              <div key={optI}>
                                <strong>({String.fromCharCode(65 + optI)})</strong> <MathText text={opt} />
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
