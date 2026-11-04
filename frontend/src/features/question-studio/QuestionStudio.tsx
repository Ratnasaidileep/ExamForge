import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Sparkles, FileText, CheckCircle2, AlertCircle, Info,
  BookOpen, Sliders, ArrowRight, ShieldCheck, KeyRound
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Alert } from '@/components/ui/Alert';
import { Spinner } from '@/components/ui/Spinner';

export const QuestionStudio: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedDocId = searchParams.get('docId');

  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string>(preselectedDocId || '');
  const [unitNumber, setUnitNumber] = useState<number>(1);
  const [questionTypes, setQuestionTypes] = useState<string[]>(['mcq', 'short_answer', 'long_answer']);
  const [difficulty, setDifficulty] = useState<string>('mixed');
  const [questionCount, setQuestionCount] = useState<number>(5);
  const [customInstructions, setCustomInstructions] = useState<string>('');

  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<any | null>(null);
  const [healthStatus, setHealthStatus] = useState<any | null>(null);

  useEffect(() => {
    // Check health to see if Gemini key is configured
    apiFetch('/health')
      .then(setHealthStatus)
      .catch(console.error);

    // Load available documents
    apiFetch<any[]>('/documents')
      .then((docs) => {
        setDocuments(docs);
        if (!selectedDocId && docs.length > 0) {
          setSelectedDocId(docs[0].id);
        }
      })
      .catch(console.error);
  }, []);

  const handleTypeToggle = (type: string) => {
    if (questionTypes.includes(type)) {
      if (questionTypes.length > 1) {
        setQuestionTypes(questionTypes.filter(t => t !== type));
      }
    } else {
      setQuestionTypes([...questionTypes, type]);
    }
  };

  const handleGenerate = async (useOfflineDemo = false) => {
    if (!selectedDocId) {
      alert('Please select a source document.');
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);

    const selectedDoc = documents.find(d => d.id === selectedDocId);
    const payload = {
      document_id: selectedDocId,
      subject_id: selectedDoc?.subject_id || 'ITS-401',
      unit_number: unitNumber,
      question_types: questionTypes,
      difficulty,
      requested_count: questionCount,
      custom_instructions: customInstructions,
      use_offline_demo: useOfflineDemo
    };

    try {
      const res = await apiFetch<any>('/generations', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      if (!res.success) {
        setGenerationError(res);
      } else {
        navigate(`/faculty/generation/${res.job_id}`);
      }
    } catch (err: any) {
      setGenerationError({
        error_type: 'API_ERROR',
        message: err.message || 'Generation request failed.'
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const selectedDoc = documents.find(d => d.id === selectedDocId);

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="pb-2 border-b border-[#E2E8F0]">
        <div className="flex items-center gap-2 mb-1">
          <h1 className="text-2xl font-bold text-[#0F172A]">AI Question Generation Studio</h1>
          <Badge variant="teal">Google GenAI Grounded</Badge>
        </div>
        <p className="text-xs text-[#64748B]">
          Generate syllabus-aligned exam questions strictly grounded in your curriculum notes.
        </p>
      </div>

      {/* Gemini Configuration Status Banner */}
      {healthStatus && !healthStatus.gemini_configured && (
        <Alert
          type="warning"
          title="Gemini API Key Required for Live AI"
          action={
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                alert('Add your GEMINI_API_KEY into backend/.env and restart the backend server.');
              }}
            >
              Setup Guide
            </Button>
          }
        >
          No active <code>GEMINI_API_KEY</code> detected in <code>backend/.env</code>. Live AI requests will prompt for configuration. You can also review and approve pre-seeded course questions in the Question Bank.
        </Alert>
      )}

      {/* Generation Error Banner */}
      {generationError && (
        <Alert
          type="error"
          title={generationError.error_type === 'MISSING_API_KEY' ? 'Gemini Key Missing' : 'Generation Notice'}
        >
          {generationError.message}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Source Document Card */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#3730A3]" />
                <span>1. Source Document</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 pt-0">
              <Select
                label="Selected Document"
                value={selectedDocId}
                onChange={(e) => setSelectedDocId(e.target.value)}
                options={documents.map(d => ({
                  value: d.id,
                  label: d.title
                }))}
              />

              {selectedDoc && (
                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg space-y-1.5 text-xs">
                  <div className="text-slate-500 font-medium">Document Details:</div>
                  <div className="text-[#0F172A] dark:text-white font-semibold">{selectedDoc.title}</div>
                  <div className="text-slate-500">Subject: <span className="font-semibold text-indigo-700 dark:text-indigo-400">{selectedDoc.subject_id}</span></div>
                  <div className="text-slate-500">Unit: {selectedDoc.unit_number || 'All'}</div>
                  <div className="text-slate-500">Format: {selectedDoc.file_type.toUpperCase()}</div>
                  <div className="flex items-center gap-1.5 text-emerald-700 font-medium pt-1">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Evidence base ready</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-indigo-50/50 border-indigo-100">
            <CardContent className="p-4 space-y-2 text-xs">
              <div className="flex items-center gap-2 font-bold text-[#3730A3]">
                <ShieldCheck className="w-4 h-4" />
                <span>Grounding Guarantee</span>
              </div>
              <p className="text-slate-600 leading-relaxed text-[11px]">
                Every generated question quotes an excerpt from the document. Excerpts are verified through lexical substring checks to prevent hallucinations.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Right 2 Columns: Generation Parameters */}
        <div className="md:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Sliders className="w-4 h-4 text-[#0F766E]" />
                <span>2. Question Blueprint Parameters</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-0">
              {/* Question Types (Multi-select) */}
              <div>
                <label className="block text-xs font-semibold text-[#1E293B] mb-1.5">
                  Allowed Question Types (Mixed Mode supported)
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => handleTypeToggle('mcq')}
                    className={`p-2.5 rounded-lg border text-xs font-semibold flex flex-col items-center gap-1 transition-all ${
                      questionTypes.includes('mcq')
                        ? 'border-[#3730A3] bg-indigo-50/70 text-[#3730A3]'
                        : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <span>Multiple Choice</span>
                    <span className="text-[10px] font-normal opacity-75">4 options + explanation</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleTypeToggle('short_answer')}
                    className={`p-2.5 rounded-lg border text-xs font-semibold flex flex-col items-center gap-1 transition-all ${
                      questionTypes.includes('short_answer')
                        ? 'border-[#3730A3] bg-indigo-50/70 text-[#3730A3]'
                        : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <span>Short Answer</span>
                    <span className="text-[10px] font-normal opacity-75">Concise model answer</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleTypeToggle('long_answer')}
                    className={`p-2.5 rounded-lg border text-xs font-semibold flex flex-col items-center gap-1 transition-all ${
                      questionTypes.includes('long_answer')
                        ? 'border-[#3730A3] bg-indigo-50/70 text-[#3730A3]'
                        : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <span>Long Answer</span>
                    <span className="text-[10px] font-normal opacity-75">System analysis + rubric</span>
                  </button>
                </div>
              </div>

              {/* Difficulty and Count Grid */}
              <div className="grid grid-cols-2 gap-4">
                <Select
                  label="Difficulty Level"
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  options={[
                    { value: 'mixed', label: 'Mixed (Balanced distribution)' },
                    { value: 'easy', label: 'Easy (Recall & definitions)' },
                    { value: 'medium', label: 'Medium (Application & analysis)' },
                    { value: 'hard', label: 'Hard (System design & trade-offs)' }
                  ]}
                />

                <Select
                  label="Question Count"
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                  options={[
                    { value: 3, label: '3 Questions' },
                    { value: 5, label: '5 Questions' },
                    { value: 8, label: '8 Questions' },
                    { value: 10, label: '10 Questions' }
                  ]}
                />
              </div>

              {/* Custom Instructions */}
              <div>
                <label className="block text-xs font-semibold text-[#1E293B] mb-1.5">
                  Specific Focus / Custom Instructions (Optional)
                </label>
                <textarea
                  rows={3}
                  value={customInstructions}
                  onChange={(e) => setCustomInstructions(e.target.value)}
                  placeholder="e.g. Focus heavily on Section 4.2 Cooperative Adaptive Cruise Control (CACC) platooning equations and DSRC latency benchmarks."
                  className="w-full text-xs rounded-lg border border-[#CBD5E1] p-3 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
              </div>

              {/* Submit Buttons */}
              <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
                <Button
                  variant="primary"
                  size="lg"
                  className="w-full sm:flex-1 justify-center"
                  onClick={() => handleGenerate(false)}
                  isLoading={isGenerating}
                  leftIcon={<Sparkles className="w-4 h-4" />}
                >
                  Generate with Gemini AI
                </Button>
                <Button
                  variant="secondary"
                  size="lg"
                  className="w-full sm:flex-1 justify-center border-teal-200 text-teal-800 hover:bg-teal-50"
                  onClick={() => handleGenerate(true)}
                  isLoading={isGenerating}
                  leftIcon={<BookOpen className="w-4 h-4 text-teal-600" />}
                >
                  Generate Sample (Demo Mode)
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
