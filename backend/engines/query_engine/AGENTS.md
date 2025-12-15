# QueryEngine - Precise Information Search

## Package Identity
QueryEngine is precise information search and query optimization agent of BettaFish multi-agent system. It specializes in advanced search query formulation, result ranking and filtering, and cross-platform information synthesis.

Primary tech/framework: Python with Streamlit UI, advanced search algorithms, and integration with multiple search providers for comprehensive information retrieval.

## Setup & Run
```bash
# Start QueryEngine standalone
streamlit run SingleEngineApp/query_engine_streamlit_app.py --server.port 8503

# Or start via main system
python app.py  # Then start QueryEngine through web UI
```

## Patterns & Conventions

### File Organization
- `agent.py` - Main agent implementation with DeepSearchAgent class
- `llms/` - LLM interface abstractions for query optimization
- `nodes/` - Processing pipeline nodes (search, formatting, summary, etc.)
- `tools/` - Search optimization and result processing tools
- `utils/` - Text processing and query optimization utilities
- `state/` - Agent state management and persistence
- `prompts/` - LLM prompt templates for query formulation

### Query Optimization Pattern
✅ DO: Use structured query optimization:
```python
class DeepSearchAgent:
    def __init__(self, config=None):
        self.config = config or Config()
        self.query_optimizer = QueryOptimizer()
        self.result_ranker = ResultRanker()
    
    def execute_search(self, query: str):
        # 1. Optimize query for better results
        optimized_query = self.query_optimizer.optimize(query)
        
        # 2. Execute search across multiple sources
        raw_results = self.search_multiple_sources(optimized_query)
        
        # 3. Rank and filter results
        ranked_results = self.result_ranker.rank(raw_results)
        
        # 4. Synthesize information across platforms
        synthesized_info = self.synthesize_information(ranked_results)
        
        return synthesized_info
```

❌ DON'T: Use simple keyword matching without optimization:
```python
# Avoid this pattern
def simple_search(self, query):
    # Direct keyword search without optimization
    results = search_engine.search(query)
    return results
```

### Multi-Source Search Integration
✅ DO: Integrate multiple search providers:
```python
from QueryEngine.tools.search import MultiSourceSearchManager

# Example from QueryEngine/tools/search.py
class SearchManager:
    def __init__(self):
        self.primary_search = PrimarySearchProvider()
        self.secondary_search = SecondarySearchProvider()
        self.fallback_search = FallbackSearchProvider()
    
    def comprehensive_search(self, query: str):
        # Parallel search across multiple providers
        results = self.parallel_search(query)
        
        # Merge and deduplicate results
        merged_results = self.merge_results(results)
        
        # Rank by relevance and authority
        ranked_results = self.rank_by_authority(merged_results)
        
        return ranked_results
```

### Result Synthesis
✅ DO: Implement cross-platform information synthesis:
```python
from QueryEngine.tools.synthesis import InformationSynthesizer

synthesizer = InformationSynthesizer()
# Synthesize information from different sources
unified_info = synthesizer.synthesize(search_results, query)
```

## Touch Points / Key Files

- Agent implementation: `agent.py` - Core DeepSearchAgent class
- Search tools: `tools/search.py` - Multi-source search integration
- Query optimization: `tools/query_optimizer.py` - Search query enhancement
- Result processing: `tools/result_processor.py` - Result ranking and filtering
- Information synthesis: `tools/synthesis.py` - Cross-platform information integration
- Configuration: `utils/config.py` - Engine-specific settings
- State management: `state/state.py` - Agent state persistence

## JIT Index Hints

- Find search implementations: `rg -n "class.*Search" tools/search.py`
- Find query optimization: `rg -n "optimize.*query\|query.*optimization" tools/query_optimizer.py`
- Find result processing: `rg -n "rank\|filter\|process.*result" tools/result_processor.py`
- Find information synthesis: `rg -n "synthesize\|cross.*platform" tools/synthesis.py`
- Find LLM integration: `rg -n "OpenAI\|llm" llms/base.py`
- Find node implementations: `rg -n "class.*Node" nodes/`

## Common Gotchas

- Query optimization requires understanding of search provider capabilities
- Result ranking must balance relevance, recency, and authority
- Cross-platform synthesis needs proper source attribution
- Search rate limits must be respected across all providers
- Query formulation should be adapted for different search engines
- Result caching can improve performance but may affect freshness

## Pre-PR Checks

```bash
# Run QueryEngine tests
python -m pytest tests/test_query_engine.py -v

# Test search functionality
python -c "from QueryEngine.tools.search import SearchManager; SearchManager().test_providers()"

# Validate query optimization
python -c "from QueryEngine.tools.query_optimizer import QueryOptimizer; QueryOptimizer().test_optimization()"

# Test result synthesis
python -c "from QueryEngine.tools.synthesis import InformationSynthesizer; InformationSynthesizer().test_synthesis()"