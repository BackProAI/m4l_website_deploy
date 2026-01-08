'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { 
  Menu, 
  Home, 
  FileText, 
  FileCheck2, 
  FileEdit, 
  History, 
  Settings, 
  User 
} from 'lucide-react';
import Image from 'next/image';
import SettingsModal from './SettingsModal';

export default function Sidebar() {
  const [isExpanded, setIsExpanded] = useState(true);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const pathname = usePathname();

  const toggleSidebar = () => {
    setIsExpanded(!isExpanded);
  };

  const navItems = [
    { icon: Home, label: 'Dashboard', href: '/' },
    { icon: FileText, label: 'Post Review', href: '/post-review' },
    { icon: FileCheck2, label: 'A3 Form Processing', href: '/a3-automation' },
    { icon: FileEdit, label: 'Value Creator Letters', href: '/value-creator' },
  ];

  const bottomNavItems = [
    { icon: History, label: 'History', href: '/history', action: null },
    { icon: Settings, label: 'Settings', href: null, action: () => setShowSettingsModal(true) },
  ];

  return (
    <aside 
      className={`bg-[var(--surface)] dark:bg-[var(--surface)] shadow-lg flex flex-col transition-all duration-300 ease-in-out ${
        isExpanded ? 'w-[280px]' : 'w-[80px]'
      }`}
    >
      {/* Logo Section */}
      <div className="p-6 border-b border-[rgba(0,0,0,0.06)] dark:border-[rgba(255,255,255,0.06)] flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 bg-m4l-orange rounded-lg flex items-center justify-center text-white font-bold">
            M4L
          </div>
          {isExpanded && (
            <div className="transition-opacity duration-200">
              <h1 className="text-lg font-bold text-[var(--foreground)]">More4Life</h1>
              <p className="text-xs text-[var(--muted)]">Automation Hub</p>
            </div>
          )}
        </div>
        <button
          onClick={toggleSidebar}
          className="text-[var(--muted)] hover:text-[var(--foreground)] focus:outline-none"
        >
          <Menu className="h-6 w-6" />
        </button>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item, index) => {
          const isActive = pathname === item.href;
          return (
            <a
              key={index}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                isActive
                  ? 'bg-orange-50 dark:bg-orange-900/30 text-m4l-orange dark:text-orange-400'
                  : 'text-[var(--foreground)] hover:bg-[var(--surface)] dark:hover:bg-[rgba(255,255,255,0.02)]'
              }`}
            >
              <item.icon className="h-6 w-6 flex-shrink-0" />
              {isExpanded && (
                <span className="transition-opacity duration-200">{item.label}</span>
              )}
            </a>
          );
        })}

        <div className="border-t border-[rgba(0,0,0,0.06)] dark:border-[rgba(255,255,255,0.06)] my-4"></div>

        {bottomNavItems.map((item, index) => {
          const isActive = pathname === item.href;
          
          if (item.action) {
            // Settings button - opens modal
            return (
              <button
                key={index}
                onClick={item.action}
                className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-[var(--foreground)] hover:bg-[var(--surface)] dark:hover:bg-[rgba(255,255,255,0.02)] font-medium transition-colors"
              >
                <item.icon className="h-6 w-6 flex-shrink-0" />
                {isExpanded && (
                  <span className="transition-opacity duration-200">{item.label}</span>
                )}
              </button>
            );
          }
          
          // History link - navigates to page
          return (
            <a
              key={index}
              href={item.href!}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                isActive
                  ? 'bg-orange-50 dark:bg-orange-900/30 text-m4l-orange dark:text-orange-400'
                    : 'text-[var(--foreground)] hover:bg-[var(--surface)] dark:hover:bg-[rgba(255,255,255,0.02)]'
              }`}
            >
              <item.icon className="h-6 w-6 flex-shrink-0" />
              {isExpanded && (
                <span className="transition-opacity duration-200">{item.label}</span>
              )}
            </a>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-[rgba(0,0,0,0.06)] dark:border-[rgba(255,255,255,0.06)]">
        <div className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-[var(--surface)] dark:hover:bg-[rgba(255,255,255,0.02)] cursor-pointer">
          <div className="w-10 h-10 rounded-full bg-m4l-orange flex items-center justify-center text-white font-semibold flex-shrink-0">
            <User className="h-5 w-5" />
          </div>
          {isExpanded && (
            <div className="transition-opacity duration-200">
              <p className="text-sm font-medium text-[var(--foreground)]">Admin User</p>
              <p className="text-xs text-[var(--muted)]">admin@more4life.com.au</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Settings Modal */}
      <SettingsModal 
        isOpen={showSettingsModal} 
        onClose={() => setShowSettingsModal(false)} 
      />
    </aside>
  );
}
