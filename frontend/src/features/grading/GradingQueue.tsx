import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  CheckSquare, Clock, User, ArrowRight, AlertCircle,
  CheckCircle2, RefreshCw
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatDate } from '@/lib/formatters';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';

export const GradingQueue: React.FC = () => {
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadQueue = () => {
    setLoading(true);
    apiFetch('/grading/queue')
      .then(setQueue)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQueue();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#E2E8F0]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-[#0F172A]">Descriptive Grading Queue</h1>
            <Badge variant="warning">{queue.length} Pending Submissions</Badge>
          </div>
          <p className="text-xs text-[#64748B]">
            Evaluate short-answer and long-answer descriptive submissions against model answers and rubric criteria.
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
          onClick={loadQueue}
        >
          Refresh Queue
        </Button>
      </div>

      {/* Queue List Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <Spinner size="lg" className="h-64" />
          ) : queue.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              All student submissions have been evaluated. Grading queue is clear!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#F8FAFC] text-[#64748B] font-semibold border-b border-[#E2E8F0]">
                  <tr>
                    <th className="py-3 px-4">Student</th>
                    <th className="py-3 px-4">Assessment Paper</th>
                    <th className="py-3 px-4">Submitted At</th>
                    <th className="py-3 px-4">Objective Score</th>
                    <th className="py-3 px-4">Descriptive Status</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {queue.map((item) => (
                    <tr key={item.attempt_id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-medium text-[#0F172A]">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded-full bg-indigo-50 border border-indigo-200 flex items-center justify-center font-bold text-[#3730A3]">
                            {item.student_name[0]}
                          </div>
                          <div>
                            <div className="font-semibold">{item.student_name}</div>
                            <div className="text-[11px] text-slate-400">{item.student_id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-medium text-slate-700">{item.title}</td>
                      <td className="py-3 px-4 text-slate-500">{formatDate(item.submitted_at)}</td>
                      <td className="py-3 px-4 font-semibold text-emerald-700">
                        {item.objective_score !== null ? `${item.objective_score} Marks` : '—'}
                      </td>
                      <td className="py-3 px-4">
                        <Badge
                          variant={item.pending_count === 0 ? 'success' : 'warning'}
                          size="sm"
                        >
                          {item.pending_count} of {item.total_descriptive} pending
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link to={`/faculty/grading/${item.attempt_id}`}>
                          <Button variant="primary" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                            Open Grading Workspace
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
