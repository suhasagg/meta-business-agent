from .base import Agent
class HandoffAgent(Agent):
 async def run(self,s):
  return {"handoff":{"required":True,"reason":"complex or requested human support","thread_id":s["thread_id"],"context":{"customer":s.get("customer"),"message":s["message"],"case":s.get("case")}},"last_result":{"ok":True}}
