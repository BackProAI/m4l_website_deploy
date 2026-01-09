import { Bell, HelpCircle, FileText, FileCheck2, FileEdit } from 'lucide-react';
import DashboardStats from '@/components/DashboardStats';
import ToolCard from '@/components/ToolCard';
import RecentActivity from '@/components/RecentActivity';

export default function Home() {
  return (
    <main className="flex-1 overflow-y-auto">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-8 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-m4l-blue">Automation Dashboard</h2>
            <p className="text-gray-600 mt-1">Select a tool to streamline your workflow</p>
          </div>
          <div className="flex items-center space-x-4">
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900">
              <Bell className="h-6 w-6" />
            </button>
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900">
              <HelpCircle className="h-6 w-6" />
            </button>
          </div>
        </div>
      </header>

      {/* Content Area */}
      <div className="p-8">
        {/* Stats Cards */}
        <DashboardStats />

        {/* Tool Cards */}
        <h3 className="text-xl font-bold text-m4l-blue mb-6">Automation Tools</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ToolCard
            icon={FileText}
            iconBg="bg-orange-100"
            iconColor="text-m4l-orange"
            title="Post Review Automation"
            description="Process handwritten annotations on PDF documents and automatically apply changes to Word documents using AI-powered vision recognition."
            features={[
              'PDF annotation extraction',
              'M4L VL Model powered',
              'Auto-apply to Word docs',
            ]}
            buttonColor="bg-m4l-orange"
            buttonHoverColor="hover:bg-orange-600"
            href="/post-review"
          />

          <ToolCard
            icon={FileCheck2}
            iconBg="bg-blue-100"
            iconColor="text-m4l-blue"
            title="A3 Form Processing"
            description="Extract handwriting from A3 financial planning forms using advanced OCR technology and automatically populate PDF templates with recognised data."
            features={[
              'Sectioned OCR extraction',
              'M4L VL Model powered',
              'Auto-populate templates',
            ]}
            buttonColor="bg-m4l-blue"
            buttonHoverColor="hover:bg-blue-800"
            href="/a3-automation"
          />

          <ToolCard
            icon={FileEdit}
            iconBg="bg-green-100"
            iconColor="text-green-600"
            title="Value Creator Letters"
            description="Parse financial documents, detect strikethroughs and changes using intelligent chunking, and generate professional Word documents automatically."
            features={[
              '10-chunk detection system',
              'M4L VL Model powered',
              'Professional formatting',
            ]}
            buttonColor="bg-green-600"
            buttonHoverColor="hover:bg-green-700"
            href="/value-creator"
          />
        </div>

        {/* Recent Activity */}
        <RecentActivity />
      </div>
    </main>
  );
}
