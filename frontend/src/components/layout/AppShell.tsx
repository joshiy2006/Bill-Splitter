import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Layers,
  LayoutDashboard,
  Moon,
  Sun,
  LogOut,
  Plus,
  Zap,
  Menu,
  X,
  BookOpen
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

interface AppShellProps {
  children: React.ReactNode;
  groups?: Array<{ id: string; name: string }>;
  onCreateGroup?: () => void;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  groups = [],
  onCreateGroup,
}) => {
  const { user, signOut } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col md:flex-row">
      {/* Sidebar for Desktop */}
      <aside className="hidden md:flex flex-col w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 min-h-screen p-4 justify-between sticky top-0 h-screen z-20">
        <div className="space-y-6">
          {/* App Logo */}
          <Link to="/dashboard" className="flex items-center space-x-3 px-2">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
              <Zap className="w-5 h-5 fill-current" />
            </div>
            <div>
              <h1 className="font-extrabold font-heading text-base leading-tight tracking-tight">
                BillSplitter
              </h1>
              <span className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">
                Smart Debt Settlement
              </span>
            </div>
          </Link>

          {/* Nav Items */}
          <nav className="space-y-1">
            <Link
              to="/dashboard"
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-colors ${
                isActive('/dashboard')
                  ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>

            <Link
              to="/how-it-works"
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-colors ${
                isActive('/how-it-works')
                  ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>How It Works</span>
            </Link>
          </nav>

          {/* Group Section */}
          <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
            <div className="flex items-center justify-between px-3 mb-2">
              <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                My Groups
              </span>
              {onCreateGroup && (
                <button
                  onClick={onCreateGroup}
                  className="p-1 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950 rounded-lg transition-colors"
                  title="Create New Group"
                >
                  <Plus className="w-4 h-4" />
                </button>
              )}
            </div>

            <div className="space-y-1 max-h-48 overflow-y-auto no-scrollbar">
              {groups.length === 0 ? (
                <p className="text-xs text-slate-400 px-3 py-1 italic">No groups yet</p>
              ) : (
                groups.map((g) => (
                  <Link
                    key={g.id}
                    to={`/group/${g.id}`}
                    className={`flex items-center space-x-2.5 px-3 py-2 rounded-xl text-sm font-medium transition-colors ${
                      location.pathname.includes(g.id)
                        ? 'bg-slate-100 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    <Layers className="w-4 h-4 opacity-70" />
                    <span className="truncate">{g.name}</span>
                  </Link>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Footer / User & Theme */}
        <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-3">
          <button
            onClick={toggleDarkMode}
            className="flex items-center justify-between w-full px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <span className="flex items-center space-x-2">
              {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-500" />}
              <span>{isDarkMode ? 'Light Theme' : 'Dark Theme'}</span>
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700">
              {isDarkMode ? 'Dark' : 'Light'}
            </span>
          </button>

          <div className="flex items-center justify-between px-2 pt-2">
            <div className="truncate pr-2">
              <p className="text-xs font-bold truncate text-slate-800 dark:text-slate-200">
                {user?.email || 'Demo User'}
              </p>
              <p className="text-[10px] text-slate-400">Signed in</p>
            </div>
            <button
              onClick={() => signOut()}
              className="text-slate-400 hover:text-rose-500 p-1.5 rounded-lg transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile Header Bar */}
      <header className="md:hidden flex items-center justify-between px-4 py-3 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30">
        <Link to="/dashboard" className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white">
            <Zap className="w-4 h-4 fill-current" />
          </div>
          <span className="font-extrabold font-heading text-base">BillSplitter</span>
        </Link>
        <div className="flex items-center space-x-2">
          <button onClick={toggleDarkMode} className="p-2 rounded-lg text-slate-500">
            {isDarkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5" />}
          </button>
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-2 rounded-lg text-slate-500">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-4 sm:p-6 md:p-8 max-w-7xl mx-auto w-full mb-16 md:mb-0">
        {children}
      </main>
    </div>
  );
};
