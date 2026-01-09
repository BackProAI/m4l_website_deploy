'use client';

import { FileText, FileCheck2, FileEdit } from 'lucide-react';
import { useEffect, useState } from 'react';

interface HistoryItem {
  id: string;
  fileName: string;
  tool: string;
  status: string;
  timestamp: string;
}

const getStatusIconColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'bg-green-400';
    case 'failed':
      return 'bg-red-400';
    case 'processing':
      return 'bg-blue-400';
    default:
      return 'bg-[var(--muted)]';
  }
};

const getToolIcon = (tool: string) => {
  const toolLower = tool.toLowerCase();
  if (toolLower.includes('post')) {
    return { icon: FileText, iconBg: 'bg-[rgba(245,158,11,0.08)]', iconColor: 'text-m4l-orange' };
  } else if (toolLower.includes('a3')) {
    return { icon: FileCheck2, iconBg: 'bg-[rgba(59,130,246,0.08)]', iconColor: 'text-m4l-blue' };
  } else if (toolLower.includes('value')) {
    return { icon: FileEdit, iconBg: 'bg-[rgba(34,197,94,0.08)]', iconColor: 'text-green-500' };
  }
  return { icon: FileText, iconBg: 'bg-gray-100', iconColor: 'text-gray-500' };
};

const formatTimeAgo = (timestamp: string) => {
  const now = new Date();
  const time = new Date(timestamp);
  const diffMs = now.getTime() - time.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
};

export default function RecentActivity() {
  const [activities, setActivities] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRecentActivity() {
      try {
        const response = await fetch('/api/history?days=30');
        const data = await response.json();
        
        const historyItems: HistoryItem[] = Array.isArray(data) ? data : data.history || [];
        // Get the 3 most recent items
        setActivities(historyItems.slice(0, 3));
      } catch (error) {
        console.error('Error fetching recent activity:', error);
        setActivities([]);
      } finally {
        setLoading(false);
      }
    }

    fetchRecentActivity();
  }, []);

  if (loading) {
    return (
      <div className="mt-8 bg-[var(--surface)] rounded-xl shadow-sm p-6 border border-[rgba(255,255,255,0.04)]">
        <h3 className="text-xl font-bold text-[var(--foreground)] mb-4">Recent Activity</h3>
        <p className="text-[var(--muted)] text-center py-8">Loading...</p>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="mt-8 bg-[var(--surface)] rounded-xl shadow-sm p-6 border border-[rgba(255,255,255,0.04)]">
        <h3 className="text-xl font-bold text-[var(--foreground)] mb-4">Recent Activity</h3>
        <p className="text-[var(--muted)] text-center py-8">No recent activity</p>
      </div>
    );
  }

  return (
    <div className="mt-8 bg-[var(--surface)] rounded-xl shadow-sm p-6 border border-[rgba(255,255,255,0.04)]">
      <h3 className="text-xl font-bold text-[var(--foreground)] mb-4">Recent Activity</h3>
      
      <div className="space-y-4">
        {activities.map((activity) => {
          const toolStyle = getToolIcon(activity.tool);
          const Icon = toolStyle.icon;
          return (
            <div
              key={activity.id}
              className="flex items-center justify-between p-4 bg-[rgba(255,255,255,0.01)] rounded-lg"
            >
              <div className="flex items-center space-x-4">
                <div
                  className={`w-10 h-10 ${toolStyle.iconBg} rounded-full flex items-center justify-center`}
                >
                  <Icon className={`h-5 w-5 ${toolStyle.iconColor}`} />
                </div>
                <div>
                  <p className="font-medium text-[var(--foreground)]">{activity.fileName}</p>
                  <p className="text-sm text-[var(--muted)]">
                    {activity.tool} • {formatTimeAgo(activity.timestamp)}
                  </p>
                </div>
              </div>
              <span className="px-3 py-1 bg-[var(--surface)] border-[rgba(255,255,255,0.04)] rounded-full text-sm font-medium text-[var(--foreground)] flex items-center gap-2">
                <span className={`${getStatusIconColor(activity.status)} inline-block w-2 h-2 rounded-full`} />
                <span className="capitalize">{activity.status}</span>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
