import { FileCheck, Clock, Loader2, ArrowUp } from 'lucide-react';

export default function DashboardStats() {
  const stats = [
    {
      title: 'Documents Processed',
      value: '1,247',
      change: '+12% this month',
      changePositive: true,
      icon: FileCheck,
      iconBg: 'bg-orange-100',
      iconColor: 'text-m4l-orange',
    },
    {
      title: 'Time Saved',
      value: '342 hrs',
      change: '+76% efficiency',
      changePositive: true,
      icon: Clock,
      iconBg: 'bg-blue-100',
      iconColor: 'text-m4l-blue',
    },
    {
      title: 'Active Jobs',
      value: '3',
      change: 'In processing queue',
      changePositive: null,
      icon: Loader2,
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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
