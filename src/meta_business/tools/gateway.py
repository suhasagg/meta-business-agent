from langgraph.types import interrupt
from meta_business.security.policy import Policy
from meta_business.security.audit import Audit
class Gateway:
 def __init__(self,roles=None):self.h={};self.roles=set(roles or []);self.policy=Policy();self.audit=Audit();self.done={}
 def register(self,n,h):self.h[n]=h
 async def call(self,a):
  d=self.policy.decide(a,self.roles);self.audit.append({"action":a.model_dump(mode="json"),"decision":d.__dict__})
  if not d.allow:return {"ok":False,"error":d.reason}
  if d.approval:
   x=interrupt({"type":"approval","action":a.model_dump(mode="json")})
   if not (x is True or isinstance(x,dict) and x.get("approve")):return {"ok":False,"error":"approval denied"}
  if a.idempotency_key and a.idempotency_key in self.done:return self.done[a.idempotency_key]
  if a.tool not in self.h:return {"ok":False,"error":"capability unavailable"}
  try:r={"ok":True,"output":await self.h[a.tool](a.args)}
  except Exception as e:r={"ok":False,"error":type(e).__name__+":"+str(e)[:500]}
  if a.idempotency_key and r["ok"]:self.done[a.idempotency_key]=r
  return r
