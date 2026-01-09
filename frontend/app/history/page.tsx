'use client';

import { useState, useEffect } from 'react';
import { 
  Download, 
  FileText, 
  FileCheck2, 
  FileEdit, 
  CheckCircle, 
  XCircle, 
  Clock,
  Search,
  Filter,
  Calendar,
  Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';

interface HistoryItem {
  id: string;
  tool: 'post-review' | 'a3-automation' | 'value-creator';
  fileName: string;
  status: 'completed' | 'failed' | 'processing';
  timestamp: string;
  downloadUrl?: string;
  error?: string;
}

export default function HistoryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTool, setFilterTool] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/history?days=30');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('History API response:', data); // Debug log
      
      // Handle both possible response formats
      if (Array.isArray(data)) {
        setHistory(data);
      } else if (data && Array.isArray(data.history)) {
        setHistory(data.history);
      } else {
        console.error('Unexpected response format:', data);
        setHistory([]);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load history';
      console.error('History fetch error:', err);
      setError(errorMsg);
      toast.error(errorMsg);
      setHistory([]); // Set empty array on error
    } finally {
      setIsLoading(false);
    }
  };

  const getToolIcon = (tool: string) => {
    switch (tool) {
      case 'post-review':
        return FileText;
      case 'a3-automation':
        return FileCheck2;
      case 'value-creator':
        return FileEdit;
      default:
        return FileText;
    }
  };

  const getToolName = (tool: string) => {
    switch (tool) {
      case 'post-review':
        return 'Post Review';
      case 'a3-automation':
        return 'A3 Form Processing';
      case 'value-creator':
        return 'Value Creator';
      default:
        return tool;
    }
  };

  const getStatusColor = (_status: string) => {
    // Use neutral dark-mode friendly badge base; color is shown on the icon instead.
    return 'text-[var(--foreground)] bg-[var(--surface)] border-[rgba(255,255,255,0.04)]';
  };

  const getStatusIconColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'failed':
        return 'text-red-400';
      case 'processing':
        return 'text-blue-400';
      default:
        return 'text-[var(--muted)]';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircle;
      case 'failed':
        return XCircle;
      case 'processing':
        return Clock;
      default:
        return Clock;
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Filter history
  const filteredHistory = history.filter((item) => {
    const matchesSearch = item.fileName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTool = filterTool === 'all' || item.tool === filterTool;
    const matchesStatus = filterStatus === 'all' || item.status === filterStatus;
    return matchesSearch && matchesTool && matchesStatus;
  });

  return (
    <main className="flex-1 overflow-y-auto">
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-m4l-blue mb-2">Processing History</h1>
          <p className="text-gray-600">
            View and download your previously processed documents (last 30 days)
          </p>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 text-m4l-blue animate-spin" />
            <span className="ml-3 text-gray-600">Loading history...</span>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6">
            <p className="text-red-800">{error}</p>
            <button
              onClick={fetchHistory}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Content */}
        {!isLoading && !error && (
          <>
        <div className="bg-[var(--surface)] rounded-xl shadow-sm border border-[rgba(255,255,255,0.04)] p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Files
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-[var(--muted)]" />
                <input
                  type="text"
                  placeholder="Search by filename..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-[rgba(255,255,255,0.04)] rounded-lg focus:ring-2 focus:ring-m4l-orange focus:border-transparent bg-[var(--surface)] text-[var(--foreground)]"
                />
              </div>
            </div>

            {/* Tool Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Tool
              </label>
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-[var(--muted)]" />
                <select
                  value={filterTool}
                  onChange={(e) => setFilterTool(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-[rgba(255,255,255,0.04)] rounded-lg focus:ring-2 focus:ring-m4l-orange focus:border-transparent appearance-none bg-[var(--surface)] text-[var(--foreground)]"
                >
                  <option value="all">All Tools</option>
                  <option value="post-review">Post Review</option>
                  <option value="a3-automation">A3 Form Processing</option>
                  <option value="value-creator">Value Creator</option>
                </select>
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Status
              </label>
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-[var(--muted)]" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-[rgba(255,255,255,0.04)] rounded-lg focus:ring-2 focus:ring-m4l-orange focus:border-transparent appearance-none bg-[var(--surface)] text-[var(--foreground)]"
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                  <option value="processing">Processing</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* History List */}
        <div className="space-y-4">
          {filteredHistory.length === 0 ? (
            <div className="bg-[var(--surface)] rounded-xl shadow-sm border border-[rgba(255,255,255,0.04)] p-12 text-center">
              <Calendar className="h-16 w-16 text-[var(--muted)] mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-[var(--foreground)] mb-2">No history found</h3>
              <p className="text-[var(--muted)]">
                {searchQuery || filterTool !== 'all' || filterStatus !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Start processing documents to see them here'}
              </p>
            </div>
          ) : (
            filteredHistory.map((item) => {
              const ToolIcon = getToolIcon(item.tool);
              const StatusIcon = getStatusIcon(item.status);
              
              return (
                <div
                  key={item.id}
                  className="bg-[var(--surface)] rounded-xl shadow-sm border border-[rgba(255,255,255,0.04)] p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* Left Side - Info */}
                    <div className="flex items-start gap-4 flex-1">
                      {/* Tool Icon */}
                      <div className="bg-[rgba(14,165,164,0.06)] p-3 rounded-lg">
                        <ToolIcon className="h-6 w-6 text-m4l-blue" />
                      </div>

                      {/* Details */}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-[var(--foreground)] mb-1 truncate">
                          {item.fileName}
                        </h3>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-[var(--muted)]">
                          <span className="flex items-center gap-1">
                            <ToolIcon className="h-4 w-4" />
                            {getToolName(item.tool)}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            {formatDate(item.timestamp)}
                          </span>
                        </div>
                        {item.error && (
                          <p className="text-sm text-red-400 mt-2">
                            Error: {item.error}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Right Side - Status & Actions */}
                    <div className="flex items-center gap-3">
                      {/* Status Badge */}
                      <div
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-full border font-medium text-sm ${getStatusColor(
                          item.status
                        )}`}
                      >
                        <StatusIcon className={`${getStatusIconColor(item.status)} h-4 w-4`} />
                        <span className="capitalize">{item.status}</span>
                      </div>

                      {/* Download Button */}
                      {item.status === 'completed' && item.downloadUrl && (
                        <a
                          href={item.downloadUrl}
                          download
                          className="flex items-center gap-2 px-4 py-2 bg-m4l-orange text-white rounded-lg hover:bg-orange-600 transition-colors"
                        >
                          <Download className="h-5 w-5" />
                          <span className="hidden sm:inline">Download</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Summary Stats */}
        {filteredHistory.length > 0 && (
          <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-3xl font-bold text-m4l-blue">
                  {filteredHistory.length}
                </p>
                <p className="text-sm text-gray-600 mt-1">Total Jobs</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-green-600">
                  {filteredHistory.filter((i) => i.status === 'completed').length}
                </p>
                <p className="text-sm text-gray-600 mt-1">Completed</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-red-600">
                  {filteredHistory.filter((i) => i.status === 'failed').length}
                </p>
                <p className="text-sm text-gray-600 mt-1">Failed</p>
              </div>
            </div>
          </div>
        )}
        </>
        )}
      </div>
    </main>
  );
}
