from .base import Agent
from meta_business.security.guard import Guard
class ComplianceAgent(Agent):
 async def run(self,s):
  x=Guard().inspect(s["message"]);return {"last_result":{"ok":not x["suspicious"],"compliance":x}}
