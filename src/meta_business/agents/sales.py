from .base import Agent
class SalesAgent(Agent):
 async def run(self,s):
  return {"last_result":{"ok":True,"sales_intent":{"customer":s.get("customer",{}),"message":s["message"],"catalog_evidence":s.get("evidence",[])}}}
