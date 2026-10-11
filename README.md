# Smart Bill-Splitting & Debt Settlement System (DAA Assignment)

A full-stack web application designed for group expense splitting and debt settlement using advanced algorithms and data structures.

---

## Core Algorithm Strategies & Implementations

| Strategy | Where it is used | Complexity | Pure Module File |
| :--- | :--- | :--- | :--- |
| **Greedy + Priority Queue (Max-Heap)** | Debt settlement (fast, at most $n-1$ transactions) | $O(n \log n)$ | [`backend/app/algorithms/greedy.py`](file:///c:/Users/HP/OneDrive/Desktop/CN%20assignment/backend/app/algorithms/greedy.py) |
| **Graphs (DFS 3-Coloring)** | Debt network, cycle cancellation before/after visualization | $O(V \cdot (V+E))$ | [`backend/app/algorithms/graph.py`](file:///c:/Users/HP/OneDrive/Desktop/CN%20assignment/backend/app/algorithms/graph.py) |
| **Dynamic Programming (Bitmask)** | Optimal minimum-transaction debt settlement | $O(m \cdot 2^m)$ | [`backend/app/algorithms/dp_optimal.py`](file:///c:/Users/HP/OneDrive/Desktop/CN%20assignment/backend/app/algorithms/dp_optimal.py) |
| **Dynamic Programming (Subset-Sum)** | Balanced item allocation between two payers | $O(n \cdot \text{sum}/\text{gcd})$ | [`backend/app/algorithms/partition.py`](file:///c:/Users/HP/OneDrive/Desktop/CN%20assignment/backend/app/algorithms/partition.py) |
| **Priority Queue (Min-Heap)** | Payment scheduling ("who pays next") & top-$k$ spenders | $O(t \log t)$ | [`backend/app/algorithms/scheduler.py`](file:///c:/Users/HP/OneDrive/Desktop/CN%20assignment/backend/app/algorithms/scheduler.py) |
| **Hashing + Trie** | Expense search, filtering, and autocomplete | $O(L + K)$ | [`backend/app/algorithms/search.py`](file:///c:/Users/HP/OneDrive/Desktop/CN%20assignment/backend/app/algorithms/search.py) |
| **Largest Remainder Method** | Exact unequal / percentage / share-based splits | $O(k \log k)$ | [`backend/app/algorithms/splits.py`](file:///c:/Users/HP/OneDrive/Desktop/CN%20assignment/backend/app/algorithms/splits.py) |

---

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Framer Motion + Recharts + React Flow + `@supabase/supabase-js`
- **Backend**: FastAPI + Pydantic v2 + Python 3.11
- **Database & Auth**: Supabase Postgres + Row-Level Security (RLS) + JWT Auth

---

## Project Structure

```
CN assignment/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── db.py
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── algorithms/
│   │       ├── heap.py
│   │       ├── splits.py
│   │       ├── balances.py
│   │       ├── graph.py
│   │       ├── greedy.py
│   │       ├── dp_optimal.py
│   │       ├── partition.py
│   │       ├── scheduler.py
│   │       └── search.py
│   ├── tests/
│   │   ├── test_phase1_health.py
│   │   ├── test_algorithms.py
│   │   └── test_phase3_integration.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── lib/
│   │   ├── pages/
│   │   ├── styles/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── supabase/
│   ├── migrations/0001_init.sql
│   └── seed.sql
├── docs/
│   └── ALGORITHMS.md
└── README.md
```

---

## Environment Setup

### 1. Supabase Database Migration & Seed
Execute SQL scripts in Supabase SQL Editor:
- `supabase/migrations/0001_init.sql`
- `supabase/seed.sql`

### 2. Backend Setup & Run
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup & Run
```bash
cd frontend
npm install
npm run dev
```

### 4. Running Backend Tests
```bash
cd backend
python -m pytest tests/test_algorithms.py
```

---

## Documentation & Viva Reference

See [`docs/ALGORITHMS.md`](file:///c:/Users/HP/OneDrive/Desktop/CN%20assignment/docs/ALGORITHMS.md) for full algorithm pseudocode, time & space complexities, correctness proofs, and the mandatory Greedy sub-optimality counterexample.
