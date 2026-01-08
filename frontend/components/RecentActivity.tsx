import { FileText, FileCheck2, FileEdit } from 'lucide-react';

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

export default function RecentActivity() {
  const activities = [
    {
      icon: FileText,
      iconBg: 'bg-[rgba(245,158,11,0.08)]',
      iconColor: 'text-m4l-orange',
      fileName: 'Client_Review_Q4_2024.pdf',
      toolName: 'Post Review Automation',
      time: '5 minutes ago',
      status: 'Completed',
    },
    {
      icon: FileCheck2,
      iconBg: 'bg-[rgba(59,130,246,0.08)]',
      iconColor: 'text-m4l-blue',
      fileName: 'Financial_Plan_A3_Form.pdf',
      toolName: 'A3 Form Processing',
      time: '12 minutes ago',
      status: 'Processing',
    },
    {
      icon: FileEdit,
      iconBg: 'bg-[rgba(34,197,94,0.08)]',
      iconColor: 'text-green-500',
      fileName: 'Value_Letter_Smith_Family.docx',
      toolName: 'Value Creator Letters',
      time: '28 minutes ago',
      status: 'Completed',
    },
  ];

  return (
    <div className="mt-8 bg-[var(--surface)] rounded-xl shadow-sm p-6 border border-[rgba(255,255,255,0.04)]">
      <h3 className="text-xl font-bold text-[var(--foreground)] mb-4">Recent Activity</h3>
      
      <div className="space-y-4">
        {activities.map((activity, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-4 bg-[rgba(255,255,255,0.01)] rounded-lg"
          >
            <div className="flex items-center space-x-4">
              <div
                className={`w-10 h-10 ${activity.iconBg} rounded-full flex items-center justify-center`}
              >
                <activity.icon className={`h-5 w-5 ${activity.iconColor}`} />
              </div>
              <div>
                <p className="font-medium text-[var(--foreground)]">{activity.fileName}</p>
                <p className="text-sm text-[var(--muted)]">
                  {activity.toolName} • {activity.time}
                </p>
              </div>
            </div>
            <span className="px-3 py-1 bg-[var(--surface)] border-[rgba(255,255,255,0.04)] rounded-full text-sm font-medium text-[var(--foreground)] flex items-center gap-2">
              <span className={`${getStatusIconColor(activity.status)} inline-block w-2 h-2 rounded-full`} />
              <span className="capitalize">{activity.status}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
