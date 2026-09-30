from .base import Agent
from meta_business.core.models import Action,Risk
class Customer360Agent(Agent):
 async def run(self,s):
  r=await self.g.call(Action(tool="crm.customer",args={"customer_id":s["customer_id"]},risk=Risk.READ));return {"customer":r.get("output",{}),"last_result":r}
