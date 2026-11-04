import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Layers, Plus, FileText, Printer, FileDown,
  Edit3, Trash2, CheckCircle2, Clock, Search, BookOpen
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatDate } from '@/lib/formatters';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';

export const PaperLibrary: React.FC = () => {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<any[]>([]);
  const [subjects, setSubjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [search, setSearch] = useState('');
  const [publishingId, setPublishingId] = useState<string | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  const loadPapers = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);
    if (subjectFilter) params.append('subject_id', subjectFilter);

    apiFetch(`/papers?${params.toString()}`)
      .then(setPapers)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    // Load subjects
    apiFetch<any[]>('/subjects')
      .then(setSubjects)
      .catch(console.error);
  }, []);

  useEffect(() => {
    loadPapers();
  }, [statusFilter, subjectFilter]);

  const handleExport = (paperId: string, type: 'paper' | 'key') => {
    const endpoint = type === 'paper' ? `/papers/${paperId}/export` : `/papers/${paperId}/answer-key`;
    window.open(`/api/v1${endpoint}`, '_blank');
  };

  const handleQuickPublish = async (paperId: string, title: string) => {
    if (!confirm(`Are you ready to formally publish "${title}"? This will make the examination immediately accessible to enrolled students.`)) {
      return;
    }

    setPublishingId(paperId);
    setFeedbackMessage(null);
    try {
      const res = await apiFetch(`/papers/${paperId}/publish`, { method: 'POST' });
      setFeedbackMessage(`Paper "${title}" published successfully as an official examination!`);
      loadPapers();
    } catch (e: any) {
      alert(`Publication failed: ${e.message}`);
    } finally {
      setPublishingId(null);
    }
  };

  const filteredPapers = papers.filter(p => {
    const matchesSearch = !search ||
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      (p.subject_id && p.subject_id.toLowerCase().includes(search.toLowerCase()));
    return matchesSearch;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0] dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-[#0F172A] dark:text-white">Examination Papers Library</h1>
            <Badge variant="indigo">{subjects.length > 0 ? `${subjects.length} Subjects Preloaded` : 'Multi-Subject'}</Badge>
          </div>
          <p className="text-xs text-[#64748B] dark:text-slate-400">
            Manage draft, practice, and published formal question papers and export official PDFs.
          </p>
        </div>

        <Link to="/faculty/papers/new">
          <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
            Create New Paper
          </Button>
        </Link>
      </div>

      {/* Success Notification Alert */}
      {feedbackMessage && (
        <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 text-xs rounded-xl flex items-center justify-between animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <span>{feedbackMessage}</span>
          </div>
          <button
            onClick={() => setFeedbackMessage(null)}
            className="text-emerald-600 hover:text-emerald-900 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="flex flex-col gap-3 bg-white dark:bg-[#1E293B] p-4 rounded-xl border border-[#E2E8F0] dark:border-slate-800 shadow-sm">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search papers by title or subject code (e.g. CS-301, ITS-401)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 text-xs rounded-lg border border-[#CBD5E1] dark:border-slate-700 bg-white dark:bg-slate-900 text-[#0F172A] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-100 dark:focus:ring-indigo-900"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={() => setStatusFilter('')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === '' ? 'bg-[#3730A3] text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
              }`}
            >
              All Papers
            </button>
            <button
              onClick={() => setStatusFilter('published')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === 'published' ? 'bg-emerald-700 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
              }`}
            >
              Published
            </button>
            <button
              onClick={() => setStatusFilter('draft')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === 'draft' ? 'bg-amber-700 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
              }`}
            >
              Drafts (Ready)
            </button>
          </div>
        </div>

        {/* Subject Filter Pills */}
        <div className="flex items-center gap-2 flex-wrap pt-2 border-t border-slate-100 dark:border-slate-800">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Subject:</span>
          <button
            onClick={() => setSubjectFilter('')}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition-all ${
              subjectFilter === '' ? 'bg-indigo-900 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
            }`}
          >
            All Subjects
          </button>
          {subjects.map(s => (
            <button
              key={s.id}
              onClick={() => setSubjectFilter(s.id)}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-all ${
                subjectFilter === s.id ? 'bg-[#3730A3] text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
              }`}
            >
              {s.code}
            </button>
          ))}
        </div>
      </div>

      {/* Papers Grid */}
      {loading ? (
        <Spinner size="lg" className="h-64" />
      ) : filteredPapers.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-xs bg-white dark:bg-[#1E293B] rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
          No examination papers found matching your criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredPapers.map((paper) => (
            <Card key={paper.id} className="hover:border-indigo-300 dark:hover:border-indigo-600 transition-all flex flex-col justify-between">
              <CardContent className="p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <Badge
                    variant={
                      paper.status === 'published'
                        ? 'success'
                        : paper.status === 'practice'
                        ? 'teal'
                        : 'warning'
                    }
                  >
                    {paper.status === 'draft' ? 'DRAFT (READY TO PUBLISH)' : paper.status.toUpperCase()}
                  </Badge>
                  <Badge variant="indigo" size="sm">{paper.subject_id}</Badge>
                </div>

                <div>
                  <h3 className="font-bold text-sm text-[#0F172A] dark:text-white line-clamp-2">{paper.title}</h3>
                  <span className="text-[10px] font-mono text-slate-400 block mt-1">{paper.id}</span>
                </div>

                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg grid grid-cols-3 gap-2 text-center text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Questions</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">{paper.question_count ?? '—'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Marks</span>
                    <span className="font-bold text-indigo-900 dark:text-indigo-400">{paper.total_marks}M</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Duration</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">{paper.duration_minutes}m</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400">
                  Last updated: {formatDate(paper.updated_at || paper.created_at)}
                </div>
              </CardContent>

              {/* Card Footer Actions */}
              <div className="p-3 bg-[#F8FAFC] dark:bg-slate-800/80 border-t border-[#E2E8F0] dark:border-slate-800 flex items-center justify-between gap-2 flex-wrap">
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    title="Export Question Paper PDF"
                    onClick={() => handleExport(paper.id, 'paper')}
                  >
                    <Printer className="w-4 h-4 text-slate-700 dark:text-slate-300" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    title="Export Answer Key PDF"
                    onClick={() => handleExport(paper.id, 'key')}
                  >
                    <FileDown className="w-4 h-4 text-red-600 dark:text-red-400" />
                  </Button>
                </div>

                <div className="flex items-center gap-1.5">
                  {paper.status === 'draft' && (
                    <Button
                      variant="primary"
                      size="sm"
                      isLoading={publishingId === paper.id}
                      leftIcon={<CheckCircle2 className="w-3.5 h-3.5" />}
                      onClick={() => handleQuickPublish(paper.id, paper.title)}
                    >
                      Publish
                    </Button>
                  )}

                  <Link to={`/faculty/papers/${paper.id}`}>
                    <Button variant="outline" size="sm" leftIcon={<Edit3 className="w-3.5 h-3.5" />}>
                      Builder
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
