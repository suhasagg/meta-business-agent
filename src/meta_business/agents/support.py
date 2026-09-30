from .base import Agent
class SupportAgent(Agent):
 async def run(self,s):
  return {"last_result":{"ok":True,"support_context":{"customer":s.get("customer"),"evidence":s.get("evidence",[]),"message":s["message"]}}}
