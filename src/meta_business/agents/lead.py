from .base import Agent
from meta_business.core.models import Action,Risk
class LeadAgent(Agent):
 async def run(self,s):
  a={"customer_id":s["customer_id"],"source":s["channel"],"notes":s["message"],"status":"qualified"};r=await self.g.call(Action(tool="crm.lead",args=a,risk=Risk.WRITE,idempotency_key=f"lead:{s['thread_id']}"));return {"lead":r.get("output",a),"last_result":r}
