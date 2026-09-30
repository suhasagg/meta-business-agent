from mcp.server.fastmcp import FastMCP
mcp=FastMCP("business-agent-tools")
@mcp.tool()
def health()->dict:return {"ok":True}
@mcp.tool()
def capabilities()->dict:return {"domains":["customer","knowledge","catalog","lead","appointment","order","support"]}
if __name__=="__main__":mcp.run()
