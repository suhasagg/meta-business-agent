from .base import Agent
class CriticAgent(Agent):
 async def run(self,s):
  issues=[] 
  if not s.get("last_result",{}).get("ok",False):issues.append("previous step failed")
  return {"last_result":{"ok":not issues,"issues":issues}}
