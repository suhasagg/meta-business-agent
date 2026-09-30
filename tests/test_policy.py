from meta_business.security.policy import Policy
from meta_business.core.models import Action,Risk
def test_payment_denied():assert not Policy().decide(Action(tool="payment.capture",risk=Risk.FINANCIAL)).allow
def test_read_autonomous():assert not Policy().decide(Action(tool="commerce.products",risk=Risk.READ)).approval
def test_write_approval():assert Policy().decide(Action(tool="crm.lead",risk=Risk.WRITE)).approval
