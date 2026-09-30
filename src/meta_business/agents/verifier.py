from .base import Agent
class VerifierAgent(Agent):
 async def run(self,s):
  p=s.get("plan",{});bad=[x for x in p.get("steps",[]) if x.get("status")!="done"];v={"ok":not bad,"unfinished":[x.get("id") for x in bad]};return {"verification":v,"last_result":v}
