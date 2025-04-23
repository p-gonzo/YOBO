# 🧨 YOBO: You Only Bash Once

#### A terminal agent with absolutely no guardrails.
No tutorials, no code blocks, just cold, hard execution.  

Built on [LangChain's MCP](https://github.com/langchain-ai/langchain), YOBO is a local-first, terminal-purist shell command interface that turns your language model into a bash-native operator on macOS.  
Why type `ls -la` yourself when you can make a moderately intelligent machine do it with existential dread?

## 🚀 What is YOBO?

- A bash-first terminal automation assistant
- Controlled via natural language
- Deployed locally via the **Model Context Protocol (MCP)**
- Obsessed with following orders, not giving lectures


## 🧠 Architecture
```
        +-------------+
        |   You, 👑   |
        +------+------+
               |
               v
    +----------+----------+
    | YOBO (LLM via MCP)  |
    +----------+----------+
               |
     +---------+---------+
     |  Shell MCP Server |
     +-------------------+
               |
           /bin/bash
```

Under the hood:

- 🧠 Local LLM (e.g., `mistral-small3.1` via Ollama)
- 🧪 Tool-based agent using LangChain + LangGraph
- 🔨 Real-time terminal execution via `subprocess` and `/bin/bash`
- 🎯 MCP handles agent-tool interaction over `stdio`

## 🛠️ Setup

**Install dependencies**

```bash
pipenv install
```
Start Ollama locally
* Make sure OLLAMA_MODEL in .env is downloaded and running.
```bash
pipenv run python yobo.py
```

## 🧱 Philosophy
"Those who describe commands are doomed to never execute them."
— YOBO, probably

This agent follows a strict dogma:

❌ No code snippets
❌ No shell tutorials
❌ No ‘helpful’ explanations

Just bash, executed on your behalf, until your task is done or your patience is gone.

## 😈 Known Limitations
Does not validate commands before execution. YOLOps? No, YOBO.

Shells out via bash. No PowerShell nonsense.

Errors? Oh yes. Expect them. Embrace them. YOBO handles stderr like a dramatic actor.

## ⚠️ Disclaimer

This is for local-only, non-production, you-break-it-you-buy-it use.

You are literally telling an LLM to run terminal commands. What could possibly go wrong?

YOBO exists because someone got tired of typing ls and decided an LLM should suffer instead.

## 📎 License
MIT. Because you probably weren’t going to read this section anyway.