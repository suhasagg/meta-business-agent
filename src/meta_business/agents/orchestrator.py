from meta_business.core.models import Plan,Step
class Orchestrator:
 def plan(self,s):
  m=s["message"].lower();steps=[Step(objective="load customer context",agent="customer360"),Step(objective="retrieve business knowledge",agent="knowledge")]
  if any(x in m for x in ["product","recommend","buy","price"]):steps += [Step(objective="search catalog",agent="catalog"),Step(objective="recommend relevant products",agent="recommendation")]
  if "appointment" in m or "book" in m:steps += [Step(objective="book requested appointment",agent="appointment")]
  if "lead" in m or "quote" in m:steps += [Step(objective="qualify and capture lead",agent="lead")]
  if "order" in m:steps += [Step(objective="retrieve order",agent="order")]
  if any(x in m for x in ["human","agent","representative","complaint"]):steps += [Step(objective="create support case",agent="case"),Step(objective="handoff to human",agent="handoff")]
  steps += [Step(objective="check compliance",agent="compliance"),Step(objective="compose customer response",agent="response")]
  for i in range(1,len(steps)):steps[i].depends_on=[steps[i-1].id]
  return Plan(goal=s["message"],steps=steps).model_dump()
 def dispatch(self,s):
  for x in s["plan"]["steps"]:
   if x["status"]=="pending" and all(next(y for y in s["plan"]["steps"] if y["id"]==d)["status"]=="done" for d in x["depends_on"]):return x
  return None
 def review(self,s):
  p=s["plan"];a=s["active_step"]
  for x in p["steps"]:
   if x["id"]==a["id"]:x["attempts"]+=1;x["status"]="done" if s.get("last_result",{}).get("ok") else "failed";x["result"]=s.get("last_result")
  return p
