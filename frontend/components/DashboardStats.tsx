'use client';

import { FileCheck, ArrowUp } from 'lucide-react';
import { useEffect, useState } from 'react';

interface HistoryItem {
  id: string;
  tool: string;
  status: string;
  timestamp: string;
}

export default function DashboardStats() {
  const [totalDocs, setTotalDocs] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch('/api/history?days=30');
        const data = await response.json();
        
        const historyItems: HistoryItem[] = Array.isArray(data) ? data : data.history || [];
        setTotalDocs(historyItems.length);
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        setTotalDocs(0);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  const stats = [
    {
      title: 'Documents Processed',
      value: loading ? '...' : totalDocs.toString(),
      change: 'Last 30 days',
      changePositive: null,
      icon: FileCheck,
      iconBg: 'bg-orange-100',
      iconColor: 'text-m4l-orange',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-1 gap-6 mb-8">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">{stat.title}</p>
              <p className="text-3xl font-bold text-m4l-blue mt-2">{stat.value}</p>
              <p
                className={`text-sm mt-2 ${
                  stat.changePositive === true
                    ? 'text-green-600'
                    : stat.changePositive === false
                    ? 'text-red-600'
                    : 'text-gray-500'
                }`}
              >
                {stat.changePositive === true && (
                  <ArrowUp className="inline h-4 w-4" />
                )}
                {stat.change}
              </p>
            </div>
            <div
              className={`w-14 h-14 ${stat.iconBg} rounded-full flex items-center justify-center`}
            >
              <stat.icon className={`h-7 w-7 ${stat.iconColor}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
