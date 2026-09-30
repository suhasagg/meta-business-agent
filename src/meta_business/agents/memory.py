from .base import Agent
class MemoryAgent(Agent):
 async def run(self,s):
  x=await self.memory.hydrate(s);return {"memory_context":x,"last_result":{"ok":True,"layers":list(x)}}
