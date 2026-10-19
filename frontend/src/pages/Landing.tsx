import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Zap,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Users,
  CreditCard,
  Sparkles,
  TrendingUp,
  Lock,
  RefreshCw,
  Sun,
  Moon,
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { AmountText } from "../components/ui/AmountText";
import { Avatar } from "../components/ui/Avatar";

export const Landing: React.FC = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 overflow-hidden relative selection:bg-indigo-500 selection:text-white">
      {/* Floating Background Glow Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-500/15 dark:bg-indigo-500/20 rounded-full blur-[120px] pointer-events-none animate-float-slow" />
      <div
        className="absolute top-[40%] right-[-10%] w-[600px] h-[600px] bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-[140px] pointer-events-none animate-float-slow"
        style={{ animationDelay: "3s" }}
      />

      {/* Header / Navbar */}
      <nav className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between relative z-20">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
            <Zap className="w-5 h-5 fill-current" />
          </div>
          <span className="font-extrabold font-heading text-xl tracking-tight">
            BillSplitter
          </span>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={toggleDarkMode}
            className="p-2.5 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Toggle theme"
          >
            {isDarkMode ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-indigo-500" />
            )}
          </button>

          <Link
            to="/login"
            className="text-sm font-bold text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 px-4 py-2 transition-colors hidden sm:inline-block"
          >
            Sign In
          </Link>

          <Link
            to="/login"
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-lg shadow-indigo-500/25 transition-all hover:-translate-y-0.5"
          >
            <span>Get Started</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 pt-12 pb-20 relative z-10">
        <div className="text-center space-y-6 max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs font-bold tracking-wide uppercase shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Smart Minimum-Transaction Debt Settlement</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl sm:text-6xl font-extrabold font-heading text-slate-900 dark:text-slate-100 tracking-tight leading-[1.15]"
          >
            Split bills effortlessly.{" "}
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-emerald-500 bg-clip-text text-transparent">
              Settle debts in minimum payments.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-base sm:text-lg text-slate-600 dark:text-slate-400 font-normal leading-relaxed"
          ></motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4"
          >
            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-base shadow-xl shadow-indigo-500/30 transition-all hover:-translate-y-1 flex items-center justify-center space-x-2"
            >
              <span>Start Splitting Bills</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>

        {/* Dynamic Moving Elements & Card Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
          className="mt-16 max-w-4xl mx-auto relative"
        >
          {/* Main App Preview Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden backdrop-blur-xl">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4 mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full bg-rose-500" />
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-xs font-bold text-slate-400 pl-2">
                  Goa Trip & Flatmates
                </span>
              </div>
              <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
                Debts Simplified
              </span>
            </div>

            {/* Live Moving Settlement Card Previews */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 rounded-2xl p-4 space-y-3">
                <div className="flex items-center justify-between text-xs font-bold text-slate-400 uppercase">
                  <span>Smart Settlement Plan</span>
                  <span className="text-indigo-600 dark:text-indigo-400">
                    3 Transfers Needed
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 text-xs">
                    <div className="flex items-center space-x-2">
                      <Avatar name="Karan Patel" size="sm" />
                      <span className="font-semibold">Karan → Asha</span>
                    </div>
                    <AmountText
                      amountPaise={250000}
                      currency="INR"
                      size="sm"
                      type="neutral"
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 text-xs">
                    <div className="flex items-center space-x-2">
                      <Avatar name="Sneha Gupta" size="sm" />
                      <span className="font-semibold">Sneha → Ravi</span>
                    </div>
                    <AmountText
                      amountPaise={180000}
                      currency="INR"
                      size="sm"
                      type="neutral"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-indigo-50/80 to-purple-50/80 dark:from-indigo-950/40 dark:to-purple-950/40 border border-indigo-100 dark:border-indigo-900/50 rounded-2xl p-5 flex flex-col justify-between">
                <div>
                  <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400 font-bold text-xs uppercase mb-1">
                    <Zap className="w-4 h-4 fill-current" />
                    <span>Instant Debt Reduction</span>
                  </div>
                  <p className="text-sm font-extrabold text-slate-900 dark:text-slate-100 mb-2">
                    Eliminates Circular Debts Automatically
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                    Instead of 12 pairwise IOUs between 6 friends, BillSplitter
                    condenses the entire group into just 3 clean payments.
                  </p>
                </div>

                <div className="pt-4 border-t border-indigo-200/50 dark:border-indigo-800/50 flex items-center justify-between text-xs font-bold text-indigo-700 dark:text-indigo-300">
                  <span>Saved 9 Unnecessary Transfers</span>
                  <CheckCircle2 className="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Feature Grid */}
      <section className="max-w-7xl mx-auto px-6 py-16 border-t border-slate-200 dark:border-slate-800 relative z-10">
        <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold font-heading text-slate-900 dark:text-slate-100">
            Everything you need to manage group expenses
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Engineered for precision, clarity, and zero math headaches.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <CreditCard className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold font-heading text-slate-900 dark:text-slate-100">
              4 Split Modes with Exact Paise Precision
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Split bills equally, by exact amounts, percentages, or shares.
              Largest-remainder rounding guarantees every single paisa adds up
              perfectly.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <RefreshCw className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold font-heading text-slate-900 dark:text-slate-100">
              Automatic Debt Network Simplification
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Circular debts like A paying B, B paying C, and C paying A are
              instantly detected and cancelled out behind the scenes.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-purple-100 dark:bg-purple-950 text-purple-600 dark:text-purple-400 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold font-heading text-slate-900 dark:text-slate-100">
              Prioritized Payment Queue
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Never miss a settlement. Pending payments are automatically queued
              by urgency and due date so everyone knows who pays next.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <footer className="max-w-7xl mx-auto px-6 py-12 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 dark:text-slate-400 gap-4">
        <div className="flex items-center space-x-6">
          <Link
            to="/login"
            className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
          >
            Sign In
          </Link>
          <Link
            to="/login"
            className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
          >
            Sign Up
          </Link>
        </div>
      </footer>
    </div>
  );
};
