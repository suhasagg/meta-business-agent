import re
class Guard:
 inj=re.compile(r"ignore (all|previous)|system prompt|developer message|reveal.*secret|bypass.*policy",re.I)
 def inspect(self,text):return {"suspicious":bool(self.inj.search(text or ""))}
 def redact(self,text):return re.sub(r"\b\d{12,19}\b","[REDACTED]",text or "")
