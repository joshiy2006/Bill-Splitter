import React from 'react';
import { BookOpen, ShieldCheck, Zap, Layers, RefreshCw, Cpu, CheckCircle } from 'lucide-react';
import { AppShell } from '../components/layout/AppShell';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';

export const HowItWorks: React.FC = () => {
  const ALGORITHMS = [
    {
      name: 'Greedy Debt Settlement',
      module: 'app/algorithms/greedy.py',
      strategy: 'Two Max-Heaps (Creditors by credit amount, Debtors by absolute debt amount). Pop top of each, settle min(credit, debt), push back remainder.',
      timeComplexity: 'O(n log n)',
      spaceComplexity: 'O(n)',
      correctness: 'Resolves all net balances to zero in at most n - 1 transactions.'
    },
    {
      name: 'Optimal Bitmask Dynamic Programming',
      module: 'app/algorithms/dp_optimal.py',
      strategy: 'Bitmask DP over subset states to find the maximum number of zero-sum partitions. Cuts ordering into zero-sum groups and runs greedy on each group.',
      timeComplexity: 'O(m · 2ᵐ)',
      spaceComplexity: 'O(2ᵐ)',
      correctness: 'Proved by graph theory that minimum transactions = m - max_zero_sum_subsets.'
    },
    {
      name: 'Directed Debt Graph & Cycle Cancellation',
      module: 'app/algorithms/graph.py',
      strategy: 'DFS with 3-color code (White, Grey, Black) and parent tracking to find directed cycles, then subtracts cycle bottleneck edge weight.',
      timeComplexity: 'O(V · (V + E))',
      spaceComplexity: 'O(V + E)',
      correctness: 'Subtracting edge weight along a directed cycle preserves net balances for all nodes.'
    },
    {
      name: 'Largest Remainder Split Resolution',
      module: 'app/algorithms/splits.py',
      strategy: 'Hare-Niemeyer Largest Remainder Method for percentage/shares splits + integer division with deterministic remainder distribution for equal splits.',
      timeComplexity: 'O(k log k)',
      spaceComplexity: 'O(k)',
      correctness: 'Guarantees whole integer paise summing strictly to total amount, breaking remainder ties deterministically.'
    },
    {
      name: 'Balanced Item Allocation / Partition DP',
      module: 'app/algorithms/partition.py',
      strategy: 'Subset-sum DP over integer paise using Python arbitrary-precision big-int bitset operations (reachable |= reachable << w) with GCD reduction.',
      timeComplexity: 'O(n · (sum / gcd))',
      spaceComplexity: 'O(n · (sum / gcd))',
      correctness: 'Reconstructs exact subset of items closest to total / 2.'
    },
    {
      name: 'Priority Queue Smart Payment Scheduler',
      module: 'app/algorithms/scheduler.py',
      strategy: 'MinHeap priority queue ordering pending settlement transactions by due_date ascending, then amount_paise descending.',
      timeComplexity: 'O(t log t)',
      spaceComplexity: 'O(t)',
      correctness: 'Guarantees highest urgency payments receive top priorities (1, 2, 3, ...).'
    },
    {
      name: 'Trie Prefix Search & Inverted Expense Index',
      module: 'app/algorithms/search.py',
      strategy: 'Trie prefix tree for word autocomplete + hash-map category/payer inverted index intersecting candidate sets starting with the smallest set.',
      timeComplexity: 'O(L + K)',
      spaceComplexity: 'O(W · L)',
      correctness: 'Intersects candidate sets starting with smallest set to minimize comparison steps.'
    },
  ];

  return (
    <AppShell>
      <div className="space-y-8 max-w-4xl mx-auto">
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-indigo-600 text-white flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/30">
            <BookOpen className="w-7 h-7" />
          </div>
          <h1 className="text-3xl font-extrabold font-heading text-slate-900 dark:text-slate-100">
            How It Works — Algorithm Viva Guide
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Comprehensive reference of algorithm design strategies, complexities, and correctness proofs
          </p>
        </div>

        <div className="space-y-4">
          {ALGORITHMS.map((alg, idx) => (
            <Card key={idx} hoverEffect={false} className="p-6 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                <div>
                  <h3 className="text-lg font-bold font-heading text-slate-900 dark:text-slate-100">
                    {alg.name}
                  </h3>
                  <code className="text-xs text-indigo-600 dark:text-indigo-400 font-mono">{alg.module}</code>
                </div>
                <div className="flex space-x-2">
                  <Badge variant="info">{alg.timeComplexity}</Badge>
                  <Badge variant="neutral">Space {alg.spaceComplexity}</Badge>
                </div>
              </div>

              <div className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
                <p><strong>Strategy:</strong> {alg.strategy}</p>
                <p><strong>Correctness Argument:</strong> {alg.correctness}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
};
