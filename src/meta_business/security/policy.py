from dataclasses import dataclass
from meta_business.core.models import Risk
@dataclass(frozen=True)
class Decision: allow:bool;approval:bool;reason:str
class Policy:
 deny={"payment.capture","refund.execute","credential.read","admin.impersonate","raw_sql"}
 def decide(self,a,roles=frozenset()):
  if a.tool in self.deny:return Decision(False,False,"prohibited capability")
  if a.risk==Risk.FINANCIAL and "financial_operator" not in roles:return Decision(False,False,"financial role required")
  if a.risk==Risk.PRIVILEGED and "admin" not in roles:return Decision(False,False,"admin role required")
  x=a.risk in {Risk.WRITE,Risk.COMMUNICATE,Risk.FINANCIAL,Risk.PRIVILEGED};return Decision(True,x,"approval required" if x else "allowed")
