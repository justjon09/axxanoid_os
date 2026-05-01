# Axxanoid OS (Project Q)

A sovereign, local-first intelligence daemon built to run natively on Apple Silicon (M4 Pro). Q is not a chatbot; Q is a digital co-founder and lead architect responsible for managing state, auditing hardware, and enforcing strict, ruthless business prioritization.

## Core Architecture
* **The Engine:** Local Ollama (`dolphin3`) for uncensored, offline inference.
* **The Bridge:** FastAPI backend (`main.py`) running on port 8000.
* **The Memory:** Tri-layer architecture utilizing RAM (Markdown config injection), SQLite (short-term chat state), and ChromaDB (long-term vector vault).
* **The Subconscious:** An asynchronous 15-minute background heartbeat (`q_heartbeat.py`) that audits system hardware/APIs and proactively alerts the UI if action is needed.
* **The Glass:** React + TypeScript + Vite frontend (`frontend/`) running on port 5173.

---

## Boot Sequence (Start Instructions)

### 1. Start the Inference Engine
Ensure Ollama is running in the background and the model is ready.

```bash
ollama run dolphin3

2. Boot the Daemon (Backend)
Open a terminal, activate the Python virtual environment, and execute the FastAPI bridge. This mounts the API routes, connects to the database, and automatically starts Q's 15-minute background heartbeat.

source q_env/bin/activate
python main.py

Backend runs on: http://127.0.0.1:8000

3. Initialize the Glass (Frontend)
Open a second terminal window, navigate to the frontend directory, and start the Vite development server.

cd frontend
npm run dev

UI runs on: http://localhost:5173

Testing the Subconscious
To manually force Q to run his system audits (Hardware verification, API pings) and review recent memory without waiting for the scheduled cron cycle, run the test script from the root directory:

source q_env/bin/activate
python test_heartbeat.py