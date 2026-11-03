import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen, Clock, Layers, Award, ArrowRight,
  ShieldCheck, AlertCircle, Sparkles
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

      {/* Papers Grid */}
      {loading ? (
        <Spinner size="lg" className="h-64" />
      ) : papers.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-xs bg-white rounded-xl border border-dashed border-slate-300">
          No published examinations or practice sets available currently.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {papers.map((paper) => (
            <Card
              key={paper.id}
              className="hover:border-teal-400 transition-all flex flex-col justify-between"
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
                  variant="teal"
                  size="sm"
                  className="w-full justify-center"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                  onClick={() => setSelectedPaper(paper)}
                >
                  Start Assessment
                </Button>
              </div>
            </Card>
          ))}
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
