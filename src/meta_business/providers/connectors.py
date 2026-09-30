class Connectors:
 def __init__(self,http,meta_base="",meta_version="v24.0",meta_token="",phone_id="",shopify="",shopify_token="",zendesk="",zendesk_token="",crm="",crm_token=""):
  self.h=http;self.mb=meta_base.rstrip("/");self.mv=meta_version;self.mt=meta_token;self.phone=phone_id;self.shop=shopify.rstrip("/");self.st=shopify_token;self.z=zendesk.rstrip("/");self.zt=zendesk_token;self.crm=crm.rstrip("/");self.ct=crm_token
 async def whatsapp_send(self,a):return await self.h.request("POST",f"{self.mb}/{self.mv}/{self.phone}/messages",headers={"Authorization":f"Bearer {self.mt}"},json={"messaging_product":"whatsapp","to":a["to"],"type":"text","text":{"body":a["text"]}})
 async def products(self,a):
  d=await self.h.request("GET",f"{self.shop}/admin/api/2026-07/products.json",headers={"X-Shopify-Access-Token":self.st},params={"limit":min(a.get("limit",20),100)});q=a.get("query","").lower();xs=d.get("products",[]);return [x for x in xs if not q or q in (x.get("title","")+" "+x.get("body_html","")).lower()][:a.get("limit",10)]
 async def order(self,a):return await self.h.request("GET",f"{self.shop}/admin/api/2026-07/orders/{a['order_id']}.json",headers={"X-Shopify-Access-Token":self.st})
 async def customer(self,a):return await self.h.request("GET",f"{self.crm}/customers/{a['customer_id']}",headers={"Authorization":f"Bearer {self.ct}"})
 async def lead(self,a):return await self.h.request("POST",f"{self.crm}/leads",headers={"Authorization":f"Bearer {self.ct}"},json=a)
 async def appointment(self,a):return await self.h.request("POST",f"{self.crm}/appointments",headers={"Authorization":f"Bearer {self.ct}"},json=a)
 async def ticket(self,a):return await self.h.request("POST",f"{self.z}/api/v2/tickets.json",headers={"Authorization":f"Bearer {self.zt}"},json={"ticket":{"subject":a["subject"],"comment":{"body":a["body"]},"priority":a.get("priority","normal")}})
