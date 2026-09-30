import hashlib,json,time
class Audit:
 def __init__(self):self.prev="0"*64;self.rows=[]
 def append(self,e):
  r={"ts":time.time(),"prev":self.prev,**e};r["hash"]=hashlib.sha256(json.dumps(r,sort_keys=True,default=str).encode()).hexdigest();self.prev=r["hash"];self.rows.append(r);return r
