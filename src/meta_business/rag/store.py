class Knowledge:
 def __init__(self,docs=None):self.docs=docs or []
 async def search(self,tenant,q,k=5):
  terms=set(q.lower().split());xs=[]
  for d in self.docs:
   if d.get("tenant_id")!=tenant:continue
   s=len(terms&set(d.get("text","").lower().split()))
   if s:xs.append((s,d))
  return [d for _,d in sorted(xs,key=lambda x:x[0],reverse=True)[:k]]
