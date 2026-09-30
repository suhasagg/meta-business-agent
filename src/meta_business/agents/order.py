from .base import Agent
from meta_business.core.models import Action,Risk
import re
class OrderAgent(Agent):
 async def run(self,s):
  m=re.search(r"order\s*#?([A-Za-z0-9_-]+)",s["message"],re.I)
  if not m:return {"last_result":{"ok":False,"error":"order id required"}}
  r=await self.g.call(Action(tool="commerce.order",args={"order_id":m.group(1)},risk=Risk.READ));return {"order":r.get("output",{}),"last_result":r}
