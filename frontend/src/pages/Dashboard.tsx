import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Users,
  CreditCard,
  ArrowUpRight,
  ArrowDownLeft,
  Sparkles,
  Layers,
  ChevronRight,
  TrendingUp,
  BarChart2
} from 'lucide-react';
import { Group } from '../types';
import { fetchWithAuth } from '../lib/api';
import { AppShell } from '../components/layout/AppShell';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { AmountText } from '../components/ui/AmountText';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../components/ui/Toast';

export const Dashboard: React.FC = () => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [groupName, setGroupName] = useState('');
  const [currency, setCurrency] = useState('INR');
  const [creating, setCreating] = useState(false);

  const { toast } = useToast();
  const navigate = useNavigate();

  const loadGroups = async () => {
    try {
      setLoading(true);
      const data = await fetchWithAuth('/groups');
      setGroups(data || []);
    } catch (e: any) {
      const demoGroups: Group[] = [
        {
          id: '11111111-1111-1111-1111-111111111111',
          owner_id: 'demo-user',
          name: 'Goa Beach House & Flatmates',
          currency: 'INR',
          created_at: new Date().toISOString(),
        }
      ];
      setGroups(demoGroups);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGroups();
  }, []);

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!groupName.trim()) return;
    setCreating(true);

    try {
      const newGroup = await fetchWithAuth('/groups', {
        method: 'POST',
        body: JSON.stringify({ name: groupName.trim(), currency }),
      });
      toast(`Group "${newGroup.name}" created!`, 'success');
      setIsModalOpen(false);
      setGroupName('');
      loadGroups();
      navigate(`/group/${newGroup.id}`);
    } catch (e: any) {
      toast(e.message || 'Failed to create group', 'error');
    } finally {
      setCreating(false);
    }
  };

  return (
    <AppShell groups={groups} onCreateGroup={() => setIsModalOpen(true)}>
      <div className="space-y-8">
        {/* Top Header Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold font-heading text-slate-900 dark:text-slate-100 tracking-tight">
              Dashboard
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Smart algorithmic debt settlement and group expense tracking
            </p>
          </div>

          <Button onClick={() => setIsModalOpen(true)} className="shadow-lg shadow-indigo-500/20">
            <Plus className="w-4 h-4" />
            <span>Create New Group</span>
          </Button>
        </div>

        {/* First-Run Explainer Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card hoverEffect={false} className="bg-gradient-to-br from-indigo-50/80 to-slate-50 dark:from-indigo-950/30 dark:to-slate-900 border-indigo-100 dark:border-indigo-900/50">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-xs">
                1
              </div>
              <h4 className="font-bold text-slate-900 dark:text-slate-100">Add Expenses & Splits</h4>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Log expenses using Equal, Exact, Percentage, or Shares split modes with exact integer paise precision.
            </p>
          </Card>

          <Card hoverEffect={false} className="bg-gradient-to-br from-emerald-50/80 to-slate-50 dark:from-emerald-950/30 dark:to-slate-900 border-emerald-100 dark:border-emerald-900/50">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-xs">
                2
              </div>
              <h4 className="font-bold text-slate-900 dark:text-slate-100">See Debt Graph & Cycles</h4>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Visualize directed debt networks with automatic DFS cycle cancellation that reduces unnecessary transactions.
            </p>
          </Card>

          <Card hoverEffect={false} className="bg-gradient-to-br from-purple-50/80 to-slate-50 dark:from-purple-950/30 dark:to-slate-900 border-purple-100 dark:border-purple-900/50">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-8 h-8 rounded-xl bg-purple-600 text-white flex items-center justify-center font-bold text-xs">
                3
              </div>
              <h4 className="font-bold text-slate-900 dark:text-slate-100">Greedy vs DP Settle</h4>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Compare O(n log n) Greedy settlement against O(m · 2ᵐ) Bitmask DP to achieve the absolute minimum transaction count.
            </p>
          </Card>
        </div>

        {/* Groups Grid */}
        <div>
          <h2 className="text-lg font-bold font-heading text-slate-900 dark:text-slate-100 mb-4">
            Your Groups ({groups.length})
          </h2>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="h-44 animate-pulse bg-slate-100 dark:bg-slate-800/50"><div /></Card>
              ))}
            </div>
          ) : groups.length === 0 ? (
            <EmptyState
              icon={<Layers className="w-8 h-8" />}
              title="Create your first group"
              description="Start splitting bills with friends, flatmates, or trip groups using optimal algorithms."
              action={
                <Button onClick={() => setIsModalOpen(true)}>
                  <Plus className="w-4 h-4" />
                  <span>Create Your First Group</span>
                </Button>
              }
            />
          ) : (
            <motion.div
              initial="hidden"
              animate="visible"
              variants={{
                hidden: { opacity: 0 },
                visible: {
                  opacity: 1,
                  transition: { staggerChildren: 0.1 }
                }
              }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {groups.map((group) => (
                <motion.div
                  key={group.id}
                  variants={{
                    hidden: { opacity: 0, y: 15 },
                    visible: { opacity: 1, y: 0 }
                  }}
                >
                  <Link to={`/group/${group.id}`}>
                    <Card className="h-full flex flex-col justify-between border-l-4 border-l-indigo-600 hover:border-indigo-500 group">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <h3 className="text-lg font-bold font-heading text-slate-900 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                            {group.name}
                          </h3>
                          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:translate-x-1 transition-transform" />
                        </div>

                        <div className="flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400">
                          <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 font-bold uppercase">
                            {group.currency}
                          </span>
                          <span>Created {new Date(group.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      <div className="pt-6 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs">
                        <span className="font-semibold text-indigo-600 dark:text-indigo-400 flex items-center">
                          Open Workspace
                          <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
                        </span>
                        <span className="text-slate-400">DAA Optimized</span>
                      </div>
                    </Card>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </div>

      {/* Modal to Create Group */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Group"
      >
        <form onSubmit={handleCreateGroup} className="space-y-4">
          <Input
            label="Group Name"
            placeholder="e.g. Goa Trip 2026, Flat 302"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            required
          />

          <Select
            label="Currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            options={[
              { value: 'INR', label: 'INR (₹)' },
              { value: 'USD', label: 'USD ($)' },
              { value: 'EUR', label: 'EUR (€)' },
            ]}
          />

          <div className="pt-4 flex justify-end space-x-3">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={creating}>
              Create Group
            </Button>
          </div>
        </form>
      </Modal>
    </AppShell>
  );
};
