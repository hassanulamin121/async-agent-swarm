# 🚀 Async Multi-Agent Swarm API

A robust, production-ready, asynchronous multi-agent microservice backend built with **FastAPI** and **Google Gemini 3.8-flash**. This system orchestrates a specialized swarm of AI agents to research real-time data, draft structured content, and refine it into professional cinematic scripts.

---

## 🛠️ Architecture & Agent Swarm Pipeline
1. **🔍 Research Agent:** Fetches external data (via Public APIs like PoetryDB) and utilizes Gemini for deep contextual research.
2. **✍️ Writer Agent:** Transforms research insights into a structured, engaging cinematic script tailored for modern audiences.
3. **🧐 Reviewer Agent:** Acts as a creative director to polish tone, fix logical flows, and ensure production-ready quality.

---

## ⚙️ Tech Stack
* **Backend Framework:** FastAPI (Asynchronous, High-Performance)
* **Data Validation:** Pydantic v2
* **AI Engine:** Google Gemini (`gemini-3.8-flash`)
* **HTTP Client:** HTTPX (Async requests)
* **Environment & Security:** Python-Dotenv, Strict CORS & Gitignore protocols.

---

## 🚀 Getting Started Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/async-agent-swarm.git](https://github.com/YOUR_USERNAME/async-agent-swarm.git)
   cd async-agent-swarm

Bash:

python -m venv venv
venv\Scripts\activate  # On Windows 

Bash:

pip install fastapi uvicorn pydantic python-dotenv google-generativeai httpx

Code snippet:

GEMINI_API_KEY="your_google_gemini_api_key_here"("keep your personal data in .env")

Bash:

uvicorn main:app --reload --reload-exclude "venv*"