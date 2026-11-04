import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, Upload, Trash2, Eye, Sparkles, AlertCircle,
  CheckCircle2, Search, Filter, BookOpen, Clock, Tag
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatDate, formatFileSize } from '@/lib/formatters';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Spinner } from '@/components/ui/Spinner';
import { Alert } from '@/components/ui/Alert';

export const DocumentLibrary: React.FC = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<any[]>([]);
  const [subjects, setSubjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  
  // Upload modal state
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docTitle, setDocTitle] = useState('');
  const [selectedSubjectId, setSelectedSubjectId] = useState('ITS-401');
  const [unitNumber, setUnitNumber] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [loadingSample, setLoadingSample] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Preview modal state
  const [previewDoc, setPreviewDoc] = useState<any | null>(null);
  const [previewContent, setPreviewContent] = useState<any | null>(null);
  const [loadingContent, setLoadingContent] = useState(false);

  // Delete modal state
  const [deleteDoc, setDeleteDoc] = useState<any | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    apiFetch<any[]>('/subjects')
      .then(setSubjects)
      .catch(console.error);
  }, []);

  const loadDocuments = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (subjectFilter) params.append('subject_id', subjectFilter);

    apiFetch(`/documents?${params.toString()}`)
      .then(setDocuments)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const handleLoadSample = async () => {
    setLoadingSample(true);
    try {
      await apiFetch('/documents/sample', { method: 'POST' });
      setUploadModalOpen(false);
      setSelectedFile(null);
      setDocTitle('');
      setUploadError(null);
      loadDocuments();
    } catch (e: any) {
      alert(`Failed to load sample notes: ${e.message}`);
    } finally {
      setLoadingSample(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [search, subjectFilter]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setUploadError(null);
      if (!docTitle) {
        setDocTitle(file.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' '));
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setUploadError(null);
      if (!docTitle) {
        setDocTitle(file.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' '));
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadError('Please select a PDF or DOCX file to upload.');
      return;
    }
    
    setUploading(true);
    setUploadError(null);
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('title', docTitle.trim() || selectedFile.name);
    formData.append('subject_id', selectedSubjectId);
    formData.append('unit_number', String(unitNumber));
    
    try {
      await apiFetch('/documents', {
        method: 'POST',
        body: formData
      });
      setUploadModalOpen(false);
      setSelectedFile(null);
      setDocTitle('');
      setUploadError(null);
      loadDocuments();
    } catch (err: any) {
      setUploadError(err.message || 'File upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleOpenPreview = async (doc: any) => {
    setPreviewDoc(doc);
    setLoadingContent(true);
    try {
      const content = await apiFetch(`/documents/${doc.id}/content`);
      setPreviewContent(content);
    } catch (e: any) {
      setPreviewContent({ full_text: 'Failed to load text content.' });
    } finally {
      setLoadingContent(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteDoc) return;
    setDeleting(true);
    try {
      await apiFetch(`/documents/${deleteDoc.id}`, { method: 'DELETE' });
      setDeleteDoc(null);
      loadDocuments();
    } catch (e: any) {
      alert(`Deletion failed: ${e.message}`);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <h1 className="text-2xl font-bold text-[#0F172A]">Document Library</h1>
          <p className="text-xs text-[#64748B]">
            Upload course notes and syllabus documents to ground AI question generation.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="secondary"
            leftIcon={<BookOpen className="w-4 h-4 text-teal-600" />}
            onClick={handleLoadSample}
            isLoading={loadingSample}
          >
            Load Sample Notes
          </Button>
          <Button
            variant="primary"
            leftIcon={<Upload className="w-4 h-4" />}
            onClick={() => {
              setUploadError(null);
              setUploadModalOpen(true);
            }}
          >
            Upload Course Notes
          </Button>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 bg-white dark:bg-[#1E293B] p-3 rounded-xl border border-[#E2E8F0] dark:border-slate-800 shadow-sm">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search notes by title or keywords..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs rounded-lg border border-[#CBD5E1] dark:border-slate-700 bg-white dark:bg-slate-900 text-[#0F172A] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-100 dark:focus:ring-indigo-900"
          />
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={() => setSubjectFilter('')}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition-all ${
              subjectFilter === '' ? 'bg-[#3730A3] text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
            }`}
          >
            All Subjects
          </button>
          {subjects.map(s => (
            <button
              key={s.id}
              onClick={() => setSubjectFilter(s.id)}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-all ${
                subjectFilter === s.id ? 'bg-[#3730A3] text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
              }`}
            >
              {s.code}
            </button>
          ))}
        </div>
      </div>

      {/* Documents Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <Spinner size="lg" className="h-64" />
          ) : documents.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              No curriculum documents found. Click "Upload Course Notes" to get started.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#F8FAFC] text-[#64748B] font-semibold border-b border-[#E2E8F0]">
                  <tr>
                    <th className="py-3 px-4">Document Title</th>
                    <th className="py-3 px-4">Subject</th>
                    <th className="py-3 px-4">Unit</th>
                    <th className="py-3 px-4">Format / Size</th>
                    <th className="py-3 px-4">Extraction Status</th>
                    <th className="py-3 px-4">Uploaded</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-medium text-[#0F172A]">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-[#3730A3] flex-shrink-0" />
                          <div>
                            <div className="font-semibold">{doc.title}</div>
                            <div className="text-[11px] text-slate-400">{doc.original_filename}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="indigo" size="sm">{doc.subject_id || 'ITS-401'}</Badge>
                      </td>
                      <td className="py-3 px-4 text-slate-600">Unit {doc.unit_number || 'All'}</td>
                      <td className="py-3 px-4 text-slate-500">
                        <span className="uppercase font-semibold">{doc.file_type}</span> • {formatFileSize(doc.file_size)}
                      </td>
                      <td className="py-3 px-4">
                        <Badge
                          variant={
                            doc.extraction_status === 'completed'
                              ? 'success'
                              : doc.extraction_status === 'scanned_ocr_unsupported'
                              ? 'warning'
                              : 'error'
                          }
                          size="sm"
                        >
                          {doc.extraction_status === 'scanned_ocr_unsupported'
                            ? 'Scanned (No OCR)'
                            : doc.extraction_status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-slate-500">{formatDate(doc.created_at)}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Preview Extracted Text & Headings"
                            onClick={() => handleOpenPreview(doc)}
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </Button>
                          <Button
                            variant="teal"
                            size="sm"
                            title="Generate Questions from this Document"
                            onClick={() => navigate(`/faculty/generate?docId=${doc.id}`)}
                            leftIcon={<Sparkles className="w-3 h-3" />}
                          >
                            Generate
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700"
                            title="Delete Document"
                            onClick={() => setDeleteDoc(doc)}
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Document Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Upload Curriculum Notes"
        description="Supported formats: PDF or DOCX (up to 15 MB)"
        footer={
          <>
            <Button variant="secondary" onClick={() => setUploadModalOpen(false)} disabled={uploading}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleUpload}
              isLoading={uploading}
              disabled={!selectedFile || !docTitle.trim()}
            >
              Extract & Save
            </Button>
          </>
        }
      >
        <form onSubmit={handleUpload} className="space-y-4">
          {uploadError && (
            <Alert type="error" title="Upload Failed">
              {uploadError}
            </Alert>
          )}

          {/* Quick Sample Option */}
          <div className="p-3 bg-indigo-50/70 border border-indigo-200/80 rounded-xl space-y-1.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-[#1E293B]">Need sample curriculum files to test?</span>
              <button
                type="button"
                onClick={handleLoadSample}
                disabled={loadingSample}
                className="text-[#3730A3] font-bold hover:underline"
              >
                {loadingSample ? 'Loading...' : '⚡ Quick Load Sample Notes'}
              </button>
            </div>
            <p className="text-[11px] text-slate-500">
              Or <a href="/sample_its_notes.pdf" download="sample_its_notes.pdf" className="text-teal-700 font-semibold underline">download this pre-formatted sample PDF</a> and drop it below to test real file parsing.
            </p>
          </div>

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-6 text-center transition-all ${
              isDragging
                ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]'
                : selectedFile
                ? 'border-emerald-400 bg-emerald-50/30'
                : 'border-[#CBD5E1] hover:bg-slate-50'
            }`}
          >
            <input
              type="file"
              accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
              id="file-upload"
              className="hidden"
              onChange={handleFileChange}
            />
            <label htmlFor="file-upload" className="cursor-pointer block">
              {selectedFile ? (
                <div className="space-y-2">
                  <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-800 block">
                      {selectedFile.name}
                    </span>
                    <span className="text-[11px] text-emerald-700 font-medium block mt-0.5">
                      Ready for extraction • {(selectedFile.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                  <span className="text-[11px] text-indigo-600 hover:underline block pt-1">
                    Click or drop another file to replace
                  </span>
                </div>
              ) : (
                <>
                  <Upload className="w-8 h-8 text-[#3730A3] mx-auto mb-2" />
                  <span className="text-xs font-semibold text-[#0F172A] block">
                    Click to browse or drop PDF, DOCX, or TXT file here
                  </span>
                  <span className="text-[11px] text-slate-500 block mt-1">
                    Text-based notes (PDF, DOCX, TXT). Max size 15 MB.
                  </span>
                </>
              )}
            </label>
          </div>

          <Input
            label="Document Title"
            value={docTitle}
            onChange={(e) => setDocTitle(e.target.value)}
            placeholder="e.g. Unit 2: Advanced Traffic Management Systems Notes"
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Course Unit"
              value={unitNumber}
              onChange={(e) => setUnitNumber(Number(e.target.value))}
              options={[
                { value: 1, label: 'Unit 1: Fundamentals' },
                { value: 2, label: 'Unit 2: Architecture & Protocols' },
                { value: 3, label: 'Unit 3: Applied Systems & Algorithms' },
                { value: 4, label: 'Unit 4: Advanced Architectures' }
              ]}
            />
            <Select
              label="Subject"
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(e.target.value)}
              options={
                subjects.length > 0
                  ? subjects.map(s => ({ value: s.id, label: `${s.code} (${s.name.slice(0, 20)}...)` }))
                  : [
                      { value: 'ITS-401', label: 'ITS-401 (Intelligent Transport)' },
                      { value: 'CS-301', label: 'CS-301 (Distributed Systems)' },
                      { value: 'AI-402', label: 'AI-402 (NLP & LLMs)' },
                      { value: 'CY-201', label: 'CY-201 (Cryptography)' },
                      { value: 'DS-202', label: 'DS-202 (Advanced DSA)' }
                    ]
              }
            />
          </div>
        </form>
      </Modal>

      {/* Preview Extracted Text Modal */}
      <Modal
        isOpen={!!previewDoc}
        onClose={() => setPreviewDoc(null)}
        title={previewDoc?.title || 'Document Preview'}
        description={`File: ${previewDoc?.original_filename || ''}`}
        maxWidth="3xl"
        footer={
          <Button variant="secondary" onClick={() => setPreviewDoc(null)}>
            Close
          </Button>
        }
      >
        {loadingContent ? (
          <Spinner size="md" className="h-48" />
        ) : (
          <div className="space-y-4">
            {/* Detected Headings */}
            {previewDoc?.detected_headings && previewDoc.detected_headings.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-[#0F172A] mb-2 uppercase tracking-wider">
                  Detected Outline & Headings
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {previewDoc.detected_headings.map((h: string, idx: number) => (
                    <span key={idx} className="px-2 py-1 rounded bg-slate-100 text-slate-700 text-[11px]">
                      {h}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Text Body */}
            <div>
              <h4 className="text-xs font-bold text-[#0F172A] mb-1.5 uppercase tracking-wider">
                Extracted Text Content ({previewContent?.page_count || 1} pages)
              </h4>
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg max-h-96 overflow-y-auto text-xs font-mono text-slate-800 leading-relaxed whitespace-pre-wrap">
                {previewContent?.full_text || 'No text content available.'}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteDoc}
        onClose={() => setDeleteDoc(null)}
        title="Delete Document?"
        description="Are you sure you want to delete this curriculum document?"
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteDoc(null)} disabled={deleting}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDelete} isLoading={deleting}>
              Confirm Delete
            </Button>
          </>
        }
      >
        <p className="text-xs text-slate-600 leading-relaxed">
          Deleting <strong>"{deleteDoc?.title}"</strong> will remove it from the document library. Historical questions and question papers already created will preserve their citations and text snapshots.
        </p>
      </Modal>
    </div>
  );
};
