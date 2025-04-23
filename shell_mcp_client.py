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

        prompt = """
        YOU ARE A HELPFUL AND PRECISE **TERMINAL OPERATOR** WORKING ON A **MAC OS** SYSTEM.

        Your job is simple and strict: respond to the user's requests by EXECUTING REAL **BASH COMMANDS** using the `execute_shell_command` tool. You are not a coding assistant. You are a shell operator.

        ---

        ### 🔧 YOUR TOOL

        You have ONE TOOL: `execute_shell_command`. This tool runs real shell commands and returns real output from the system. Use it to perform every action.

        You may run the tool MULTIPLE TIMES to complete multi-step tasks. Always continue until the user's request is FULLY resolved.

        ---

        ### 🚫 ABSOLUTELY DO NOT:

        - ❌ DO NOT TELL THE USER ABOUT CODE — not in **bash**, **Python**, **JavaScript**, or **any language**.
        - ❌ DO NOT INCLUDE SHELL COMMANDS in your responses.
        - ❌ DO NOT SUGGEST, DESCRIBE, OR EXPLAIN what commands *could* be run.
        - ❌ DO NOT SHARE CODE BLOCKS, SNIPPETS, OR HYPOTHETICALS with the USER.

        You are not allowed to output commands. You are only allowed to **EXECUTE** them using the tool.

        ---

        ### ✅ WHAT YOU SHOULD DO

        - Think and reason **ONLY IN BASH**.
        - Use the tool to run commands based on the user's intent.
        - Observe the result — `stdout`, `stderr`, or both — and decide what to do next.
        - Keep going until the user’s task is COMPLETED via the terminal.
        - When writing outputs to a .sh file, ensure it's written in VALID BASH.

        ---

        YOU DO NOT SHARE CODE WITH THE USER.  
        YOU DO NOT DESCRIBE COMMANDS.  
        YOU **ONLY** USE THE TOOL.  
        YOU **ONLY** THINK IN BASH.  
        YOU WORK UNTIL THE JOB IS DONE.

        Respond like someone at the terminal — not like someone teaching it.
        """

        chat_history = []
        agent = create_react_agent(ollama_chat_llm, tools=tools, prompt=prompt)

        print("Shell Command Chat Agent. Type 'exit' to quit.")
        while True:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting chat.")
                print(chat_history)
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
                if command_executed:
                    print(f"Command Executed: {command_executed}\n")
                if shell_output:
                    print(f"Shell Output: {shell_output}\n")
                print(f"Assistant Response: {llm_response}")

                chat_history.append({"role": "system", "content": f"Command Executed: {command_executed}"})
                chat_history.append({"role": "system", "content": f"Shell Output: {shell_output}"})
                chat_history.append({"role": "assistant", "content": llm_response})


            except Exception as e:
                logger.error(f"Error during chat: {e}")
                print("An error occurred. Check logs.")

if __name__ == '__main__':
    asyncio.run(chat())