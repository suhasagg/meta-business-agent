from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from langgraph.types import Command
from meta_business.core.bootstrap import build_runtime
from meta_business.core.graph import build
app=FastAPI(title="Meta Business Agent Inspired Platform")
graph=build(build_runtime())
class Req(BaseModel):tenant_id:str;customer_id:str;channel:str="whatsapp";message:str;thread_id:str|None=None;locale:str="en"
@app.get("/health")
async def health():return {"ok":True}
@app.post("/v1/conversations")
async def run(x:Req):
 t=x.thread_id or str(uuid4());s={**x.model_dump(),"thread_id":t,"request_id":str(uuid4())}
 r=await graph.ainvoke(s,config={"configurable":{"thread_id":t}});return {"thread_id":t,"result":r}
@app.post("/v1/conversations/{thread_id}/resume")
async def resume(thread_id:str,approve:bool):
 r=await graph.ainvoke(Command(resume={"approve":approve}),config={"configurable":{"thread_id":thread_id}});return {"thread_id":thread_id,"result":r}
