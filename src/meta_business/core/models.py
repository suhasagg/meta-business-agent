from enum import Enum
from typing import Any,Literal,TypedDict
from pydantic import BaseModel,Field
from uuid import uuid4
class Risk(str,Enum): READ="read";WRITE="write";COMMUNICATE="communicate";FINANCIAL="financial";PRIVILEGED="privileged"
Agent=Literal["intent","customer360","knowledge","catalog","recommendation","lead","appointment","sales","order","support","case","handoff","compliance","memory","critic","verifier","response"]
class Step(BaseModel):
 id:str=Field(default_factory=lambda:str(uuid4()));objective:str;agent:Agent;depends_on:list[str]=Field(default_factory=list);status:Literal["pending","running","done","failed","blocked"]="pending";attempts:int=0;result:Any=None
class Plan(BaseModel): goal:str;steps:list[Step];revision:int=0
class Action(BaseModel):
 id:str=Field(default_factory=lambda:str(uuid4()));tool:str;args:dict[str,Any]=Field(default_factory=dict);risk:Risk=Risk.READ;reason:str="";idempotency_key:str|None=None
class MemoryRecord(BaseModel):
 id:str=Field(default_factory=lambda:str(uuid4()));layer:Literal["working","episodic","semantic","procedural","preference","artifact","organization"];tenant_id:str;customer_id:str|None=None;thread_id:str|None=None;key:str;text:str;confidence:float=1.0;provenance:dict[str,Any]=Field(default_factory=dict);tags:list[str]=Field(default_factory=list)
class State(TypedDict,total=False):
 request_id:str;thread_id:str;tenant_id:str;customer_id:str;channel:str;message:str;locale:str;plan:dict;active_step:dict;customer:dict;memory_context:dict;evidence:list[dict];cart:list[dict];lead:dict;appointment:dict;order:dict;case:dict;handoff:dict;iteration:int;stall:int;max_iterations:int;last_result:dict;verification:dict;final_answer:str
