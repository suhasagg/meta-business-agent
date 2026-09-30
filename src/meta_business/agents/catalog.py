from .base import Agent
from meta_business.core.models import Action,Risk
class CatalogAgent(Agent):
 async def run(self,s):
  r=await self.g.call(Action(tool="commerce.products",args={"query":s["message"],"limit":10},risk=Risk.READ));return {"last_result":r,"evidence":s.get("evidence",[])+([{"source":"catalog","content":str(r.get("output"))}] if r["ok"] else [])}
