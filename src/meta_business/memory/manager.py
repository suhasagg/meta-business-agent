from meta_business.core.models import MemoryRecord
class MemoryManager:
 def __init__(self,s):self.s=s
 async def hydrate(self,st):
  c=dict(tenant_id=st["tenant_id"],q=st["message"],customer_id=st.get("customer_id"),thread_id=st["thread_id"])
  return {x:await self.s.search(**c,layers=[x],k=8) for x in ["working","episodic","semantic","procedural","preference","artifact","organization"]}
 async def remember(self,st,layer,key,text,thread=False,**kw):
  r=MemoryRecord(layer=layer,tenant_id=st["tenant_id"],customer_id=kw.get("customer_id",st.get("customer_id")),thread_id=st["thread_id"] if thread else None,key=key,text=text,confidence=kw.get("confidence",1),provenance=kw.get("provenance",{}),tags=kw.get("tags",[]));return await self.s.put(r)
