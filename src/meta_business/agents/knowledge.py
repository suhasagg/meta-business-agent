from .base import Agent
class KnowledgeAgent(Agent):
 async def run(self,s):
  x=await self.knowledge.search(s["tenant_id"],s["message"],5);return {"evidence":s.get("evidence",[])+x,"last_result":{"ok":bool(x),"knowledge":x}}
