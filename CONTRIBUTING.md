# Contributing to ACT-II Hackathon Platform

Thank you for your interest in contributing! This guide assumes you've read the [README.md](./README.md) and are ready to work on the codebase.

---

## 🎯 Development Setup

### Prerequisites

- **Python 3.11+** with `pip`
- **Node.js 18+** with `npm`
- **Git** for version control
- Familiarity with FastAPI, React, and CrewAI frameworks

### Local Development Environment

1. **Fork & Clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ACT-II-Hackathon-AMD.git
   cd ACT-II-Hackathon-AMD
   ```

2. **Python Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt --ignore-requires-python
   ```

3. **Environment Config**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Frontend Setup**:
   ```bash
   cd frontend && npm install && cd ..
   ```

5. **Database Init** (automatic on first backend startup, but manual init if needed):
   ```bash
   python -c "from Backend.database.db_setup import init_db; init_db()"
   ```

---

## 📋 Branch & Commit Conventions

### Branch Naming

- `feature/description` - New features or enhancements
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code quality improvements
- `test/description` - Test additions

**Examples**: `feature/add-speech-recognition`, `bugfix/websocket-timeout`, `docs/api-guide`

### Commit Messages

Follow the conventional commits format:

```
[TYPE] Brief description (50 chars max)

Optional detailed explanation
- Bullet 1
- Bullet 2

Fixes #123  (if applicable)
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## 🔄 Development Workflow

### Step 1: Create Feature Branch
```bash
git checkout -b feature/my-feature
```

### Step 2: Make Changes
- Keep commits focused and logical
- Follow code style guidelines (see below)
- Write clear commit messages

### Step 3: Test Your Changes

**Backend**:
```bash
# Run existing tests
pytest

# Or test manually
python -m uvicorn Backend.main_orchestrator:app --reload
curl -X POST http://localhost:8000/api/run-aptitude -d '{...}'
```

**Frontend**:
```bash
cd frontend

# Check linting
npm run lint

# Build check
npm run build

# Dev server
npm run dev
```

### Step 4: Push & Create PR
```bash
git push origin feature/my-feature
```

Then on GitHub, click "Compare & pull request" and fill in:

```markdown
## Description
What this PR does and why.

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Documentation

## Testing
How you verified the changes.

## Related Issue
Closes #123

## Environment Variables (if any)
- `WS_BASE_URL`: WebSocket URL

## Checklist
- [x] Code follows PEP 8 (Python) / ESLint (JS)
- [x] Comments added for complex logic
- [x] No debugging statements left (print/console.log)
- [x] API endpoints documented
```

---

## 🎨 Code Style Guidelines

### Python (Backend)

**Follow**: [PEP 8](https://pep8.org/)

```python
# Type hints required
def generate_mcq(user_id: str, role: str, difficulty: str) -> dict:
    """Generate a multiple-choice question.
    
    Args:
        user_id: Unique identifier for the user
        role: Target career role (SWE, DA, ML)
        difficulty: Question difficulty level
    
    Returns:
        Dictionary with MCQ data, options, and correct answer
    
    Raises:
        ValueError: If role is unsupported
    """
    pass

# Imports: stdlib, third-party, local (in groups)
import os
from typing import Dict

import fastapi
from crewai import Agent

from Backend.auth import get_current_user
```

- **Line length**: Max 88 characters
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **No bare exceptions**: Use specific exception types

### JavaScript/React (Frontend)

**Follow**: ESLint config in `.eslintrc.js`

```javascript
// Functional components with hooks
const UserCard = ({ userName, userRole, isActive }) => {
  const [loading, setLoading] = useState(false);
  
  return (
    <div className="card">
      <h2>{userName}</h2>
      <p role={userRole}</p>
    </div>
  );
};
```

- **Naming**: `PascalCase` components, `camelCase` variables/functions
- **Props**: Always destructure
- **Comments**: Explain "why", not "what"
- **No console.log** in production (use proper logging)
- **Imports**: Sort alphabetically, group by source

### SQL & Database

- Use meaningful names for tables/columns
- Add indexes for frequently queried fields
- Document complex queries with comments

---

## ✅ Pre-PR Checklist

- [ ] **Code Quality**
  - [ ] No `print()` or `console.log()` in code
  - [ ] Type hints added (Python)
  - [ ] Comments for complex logic
  - [ ] No trailing whitespace

- [ ] **Testing**
  - [ ] Tested locally (backend + frontend)
  - [ ] Existing functionality not broken
  - [ ] Edge cases considered

- [ ] **Documentation**
  - [ ] README updated (if feature addition)
  - [ ] API docs updated (if new endpoints)
  - [ ] Environment variables documented (if added)

- [ ] **Git**
  - [ ] Branch follows naming convention
  - [ ] Commits have clear messages
  - [ ] No merge conflicts
  - [ ] Rebased on latest main (if needed)

---

## 🚀 Feature Development Guides

### Adding a New Career Role (e.g., DevOps Engineer)

1. **Create curriculum**:
   ```bash
   cp agent2/Curriculum/swe_Curriculum.yaml agent2/Curriculum/devops_Curriculum.yaml
   # Edit with DevOps-specific topics
   ```

2. **Create knowledge base**:
   ```bash
   mkdir -p agent2/knowledge_base_DEVOPS
   # Add role-specific knowledge files
   ```

3. **Update mappings**:
   - `Backend/main_orchestrator.py` - Add DevOps enum
   - `agent2/agents.py` - Add DevOps agent config
   - `agent2/tasks.py` - Add DevOps task definition
   - Frontend role selector component

4. **Test end-to-end**:
   ```bash
   curl -X POST http://localhost:8000/api/run-tech \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test", "target_role": "DevOps Engineer"}'
   ```

### Modifying Agent Behavior

1. **Update agent** (`agent2/agents.py`):
   ```python
   agent = Agent(
       role="New Role Name",
       goal="What this agent should achieve",
       backstory="Background/expertise",
       llm=llm,
       tools=[tool1, tool2]
   )
   ```

2. **Update tasks** (`agent2/tasks.py`):
   ```python
   task = Task(
       description="What to do",
       agent=agent,
       expected_output="What the output should look like"
   )
   ```

3. **Update tools** (`agent2/tools.py`):
   - Add new tools as needed
   - Modify existing tools with new parameters

4. **Test via API**:
   ```bash
   curl -X POST http://localhost:8000/api/run-aptitude ...
   ```

### Adding API Endpoints

1. **Create Pydantic models** in `Backend/main_orchestrator.py`:
   ```python
   from pydantic import BaseModel
   
   class MyRequest(BaseModel):
       user_id: str
       param: str
   
   class MyResponse(BaseModel):
       status: str
       data: dict
   ```

2. **Add route**:
   ```python
   @app.post("/api/my-endpoint")
   async def my_endpoint(
       request: MyRequest,
       current_user: dict = Depends(get_current_user)
   ) -> MyResponse:
       """Endpoint description."""
       try:
           result = process(request.param)
           return MyResponse(status="success", data=result)
       except Exception as e:
           return MyResponse(status="error", data={"error": str(e)})
   ```

3. **Document** in README API section

---

## 🛠️ Common Development Issues & Solutions

### Backend Import Errors

**Problem**: "Failed to import Agent 1" or ModuleNotFoundError

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --ignore-requires-python

# Always run from project root using module syntax
python -m Backend.main_orchestrator

# Or with uvicorn
python -m uvicorn Backend.main_orchestrator:app --reload
```

**Tip**: Never run files directly from subdirectories.

---

### WebSocket Connection Failures

**Problem**: Frontend can't connect to WebSocket during interviews, connection errors

**Common Causes**:
- CORS policy mismatch
- Frontend/backend URL mismatch
- Wrong environment variables

**Solution**:
```bash
# Check environment config
cat .env | grep -E "FRONTEND_URL|WS_BASE_URL"

# For local development:
export FRONTEND_URL=http://localhost:5173
export WS_BASE_URL=ws://localhost:8000

# For production:
export FRONTEND_URL=https://your-frontend.vercel.app
export WS_BASE_URL=wss://your-backend.onrender.com

# Restart backend
python -m uvicorn Backend.main_orchestrator:app --reload
```

**Debug**: Open browser DevTools (F12) → Console tab → Look for WebSocket errors (they indicate CORS or connection issues)

---

### Stale Cache Responses

**Problem**: Getting cached responses even after code changes to question generation or resources

**Why**: Caching uses key `user_id + role + level + day` — same params return cached results

**Solution**:
```bash
# Reset cache for specific role/level
curl -X DELETE "http://localhost:8000/api/journey/reset?role=Software Engineer&level=Beginner" \
  -H "Authorization: Bearer <token>"

# Or reset all data for user
curl -X DELETE "http://localhost:8000/api/journey/reset" \
  -H "Authorization: Bearer <token>"
```

**For Development**: Temporarily disable caching in `Backend/main_orchestrator.py`:
```python
# Comment out during dev
# if cache_exists(cache_key):
#     return cached_result
```

---

### LLM Rate Limiting (Fireworks API)

**Problem**: 429 Too Many Requests or "rate limit exceeded" errors

**Solution**:

1. **Reduce token usage**:
   ```python
   # In agent configs, lower max_tokens:
   "max_tokens": 256  # Reduce from 512+
   ```

2. **Add delays between requests**:
   ```python
   import time
   time.sleep(2)  # Wait 2 seconds between calls during testing
   ```

3. **Use fewer concurrent requests**:
   - Don't run multiple interviews simultaneously
   - Test sequentially, not in parallel

4. **Contact Fireworks support** for rate limit increases if needed

**Best Practice**: Use mock responses during development:
```python
if os.getenv("ENVIRONMENT") == "test":
    return mock_mcq_response()  # Hardcoded test data
```

---

### Frontend Build & Node Issues

**Problem**: Frontend won't start or compilation errors

**Solution**:
```bash
# Module not found
npm install

# Node version mismatch
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Vite cache issues
rm -rf .vite
npm run dev

# ESLint blocking development
npm run lint -- --fix  # Auto-fix common issues
```

---

### Database Errors

**Problem**: Schema mismatches, database locked, or init failures

**Solution**:
```bash
# Reinitialize (development only!)
rm -f app.db scheduler.db

# Create fresh database
python -c "from Backend.database.db_setup import init_db; init_db()"

# Verify creation
ls -lh app.db scheduler.db
```

⚠️ **Warning**: Only do this in development. Production databases require migrations.

---

### Dependency Conflicts

**Problem**: Version conflicts between `requirements.txt` and `package.json`

**Solution**:
```bash
# Check installed versions
pip freeze | grep -E "crewai|langchain|fastapi"

# Upgrade pip first
pip install --upgrade pip

# Reinstall all requirements
pip install -r requirements.txt --ignore-requires-python --upgrade

# For Node
npm update
npm cache clean --force
npm install
```

---

## 🐛 Reporting Issues

### Before Reporting

1. Check existing issues for duplicates
2. Try the solutions in "Development Issues & Solutions" above
3. Gather debugging info

### Issue Template

```markdown
## Environment
- OS: macOS 14.2 / Ubuntu 22.04 / Windows 11
- Python: 3.11.2
- Node: 18.16.0
- Browser: Chrome 120 (if frontend issue)

## Describe the Bug
Clear, concise description of the problem.

## Steps to Reproduce
1. Do this
2. Then this
3. See error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happened.

## Logs/Screenshots
```bash
Error output here
```

## Possible Cause
Any theories on what went wrong.
```

---

## 📞 Communication

- **Questions?** → [GitHub Discussions](https://github.com/ermadanvk-afk/ACT-II-Hackathon-AMD/discussions)
- **Found a bug?** → [GitHub Issues](https://github.com/ermadanvk-afk/ACT-II-Hackathon-AMD/issues)
- **Have a fix?** → [GitHub Pull Requests](https://github.com/ermadanvk-afk/ACT-II-Hackathon-AMD/pulls)

**Be respectful and constructive in all interactions.**

---

## 🎓 Learning Resources

- **CrewAI**: https://docs.crewai.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **SQLite**: https://www.sqlite.org/docs.html
- **Fireworks API**: https://readme.fireworks.ai/
- **Project Architecture**: See [README.md](./README.md)

---

## 📜 License

By contributing, you agree your work will be licensed under the MIT License. See [LICENSE](./LICENSE).

---

## 🙏 Thank You!

Your contributions directly impact students preparing for technical interviews. Whether you're fixing bugs, adding features, or improving docs—**you're helping people achieve their career goals!**

**Happy coding! 🚀**
