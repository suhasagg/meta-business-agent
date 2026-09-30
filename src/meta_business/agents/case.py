from .base import Agent
from meta_business.core.models import Action,Risk
class CaseAgent(Agent):
 async def run(self,s):
  a={"subject":"Business Agent escalation","body":s["message"],"priority":"normal"};r=await self.g.call(Action(tool="support.ticket",args=a,risk=Risk.WRITE,idempotency_key=f"case:{s['thread_id']}"));return {"case":r.get("output",a),"last_result":r}
