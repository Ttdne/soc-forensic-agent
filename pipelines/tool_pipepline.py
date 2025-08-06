from agents.tool_agent import ToolAgent

def run_tool_pipeline(tool_name: str, tool_input: str):
    tool_agent = ToolAgent(tool_name)
    result = tool_agent.run(tool_input)
    return result