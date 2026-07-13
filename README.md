# ACT-II Hackathon - AI Career Training Platform

> A comprehensive AI-powered platform for personalized interview preparation and career skill development across Software Engineering, Data Analysis, and Machine Learning roles.

**Live Demo:** [https://act-ii-hackathon-amd.vercel.app](https://act-ii-hackathon-amd.vercel.app)

## 📋 Overview

ACT-II is an intelligent career training platform that combines three specialized AI agents to provide a holistic interview preparation experience:

1. **Agent 1 - Tech Resource Gatherer**: Collects and curates technical learning resources (GitHub repos, official documentation, YouTube tutorials)
2. **Agent 2 - Aptitude Quiz Master**: Generates role-specific multiple-choice questions with dynamic difficulty
3. **Agent 3 - Mock Interviewer**: Conducts live voice-based technical interviews with real-time feedback

The platform tracks user progress through a 30-day structured curriculum and caches generated content for optimal performance.

---

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLite
- **Frontend**: React 19, Vite, Axios, Tailwind CSS
- **AI/ML**: CrewAI, Fireworks API, OpenAI-compatible endpoints
- **Infrastructure**: Docker, Vercel, Render

### Language Distribution

- **Python**: 50% (Backend, AI agents)
- **JavaScript**: 37.8% (Frontend)
- **CSS**: 11.4% (Styling)
- **Other**: 0.8%

### Directory Structure

```
├── Backend/                          # FastAPI orchestrator server
│   ├── main_orchestrator.py         # Central API router
│   ├── auth.py                      # JWT authentication & password hashing
│   ├── database/                    # SQLite schemas and initialization
│   └── __init__.py
├── agent1/                           # Tech Resource Gatherer
│   ├── main.py                      # CrewAI entry point
│   ├── agents/                      # Agent definitions
│   ├── tasks/                       # Task workflows
│   ├── tools/                       # Web search, curriculum access, DB tools
│   ├── config/                      # Agent configurations
│   ├── data/                        # Local curriculum data
│   └── tests/                       # Unit tests
├── agent2/                           # Aptitude Quiz Master & Mock Interviewer
│   ├── agents.py                    # Quizmaster & Evaluator agents
│   ├── crew.py                      # CrewAI crew orchestration
│   ├── tasks.py                     # Question generation & evaluation tasks
│   ├── tools.py                     # Curriculum reader & KB search
│   ├── interview_server.py          # WebSocket live interview engine
│   ├── interview_memory.py          # Conversation state management
│   ├── Curriculum/                  # YAML curriculum for DA, SWE, ML
│   └── knowledge_base_[DA|SWE|ML]/  # Domain-specific knowledge bases
├── frontend/                         # React + Vite application
│   ├── src/                         # React components and hooks
│   ├── public/                      # Static assets
│   ├── index.html                   # Entry HTML
│   ├── vite.config.js              # Vite configuration
│   └── package.json                # Dependencies
├── Dockerfile                        # Containerized backend deployment
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment configuration template
└── techguide.db                      # Embedded resource database
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **API Keys**:
  - `FIREWORKS_API_KEY` - Fireworks AI (LLM provider)
  - `YOUTUBE_API_KEY` - YouTube Data API (video search)
  - `SERPER_API_KEY` - Serper (web search)
  - `GEMINI_API_KEY` - Google Gemini (Agent 1)
  - `GITHUB_TOKEN` - GitHub API (repository search)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/ermadanvk-afk/ACT-II-Hackathon-AMD.git
cd ACT-II-Hackathon-AMD
```

#### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt --ignore-requires-python

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# For Agent 1, also set up its .env
cp agent1/.env.example agent1/.env
# Fill in the API keys
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
```

#### 4. Initialize Database

```bash
# From project root - the database initializes automatically on first backend startup
python -c "from Backend.database.db_setup import init_db; init_db()"
```

### Running Locally

#### Backend (FastAPI Server)

```bash
# From project root
python -m uvicorn Backend.main_orchestrator:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

#### Frontend (Development Server)

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

#### Docker Deployment

```bash
# Build the Docker image
docker build -t amd-act-hackathon .

# Run the container
docker run -p 8000:8000 \
  -e FIREWORKS_API_KEY=your_key \
  -e YOUTUBE_API_KEY=your_key \
  -e SERPER_API_KEY=your_key \
  -e SECRET_KEY=your_secret_key \
  amd-act-hackathon
```

---

## 📊 How It Works

### User Journey

```
1. Register/Login
   ↓
2. Select Role (SWE, DA, ML) & Difficulty (Beginner/Intermediate/Advanced)
   ↓
3. Daily Cycle (30-day curriculum):
   a) Tech Resources (Agent 1)     → Learn concepts
   b) Aptitude Quiz (Agent 2)      → Practice MCQs
   c) Mock Interview (Agent 2/3)   → Live interview simulation
   ↓
4. Progress Tracking & Completion
```

### Agent Workflows

#### Agent 1: Tech Resource Gatherer

**Goal**: Curate personalized learning resources

**Tools**:
- **webaccess**: Searches GitHub repositories, official documentation, YouTube tutorials (concurrent/async)
- **curriculumaccess**: Retrieves structured local curriculum + live roadmap enrichment
- **database_interact**: Stores/retrieves gathered resources in SQLite

**API Endpoint**: `POST /api/run-tech`

**Response**:
```json
{
  "status": "success",
  "type": "tech",
  "tech_data": "Learning resources and recommended materials",
  "cached": false
}
```

#### Agent 2: Aptitude Quiz Master

**Goal**: Generate and evaluate role-specific MCQs

**Agents**:
- **Quizmaster Agent**: Generates 8-10 MCQs formatted as JSON
- **Evaluator Agent**: Scores user answers and provides explanations

**Knowledge Bases**:
- `knowledge_base_SWE`: Data structures, algorithms, system design
- `knowledge_base_DA`: Statistics, SQL, business metrics
- `knowledge_base_ML`: Linear algebra, ML algorithms, neural networks

**API Endpoints**:
- `POST /api/run-aptitude` - Generate MCQ
- WebSocket `/ws/interview` - Live mock interview

**Response (MCQ)**:
```json
{
  "status": "success",
  "type": "aptitude",
  "mcq_data": [
    {
      "question": "What is time complexity of merge sort?",
      "options": ["O(n)", "O(n log n)", "O(n²)", "O(2^n)"],
      "correct": 1
    }
  ],
  "cached": false
}
```

#### Agent 3: Mock Interviewer

**Goal**: Conduct real-time voice-based technical interviews

**Technology**:
- WebSocket for bidirectional streaming
- Fireworks API for streaming LLM responses
- Frontend STT/TTS (Speech-to-Text / Text-to-Speech)
- Knowledge base context injection for accuracy

**Flow**:
1. User connects via WebSocket
2. AI greets and asks first question
3. User speaks → Frontend converts to text via STT
4. Text sent to AI via WebSocket
5. AI responds → Frontend converts to speech via TTS
6. Process repeats

---

## 🔧 Technical Decisions

### 1. **CrewAI for Multi-Agent Orchestration**

**Why**: Enables agent-to-agent collaboration, shared tools, and sequential/hierarchical task execution.

**Trade-offs**:
- ✅ Simplified agent management
- ✅ Built-in tool framework
- ❌ Monkeypatch required for Fireworks API compatibility (removed `cache_breakpoint` field)

### 2. **Fireworks API over OpenAI**

**Why**: Cost-effective, high-performance inference with OpenAI-compatible API.

**Implementation**:
```python
fireworks_llm = LLM(
    model="accounts/fireworks/models/minimax-m3",
    provider="openai",  # Routes through OpenAI SDK
    api_key=os.getenv("FIREWORKS_API_KEY"),
    base_url="https://api.fireworks.ai/inference/v1"
)
```

### 3. **SQLite for Caching & User State**

**Why**: No DevOps overhead, embedded database, ACID compliance.

**Caching Strategy**:
- **Key**: `user_id + role + level + day`
- **Benefit**: Instant response for repeat queries (no re-generation)
- **Tables**: `session_cache`, `user_journeys`, `users`

### 4. **WebSocket for Live Interviews**

**Why**: Low-latency bidirectional communication for real-time speech interaction.

**Architecture**:
- Single FastAPI server hosts HTTP APIs + WebSocket endpoint
- CORS configured for frontend domains
- Connection-per-interview model (no persistent storage during interview)

### 5. **React + Vite for Frontend**

**Why**: Fast build times, modern bundling, optimized for SPAs.

**Dependencies**:
- `axios`: HTTP client for API calls
- `react-router-dom`: Client-side routing
- `lucide-react`: Icon library
- `oxlint`: Fast linting

### 6. **JWT Authentication**

**Why**: Stateless, scalable authentication for APIs.

**Implementation**:
- 7-day token expiry
- SHA256 password hashing with passlib
- Token includes username claim (`sub`)

### 7. **Environment-Based Configuration**

**Why**: Support development, staging, and production seamlessly.

**Key Variables**:
- `ENVIRONMENT`: "development" or "production"
- `FIREWORKS_BASE_URL`: LLM provider endpoint
- `FRONTEND_URL`: CORS allowlist
- `DATABASE_PATH`, `SCHEDULE_DB_PATH`: Data persistence locations

### 8. **No Redis Cache**

**Why**: SQLite provides sufficient performance for hackathon MVP + reduced infrastructure complexity.

**Trade-off**: For production at scale, consider Redis for session state.

---

## 📚 API Documentation

### Authentication

All endpoints (except `/api/register` and `/api/login`) require JWT token.

```bash
# Login
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=pass"

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}

# Use token in headers
Authorization: Bearer <access_token>
```

### Key Endpoints

#### User Management

- `POST /api/register` - Create account
- `POST /api/login` - Get JWT token
- `GET /api/me` - Get current user & journeys

#### Orchestration

- `POST /api/next-action` - Determine what user should do next
- `POST /api/run-tech` - Generate tech resources (Agent 1)
- `POST /api/run-aptitude` - Generate MCQ (Agent 2)
- `POST /api/run-interview` - Start mock interview (WebSocket)

#### Progress Tracking

- `POST /api/complete-day` - Mark day as complete & unlock next
- `DELETE /api/journey/reset` - Reset progress & cache
- `GET /api/schedule/{role}` - Fetch 30-day curriculum schedule

#### Example: Run Aptitude Quiz

```bash
curl -X POST http://localhost:8000/api/run-aptitude \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john_doe",
    "target_role": "Software Engineer",
    "topic_name": "Arrays and Strings",
    "difficulty": "Intermediate",
    "day": 1
  }'
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code improvements

### Development Workflow

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make changes** with clear commit messages
4. **Test locally**:
   ```bash
   # Backend tests (if available)
   pytest
   
   # Frontend linting
   cd frontend && npm run lint
   ```
5. **Submit a Pull Request** with:
   - Description of changes
   - Any API modifications documented
   - Environment variables added (if any)

### Code Style

- **Python**: Follow PEP 8, use type hints where possible
- **JavaScript/React**: Use ESLint rules (configured in project)
- **Comments**: Document complex logic, especially in agents

### Adding New Features

#### To Add a New Role (e.g., DevOps Engineer)

1. Create curriculum: `agent2/Curriculum/devops_Curriculum.yaml`
2. Create knowledge base: `agent2/knowledge_base_DEVOPS/`
3. Update role mapping in:
   - `Backend/main_orchestrator.py`
   - `agent2/crew.py`
   - `agent2/agents.py`
4. Update frontend role selector

#### To Modify Agent Behavior

1. Edit agent definition in `agent2/agents.py`
2. Update task prompts in `agent2/tasks.py`
3. Modify tools in `agent2/tools.py`
4. Test via `POST /api/run-aptitude` endpoint

#### To Add API Endpoints

1. Create route in `Backend/main_orchestrator.py`
2. Define request/response Pydantic models
3. Add authentication if needed via `get_current_user` dependency
4. Document in API section above

---

## 📦 Dependencies

### Python (requirements.txt)

- **crewai (≥1.15.0)**: Multi-agent orchestration framework
- **langchain (≥0.2.0)**: LLM integration utilities
- **openai (≥1.0.0)**: OpenAI SDK (works with Fireworks)
- **fastapi (≥0.111.0)**: API framework
- **uvicorn (≥0.30.0)**: ASGI server
- **websockets (≥12.0)**: WebSocket support
- **pyjwt, passlib**: Authentication
- **aiosqlite**: Async SQLite access
- **python-dotenv**: Environment configuration

### JavaScript/Node (frontend/package.json)

- **react (^19.2.7)**: UI framework
- **react-router-dom (^7.18.1)**: Routing
- **axios (^1.18.1)**: HTTP client
- **vite (^8.1.1)**: Build tool

---

## 🐛 Troubleshooting

### Issue: "Failed to import Agent 1"

**Cause**: Missing dependencies or incorrect Python path

**Solution**:
```bash
pip install -r requirements.txt --ignore-requires-python
python -m Backend.main_orchestrator  # Use module syntax
```

### Issue: WebSocket connection fails

**Cause**: CORS misconfiguration or frontend URL mismatch

**Solution**:
```bash
# Check .env
echo $FRONTEND_URL  # Should match your frontend origin

# Update if needed
export FRONTEND_URL=http://localhost:5173
```

### Issue: Cached responses not updating

**Cause**: `day` parameter still matches cache key

**Solution**:
```bash
# Reset cache for a role
DELETE /api/journey/reset?role=Software Engineer&level=Beginner
```

### Issue: LLM Rate Limiting

**Cause**: Too many concurrent requests

**Solution**:
- Adjust `max_tokens` in agent configs
- Implement request queuing in production
- Contact Fireworks for rate limit increase

---

## 📝 Environment Configuration

Create a `.env` file in the project root:

```dotenv
# === Required in Production ===
SECRET_KEY=generate_a_random_64_char_string
ENVIRONMENT=production
FIREWORKS_API_KEY=your_fireworks_api_key
FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
YOUTUBE_API_KEY=your_youtube_api_key
SERPER_API_KEY=your_serper_api_key

# === Optional Overrides ===
PORT=8000
DATABASE_PATH=/app/database/app.db
SCHEDULE_DB_PATH=/app/database/scheduler.db
FRONTEND_URL=https://your-frontend.vercel.app
WS_BASE_URL=wss://your-backend.onrender.com
```

---

## 📄 License

This project is part of the ACT-II Hackathon. Usage governed by hackathon terms.

---

## 👥 Team & Support

**Developers**: [ermadanvk-afk](https://github.com/ermadanvk-afk)

**Questions or Issues?**
- Open a [GitHub Issue](https://github.com/ermadanvk-afk/ACT-II-Hackathon-AMD/issues)
- Check existing documentation in agent READMEs
- Review API logs via Docker container

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

**Built with ❤️ for career advancement at the ACT-II Hackathon**
