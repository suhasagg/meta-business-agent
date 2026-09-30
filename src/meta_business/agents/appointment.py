from .base import Agent
from meta_business.core.models import Action,Risk
class AppointmentAgent(Agent):
 async def run(self,s):
  a={"customer_id":s["customer_id"],"request":s["message"],"status":"requested"};r=await self.g.call(Action(tool="crm.appointment",args=a,risk=Risk.WRITE,idempotency_key=f"appt:{s['thread_id']}"));return {"appointment":r.get("output",a),"last_result":r}
