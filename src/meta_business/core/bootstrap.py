from meta_business.tools.gateway import Gateway
from meta_business.providers.http import HTTP
from meta_business.providers.connectors import Connectors
from meta_business.memory.store import MemoryStore
from meta_business.memory.manager import MemoryManager
from meta_business.rag.store import Knowledge
from meta_business.agents.memory import MemoryAgent
from meta_business.agents.verifier import VerifierAgent
def build_runtime(cfg=None):
 from meta_business.agents.customer360 import Customer360Agent
 from meta_business.agents.knowledge import KnowledgeAgent
 from meta_business.agents.catalog import CatalogAgent
 from meta_business.agents.recommendation import RecommendationAgent
 from meta_business.agents.lead import LeadAgent
 from meta_business.agents.appointment import AppointmentAgent
 from meta_business.agents.sales import SalesAgent
 from meta_business.agents.order import OrderAgent
 from meta_business.agents.support import SupportAgent
 from meta_business.agents.case import CaseAgent
 from meta_business.agents.handoff import HandoffAgent
 from meta_business.agents.compliance import ComplianceAgent
 from meta_business.agents.critic import CriticAgent
 from meta_business.agents.response import ResponseAgent
 g=Gateway();mem=MemoryManager(MemoryStore());kb=Knowledge([]);http=HTTP()
 c=Connectors(http,getattr(cfg,"meta_graph_base",""),getattr(cfg,"meta_graph_version","v24.0"),getattr(cfg,"meta_access_token",""),getattr(cfg,"whatsapp_phone_number_id",""),getattr(cfg,"shopify_base_url",""),getattr(cfg,"shopify_access_token",""),getattr(cfg,"zendesk_base_url",""),getattr(cfg,"zendesk_token",""),getattr(cfg,"crm_base_url",""),getattr(cfg,"crm_token",""))
 for n,h in {"channel.whatsapp.send":c.whatsapp_send,"commerce.products":c.products,"commerce.order":c.order,"crm.customer":c.customer,"crm.lead":c.lead,"crm.appointment":c.appointment,"support.ticket":c.ticket}.items():g.register(n,h)
 kw=dict(gateway=g,memory=mem,knowledge=kb)
 return {"memory":MemoryAgent(**kw),"customer360":Customer360Agent(**kw),"knowledge":KnowledgeAgent(**kw),"catalog":CatalogAgent(**kw),"recommendation":RecommendationAgent(**kw),"lead":LeadAgent(**kw),"appointment":AppointmentAgent(**kw),"sales":SalesAgent(**kw),"order":OrderAgent(**kw),"support":SupportAgent(**kw),"case":CaseAgent(**kw),"handoff":HandoffAgent(**kw),"compliance":ComplianceAgent(**kw),"critic":CriticAgent(**kw),"response":ResponseAgent(**kw),"verifier":VerifierAgent(**kw)}
