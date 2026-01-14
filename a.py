import os

def create_structure():
    # تعريف هيكلية المجلدات والملفات
    project_name = "ehjezli_agent"
    structure = {
        "app": {
            "__init__.py": "",
            "core": {
                "__init__.py": "",
                "config.py": "# Configuration logic",
                "registry.py": "# Model Failover logic",
                "logger.py": "# Logging setup"
            },
            "services": {
                "__init__.py": "",
                "api_service.py": "# HTTP Client logic",
                "tool_factory.py": "# Dynamic Tool creation"
            },
            "agents": {
                "__init__.py": "",
                "orchestrator.py": "# LangGraph logic"
            },
            "main.py": "# FastAPI entry point"
        },
        "data": {
            "api_docs.json": "[]",
            "agent_profile.json": "{}"
        },
        ".env": "GROQ_API_KEY=your_key_here\nTOOLS_API_BASE_URL=https://api.example.com",
        "requirements.txt": "fastapi\nuvicorn\nlangchain-groq\nlanggraph\nhttpx\npython-dotenv"
    }

    def build(base_path, struct):
        for name, content in struct.items():
            path = os.path.join(base_path, name)
            if isinstance(content, dict):
                # إذا كان القيمة قاموس، أنشئ مجلد
                os.makedirs(path, exist_ok=True)
                build(path, content)
            else:
                # إذا كان القيمة نص، أنشئ ملفاً
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Created: {path}")

    print(f"🚀 Starting creation of {project_name} structure...")
    build(".", {project_name: structure})
    print("\n✨ Structure created successfully! Now you can copy the codes into their files.")

if __name__ == "__main__":
    create_structure()