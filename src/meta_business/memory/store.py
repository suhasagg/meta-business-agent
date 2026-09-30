from meta_business.core.models import MemoryRecord
class MemoryStore:
 def __init__(self):self.rows=[]
 async def put(self,r:MemoryRecord):self.rows.append(r);return r.model_dump()
 async def search(self,tenant_id,q,layers=None,customer_id=None,thread_id=None,k=10):
  qs=set(q.lower().split());out=[]
  for r in self.rows:
   if r.tenant_id!=tenant_id or layers and r.layer not in layers:continue
   if r.customer_id not in (None,customer_id) or r.thread_id not in (None,thread_id):continue
   s=len(qs&set((r.key+" "+r.text).lower().split()))*r.confidence
   if s:out.append((s,r))
  return [r.model_dump() for _,r in sorted(out,key=lambda x:x[0],reverse=True)[:k]]
