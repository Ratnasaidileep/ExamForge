import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen, Clock, Layers, Award, ArrowRight,
  ShieldCheck, AlertCircle, Sparkles, Calendar, Lock
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Spinner } from '@/components/ui/Spinner';

export const PracticeLibrary: React.FC = () => {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedPaper, setSelectedPaper] = useState<any | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    apiFetch('/papers')
      .then((res: any[]) => {
        // Only show published and practice papers for students
        setPapers(res.filter(p => p.status === 'published' || p.status === 'practice'));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const availableSubjects = Array.from(new Set(papers.map(p => p.subject_id).filter(Boolean)));

  const filteredPapers = papers.filter(p => !selectedSubject || p.subject_id === selectedSubject);

  const handleStartAttempt = async () => {
    if (!selectedPaper) return;
    setStarting(true);
    try {
      const res = await apiFetch('/attempts', {
        method: 'POST',
        body: JSON.stringify({
          paper_id: selectedPaper.id,
          mode: selectedPaper.status === 'published' ? 'assessment' : 'practice'
        })
      });
      navigate(`/student/attempt/${res.attempt_id}`);
    } catch (e: any) {
      alert(`Could not start attempt: ${e.message}`);
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="pb-2 border-b border-[#E2E8F0]">
        <div className="flex items-center gap-2 mb-1">
          <h1 className="text-2xl font-bold text-[#0F172A]">Examinations & Practice Library</h1>
          <Badge variant="teal">Exams Available</Badge>
        </div>
        <p className="text-xs text-[#64748B]">
          Choose an assessment to test your knowledge with real curriculum-grounded questions.
        </p>
      </div>

      {/* Subject Filter Pills */}
      {availableSubjects.length > 1 && (
        <div className="flex items-center gap-2 flex-wrap bg-white dark:bg-[#1E293B] p-2.5 rounded-xl border border-slate-200 dark:border-slate-800">
          <span className="text-[11px] font-semibold text-slate-500">Filter by Subject:</span>
          <button
            onClick={() => setSelectedSubject('')}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition-all ${
              selectedSubject === '' ? 'bg-teal-700 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
            }`}
          >
            All Subjects
          </button>
          {availableSubjects.map(sub => (
            <button
              key={sub}
              onClick={() => setSelectedSubject(sub)}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-all ${
                selectedSubject === sub ? 'bg-teal-700 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
              }`}
            >
              {sub}
            </button>
          ))}
        </div>
      )}

      {/* Papers Grid */}
      {loading ? (
        <Spinner size="lg" className="h-64" />
      ) : filteredPapers.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-xs bg-white rounded-xl border border-dashed border-slate-300">
          No published examinations or practice sets available currently.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredPapers.map((paper) => {
            const now = new Date();
            const startDate = paper.window_start ? new Date(paper.window_start) : null;
            const endDate = paper.window_end ? new Date(paper.window_end) : null;
            const isUpcoming = startDate ? now < startDate : false;
            const isClosed = endDate ? now > endDate : false;
            const hasWindow = !!(paper.window_start || paper.window_end);

            return (
              <Card
                key={paper.id}
                className={`transition-all flex flex-col justify-between ${
                  isUpcoming || isClosed ? 'opacity-85 border-slate-300' : 'hover:border-teal-400'
                }`}
              >
                <CardContent className="p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <Badge variant={paper.status === 'published' ? 'success' : 'teal'}>
                      {paper.status === 'published' ? 'Formal Exam' : 'Practice Set'}
                    </Badge>
                    <span className="text-[11px] font-mono text-slate-400">{paper.subject_id}</span>
                  </div>

                  <div>
                    <h3 className="font-bold text-sm text-[#0F172A] line-clamp-1">{paper.title}</h3>
                    <div className="text-[11px] text-slate-500 mt-1 line-clamp-2">
                      {paper.instructions || 'Answer all questions. Figures on the right indicate marks.'}
                    </div>
                  </div>

                  {/* Window Schedule Badges */}
                  {hasWindow && (
                    <div className="pt-1">
                      {isUpcoming && (
                        <div className="flex items-center gap-1.5 text-[11px] text-amber-700 bg-amber-50 p-1.5 rounded border border-amber-200">
                          <Clock className="w-3.5 h-3.5 flex-shrink-0" />
                          <span>Window opens {startDate?.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                      )}
                      {isClosed && (
                        <div className="flex items-center gap-1.5 text-[11px] text-red-700 bg-red-50 p-1.5 rounded border border-red-200">
                          <Lock className="w-3.5 h-3.5 flex-shrink-0" />
                          <span>Window closed {endDate?.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                      )}
                      {!isUpcoming && !isClosed && (
                        <div className="flex items-center gap-1.5 text-[11px] text-emerald-800 bg-emerald-50 p-1.5 rounded border border-emerald-200">
                          <Clock className="w-3.5 h-3.5 flex-shrink-0" />
                          <span>Window active until {endDate ? endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'close'}</span>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="p-3 bg-slate-50 rounded-lg grid grid-cols-3 gap-2 text-center text-xs">
                    <div>
                      <span className="text-[10px] text-slate-400 block">Questions</span>
                      <span className="font-bold text-slate-800">{paper.question_count || 'Multiple'}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block">Marks</span>
                      <span className="font-bold text-teal-800">{paper.total_marks}M</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block">Duration</span>
                      <span className="font-bold text-slate-800">{paper.duration_minutes}m</span>
                    </div>
                  </div>
                </CardContent>

                <div className="p-4 bg-[#F8FAFC] border-t border-[#E2E8F0]">
                  <Button
                    variant={isUpcoming || isClosed ? 'secondary' : 'teal'}
                    size="sm"
                    className="w-full justify-center"
                    disabled={isUpcoming || isClosed}
                    rightIcon={!isUpcoming && !isClosed ? <ArrowRight className="w-3.5 h-3.5" /> : undefined}
                    onClick={() => setSelectedPaper(paper)}
                  >
                    {isUpcoming ? 'Window Not Open' : isClosed ? 'Window Closed' : 'Start Assessment'}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Confirmation Modal Before Starting Assessment */}
      <Modal
        isOpen={!!selectedPaper}
        onClose={() => setSelectedPaper(null)}
        title="Start Assessment?"
        description={selectedPaper?.title}
        footer={
          <>
            <Button variant="secondary" onClick={() => setSelectedPaper(null)} disabled={starting}>
              Cancel
            </Button>
            <Button variant="teal" onClick={handleStartAttempt} isLoading={starting}>
              Begin Test Now
            </Button>
          </>
        }
      >
        <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
          {selectedPaper && (selectedPaper.window_start || selectedPaper.window_end) && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 space-y-1">
              <div className="flex items-center gap-1.5 font-bold">
                <Clock className="w-3.5 h-3.5 text-amber-700" />
                <span>Scheduled Examination Window</span>
              </div>
              <div className="text-[11px]">
                {selectedPaper.window_start && <div>• Opens: {new Date(selectedPaper.window_start).toLocaleString()}</div>}
                {selectedPaper.window_end && <div>• Closes: {new Date(selectedPaper.window_end).toLocaleString()}</div>}
              </div>
              <p className="text-[10px] text-amber-700 italic pt-0.5">
                Ensure all answers are submitted before the closing window timestamp.
              </p>
            </div>
          )}

          <div className="p-3 bg-teal-50 border border-teal-200 rounded-lg flex items-start gap-2.5 text-teal-900">
            <Clock className="w-4 h-4 text-teal-700 flex-shrink-0 mt-0.5" />
            <div>
              <strong>Timed Assessment Instructions:</strong>
              <p className="mt-1">
                You will have <strong>{selectedPaper?.duration_minutes} minutes</strong> to complete this test. The timer starts immediately upon clicking "Begin Test Now".
              </p>
            </div>
          </div>
          <ul className="list-disc pl-5 space-y-1 text-slate-600">
            <li>Answers are continuously auto-saved as you navigate questions.</li>
            <li>You may mark questions for review and return to them anytime before submission.</li>
            <li>Objective MCQs will be scored immediately upon submission.</li>
            <li>Descriptive questions will be routed to your professor's grading queue.</li>
          </ul>
        </div>
      </Modal>
    </div>
  );
};
