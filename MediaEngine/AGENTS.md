# MediaEngine - Multimodal Content Analysis

## Package Identity
MediaEngine is the multimodal content analysis agent of the BettaFish multi-agent system. It specializes in processing and analyzing multimedia content (images, videos, audio) with advanced web search capabilities and structured data extraction.

Primary tech/framework: Python with Streamlit UI, multimodal AI processing, and integration with multiple search providers (Bocha, Anspire).

## Setup & Run
```bash
# Start MediaEngine standalone
streamlit run SingleEngineApp/media_engine_streamlit_app.py --server.port 8502

# Or start via main system
python app.py  # Then start MediaEngine through web UI
```

## Patterns & Conventions

### File Organization
- `agent.py` - Main agent implementation with DeepSearchAgent class
- `llms/` - LLM interface abstractions for multimodal content processing
- `nodes/` - Processing pipeline nodes (search, formatting, summary, etc.)
- `tools/` - Multimodal search tools and content processing utilities
- `utils/` - Text processing and content analysis utilities
- `state/` - Agent state management and persistence
- `prompts/` - LLM prompt templates for multimodal analysis

### Multimodal Processing Pattern
✅ DO: Use structured approach for multimodal content:
```python
class DeepSearchAgent:
    def __init__(self, config=None):
        self.config = config or Config()
        self.multimodal_search = BochaMultimodalSearch()
        self.content_processor = MultimodalProcessor()
    
    def analyze_multimodal_content(self, query: str):
        # Process text, images, videos in unified pipeline
        search_results = self.multimodal_search.search(query)
        processed_content = self.content_processor.process(search_results)
        return self.generate_summary(processed_content)
```

❌ DON'T: Handle different media types separately without integration:
```python
# Avoid this pattern
def analyze_images(self, images):
    # Separate image processing without context
    pass

def analyze_text(self, text):
    # Separate text processing without multimodal context
    pass
```

### Search Tool Integration
✅ DO: Use multiple search providers with fallback:
```python
from MediaEngine.tools.search import BochaMultimodalSearch, AnspireAISearch

# Example from MediaEngine/tools/search.py
class SearchManager:
    def __init__(self):
        self.primary_search = BochaMultimodalSearch()
        self.fallback_search = AnspireAISearch()
    
    def search_with_fallback(self, query: str):
        try:
            return self.primary_search.search(query)
        except SearchError:
            return self.fallback_search.search(query)
```

### Time-based Search
✅ DO: Implement time-based search capabilities:
```python
from MediaEngine.tools.search import TimeBasedSearch

searcher = TimeBasedSearch()
# Search recent 24 hours
recent_results = searcher.search(query, time_range="24h")
# Search weekly trends
weekly_results = searcher.search(query, time_range="weekly")
```

## Touch Points / Key Files

- Agent implementation: `agent.py` - Core DeepSearchAgent class for multimodal analysis
- Search tools: `tools/search.py` - Bocha and Anspire search integration
- Text processing: `utils/text_processing.py` - Content analysis and extraction
- Configuration: `utils/config.py` - Engine-specific settings for search limits and providers
- LLM integration: `llms/base.py` - Multimodal LLM interface
- State management: `state/state.py` - Agent state persistence

## JIT Index Hints

- Find search implementations: `rg -n "class.*Search" tools/search.py`
- Find multimodal processing: `rg -n "def.*multimodal\|def.*process.*content" utils/`
- Find time-based search: `rg -n "time_range\|24h\|weekly" tools/search.py`
- Find LLM integration: `rg -n "OpenAI\|multimodal\|vision" llms/base.py`
- Find node implementations: `rg -n "class.*Node" nodes/`
- Find structured data extraction: `rg -n "extract.*structured\|parse.*data" utils/`

## Common Gotchas

- Multimodal search requires API keys for both Bocha and Anspire services
- Content processing must handle different media formats gracefully
- Search results should be deduplicated across providers
- Time-based searches require proper timezone handling
- Large media files need to be processed in chunks to avoid memory issues

## Pre-PR Checks

```bash
# Run MediaEngine tests
python -m pytest tests/test_media_engine.py -v

# Test multimodal search functionality
python -c "from MediaEngine.tools.search import BochaMultimodalSearch; BochaMultimodalSearch().test_connection()"

# Validate content processing
python -c "from MediaEngine.utils.text_processing import MultimodalProcessor; MultimodalProcessor().test_processors()"