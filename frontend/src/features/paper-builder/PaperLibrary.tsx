import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Layers, Plus, FileText, Printer, FileDown,
  Edit3, Trash2, CheckCircle2, Clock, Search
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
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');

  const loadPapers = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);

    apiFetch(`/papers?${params.toString()}`)
      .then(setPapers)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadPapers();
  }, [statusFilter]);

  const handleExport = (paperId: string, type: 'paper' | 'key') => {
    const endpoint = type === 'paper' ? `/papers/${paperId}/export` : `/papers/${paperId}/answer-key`;
    window.open(`/api/v1${endpoint}`, '_blank');
  };

  const filteredPapers = papers.filter(p =>
    !search || p.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-[#0F172A]">Examination Papers Library</h1>
            <Badge variant="indigo">Subject: ITS-401</Badge>
          </div>
          <p className="text-xs text-[#64748B]">
            Manage draft, practice, and published formal question papers and export official PDFs.
          </p>
        </div>

        <Link to="/faculty/papers/new">
          <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
            Create New Paper
          </Button>
        </Link>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 bg-white p-3 rounded-xl border border-[#E2E8F0] shadow-sm">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search papers by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs rounded-lg border border-[#CBD5E1] focus:outline-none focus:ring-2 focus:ring-indigo-100"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            onClick={() => setStatusFilter('')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === '' ? 'bg-[#3730A3] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Papers
          </button>
          <button
            onClick={() => setStatusFilter('published')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === 'published' ? 'bg-emerald-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Published
          </button>
          <button
            onClick={() => setStatusFilter('practice')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === 'practice' ? 'bg-teal-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Practice
          </button>
          <button
            onClick={() => setStatusFilter('draft')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === 'draft' ? 'bg-amber-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Drafts
          </button>
        </div>
      </div>

      {/* Papers Grid */}
      {loading ? (
        <Spinner size="lg" className="h-64" />
      ) : filteredPapers.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-xs bg-white rounded-xl border border-dashed border-slate-300">
          No examination papers found. Click "Create New Paper" to build one.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredPapers.map((paper) => (
            <Card key={paper.id} className="hover:border-indigo-300 transition-all flex flex-col justify-between">
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
                    {paper.status.toUpperCase()}
                  </Badge>
                  <span className="text-[11px] font-mono text-slate-400">{paper.id}</span>
                </div>

                <div>
                  <h3 className="font-bold text-sm text-[#0F172A] line-clamp-1">{paper.title}</h3>
                  <div className="text-[11px] text-slate-500 mt-1">Subject: {paper.subject_id}</div>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg grid grid-cols-3 gap-2 text-center text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Questions</span>
                    <span className="font-bold text-slate-800">{paper.question_count ?? '—'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Marks</span>
                    <span className="font-bold text-indigo-900">{paper.total_marks}M</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Duration</span>
                    <span className="font-bold text-slate-800">{paper.duration_minutes}m</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400">
                  Last updated: {formatDate(paper.updated_at || paper.created_at)}
                </div>
              </CardContent>

              {/* Card Footer Actions */}
              <div className="p-4 bg-[#F8FAFC] border-t border-[#E2E8F0] flex items-center justify-between gap-2">
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    title="Export Question Paper PDF"
                    onClick={() => handleExport(paper.id, 'paper')}
                  >
                    <Printer className="w-4 h-4 text-slate-700" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    title="Export Answer Key PDF"
                    onClick={() => handleExport(paper.id, 'key')}
                  >
                    <FileDown className="w-4 h-4 text-red-600" />
                  </Button>
                </div>

                <Link to={`/faculty/papers/${paper.id}`}>
                  <Button variant="outline" size="sm" leftIcon={<Edit3 className="w-3.5 h-3.5" />}>
                    Open Builder
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
