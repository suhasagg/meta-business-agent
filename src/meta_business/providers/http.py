import httpx,asyncio,random
class HTTP:
 def __init__(self):self.c=httpx.AsyncClient(timeout=20)
 async def request(self,m,u,**kw):
  for i in range(4):
   try:
    r=await self.c.request(m,u,**kw)
    if r.status_code in (429,500,502,503,504):raise httpx.HTTPStatusError("retry",request=r.request,response=r)
    r.raise_for_status();return r.json() if r.content else {}
   except (httpx.TimeoutException,httpx.NetworkError,httpx.HTTPStatusError):
    if i==3:raise
    await asyncio.sleep(.2*(2**i)+random.random()*.2)
