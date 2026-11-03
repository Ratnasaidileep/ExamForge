import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Clock, CheckCircle2, Bookmark, BookmarkCheck, ArrowLeft,
  ArrowRight, Send, AlertTriangle, ShieldCheck, Check, RotateCcw
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Spinner } from '@/components/ui/Spinner';
import { MathText } from '@/components/ui/MathText';

export const AssessmentAttempt: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Saved responses state: { [qRevId]: { answer: string, is_marked: boolean } }
  const [answers, setAnswers] = useState<{ [qRevId: string]: { answer: string; is_marked: boolean } }>({});
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'error'>('saved');

  // Timer state
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null);
  const [submitModalOpen, setSubmitModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load attempt data
  useEffect(() => {
    if (!attemptId) return;
    setLoading(true);
    apiFetch(`/attempts/${attemptId}`)
      .then((data) => {
        setAttempt(data);
        setRemainingSeconds(data.remaining_seconds);

        // Pre-fill answers from saved_responses
        const initialAnswers: any = {};
        Object.entries(data.saved_responses || {}).forEach(([revId, item]: [string, any]) => {
          initialAnswers[revId] = {
            answer: item.submitted_answer || '',
            is_marked: item.is_marked_for_review || false
          };
        });
        setAnswers(initialAnswers);

        // If already submitted or expired, redirect to results
        if (data.status !== 'in_progress') {
          navigate(`/student/attempt/${attemptId}/results`, { replace: true });
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [attemptId]);

  // Countdown timer effect
  useEffect(() => {
    if (remainingSeconds === null || remainingSeconds <= 0) return;
    const interval = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev === null || prev <= 1) {
          clearInterval(interval);
          handleAutoSubmitOnExpiry();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [remainingSeconds]);

  // Debounced auto-save function
  const saveAnswerToServer = async (revId: string, answerText: string, isMarked: boolean) => {
    setSaveStatus('saving');
    try {
      await apiFetch(`/attempts/${attemptId}/responses/${revId}`, {
        method: 'PUT',
        body: JSON.stringify({
          submitted_answer: answerText,
          is_marked_for_review: isMarked
        })
      });
      setSaveStatus('saved');
    } catch {
      setSaveStatus('error');
    }
  };

  const handleAnswerChange = (val: string) => {
    if (!attempt) return;
    const currentQ = attempt.questions[currentIndex];
    const revId = currentQ.question_revision_id;
    const isMarked = answers[revId]?.is_marked || false;

    setAnswers((prev) => ({
      ...prev,
      [revId]: { answer: val, is_marked: isMarked }
    }));

    saveAnswerToServer(revId, val, isMarked);
  };

  const handleToggleMark = () => {
    if (!attempt) return;
    const currentQ = attempt.questions[currentIndex];
    const revId = currentQ.question_revision_id;
    const currAns = answers[revId]?.answer || '';
    const newMarked = !(answers[revId]?.is_marked || false);

    setAnswers((prev) => ({
      ...prev,
      [revId]: { answer: currAns, is_marked: newMarked }
    }));

    saveAnswerToServer(revId, currAns, newMarked);
  };

  const handleClearAnswer = () => {
    if (!attempt) return;
    const currentQ = attempt.questions[currentIndex];
    const revId = currentQ.question_revision_id;
    const isMarked = answers[revId]?.is_marked || false;

    setAnswers((prev) => ({
      ...prev,
      [revId]: { answer: '', is_marked: isMarked }
    }));

    saveAnswerToServer(revId, '', isMarked);
  };

  const handleAutoSubmitOnExpiry = async () => {
    alert('Time has expired! Submitting your assessment automatically.');
    handleSubmit();
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await apiFetch(`/attempts/${attemptId}/submit`, { method: 'POST' });
      navigate(`/student/attempt/${attemptId}/results`, { replace: true });
    } catch (e: any) {
      alert(`Submission failed: ${e.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <Spinner size="lg" className="h-64" />;
  if (!attempt) return <div>Assessment attempt not found.</div>;

  const questions = attempt.questions || [];
  const currentQ = questions[currentIndex];
  const currentAnswer = currentQ ? (answers[currentQ.question_revision_id]?.answer || '') : '';
  const currentIsMarked = currentQ ? (answers[currentQ.question_revision_id]?.is_marked || false) : false;

  const answeredCount = questions.filter(
    (q: any) => answers[q.question_revision_id]?.answer?.trim()
  ).length;

  const formatTimer = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const s = sec % 60;
    return `${mins}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="max-w-6xl mx-auto space-y-4 animate-fade-in">
      {/* Top Distraction-Free Exam Header */}
      <div className="sticky top-16 z-20 bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-base font-bold text-[#0F172A]">{attempt.title}</h1>
          <div className="flex items-center gap-3 text-xs text-slate-500 mt-0.5">
            <span>Subject: {attempt.subject_id}</span>
            <span>•</span>
            <span>Question {currentIndex + 1} of {questions.length}</span>
            <span>•</span>
            <span className="flex items-center gap-1 font-medium text-emerald-700">
              <Check className="w-3.5 h-3.5" />
              {saveStatus === 'saving' ? 'Saving...' : 'Auto-saved'}
            </span>
          </div>
        </div>

        {/* Timer and Submit Action */}
        <div className="flex items-center gap-4">
          {remainingSeconds !== null && (
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border font-mono font-bold text-sm ${
                remainingSeconds < 300
                  ? 'bg-rose-50 border-rose-200 text-rose-700 animate-pulse'
                  : 'bg-slate-50 border-slate-200 text-slate-800'
              }`}
            >
              <Clock className="w-4 h-4 text-slate-500" />
              <span>{formatTimer(remainingSeconds)}</span>
            </div>
          )}

          <Button
            variant="teal"
            size="sm"
            leftIcon={<Send className="w-4 h-4" />}
            onClick={() => setSubmitModalOpen(true)}
          >
            Submit Assessment
          </Button>
        </div>
      </div>

      {/* Main Examination Area: Question Display + Navigator Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left 3 Columns: Active Question Workspace */}
        <div className="lg:col-span-3 space-y-4">
          <Card className="min-h-[460px] flex flex-col justify-between">
            <CardContent className="p-6 space-y-6">
              {/* Question Header */}
              <div className="flex items-center justify-between text-xs pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-[#3730A3]">Q{currentIndex + 1}</span>
                  <Badge variant="neutral" size="sm" className="uppercase font-semibold">
                    {currentQ.question_type.replace('_', ' ')}
                  </Badge>
                  <Badge variant="indigo" size="sm">
                    {currentQ.marks_allocated} Marks
                  </Badge>
                </div>

                <button
                  type="button"
                  onClick={handleToggleMark}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold transition-colors ${
                    currentIsMarked
                      ? 'bg-amber-100 text-amber-900 border border-amber-300'
                      : 'text-slate-500 hover:bg-slate-100'
                  }`}
                >
                  {currentIsMarked ? (
                    <>
                      <BookmarkCheck className="w-4 h-4 text-amber-600" />
                      <span>Marked for Review</span>
                    </>
                  ) : (
                    <>
                      <Bookmark className="w-4 h-4" />
                      <span>Mark for Review</span>
                    </>
                  )}
                </button>
              </div>

              {/* Question Text */}
              <div className="text-sm font-semibold text-[#0F172A] leading-relaxed">
                <MathText text={currentQ.question_text} />
              </div>

              {/* Input Area Based on Question Type */}
              {currentQ.question_type === 'mcq' && currentQ.options ? (
                <div className="space-y-2.5 pt-2">
                  {currentQ.options.map((opt: string, optIdx: number) => {
                    const isSelected = currentAnswer === opt || currentAnswer === String.fromCharCode(65 + optIdx);
                    return (
                      <button
                        key={optIdx}
                        type="button"
                        onClick={() => handleAnswerChange(opt)}
                        className={`w-full p-3.5 rounded-xl border text-left text-xs font-medium flex items-center gap-3 transition-all ${
                          isSelected
                            ? 'bg-teal-50 border-[#0F766E] text-teal-950 font-semibold shadow-xs ring-1 ring-[#0F766E]'
                            : 'bg-white border-slate-200 text-slate-800 hover:bg-slate-50'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full border flex items-center justify-center font-bold text-[11px] ${
                            isSelected
                              ? 'border-[#0F766E] bg-[#0F766E] text-white'
                              : 'border-slate-300 text-slate-500'
                          }`}
                        >
                          {String.fromCharCode(65 + optIdx)}
                        </div>
                        <span className="flex-1"><MathText text={opt} /></span>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="space-y-2 pt-2">
                  <div className="flex justify-between items-center text-xs text-slate-500">
                    <span>Type your technical answer below (LaTeX equations like $E=mc^2$ supported):</span>
                    <span>{currentAnswer.length} characters</span>
                  </div>
                  <textarea
                    rows={8}
                    value={currentAnswer}
                    onChange={(e) => handleAnswerChange(e.target.value)}
                    placeholder="Enter your detailed answer here... (You can write math formulas like $x^2$ or $$\frac{a}{b}$$)"
                    className="w-full text-xs rounded-xl border border-slate-300 p-4 focus:outline-none focus:ring-2 focus:ring-teal-200 leading-relaxed font-sans"
                  />
                  {currentAnswer.includes('$') && (
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 block">
                        Live LaTeX Formula Preview
                      </span>
                      <div className="text-xs text-slate-900">
                        <MathText text={currentAnswer} />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>

            {/* Bottom Nav Controls */}
            <div className="p-4 bg-[#F8FAFC] border-t border-[#E2E8F0] flex items-center justify-between">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearAnswer}
                leftIcon={<RotateCcw className="w-3.5 h-3.5 text-slate-400" />}
              >
                Clear Answer
              </Button>

              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={currentIndex === 0}
                  onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
                  leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}
                >
                  Previous
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  disabled={currentIndex >= questions.length - 1}
                  onClick={() => setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))}
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                >
                  Next Question
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Right 1 Column: Question Navigator */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
                Question Navigator
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-0">
              <div className="grid grid-cols-4 sm:grid-cols-5 lg:grid-cols-4 gap-2">
                {questions.map((q: any, idx: number) => {
                  const revId = q.question_revision_id;
                  const isAnswered = Boolean(answers[revId]?.answer?.trim());
                  const isMarked = Boolean(answers[revId]?.is_marked);
                  const isCurrent = idx === currentIndex;

                  let btnStyle = 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50';
                  if (isAnswered) {
                    btnStyle = 'bg-emerald-600 border-emerald-600 text-white font-semibold';
                  }
                  if (isMarked) {
                    btnStyle = 'bg-amber-500 border-amber-500 text-white font-semibold';
                  }

                  return (
                    <button
                      key={q.question_revision_id}
                      onClick={() => setCurrentIndex(idx)}
                      className={`h-9 rounded-lg border text-xs font-bold transition-all relative ${btnStyle} ${
                        isCurrent ? 'ring-2 ring-indigo-500 ring-offset-2' : ''
                      }`}
                    >
                      {idx + 1}
                      {isMarked && (
                        <span className="absolute top-0.5 right-0.5 w-1.5 h-1.5 bg-white rounded-full" />
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Legend */}
              <div className="pt-3 border-t border-slate-100 space-y-1.5 text-[11px] text-slate-500">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-emerald-600" />
                  <span>Answered ({answeredCount})</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-amber-500" />
                  <span>Marked for review</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-white border border-slate-300" />
                  <span>Unanswered ({questions.length - answeredCount})</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Submit Confirmation Dialog */}
      <Modal
        isOpen={submitModalOpen}
        onClose={() => setSubmitModalOpen(false)}
        title="Submit Assessment?"
        description="Are you sure you want to finish and submit your answers?"
        footer={
          <>
            <Button variant="secondary" onClick={() => setSubmitModalOpen(false)} disabled={isSubmitting}>
              Resume Test
            </Button>
            <Button variant="teal" onClick={handleSubmit} isLoading={isSubmitting}>
              Confirm Submission
            </Button>
          </>
        }
      >
        <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 grid grid-cols-2 gap-2 text-center">
            <div>
              <span className="text-[10px] text-slate-400 block">Total Answered</span>
              <span className="font-bold text-emerald-700 text-sm">{answeredCount} of {questions.length}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 block">Unanswered</span>
              <span className="font-bold text-slate-800 text-sm">{questions.length - answeredCount}</span>
            </div>
          </div>
          <p>
            Once submitted, your answers will become immutable. Objective MCQs will be scored immediately and descriptive responses will be forwarded to faculty evaluation.
          </p>
        </div>
      </Modal>
    </div>
  );
};
