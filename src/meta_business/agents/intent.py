from .base import Agent
class IntentAgent(Agent):
 async def run(self,s):
  m=s["message"].lower();intent="support"
  for k in ["appointment","order","product","lead","sales"]:
   if k in m:intent=k
  return {"last_result":{"ok":True,"intent":intent}}
