'use client';

import { X, User, Bell, Sliders, Palette } from 'lucide-react';
import { useState, useEffect } from 'react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [settings, setSettings] = useState({
    // User Profile
    userName: 'Admin User',
    userEmail: 'admin@more4life.com.au',
    
    // Notifications
    emailNotifications: true,
    processingComplete: true,
    errorAlerts: true,
    
    // Default Processing Options
    enableOCR: true,
    enableSpellCheck: true,
    autoBackup: true,
    
    // Theme
    theme: 'system' as 'light' | 'dark' | 'system',
  });

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null;
    if (savedTheme) {
      setSettings(prev => ({ ...prev, theme: savedTheme }));
      applyTheme(savedTheme);
    } else {
      applyTheme('system');
    }
  }, []);

  const applyTheme = (theme: 'light' | 'dark' | 'system') => {
    const root = document.documentElement;
    const body = document.body;

    const setDark = (isDark: boolean) => {
      if (isDark) {
        root.classList.add('dark');
        body.classList.add('dark');
        root.setAttribute('data-theme', 'dark');
      } else {
        root.classList.remove('dark');
        body.classList.remove('dark');
        root.setAttribute('data-theme', 'light');
      }
    };

    if (theme === 'dark') {
      setDark(true);
    } else if (theme === 'light') {
      setDark(false);
    } else {
      // System theme - detect OS preference
      const m = window.matchMedia('(prefers-color-scheme: dark)');
      setDark(m.matches);
      // update on system change
      try {
        // use addEventListener when available
        m.addEventListener?.('change', (e: MediaQueryListEvent) => setDark(e.matches));
      } catch (e) {
        // fallback for older browsers
        m.addListener?.((e: MediaQueryListEvent) => setDark(e.matches));
      }
    }
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setSettings({ ...settings, theme: newTheme });
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const handleSave = () => {
    // Save settings to localStorage
    localStorage.setItem('theme', settings.theme);
    localStorage.setItem('settings', JSON.stringify(settings));
    console.log('Saving settings:', settings);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="bg-m4l-orange/10 p-2 rounded-lg">
              <Sliders className="h-6 w-6 text-m4l-orange" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-m4l-blue">Settings</h2>
              <p className="text-sm text-gray-600">Manage your preferences</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="h-6 w-6 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-gray-800 dark:text-gray-100">
          {/* User Profile Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-m4l-blue font-semibold">
              <User className="h-5 w-5" />
              <h3 className="text-lg">User Profile</h3>
            </div>
            <div className="space-y-3 pl-7">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={settings.userName}
                  onChange={(e) => setSettings({ ...settings, userName: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-m4l-orange focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={settings.userEmail}
                  onChange={(e) => setSettings({ ...settings, userEmail: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-m4l-orange focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-m4l-blue font-semibold">
              <Bell className="h-5 w-5" />
              <h3 className="text-lg">Notifications</h3>
            </div>
            <div className="space-y-3 pl-7">
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-sm text-gray-700">Email notifications</span>
                <input
                  type="checkbox"
                  checked={settings.emailNotifications}
                  onChange={(e) => setSettings({ ...settings, emailNotifications: e.target.checked })}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
              </label>
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-sm text-gray-700">Notify when processing completes</span>
                <input
                  type="checkbox"
                  checked={settings.processingComplete}
                  onChange={(e) => setSettings({ ...settings, processingComplete: e.target.checked })}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
              </label>
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-sm text-gray-700">Alert on errors</span>
                <input
                  type="checkbox"
                  checked={settings.errorAlerts}
                  onChange={(e) => setSettings({ ...settings, errorAlerts: e.target.checked })}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
              </label>
            </div>
          </div>

          {/* Default Processing Options */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-m4l-blue font-semibold">
              <Sliders className="h-5 w-5" />
              <h3 className="text-lg">Default Processing Options</h3>
            </div>
            <div className="space-y-3 pl-7">
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-sm text-gray-700">Enable OCR by default</span>
                <input
                  type="checkbox"
                  checked={settings.enableOCR}
                  onChange={(e) => setSettings({ ...settings, enableOCR: e.target.checked })}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
              </label>
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-sm text-gray-700">Enable spell check by default</span>
                <input
                  type="checkbox"
                  checked={settings.enableSpellCheck}
                  onChange={(e) => setSettings({ ...settings, enableSpellCheck: e.target.checked })}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
              </label>
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-sm text-gray-700">Auto-backup original files</span>
                <input
                  type="checkbox"
                  checked={settings.autoBackup}
                  onChange={(e) => setSettings({ ...settings, autoBackup: e.target.checked })}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
              </label>
            </div>
          </div>

          {/* Theme Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-m4l-blue font-semibold">
              <Palette className="h-5 w-5" />
              <h3 className="text-lg">Appearance</h3>
            </div>
            <div className="space-y-3 pl-7">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Theme
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {(['light', 'dark', 'system'] as const).map((theme) => (
                    <button
                      key={theme}
                      onClick={() => handleThemeChange(theme)}
                      className={`px-4 py-2 rounded-lg border-2 transition-colors capitalize bg-[var(--surface)] text-[var(--foreground)] ${
                        settings.theme === theme
                          ? 'border-m4l-orange font-medium ring-2 ring-m4l-orange/20'
                          : 'border-[rgba(0,0,0,0.06)] hover:border-m4l-orange'
                      }`}
                    >
                      {theme}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-2 bg-m4l-orange text-white rounded-lg hover:bg-orange-600 transition-colors"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
