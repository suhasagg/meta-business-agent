from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from meta_business.core.models import State
from meta_business.agents.orchestrator import Orchestrator
def build(agents,checkpointer=None):
 o=Orchestrator();g=StateGraph(State)
 async def hydrate(s):
  x=await agents["memory"].run(s);return {**x,"iteration":0,"stall":0,"max_iterations":20,"evidence":s.get("evidence",[])}
 async def plan(s):return {"plan":o.plan(s)}
 async def dispatch(s):
  x=o.dispatch(s);return {"active_step":x or {}}
 async def review(s):return {"plan":o.review(s),"iteration":s.get("iteration",0)+1}
 def route(s):
  if s.get("iteration",0)>=s.get("max_iterations",20):return "verify"
  if any(x["status"]=="failed" for x in s["plan"]["steps"]):return "verify"
  return "verify" if not o.dispatch(s) else "dispatch"
 async def verify(s):return await agents["verifier"].run(s)
 g.add_node("hydrate",hydrate);g.add_node("plan",plan);g.add_node("dispatch",dispatch);g.add_node("review",review);g.add_node("verify",verify)
 for n,a in agents.items():
  if n in ("memory","verifier"):continue
  g.add_node(n,a.run);g.add_edge(n,"review")
 def agent_route(s):return s["active_step"]["agent"]
 g.add_edge(START,"hydrate");g.add_edge("hydrate","plan");g.add_edge("plan","dispatch")
 g.add_conditional_edges("dispatch",agent_route,{n:n for n in agents if n not in ("memory","verifier")})
 g.add_conditional_edges("review",route,{"dispatch":"dispatch","verify":"verify"});g.add_edge("verify",END)
 return g.compile(checkpointer=checkpointer or InMemorySaver())
