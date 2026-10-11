import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import ReactFlow, { Background, Controls, Node, Edge, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import {
  DollarSign,
  Users,
  Plus,
  ArrowRight,
  CheckCircle2,
  Zap,
  Trash2,
  Search,
  RefreshCw,
  PieChart as PieIcon,
  Sparkles,
  Clock,
  Check,
  CheckCircle,
  TrendingUp,
  SlidersHorizontal
} from 'lucide-react';

import {
  Group,
  Member,
  Expense,
  ExpenseCreatePayload,
  SplitType,
  SettleCompareResponse,
  DebtGraphResponse,
  InsightsResponse,
  SettlementTransaction
} from '../types';
import { fetchWithAuth } from '../lib/api';
import { AppShell } from '../components/layout/AppShell';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Tabs, TabItem } from '../components/ui/Tabs';
import { Avatar } from '../components/ui/Avatar';
import { AmountText } from '../components/ui/AmountText';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../components/ui/Toast';

export const GroupWorkspace: React.FC = () => {
  const { id: groupId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [group, setGroup] = useState<Group | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [balances, setBalances] = useState<Record<string, number>>({});
  const [debtGraph, setDebtGraph] = useState<DebtGraphResponse | null>(null);
  const [comparison, setComparison] = useState<SettleCompareResponse | null>(null);
  const [paymentsQueue, setPaymentsQueue] = useState<SettlementTransaction[]>([]);
  const [insights, setInsights] = useState<InsightsResponse | null>(null);

  const [activeTab, setActiveTab] = useState('expenses');
  const [loading, setLoading] = useState(true);
  const [graphMode, setGraphMode] = useState<'simplified' | 'raw'>('simplified');

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [suggestions, setSuggestions] = useState<string[]>([]);

  // Add Member Modal State
  const [isMemberModalOpen, setIsMemberModalOpen] = useState(false);
  const [newMemberName, setNewMemberName] = useState('');

  // Add Expense Modal State
  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [desc, setDesc] = useState('');
  const [category, setCategory] = useState('food');
  const [amountRupees, setAmountRupees] = useState('');
  const [paidBy, setPaidBy] = useState('');
  const [splitType, setSplitType] = useState<SplitType>('equal');
  const [selectedMemberIds, setSelectedMemberIds] = useState<string[]>([]);
  const [exactAmounts, setExactAmounts] = useState<Record<string, string>>({});
  const [percentages, setPercentages] = useState<Record<string, string>>({});
  const [shares, setShares] = useState<Record<string, string>>({});
  const [submittingExpense, setSubmittingExpense] = useState(false);

  // Partition DP Modal State
  const [allocateItems, setAllocateItems] = useState([
    { description: 'Dinner Bill', amount_paise: 120000 },
    { description: 'Movie Tickets', amount_paise: 80000 },
    { description: 'Cab Fare', amount_paise: 40000 },
  ]);
  const [allocationResult, setAllocationResult] = useState<any>(null);

  const loadData = async () => {
    if (!groupId) return;
    try {
      setLoading(true);

      const gData = await fetchWithAuth(`/groups/${groupId}`);
      setGroup(gData);

      const mData = await fetchWithAuth(`/groups/${groupId}/members`);
      setMembers(mData || []);

      if (mData && mData.length > 0) {
        setPaidBy(mData[0].id);
        setSelectedMemberIds(mData.map((m: Member) => m.id));
      }

      const eData = await fetchWithAuth(`/groups/${groupId}/expenses`);
      setExpenses(eData || []);

      const bData = await fetchWithAuth(`/groups/${groupId}/balances`);
      setBalances(bData || {});

      const dgData = await fetchWithAuth(`/groups/${groupId}/debt-graph`);
      setDebtGraph(dgData);

      const qData = await fetchWithAuth(`/groups/${groupId}/payments/queue`);
      setPaymentsQueue(qData || []);

      const iData = await fetchWithAuth(`/groups/${groupId}/insights/top?k=5`);
      setInsights(iData);
    } catch (err: any) {
      toast(err.message || 'Failed to load workspace data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [groupId]);

  useEffect(() => {
    if (desc.trim().length >= 2 && groupId) {
      fetchWithAuth(`/groups/${groupId}/expenses/suggest?prefix=${encodeURIComponent(desc.trim())}`)
        .then((data) => setSuggestions(data || []))
        .catch(() => setSuggestions([]));
    } else {
      setSuggestions([]);
    }
  }, [desc, groupId]);

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMemberName.trim() || !groupId) return;
    try {
      await fetchWithAuth(`/groups/${groupId}/members`, {
        method: 'POST',
        body: JSON.stringify({ name: newMemberName.trim() }),
      });
      toast(`Member "${newMemberName}" added!`, 'success');
      setNewMemberName('');
      setIsMemberModalOpen(false);
      loadData();
    } catch (err: any) {
      toast(err.message || 'Failed to add member', 'error');
    }
  };

  const handleAddExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!groupId || !desc.trim() || !amountRupees || selectedMemberIds.length === 0) return;

    const amountPaise = Math.round(parseFloat(amountRupees) * 100);
    if (isNaN(amountPaise) || amountPaise <= 0) {
      toast('Please enter a valid amount', 'error');
      return;
    }

    const participantsPayload = selectedMemberIds.map((mId) => {
      const p: any = { member_id: mId };
      if (splitType === 'exact') {
        p.owed_paise = Math.round(parseFloat(exactAmounts[mId] || '0') * 100);
      } else if (splitType === 'percentage') {
        p.percentage = parseFloat(percentages[mId] || '0');
      } else if (splitType === 'shares') {
        p.shares = parseFloat(shares[mId] || '1');
      }
      return p;
    });

    const payload: ExpenseCreatePayload = {
      description: desc.trim(),
      category,
      amount_paise: amountPaise,
      paid_by: paidBy,
      split_type: splitType,
      participants: participantsPayload,
    };

    setSubmittingExpense(true);
    try {
      await fetchWithAuth(`/groups/${groupId}/expenses`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      toast('Expense added successfully!', 'success');
      setIsExpenseModalOpen(false);
      setDesc('');
      setAmountRupees('');
      loadData();
    } catch (err: any) {
      toast(err.message || 'Failed to add expense', 'error');
    } finally {
      setSubmittingExpense(false);
    }
  };

  const handleDeleteExpense = async (eid: string) => {
    if (!groupId) return;
    try {
      await fetchWithAuth(`/groups/${groupId}/expenses/${eid}`, { method: 'DELETE' });
      toast('Expense deleted', 'info');
      loadData();
    } catch (err: any) {
      toast(err.message || 'Failed to delete expense', 'error');
    }
  };

  const handleCalculateSettlement = async () => {
    if (!groupId) return;
    try {
      const res = await fetchWithAuth(`/groups/${groupId}/settle/compare`, { method: 'POST' });
      setComparison(res);
      toast('Optimal settlement plan calculated!', 'success');
    } catch (err: any) {
      toast(err.message || 'Calculation failed', 'error');
    }
  };

  const handleAdoptPlan = async (runId: string) => {
    if (!groupId) return;
    try {
      await fetchWithAuth(`/groups/${groupId}/settle/adopt`, {
        method: 'POST',
        body: JSON.stringify({ run_id: runId }),
      });
      toast('Plan adopted! Payment queue updated.', 'success');
      loadData();
    } catch (err: any) {
      toast(err.message || 'Failed to adopt plan', 'error');
    }
  };

  const handlePayTransaction = async (txnId: string) => {
    if (!groupId) return;
    try {
      await fetchWithAuth(`/groups/${groupId}/payments/${txnId}/pay`, { method: 'POST' });
      toast('Transaction marked as paid!', 'success');
      loadData();
    } catch (err: any) {
      toast(err.message || 'Failed to process payment', 'error');
    }
  };

  const handleAllocatePartition = async () => {
    if (!groupId) return;
    try {
      const res = await fetchWithAuth(`/groups/${groupId}/allocate`, {
        method: 'POST',
        body: JSON.stringify(allocateItems),
      });
      setAllocationResult(res);
      toast('Balanced item split complete!', 'success');
    } catch (err: any) {
      toast(err.message || 'Allocation failed', 'error');
    }
  };

  const memberNameMap = members.reduce((acc, m) => ({ ...acc, [m.id]: m.name }), {} as Record<string, string>);
  const totalSpentPaise = expenses.reduce((sum, e) => sum + e.amount_paise, 0);

  const flowNodes: Node[] = members.map((m, idx) => {
    const angle = (idx / (members.length || 1)) * 2 * Math.PI;
    const radius = 150;
    const x = 250 + radius * Math.cos(angle);
    const y = 200 + radius * Math.sin(angle);
    return {
      id: m.id,
      data: { label: m.name },
      position: { x, y },
      style: {
        background: '#1e293b',
        color: '#fff',
        borderRadius: '12px',
        padding: '10px 16px',
        fontWeight: 'bold',
        fontSize: '13px',
        border: '2px solid #6366f1',
      },
    };
  });

  const activeEdges = debtGraph ? (graphMode === 'simplified' ? debtGraph.simplified : debtGraph.raw) : [];

  const flowEdges: Edge[] = activeEdges.map((e, idx) => ({
    id: `e-${idx}`,
    source: e.from_member,
    target: e.to_member,
    label: `₹${(e.amount_paise / 100).toFixed(2)}`,
    animated: true,
    style: { stroke: '#10b981', strokeWidth: Math.min(6, Math.max(2, e.amount_paise / 100000)) },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' },
  }));

  const tabItems: TabItem[] = [
    { id: 'expenses', label: 'Expenses', icon: <DollarSign className="w-4 h-4" />, badge: expenses.length },
    { id: 'balances', label: 'Balances', icon: <Users className="w-4 h-4" /> },
    { id: 'graph', label: 'Debt Network', icon: <RefreshCw className="w-4 h-4" /> },
    { id: 'settle', label: 'Settle Up', icon: <Zap className="w-4 h-4" /> },
    { id: 'payments', label: 'Payment Plan', icon: <Clock className="w-4 h-4" />, badge: paymentsQueue.length },
    { id: 'insights', label: 'Insights', icon: <PieIcon className="w-4 h-4" /> },
    { id: 'allocate', label: 'Fair Split Tool', icon: <Sparkles className="w-4 h-4" /> },
  ];

  // Preferred optimal plan (prefers DP if available, otherwise greedy)
  const activePlan = comparison ? (comparison.dp || comparison.greedy) : null;

  return (
    <AppShell groups={[{ id: group?.id || '', name: group?.name || 'Group' }]}>
      <div className="space-y-6">
        {/* Workspace Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <h1 className="text-2xl font-extrabold font-heading text-slate-900 dark:text-slate-100">
                {group?.name || 'Group Workspace'}
              </h1>
              <Badge variant="info">{group?.currency || 'INR'}</Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {members.length} Members · Total Spent: <AmountText amountPaise={totalSpentPaise} currency={group?.currency} size="sm" />
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <Button variant="outline" size="sm" onClick={() => setIsMemberModalOpen(true)}>
              <Users className="w-4 h-4" />
              <span>Add Member</span>
            </Button>
            <Button size="sm" onClick={() => setIsExpenseModalOpen(true)}>
              <Plus className="w-4 h-4" />
              <span>Add Expense</span>
            </Button>
          </div>
        </div>

        {/* Member Avatars Bar */}
        <div className="flex items-center space-x-2 overflow-x-auto no-scrollbar py-1">
          {members.map((m) => (
            <div key={m.id} className="flex items-center space-x-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-full px-3 py-1.5 shadow-sm">
              <Avatar name={m.name} size="sm" />
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">{m.name}</span>
            </div>
          ))}
        </div>

        {/* Workspace Navigation Tabs */}
        <Tabs tabs={tabItems} activeTab={activeTab} onChange={setActiveTab} />

        {/* TAB 1: EXPENSES */}
        {activeTab === 'expenses' && (
          <div className="space-y-4">
            {/* Search & Filter Bar */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <Input
                  placeholder="Search expense descriptions or names..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  icon={<Search className="w-4 h-4" />}
                />
              </div>
              <Select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Categories' },
                  { value: 'food', label: 'Food' },
                  { value: 'travel', label: 'Travel' },
                  { value: 'rent', label: 'Rent' },
                  { value: 'utilities', label: 'Utilities' },
                  { value: 'entertainment', label: 'Entertainment' },
                ]}
                className="sm:w-48"
              />
            </div>

            {/* Expenses List */}
            {expenses.length === 0 ? (
              <EmptyState
                icon={<DollarSign className="w-8 h-8" />}
                title="No expenses logged yet"
                description="Add expenses using Equal, Exact, Percentage, or Shares split modes."
                action={<Button onClick={() => setIsExpenseModalOpen(true)}>Add Expense</Button>}
              />
            ) : (
              <div className="space-y-3">
                {expenses
                  .filter((e) =>
                    (categoryFilter === 'all' || e.category.toLowerCase() === categoryFilter) &&
                    (searchQuery === '' || e.description.toLowerCase().includes(searchQuery.toLowerCase()))
                  )
                  .map((exp) => (
                    <Card key={exp.id} hoverEffect={false} className="flex items-center justify-between p-4">
                      <div className="flex items-center space-x-4">
                        <Avatar name={memberNameMap[exp.paid_by] || 'Member'} size="md" />
                        <div>
                          <div className="flex items-center space-x-2">
                            <h4 className="font-bold text-slate-900 dark:text-slate-100">{exp.description}</h4>
                            <Badge variant="neutral" size="sm">{exp.category}</Badge>
                            <Badge variant="info" size="sm">{exp.split_type}</Badge>
                          </div>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            Paid by <span className="font-semibold text-slate-700 dark:text-slate-300">{memberNameMap[exp.paid_by] || exp.paid_by}</span> on {exp.expense_date}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-4">
                        <AmountText amountPaise={exp.amount_paise} currency={group?.currency} size="lg" type="neutral" />
                        <button
                          onClick={() => handleDeleteExpense(exp.id)}
                          className="text-slate-400 hover:text-rose-500 p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                          title="Delete Expense"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </Card>
                  ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: BALANCES */}
        {activeTab === 'balances' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card className="text-center p-4">
                <p className="text-xs font-bold uppercase text-slate-400">Total Group Spent</p>
                <AmountText amountPaise={totalSpentPaise} currency={group?.currency} size="2xl" type="neutral" />
              </Card>
              <Card className="text-center p-4">
                <p className="text-xs font-bold uppercase text-slate-400">Group Members</p>
                <p className="text-2xl font-extrabold text-slate-900 dark:text-slate-100">{members.length}</p>
              </Card>
              <Card className="text-center p-4">
                <p className="text-xs font-bold uppercase text-slate-400">Total Outstanding Debt</p>
                <AmountText
                  amountPaise={Object.values(balances).filter((v) => v > 0).reduce((a, b) => a + b, 0)}
                  currency={group?.currency}
                  size="2xl"
                  type="owed"
                />
              </Card>
            </div>

            <Card className="p-6 space-y-4">
              <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 font-heading">
                Member Net Balances
              </h3>
              <div className="space-y-4">
                {members.map((m) => {
                  const net = balances[m.id] || 0;
                  const maxNet = Math.max(1, ...Object.values(balances).map(Math.abs));
                  const pct = Math.min(100, (Math.abs(net) / maxNet) * 100);

                  return (
                    <div key={m.id} className="space-y-1.5">
                      <div className="flex items-center justify-between text-sm font-semibold">
                        <div className="flex items-center space-x-2">
                          <Avatar name={m.name} size="sm" />
                          <span>{m.name}</span>
                        </div>
                        <AmountText amountPaise={net} currency={group?.currency} size="md" />
                      </div>

                      <div className="relative h-2.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-slate-400 z-10" />
                        {net > 0 && (
                          <div
                            className="absolute left-1/2 top-0 bottom-0 bg-emerald-500 rounded-r-full transition-all duration-500"
                            style={{ width: `${pct / 2}%` }}
                          />
                        )}
                        {net < 0 && (
                          <div
                            className="absolute right-1/2 top-0 bottom-0 bg-rose-500 rounded-l-full transition-all duration-500"
                            style={{ width: `${pct / 2}%` }}
                          />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        )}

        {/* TAB 3: DEBT NETWORK */}
        {activeTab === 'graph' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-lg font-heading text-slate-900 dark:text-slate-100">
                  Directed Debt Network
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Circular debts are automatically simplified to minimize transfers
                </p>
              </div>

              <div className="flex items-center bg-slate-200 dark:bg-slate-800 p-1 rounded-xl">
                <button
                  onClick={() => setGraphMode('simplified')}
                  className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                    graphMode === 'simplified' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Simplified Network
                </button>
                <button
                  onClick={() => setGraphMode('raw')}
                  className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                    graphMode === 'raw' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Raw Debts
                </button>
              </div>
            </div>

            <Card hoverEffect={false} className="h-96 p-0 overflow-hidden relative">
              <ReactFlow nodes={flowNodes} edges={flowEdges} fitView>
                <Background color="#6366f1" gap={16} size={1} />
                <Controls />
              </ReactFlow>
            </Card>

            {debtGraph && debtGraph.cancelled_cycles.length > 0 && (
              <Card hoverEffect={false} className="bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-900/50 p-4">
                <div className="flex items-center space-x-2 text-emerald-800 dark:text-emerald-300 font-bold text-sm mb-2">
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  <span>Automatic Cycle Debt Simplification Applied</span>
                </div>
                <div className="space-y-1 text-xs text-emerald-900 dark:text-emerald-200">
                  {debtGraph.cancelled_cycles.map((c, i) => (
                    <p key={i}>
                      Simplified circular debt loop: {c.nodes.map((nid) => memberNameMap[nid] || nid).join(' → ')} → {memberNameMap[c.nodes[0]] || c.nodes[0]} (Reduced: ₹{(c.bottleneck_paise / 100).toFixed(2)})
                    </p>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}

        {/* TAB 4: SETTLE UP (SMART OPTIMAL PLAN) */}
        {activeTab === 'settle' && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-br from-indigo-900 to-slate-900 text-white rounded-3xl p-6 shadow-xl">
              <div>
                <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/30 text-indigo-300 text-xs font-bold uppercase tracking-wide mb-2">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Optimal Minimum-Transfer Engine</span>
                </div>
                <h3 className="text-2xl font-extrabold font-heading">
                  Smart Settlement Plan
                </h3>
                <p className="text-xs text-slate-300 mt-1 max-w-lg">
                  Calculates the absolute minimum number of payments required to settle all balances in the group cleanly.
                </p>
              </div>

              <Button onClick={handleCalculateSettlement} className="bg-white text-indigo-900 hover:bg-slate-100 font-bold shadow-lg">
                <Zap className="w-4 h-4 fill-indigo-900" />
                <span>Calculate Optimal Plan</span>
              </Button>
            </div>

            {/* Active Optimal Settlement Plan Card */}
            {activePlan ? (
              <Card hoverEffect={false} className="p-6 space-y-6">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
                  <div>
                    <h4 className="font-bold text-lg font-heading text-slate-900 dark:text-slate-100">
                      Recommended Payment Transfers
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Requires only <strong className="text-indigo-600 dark:text-indigo-400 font-extrabold">{activePlan.txn_count} payment(s)</strong> to settle all group debts.
                    </p>
                  </div>
                  <Badge variant="success">Optimum Found</Badge>
                </div>

                <div className="space-y-3">
                  {activePlan.transactions.map((t, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-100 dark:border-slate-700/60">
                      <div className="flex items-center space-x-3 text-sm">
                        <Avatar name={memberNameMap[t.from_member] || t.from_member} size="sm" />
                        <span><strong className="text-indigo-600 dark:text-indigo-400 font-bold">{memberNameMap[t.from_member] || t.from_member}</strong> pays <strong className="text-emerald-600 dark:text-emerald-400 font-bold">{memberNameMap[t.to_member] || t.to_member}</strong></span>
                      </div>
                      <AmountText amountPaise={t.amount_paise} currency={group?.currency} size="lg" type="neutral" />
                    </div>
                  ))}
                </div>

                <div className="pt-2 flex justify-end">
                  <Button onClick={() => handleAdoptPlan(activePlan.id)} className="shadow-lg shadow-indigo-500/20">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    <span>Adopt & Queue Payment Plan</span>
                  </Button>
                </div>
              </Card>
            ) : (
              <EmptyState
                icon={<Zap className="w-8 h-8" />}
                title="Calculate Optimal Settlement"
                description="Click 'Calculate Optimal Plan' to run the smart engine and generate the fewest transfers."
                action={
                  <Button onClick={handleCalculateSettlement}>
                    <Zap className="w-4 h-4" />
                    <span>Calculate Plan</span>
                  </Button>
                }
              />
            )}
          </div>
        )}

        {/* TAB 5: PAYMENTS QUEUE */}
        {activeTab === 'payments' && (
          <div className="space-y-4">
            <h3 className="font-bold text-lg font-heading">Upcoming Payment Schedule</h3>

            {paymentsQueue.length === 0 ? (
              <EmptyState
                icon={<CheckCircle2 className="w-8 h-8" />}
                title="No pending settlement payments"
                description="Adopt a settlement plan from the Settle Up tab to queue priority transfers."
              />
            ) : (
              <div className="space-y-3">
                {paymentsQueue.map((txn, idx) => (
                  <Card key={txn.id || idx} hoverEffect={false} className="flex items-center justify-between p-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-xs">
                        #{txn.priority}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-900 dark:text-slate-100">
                          {memberNameMap[txn.from_member] || txn.from_member} → {memberNameMap[txn.to_member] || txn.to_member}
                        </p>
                        <p className="text-xs text-slate-400">Due Date: {txn.due_date || 'Next 7 days'}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <AmountText amountPaise={txn.amount_paise} currency={group?.currency} size="md" type="neutral" />
                      {txn.status === 'paid' ? (
                        <Badge variant="success">Paid</Badge>
                      ) : (
                        <Button size="sm" onClick={() => handlePayTransaction(txn.id!)}>
                          <Check className="w-4 h-4" />
                          <span>Mark as Paid</span>
                        </Button>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 6: INSIGHTS */}
        {activeTab === 'insights' && insights && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card hoverEffect={false} className="space-y-4">
              <h4 className="font-bold text-base font-heading">Top Spenders</h4>
              <div className="space-y-3">
                {insights.top_spenders.map((s, idx) => (
                  <div key={s.member_id} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold">
                      <span>#{idx + 1} {s.member_name}</span>
                      <AmountText amountPaise={s.total_spent_paise} currency={group?.currency} size="sm" type="neutral" />
                    </div>
                    <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${Math.min(100, (s.total_spent_paise / (insights.top_spenders[0]?.total_spent_paise || 1)) * 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card hoverEffect={false} className="space-y-4">
              <h4 className="font-bold text-base font-heading">Top Expenses</h4>
              <div className="space-y-2">
                {insights.top_expenses.map((e) => (
                  <div key={e.id} className="flex items-center justify-between text-xs p-2.5 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                    <div>
                      <p className="font-bold text-slate-900 dark:text-slate-100">{e.description}</p>
                      <p className="text-[10px] text-slate-400">Paid by {e.paid_by_name}</p>
                    </div>
                    <AmountText amountPaise={e.amount_paise} currency={group?.currency} size="sm" type="neutral" />
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* TAB 7: FAIR ITEM SPLIT TOOL */}
        {activeTab === 'allocate' && (
          <div className="space-y-6">
            <Card hoverEffect={false} className="space-y-4">
              <h4 className="font-bold text-lg font-heading">Fair Item Split Tool</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Split a collection of items or bills between two people so both pay virtually identical totals.
              </p>

              <Button onClick={handleAllocatePartition}>
                <Sparkles className="w-4 h-4" />
                <span>Split Items Fairly</span>
              </Button>

              {allocationResult && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                  <div className="p-4 bg-indigo-50 dark:bg-indigo-950/40 rounded-2xl space-y-2">
                    <h5 className="font-bold text-sm text-indigo-900 dark:text-indigo-200">Person 1 Assignment</h5>
                    {allocationResult.group_1.map((it: any, idx: number) => (
                      <div key={idx} className="flex justify-between text-xs">
                        <span>{it.description}</span>
                        <AmountText amountPaise={it.amount_paise} currency={group?.currency} size="sm" type="neutral" />
                      </div>
                    ))}
                    <div className="pt-2 border-t font-bold text-xs flex justify-between">
                      <span>Total</span>
                      <AmountText amountPaise={allocationResult.group_1_total} currency={group?.currency} size="sm" type="neutral" />
                    </div>
                  </div>

                  <div className="p-4 bg-emerald-50 dark:bg-emerald-950/40 rounded-2xl space-y-2">
                    <h5 className="font-bold text-sm text-emerald-900 dark:text-emerald-200">Person 2 Assignment</h5>
                    {allocationResult.group_2.map((it: any, idx: number) => (
                      <div key={idx} className="flex justify-between text-xs">
                        <span>{it.description}</span>
                        <AmountText amountPaise={it.amount_paise} currency={group?.currency} size="sm" type="neutral" />
                      </div>
                    ))}
                    <div className="pt-2 border-t font-bold text-xs flex justify-between">
                      <span>Total</span>
                      <AmountText amountPaise={allocationResult.group_2_total} currency={group?.currency} size="sm" type="neutral" />
                    </div>
                  </div>
                </div>
              )}
            </Card>
          </div>
        )}
      </div>

      {/* Modal: Add Member */}
      <Modal isOpen={isMemberModalOpen} onClose={() => setIsMemberModalOpen(false)} title="Add Group Member">
        <form onSubmit={handleAddMember} className="space-y-4">
          <Input label="Member Name" placeholder="e.g. Asha Sharma" value={newMemberName} onChange={(e) => setNewMemberName(e.target.value)} required />
          <div className="flex justify-end space-x-3 pt-2">
            <Button type="button" variant="ghost" onClick={() => setIsMemberModalOpen(false)}>Cancel</Button>
            <Button type="submit">Add Member</Button>
          </div>
        </form>
      </Modal>

      {/* Modal: Add Expense */}
      <Modal isOpen={isExpenseModalOpen} onClose={() => setIsExpenseModalOpen(false)} title="Add Group Expense" maxWidth="lg">
        <form onSubmit={handleAddExpense} className="space-y-4">
          <div className="relative">
            <Input label="Description" placeholder="e.g. Beach Shack Dinner" value={desc} onChange={(e) => setDesc(e.target.value)} required />
            {suggestions.length > 0 && (
              <div className="absolute z-20 top-full left-0 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg mt-1 overflow-hidden">
                {suggestions.map((s, i) => (
                  <button key={i} type="button" onClick={() => { setDesc(s); setSuggestions([]); }} className="block w-full text-left px-3 py-2 text-xs hover:bg-slate-100 dark:hover:bg-slate-700">
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input label="Amount (₹)" type="number" step="0.01" placeholder="1200.00" value={amountRupees} onChange={(e) => setAmountRupees(e.target.value)} required />
            <Select label="Category" value={category} onChange={(e) => setCategory(e.target.value)} options={[
              { value: 'food', label: 'Food' },
              { value: 'travel', label: 'Travel' },
              { value: 'rent', label: 'Rent' },
              { value: 'utilities', label: 'Utilities' },
              { value: 'entertainment', label: 'Entertainment' },
              { value: 'general', label: 'General' },
            ]} />
          </div>

          <Select label="Paid By" value={paidBy} onChange={(e) => setPaidBy(e.target.value)} options={members.map((m) => ({ value: m.id, label: m.name }))} />

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Split Mode</label>
            <div className="grid grid-cols-4 gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
              {(['equal', 'exact', 'percentage', 'shares'] as SplitType[]).map((mode) => (
                <button key={mode} type="button" onClick={() => setSplitType(mode)} className={`py-1.5 text-xs font-bold rounded-lg uppercase transition-colors ${splitType === mode ? 'bg-indigo-600 text-white shadow' : 'text-slate-600 dark:text-slate-400'}`}>
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button type="button" variant="ghost" onClick={() => setIsExpenseModalOpen(false)}>Cancel</Button>
            <Button type="submit" isLoading={submittingExpense}>Add Expense</Button>
          </div>
        </form>
      </Modal>
    </AppShell>
  );
};
