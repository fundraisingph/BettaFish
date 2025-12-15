# BettaFish Multi-Agent System

## Project Snapshot
BettaFish is a multi-agent public opinion analysis system built with Python Flask orchestrator, specialized analysis engines (Insight, Media, Query, Report), and a Next.js frontend. The system analyzes 30+ social media platforms using parallel agent execution with forum-based collaboration.

## Root Setup Commands
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install

# Start database (Docker)
docker-compose up db -d

# Start main system
python app.py

# Start frontend (development)
cd frontend && npm run dev

# Run tests
python tests/run_tests.py
```

## Universal Conventions
- **Multi-Agent Architecture**: Each engine (Insight, Media, Query, Report) operates independently with shared coordination
- **Flask Orchestrator**: Central coordination via `app.py` with SocketIO for real-time communication
- **Configuration Management**: All settings via Pydantic in `config.py` with `.env` file support
- **Log-Based Communication**: Agents communicate through structured logs monitored by ForumEngine
- **Async Processing**: Use non-blocking I/O throughout the system for performance

## Security & Secrets
- Never commit API keys or tokens to repository
- All secrets stored in `.env` file (see `.env.example` for template)
- Database credentials managed through environment variables
- LLM provider keys configured per engine in config

## JIT Index - Directory Map

### Core System Components
- **Flask Orchestrator**: `app.py` → Main application with SocketIO real-time communication
- **Configuration**: `config.py` → Pydantic-based settings management
- **Frontend**: `frontend/` → [see frontend/AGENTS.md](frontend/AGENTS.md) Next.js application

### Analysis Engines
- **InsightEngine**: `InsightEngine/` → [see InsightEngine/AGENTS.md](InsightEngine/AGENTS.md) Database mining and sentiment analysis
- **MediaEngine**: `MediaEngine/` → [see MediaEngine/AGENTS.md](MediaEngine/AGENTS.md) Multimodal content analysis with web search
- **QueryEngine**: `QueryEngine/` → [see QueryEngine/AGENTS.md](QueryEngine/AGENTS.md) Precise information search and query optimization
- **ReportEngine**: `ReportEngine/` → [see ReportEngine/AGENTS.md](ReportEngine/AGENTS.md) Intelligent report generation from all agent outputs

### Supporting Systems
- **ForumEngine**: `ForumEngine/` → [see ForumEngine/AGENTS.md](ForumEngine/AGENTS.md) Agent collaboration mechanism
- **MindSpider**: `MindSpider/` → [see MindSpider/AGENTS.md](MindSpider/AGENTS.md) Social media crawling system
- **SentimentAnalysis**: `SentimentAnalysisModel/` → [see SentimentAnalysisModel/AGENTS.md](SentimentAnalysisModel/AGENTS.md) Sentiment analysis models

### Single Engine Apps
- **Streamlit Apps**: `SingleEngineApp/` → Individual Streamlit applications for each engine

### Quick Find Commands
- Search for Flask routes: `rg -n "@app.route" app.py`
- Find agent implementations: `rg -n "class.*Agent" */agent.py`
- Find configuration settings: `rg -n "Field\(" config.py`
- Find database models: `rg -n "class.*\(.*Model\)" MindSpider/schema/models_*.py`
- Find API endpoints: `rg -n "def.*api" app.py`

## Definition of Done
- All engines start successfully and communicate via ForumEngine
- Database connections established with proper migrations
- Frontend connects to Flask backend via WebSocket
- Reports generate correctly with HTML/PDF output
- Tests pass for core functionality