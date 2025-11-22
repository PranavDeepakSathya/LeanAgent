import langgraph 
import langgraph.prebuilt
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from prompts import lean_agent_prompt
from tools.misc_tools import * 
from tools.shell_tools import *

import asyncio
import vertexai

vertexai.init(
    project="gen-lang-client-0191345247",  # Your Google Cloud Project ID
    location="us-central1"          # Region (e.g., us-central1, europe-west4)
)



llm = init_chat_model(model='gemini-2.5-pro')

lean_agent = create_react_agent(prompt=lean_agent_prompt, tools = misc_tools + shell_tools, name = "lean_agent", model=llm)
file_path = "/home/blue-morphism/LeanAgent/ring.md"
result = lean_agent.invoke({"messages": f"read and analyse the file {file_path}, do the lean conversion"})

for event in result["messages"]: 
  event.pretty_print()
