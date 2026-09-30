from .base import Agent
class RecommendationAgent(Agent):
 async def run(self,s):
  ev=s.get("evidence",[]);return {"last_result":{"ok":True,"recommendations":ev[-3:]}}
