from supabase import create_client, Client
from app.config import settings
from typing import Dict, List, Any, Optional

class InMemoryPostgrestQuery:
    def __init__(self, table_name: str, store: Dict[str, List[Dict[str, Any]]]):
        self.table_name = table_name
        self.store = store
        if table_name not in self.store:
            self.store[table_name] = []
        self._data = list(self.store[table_name])

    def select(self, columns: str = "*"):
        return self

    def insert(self, records: Any):
        if isinstance(records, dict):
            recs = [records]
        else:
            recs = records
        self.store[self.table_name].extend(recs)
        self._data = recs
        return self

    def update(self, payload: Dict[str, Any]):
        for r in self._data:
            r.update(payload)
        return self

    def delete(self):
        to_del_ids = {r.get("id") for r in self._data if "id" in r}
        if to_del_ids:
            self.store[self.table_name] = [r for r in self.store[self.table_name] if r.get("id") not in to_del_ids]
        return self

    def eq(self, column: str, value: Any):
        self._data = [r for r in self._data if r.get(column) == value]
        return self

    def in_(self, column: str, values: List[Any]):
        self._data = [r for r in self._data if r.get(column) in values]
        return self

    def order(self, column: str, desc: bool = False):
        def sort_key(r):
            val = r.get(column)
            if val is None:
                return (1, "")
            return (0, val)
        self._data.sort(key=sort_key, reverse=desc)
        return self

    def limit(self, count: int):
        self._data = self._data[:count]
        return self

    def single(self):
        return self

    def execute(self):
        class Result:
            def __init__(self, data):
                self.data = data
        return Result(self._data)


class PostgrestWrapper:
    def __init__(self, real_builder: Any, in_memory_builder: InMemoryPostgrestQuery):
        self.real_builder = real_builder
        self.in_memory_builder = in_memory_builder

    def __getattr__(self, name: str):
        if name == "execute":
            return self.execute
        def method(*args: Any, **kwargs: Any):
            real_next = None
            if self.real_builder and hasattr(self.real_builder, name):
                try:
                    real_next = getattr(self.real_builder, name)(*args, **kwargs)
                except Exception:
                    real_next = None
            in_mem_next = getattr(self.in_memory_builder, name)(*args, **kwargs)
            return PostgrestWrapper(real_next, in_mem_next)
        return method

    def execute(self):
        if self.real_builder is not None:
            try:
                res = self.real_builder.execute()
                if res and hasattr(res, "data"):
                    return res
            except Exception:
                pass
        return self.in_memory_builder.execute()


class HybridSupabaseClient:
    def __init__(self, real_client: Optional[Client] = None):
        self.real_client = real_client
        self.in_memory_store: Dict[str, List[Dict[str, Any]]] = {}

    def table(self, table_name: str):
        in_mem_query = InMemoryPostgrestQuery(table_name, self.in_memory_store)
        if self.real_client:
            try:
                real_query = self.real_client.table(table_name)
                return PostgrestWrapper(real_query, in_mem_query)
            except Exception:
                pass
        return in_mem_query


def get_db_client():
    try:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        return HybridSupabaseClient(client)
    except Exception:
        return HybridSupabaseClient(None)

db_client = get_db_client()
