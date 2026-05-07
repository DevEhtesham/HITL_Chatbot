# HITL Chatbot (Memory-Enabled)

A full-stack, memory-enabled AI chatbot built with **LangGraph**, **FastAPI**, and **Next.js**. The chatbot features a **Human-in-the-Loop (HITL)** workflow, requiring user approval before executing external tools like GitHub and LinkedIn crawlers.

## 🚀 Features

- **Conversational Memory**: Uses SQLite-based persistence to remember chat history across sessions.
- **Human-in-the-Loop (HITL)**: Automatically interrupts the flow to ask for permission before performing sensitive actions.
- **GitHub Crawler**: Fetches repository details, stars, and summarizes README content.
- **LinkedIn Crawler**: Integrates with Reverse Contact API to fetch professional profile details.
- **Smart Validation**: Detects missing information or placeholders and asks for clarification instead of guessing.
- **Modern UI**: A premium dark-mode interface built with Next.js and Tailwind CSS.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, LangChain, LangGraph, Groq (Llama 3.1), SQLite.
- **Frontend**: Next.js, React, Tailwind CSS.
- **Deployment**: Docker, Docker Compose.

---

## 🚦 Getting Started

### 1. Prerequisites
- **Docker Desktop** (Recommended) or Python 3.11+ & Node.js 18+.
- **API Keys**:
  - [Groq API Key](https://console.groq.com/)
  - [GitHub Personal Access Token](https://github.com/settings/tokens)
  - [Reverse Contact API Key](https://reversecontact.com/) (for LinkedIn)

### 2. Environment Setup
Create a `.env` file in the `backend/` directory using the provided `env.example`:

```bash
GITHUB_TOKEN="your_github_token"
API_KEY_LINKEDIN_CRAWLER="your_reverse_contact_key"
GROQ_API_KEY="your_groq_api_key"
```

### 3. Running with Docker Compose (Recommended)
The easiest way to run the entire stack is using Docker Compose. This will build both the frontend and backend images and link them together.

From the root directory, run:
```bash
docker compose up --build
```

- **Wait for the build**: The first time you run this, it will download the necessary images and build your containers.
- **Access the App**: Once the logs show both services are running:
  - **Frontend Chat UI**: [http://localhost:3000](http://localhost:3000)
  - **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Stopping**: Press `Ctrl+C` in your terminal to stop the services.

### 4. Running Manually

#### Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## 🤖 Usage Examples

- **GitHub Crawl**: "Crawl the repository langchain-ai/langgraph for me."
- **LinkedIn Crawl**: "Summarize this LinkedIn profile: https://www.linkedin.com/in/username/"
- **General Chat**: "Who are you and how can you help me?"

The bot will display an **Action Card** whenever a crawl is requested. You must click **Approve** to execute the tool or **Reject** to cancel.

---

## 📁 Project Structure

```text
HITL_Chatbot/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes (Chat & Action endpoints)
│   │   ├── services/     # LangGraph logic & Tool definitions
│   │   └── models/       # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   └── components/   # React components (ActionCard, etc.)
│   └── Dockerfile
├── docker-compose.yml    # Orchestration
└── README.md             # You are here
```
