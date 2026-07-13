# ACT-II Hackathon - AI Career Training Platform

> A comprehensive AI-powered platform for personalized interview preparation and career skill development across Software Engineering, Data Analysis, and Machine Learning roles.

**Live Demo:** https://act-ii-hackathon-amd.vercel.app/

## 📋 Overview

ACT-II combines three specialized AI agents to provide a holistic interview preparation experience:

1. **Agent 1 - Tech Resource Gatherer**: Collects and curates technical learning resources
2. **Agent 2 - Aptitude Quiz Master**: Generates role-specific multiple-choice questions with dynamic difficulty
3. **Agent 3 - Mock Interviewer**: Conducts live voice-based technical interviews with real-time feedback

The platform tracks user progress through a 30-day structured curriculum with intelligent caching for optimal performance.

---

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLite
- **Frontend**: React 19, Vite, Axios, Tailwind CSS
- **AI/ML**: CrewAI, Fireworks API, OpenAI-compatible endpoints
- **Infrastructure**: Docker, Vercel, Render

### Directory Structure

```
├── Backend/                          # FastAPI orchestrator
│   ├── main_orchestrator.py         # Central API router
│   ├── auth.py                      # JWT authentication
│   └── database/                    # SQLite schemas
├── agent1/                           # Tech Resource Gatherer
│   ├── main.py, agents/, tasks/
│   ├── tools/                       # Web search, curriculum, DB
│   └── data/                        # Local curriculum
├── agent2/                           # Quiz Master & Mock Interviewer
│   ├── agents.py, tasks.py, tools.py
│   ├── interview_server.py          # WebSocket engine
│   ├── Curriculum/                  # YAML curriculum
│   └── knowledge_base_*/            # Domain-specific KBs
├── frontend/                         # React + Vite
│   ├── src/, public/
│   └── index.html
├── requirements.txt                  # Python dependencies
└── Dockerfile                        # Container setup
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** | **Node.js 18+**
- **API Keys**: `FIREWORKS_API_KEY`, `YOUTUBE_API_KEY`, `SERPER_API_KEY`, `GEMINI_API_KEY`, `GITHUB_TOKEN`

### Installation

```bash
# Clone & setup backend
git clone https://github.com/ermadanvk-afk/ACT-II-Hackathon-AMD.git
cd ACT-II-Hackathon-AMD
pip install -r requirements.txt --ignore-requires-python

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Setup frontend
cd frontend && npm install && cd ..
```

### Running Locally

```bash
# Terminal 1: Backend (FastAPI)
python -m uvicorn Backend.main_orchestrator:app --reload
# API: http://localhost:8000

# Terminal 2: Frontend (React)
cd frontend && npm run dev
# Frontend: http://localhost:5173
```

### Docker Deployment

```bash
docker build -t amd-act-hackathon .
docker run -p 8000:8000 -e FIREWORKS_API_KEY=your_key ... amd-act-hackathon
```

---

## 📊 How It Works

### User Journey
```
1. Register/Login
2. Select Role (SWE/DA/ML) & Difficulty (Beginner/Intermediate/Advanced)
3. Daily Cycle (30 days):
   - Tech Resources (Agent 1) → Learn concepts
   - Aptitude Quiz (Agent 2) → Practice MCQs
   - Mock Interview (Agent 3) → Live simulation
4. Progress Tracking & Completion
```

### Agent Workflows

| Agent | Purpose | Tools | API |
|-------|---------|-------|-----|
| **Agent 1** | Curate learning resources | Web search, curriculum access, DB storage | `POST /api/run-tech` |
| **Agent 2** | Generate & evaluate MCQs | Knowledge bases (SWE/DA/ML), curriculum | `POST /api/run-aptitude` |
| **Agent 3** | Real-time interviews | WebSocket, Fireworks API, STT/TTS | `ws://api:8000/ws/interview` |

**Example MCQ Response**:
```json
{
  "status": "success",
  "mcq_data": [
    {
      "question": "What is time complexity of merge sort?",
      "options": ["O(n)", "O(n log n)", "O(n²)", "O(2^n)"],
      "correct": 1
    }
  ]
}
```

---

## 🔧 Key Technical Decisions

| Decision | Why | Trade-off |
|----------|-----|-----------|
| **CrewAI** | Multi-agent orchestration | Requires monkeypatch for Fireworks compatibility |
| **Fireworks API** | Cost-effective, high-performance | OpenAI-compatible routing only |
| **SQLite** | No DevOps, embedded, ACID | Consider Redis for production scale |
| **WebSocket** | Real-time bidirectional comms | Connection-per-interview model |
| **JWT Auth** | Stateless, scalable | 7-day token expiry |

See [CONTRIBUTING.md](./CONTRIBUTING.md) for implementation details.

---

## 📚 API Quick Reference

### Authentication
```bash
curl -X POST http://localhost:8000/api/login \
  -d "username=user&password=pass"
# Returns: { "access_token": "...", "token_type": "bearer" }
```

### Key Endpoints
- `POST /api/register` - Create account
- `POST /api/login` - Get JWT token
- `POST /api/run-tech` - Generate resources (Agent 1)
- `POST /api/run-aptitude` - Generate MCQ (Agent 2)
- `POST /api/complete-day` - Mark progress
- `DELETE /api/journey/reset` - Reset cache

See README.md in agent subdirectories for detailed endpoint docs.

---

## 📦 Dependencies

**Python**: crewai, langchain, fastapi, uvicorn, websockets, aiosqlite, pyjwt, passlib  
**Node**: react, react-router-dom, axios, vite

---

## 📝 Environment Setup

```dotenv
# Required
SECRET_KEY=<random_64_char_string>
FIREWORKS_API_KEY=<your_key>
YOUTUBE_API_KEY=<your_key>
SERPER_API_KEY=<your_key>

# Optional
PORT=8000
FRONTEND_URL=http://localhost:5173
WS_BASE_URL=ws://localhost:8000
```

---

## 🤝 Contributing

Want to contribute? See [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Development workflow & branch conventions
- Code style guidelines
- Feature addition guides
- Common issues & solutions

---

## 📄 License

MIT License © 2026 Madan Vishwakarma. See [LICENSE](./LICENSE) for details.

---

## 🎯 Roadmap

- [ ] Integrate speech-to-text for live interviews
- [ ] Persist interview transcripts and feedback
- [ ] Add progress analytics dashboard
- [ ] Expand to additional roles (Product Manager, UX Designer)
- [ ] Implement peer comparison (anonymized benchmarking)
- [ ] Mobile app for on-the-go practice
- [ ] Multi-language support for international users

---

## ❓ Need Help?

- **Setup Issues?** → See [CONTRIBUTING.md - Development Guidance](./CONTRIBUTING.md#-development--setup-guidance)
- **Bug Report?** → [Open an Issue](https://github.com/ermadanvk-afk/ACT-II-Hackathon-AMD/issues)
- **Want to Contribute?** → Read [CONTRIBUTING.md](./CONTRIBUTING.md)

**Built with ❤️ for career advancement at the ACT-II Hackathon**
