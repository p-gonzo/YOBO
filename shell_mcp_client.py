import asyncio
import logging
import os
from dotenv import load_dotenv, find_dotenv

from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Setup logging
logging.basicConfig(format='%(levelname)s %(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('multi_mcp_client')

# Load .env variables
load_dotenv(find_dotenv())

home_dir = os.getenv('HOME')
llm_temperature = float(os.getenv('LLM_TEMPERATURE'))
ollama_model = os.getenv('OLLAMA_MODEL')
ollama_base_url = os.getenv('OLLAMA_BASE_URL')
py_project_dir = os.getenv('PY_PROJECT_DIR')

# Set up the chat model
ollama_chat_llm = ChatOllama(
    base_url=ollama_base_url,
    model=ollama_model,
    temperature=llm_temperature
)

def extract_last_contents(messages):
    last_llm_response = None
    last_shell_output = None
    last_command_executed = None

    for message in reversed(messages):
        if last_llm_response is None and type(message).__name__ == "AIMessage":
            if hasattr(message, 'content') and message.content:
                last_llm_response = message.content

        if last_shell_output is None and type(message).__name__ == "ToolMessage":
            if hasattr(message, 'content') and message.content:
                last_shell_output = message.content

        if last_command_executed is None and type(message).__name__ == "AIMessage":
            tool_calls = getattr(message, 'tool_calls', None)
            if tool_calls:
                # tool_calls should be a list of dict-like objects
                last_tool = tool_calls[-1]
                last_command_executed = last_tool['args'].get('command')

        # Break early if all values have been found
        if all([last_llm_response, last_shell_output, last_command_executed]):
            break
    return last_llm_response, last_shell_output, last_command_executed
    
    

async def chat():
    async with MultiServerMCPClient() as client:
        await client.connect_to_server(
            'ShellCommandExecutor',
            command='python',
            args=[home_dir + py_project_dir + '/servers/shell_mcp_server.py'],
            transport='stdio',
        )

        tools = client.get_tools()
        agent = create_react_agent(ollama_chat_llm, tools)

        chat_history = [
            {
                "role": "system",
                "content": (
                    "You are a helpful command-line assistant. You have access to a tool called `execute_shell_command` "
                    "that can run actual shell commands and return their output to the user.\n\n"
                    "Whenever the user asks a question that requires terminal access (like listing files, checking the current directory, "
                    "reading a file, or inspecting processes), use this tool to perform the task.\n\n"
                    "DO NOT generate code blocks like `await execute_shell_command(...)`. JUST USE THE TOOL DIRECTLY. "
                    "When appropriate, explain the results briefly after running the command. "
                    "THE HOST SYSTEM IS MAC OS, DO NOT USE LINUX COMMANDS AND EXPECT THEM TO WORK "
                    "Thank you :)"
                )
            }
        ]

        print("Shell Command Chat Agent. Type 'exit' to quit.")
        while True:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting chat.")
                break

            if user_input in ['print_chat']:
                print(chat_history)
                break

            chat_history.append({"role": "user", "content": user_input})

            try:
                result = await agent.ainvoke({"messages": chat_history})
                messages = result.get("messages", [])
                # print(f"Messages are{messages}")
                llm_response, shell_output, command_executed = extract_last_contents(messages)
                # print(f"Command Executed: {command_executed}")
                # print(f"Shell Output: {shell_output}")
                print(f"Assistant Response: {llm_response}")

                chat_history.append({"role": "system", "content": f"Command Executed: {command_executed}"})
                chat_history.append({"role": "system", "content": f"Shell Output: {shell_output}"})
                chat_history.append({"role": "assistant", "content": llm_response})


            except Exception as e:
                logger.error(f"Error during chat: {e}")
                print("An error occurred. Check logs.")

if __name__ == '__main__':
    asyncio.run(chat())