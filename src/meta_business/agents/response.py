from .base import Agent
from meta_business.security.guard import Guard
class ResponseAgent(Agent):
 async def run(self,s):
  lr=s.get("last_result",{});txt="I can help with that."
  if s.get("handoff",{}).get("required"):txt="I’ve prepared the conversation context for a human team member to continue."
  elif s.get("order"):txt="I found your order information and can help with the next question."
  elif s.get("appointment"):txt="Your appointment request has been prepared."
  elif s.get("lead"):txt="Thanks — I’ve captured the details for follow-up."
  elif s.get("evidence"):txt="Based on the business information available, "+str(s["evidence"][-1].get("content",""))[:1200]
  return {"final_answer":Guard().redact(txt),"last_result":{"ok":True}}
