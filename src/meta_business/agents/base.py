class Agent:
 def __init__(self,gateway=None,llm=None,memory=None,knowledge=None):self.g=gateway;self.llm=llm;self.memory=memory;self.knowledge=knowledge
 async def run(self,state):raise NotImplementedError
