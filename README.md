# ✈️ Ehjezli AI Agent

A high-performance, resilient AI orchestration engine designed for the **Ehjezli Platform**. 
This project leverages **LangGraph** and **Groq** to create a hybrid agent capable of handling complex booking queries with robust memory management and fault tolerance.



[Image of software architecture diagram]


## 🚀 Key Features

### 🧠 Hybrid Model Intelligence
- **Dynamic Dispatch:** Automatically routes queries between heavy "Reasoning" models (e.g., `llama-3.3-70b`) and fast "Instant" models (`llama-3.1-8b`) based on availability and load.
- **Auto-Discovery:** Automatically fetches and categorizes live models from Groq API if local configurations fail.

### 💾 Smart Persistent Memory
- **Async Architecture:** Built on `aiosqlite` and `AsyncSqliteSaver` for non-blocking I/O operations tailored for FastAPI.
- **Self-Healing Context:** Automatically detects `Context Overflow (413)` errors and seamlessly archives old sessions to start fresh without crashing user experience.
- **WAL Mode Enabled:** Optimized SQLite configuration for high-concurrency writes.

### 🛡️ Fault Tolerance (The "Registry")
- **Circuit Breaker Pattern:** Automatically blacklists failing models or dead APIs temporarily.
- **Monkey Patching:** Custom fixes for compatibility between `LangGraph` and `aiosqlite`.

## 📊 Live Dashboard
Explore the project performance and metrics here:
[**View Ehjezli Dashboard**](https://ehjezli-dash-mkhcwwnt.manus.space/)

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Async Web Server)
- **Orchestration:** [LangGraph](https://langchain-ai.github.io/langgraph/) (Stateful Agents)
- **LLM Provider:** [Groq API](https://groq.com/) (LPU Inference)
- **Database:** SQLite (Async/WAL Mode)
- **Language:** Python 3.10+

## 📂 Project Structure

```bash
ehjezli_agent/
├── app/
│   ├── agents/         # Orchestrator & Logic
│   ├── core/           # Config, Registry, Memory Manager
│   ├── memory/         # Memory Management
│   ├── services/       # External APIs
│   ├── tools/          # Dynamic Tool Factory
│   └── main.py         # Application Entry Point
├── ehjezli_memory.db   # Persistent Storage
└── requirements.txt







🔧 Installation
Clone the repo:

Bash

git clone [https://github.com/AlhusseinAliAlhaidari/Ahjezli-Agent-Backend.git](https://github.com/AlhusseinAliAlhaidari/Ahjezli-Agent-Backend.git)
cd Ahjezli-Agent-Backend
Set up Virtual Environment:

Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:

Bash

pip install -r requirements.txt
Environment Variables: Create a .env file:

مقتطف الرمز

GROQ_API_KEY=gsk_...
Run Server:

Bash

python -m app.main
🤝 Contributing
Contributions are welcome! Please open an issue or submit a PR.