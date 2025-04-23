import asyncio
import logging
import os
from dotenv import load_dotenv, find_dotenv

from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

# Load .env variables
load_dotenv(find_dotenv())

home_dir = os.getenv('HOME')
llm_temperature = float(os.getenv('LLM_TEMPERATURE'))
ollama_model = os.getenv('OLLAMA_MODEL')
ollama_base_url = os.getenv('OLLAMA_BASE_URL')
py_project_dir = os.getenv('PY_PROJECT_DIR')

# Set up the chat model
model = ChatOllama(
    base_url=ollama_base_url,
    model=ollama_model,
    temperature=llm_temperature
)

async def print_stream(stream):
    async for s in stream:
        message = s["messages"][-1]
        if not isinstance(message, HumanMessage):
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

async def chat():
    async with MultiServerMCPClient() as client:
        await client.connect_to_server(
            'ShellCommandExecutor',
            command='python',
            args=[home_dir + py_project_dir + '/servers/shell_mcp_server.py'],
            transport='stdio',
        )

        tools = client.get_tools()

        memory = MemorySaver()

        with open("system_prompt.txt", "r") as file:
            prompt = file.read()

        graph = create_react_agent(model, tools=tools, checkpointer=memory, prompt=prompt)
        config = {"configurable": {"thread_id": "1"}}
        print("Shell Command Chat Agent. Type 'exit' to quit.")
        while True:
            print("================================ Human Message =================================\n")
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                break

            inputs = {"messages": [("user", user_input)]}
            await print_stream(graph.astream(inputs, config=config, stream_mode="values"))

if __name__ == '__main__':
    asyncio.run(chat())