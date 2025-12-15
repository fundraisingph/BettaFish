# InsightEngine - Database Mining and Sentiment Analysis

## Package Identity
InsightEngine is the database mining and sentiment analysis agent of the BettaFish multi-agent system. It specializes in extracting insights from private databases, performing multilingual sentiment analysis, and optimizing search queries using AI middleware.

Primary tech/framework: Python with Streamlit UI, SQLAlchemy for database operations, and OpenAI-compatible LLM integration.

## Setup & Run
```bash
# Start InsightEngine standalone
streamlit run SingleEngineApp/insight_engine_streamlit_app.py --server.port 8501

# Or start via main system
python app.py  # Then start InsightEngine through web UI
```

## Patterns & Conventions

### File Organization
- `agent.py` - Main agent implementation with DeepSearchAgent class
- `llms/` - LLM interface abstractions and OpenAI-compatible clients
- `nodes/` - Processing pipeline nodes (search, formatting, summary, etc.)
- `tools/` - Specialized tools for database operations and sentiment analysis
- `utils/` - Database connections, text processing utilities
- `state/` - Agent state management and persistence
- `prompts/` - LLM prompt templates for various operations

### Agent Implementation Pattern
✅ DO: Follow the established agent structure:
```python
class DeepSearchAgent:
    def __init__(self, config=None):
        self.config = config or Config()
        self.state = AgentState()
        self.search_tool = DatabaseSearchTool()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def execute_search(self, query: str):
        # Implementation following node-based pipeline
        pass
```

❌ DON'T: Direct LLM calls without proper abstraction:
```python
# Avoid this pattern
from openai import OpenAI
client = OpenAI(api_key="...")
response = client.chat.completions.create(...)
```

### Database Operations
✅ DO: Use the database utility for all operations:
```python
from InsightEngine.utils.db import get_db_session
from InsightEngine.tools.search import search_topic_globally

# Example from InsightEngine/tools/search.py
def search_topic_globally(topic: str, limit: int = 100):
    with get_db_session() as session:
        # Database operations using SQLAlchemy ORM
        pass
```

### Sentiment Analysis Integration
✅ DO: Use the sentiment analyzer tool:
```python
from InsightEngine.tools.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
results = analyzer.analyze_batch(texts, model_type='multilingual')
```

## Touch Points / Key Files

- Agent implementation: `agent.py` - Core DeepSearchAgent class
- Database utilities: `utils/db.py` - SQLAlchemy session management
- Search tools: `tools/search.py` - Database search operations
- Sentiment analysis: `tools/sentiment_analyzer.py` - Multilingual sentiment analysis
- Configuration: `utils/config.py` - Engine-specific settings
- State management: `state/state.py` - Agent state persistence

## JIT Index Hints

- Find search operations: `rg -n "def.*search" tools/search.py`
- Find sentiment analysis: `rg -n "class.*Sentiment" tools/sentiment_analyzer.py`
- Find LLM integration: `rg -n "OpenAI\|openai" llms/base.py`
- Find node implementations: `rg -n "class.*Node" nodes/`
- Find database models: `rg -n "class.*\(.*Model\)" ../MindSpider/schema/`

## Common Gotchas

- Database connections must be context-managed with `get_db_session()`
- Sentiment analysis models require proper initialization before first use
- Search results must be limited to prevent LLM context overflow
- All LLM calls should go through the base LLM class for consistency

## Pre-PR Checks

```bash
# Run InsightEngine tests
python -m pytest tests/test_insight_engine.py -v

# Check database connectivity
python -c "from InsightEngine.utils.db import test_connection; test_connection()"

# Validate sentiment analysis models
python -c "from InsightEngine.tools.sentiment_analyzer import SentimentAnalyzer; SentimentAnalyzer().test_models()"