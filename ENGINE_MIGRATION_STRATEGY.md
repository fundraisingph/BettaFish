# Engine Migration Strategy for BettaFish

## Overview

This document outlines the migration strategy for each specialized engine (Insight, Media, Query, Report) from the current Flask-based system to the new FastAPI architecture. The migration will be done incrementally to maintain system functionality throughout the transition.

## Migration Principles

1. **Incremental Migration**: Migrate engines one at a time to minimize disruption
2. **Backward Compatibility**: Maintain existing functionality during transition
3. **Parallel Operation**: Run both old and new systems during migration
4. **Data Consistency**: Ensure data integrity across migration phases
5. **Performance Optimization**: Improve performance with each migration

## Engine Migration Phases

### Phase 1: InsightEngine Migration (Weeks 1-2)

#### Current Architecture Analysis
- **Location**: `InsightEngine/` directory
- **Components**: Agent, LLMs, Nodes, Tools, Utils
- **Functionality**: Database mining, sentiment analysis, keyword optimization
- **Dependencies**: SQLAlchemy, sentiment analysis models, database connections

#### Migration Strategy

##### 1. Database Layer Migration
```python
# New database access using Prisma
# backend/engines/insight/database.py
from backend.core.database import get_prisma
from backend.models.insight import InsightSearch, InsightResult

class InsightDatabase:
    def __init__(self):
        self.prisma = get_prisma()
    
    async def search_social_media(self, query: str, platforms: List[str]) -> List[InsightSearch]:
        """Search social media data using Prisma"""
        return await self.prisma.insightsearch.find_many(
            where={
                "query": {"contains": query},
                "platform": {"in": platforms},
                "isActive": True
            },
            include={"results": True}
        )
    
    async def save_search_result(self, search_data: dict) -> InsightSearch:
        """Save search result to database"""
        return await self.prisma.insightsearch.create(
            data=search_data
        )
    
    async def analyze_sentiment(self, content: str) -> dict:
        """Analyze sentiment using integrated models"""
        # Use existing sentiment analysis logic
        # but save results using Prisma
        pass
```

##### 2. Agent Migration
```python
# backend/engines/insight/agent.py
from typing import Dict, List, Optional
from datetime import datetime

from backend.core.database import get_prisma
from backend.models.insight import InsightAgentConfig
from backend.services.llm_service import LLMService
from backend.services.websocket_manager import manager

class InsightAgent:
    def __init__(self, config: InsightAgentConfig):
        self.config = config
        self.prisma = get_prisma()
        self.llm_service = LLMService(config.llmProvider)
        self.status = "idle"
    
    async def start_analysis(self, query: str, user_id: str) -> str:
        """Start insight analysis"""
        # Create analysis task
        task = await self.prisma.analysistask.create({
            "userId": user_id,
            "query": query,
            "agentType": "insight",
            "status": "running"
        })
        
        # Update agent status
        await self._update_status("running")
        
        # Send status update via WebSocket
        await manager.broadcast_agent_log("insight", {
            "level": "info",
            "message": f"Starting analysis for query: {query}",
            "timestamp": datetime.utcnow().isoformat(),
            "taskId": task.id
        })
        
        # Start analysis process
        await self._perform_analysis(task.id, query)
        
        return task.id
    
    async def _perform_analysis(self, task_id: str, query: str):
        """Perform the actual analysis"""
        try:
            # Step 1: Keyword optimization
            optimized_keywords = await self._optimize_keywords(query)
            await manager.broadcast_agent_log("insight", {
                "level": "info",
                "message": f"Optimized keywords: {', '.join(optimized_keywords)}",
                "timestamp": datetime.utcnow().isoformat(),
                "taskId": task_id
            })
            
            # Step 2: Database search
            search_results = await self._search_database(optimized_keywords)
            await manager.broadcast_agent_log("insight", {
                "level": "info",
                "message": f"Found {len(search_results)} search results",
                "timestamp": datetime.utcnow().isoformat(),
                "taskId": task_id
            })
            
            # Step 3: Sentiment analysis
            sentiment_results = await self._analyze_sentiment(search_results)
            await manager.broadcast_agent_log("insight", {
                "level": "info",
                "message": f"Analyzed sentiment for {len(sentiment_results)} items",
                "timestamp": datetime.utcnow().isoformat(),
                "taskId": task_id
            })
            
            # Step 4: Generate summary
            summary = await self._generate_summary(query, search_results, sentiment_results)
            
            # Step 5: Save results
            await self._save_results(task_id, {
                "keywords": optimized_keywords,
                "search_results": search_results,
                "sentiment_analysis": sentiment_results,
                "summary": summary
            })
            
            # Update task status
            await self.prisma.analysistask.update(
                where={"id": task_id},
                data={"status": "completed"}
            )
            
            await manager.broadcast_agent_log("insight", {
                "level": "info",
                "message": "Analysis completed successfully",
                "timestamp": datetime.utcnow().isoformat(),
                "taskId": task_id
            })
            
        except Exception as e:
            await self._handle_error(task_id, str(e))
        finally:
            await self._update_status("idle")
    
    async def _optimize_keywords(self, query: str) -> List[str]:
        """Optimize search keywords using LLM"""
        prompt = f"""
        Optimize the following search query for social media analysis:
        Query: {query}
        
        Provide 5-10 optimized keywords that will yield the best results.
        Return as a JSON array of strings.
        """
        
        response = await self.llm_service.generate_completion(prompt)
        # Parse and return keywords
        pass
    
    async def _search_database(self, keywords: List[str]) -> List[dict]:
        """Search database using optimized keywords"""
        results = []
        for keyword in keywords:
            # Use existing search logic but with Prisma
            search_results = await self.prisma.socialmediapost.find_many(
                where={
                    "content": {"contains": keyword},
                    "isActive": True
                },
                take=100
            )
            results.extend(search_results)
        return results
    
    async def _analyze_sentiment(self, search_results: List[dict]) -> List[dict]:
        """Analyze sentiment for search results"""
        # Use existing sentiment analysis logic
        # but save results using Prisma
        pass
    
    async def _generate_summary(self, query: str, search_results: List[dict], sentiment_results: List[dict]) -> str:
        """Generate analysis summary"""
        prompt = f"""
        Generate a comprehensive summary for the following social media analysis:
        Query: {query}
        Search Results: {len(search_results)} items
        Sentiment Analysis: {sentiment_results}
        
        Provide insights, trends, and key findings.
        """
        
        response = await self.llm_service.generate_completion(prompt)
        return response.content
    
    async def _save_results(self, task_id: str, results: dict):
        """Save analysis results to database"""
        await self.prisma.analysisresult.create({
            "taskId": task_id,
            "agentType": "insight",
            "results": results
        })
    
    async def _handle_error(self, task_id: str, error_message: str):
        """Handle analysis errors"""
        await self.prisma.analysistask.update(
            where={"id": task_id},
            data={
                "status": "failed",
                "errorMessage": error_message
            }
        )
        
        await manager.broadcast_agent_log("insight", {
            "level": "error",
            "message": f"Analysis failed: {error_message}",
            "timestamp": datetime.utcnow().isoformat(),
            "taskId": task_id
        })
    
    async def _update_status(self, status: str):
        """Update agent status"""
        self.status = status
        await self.prisma.agent.update(
            where={"type": "insight"},
            data={"status": status}
        )
```

##### 3. API Integration
```python
# backend/api/engines/insight.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from backend.core.database import get_prisma
from backend.models.insight import InsightRequest, InsightResponse
from backend.services.auth_service import get_current_user
from backend.engines.insight.agent import InsightAgent

router = APIRouter(prefix="/engines/insight", tags=["insight"])

@router.post("/analyze", response_model=InsightResponse)
async def analyze_insight(
    request: InsightRequest,
    user: dict = Depends(get_current_user),
    prisma = Depends(get_prisma)
):
    """Start insight analysis"""
    # Get agent configuration
    agent_config = await prisma.agent.find_unique(where={"type": "insight"})
    if not agent_config:
        raise HTTPException(status_code=404, detail="Insight agent not found")
    
    # Create agent instance
    agent = InsightAgent(agent_config)
    
    # Start analysis
    task_id = await agent.start_analysis(request.query, user["id"])
    
    return InsightResponse(
        taskId=task_id,
        status="started",
        message="Insight analysis started"
    )

@router.get("/status/{task_id}")
async def get_insight_status(
    task_id: str,
    user: dict = Depends(get_current_user),
    prisma = Depends(get_prisma)
):
    """Get insight analysis status"""
    task = await prisma.analysistask.find_first(
        where={
            "id": task_id,
            "userId": user["id"],
            "agentType": "insight"
        }
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "taskId": task_id,
        "status": task.status,
        "createdAt": task.createdAt,
        "updatedAt": task.updatedAt,
        "errorMessage": task.errorMessage
    }

@router.get("/results/{task_id}")
async def get_insight_results(
    task_id: str,
    user: dict = Depends(get_current_user),
    prisma = Depends(get_prisma)
):
    """Get insight analysis results"""
    task = await prisma.analysistask.find_first(
        where={
            "id": task_id,
            "userId": user["id"],
            "agentType": "insight"
        }
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    result = await prisma.analysisresult.find_first(
        where={
            "taskId": task_id,
            "agentType": "insight"
        }
    )
    
    return result.results if result else None
```

### Phase 2: MediaEngine Migration (Weeks 3-4)

#### Migration Strategy

##### 1. Web Search Integration
```python
# backend/engines/media/web_search.py
from typing import List, Dict, Any
from datetime import datetime

from backend.services.search_service import SearchService
from backend.models.media import MediaSearchConfig

class MediaWebSearch:
    def __init__(self, config: MediaSearchConfig):
        self.config = config
        self.search_service = SearchService()
    
    async def search_web(self, query: str, time_range: str = "24h") -> List[dict]:
        """Perform web search with multiple providers"""
        results = []
        
        # Use configured search providers
        for provider in self.config.providers:
            try:
                provider_results = await self.search_service.search(
                    provider=provider,
                    query=query,
                    time_range=time_range,
                    max_results=self.config.maxResults
                )
                results.extend(provider_results)
            except Exception as e:
                # Log error but continue with other providers
                pass
        
        # Deduplicate and rank results
        return self._process_results(results)
    
    def _process_results(self, results: List[dict]) -> List[dict]:
        """Process and rank search results"""
        # Implement deduplication and ranking logic
        pass
```

##### 2. Multimodal Analysis
```python
# backend/engines/media/multimodal_analyzer.py
from typing import List, Dict, Any
from datetime import datetime

from backend.services.llm_service import LLMService
from backend.services.image_service import ImageService
from backend.services.websocket_manager import manager

class MediaMultimodalAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.llm_service = LLMService(config["llm_provider"])
        self.image_service = ImageService()
    
    async def analyze_content(self, search_results: List[dict]) -> List[dict]:
        """Analyze multimodal content from search results"""
        analyzed_results = []
        
        for result in search_results:
            analyzed_result = await self._analyze_single_result(result)
            analyzed_results.append(analyzed_result)
        
        return analyzed_results
    
    async def _analyze_single_result(self, result: dict) -> dict:
        """Analyze a single search result"""
        analysis = {
            "original_result": result,
            "text_analysis": None,
            "image_analysis": None,
            "video_analysis": None,
            "overall_sentiment": None
        }
        
        # Text analysis
        if result.get("content"):
            analysis["text_analysis"] = await self._analyze_text(result["content"])
        
        # Image analysis
        if result.get("images"):
            analysis["image_analysis"] = await self._analyze_images(result["images"])
        
        # Video analysis
        if result.get("videos"):
            analysis["video_analysis"] = await self._analyze_videos(result["videos"])
        
        # Overall sentiment
        analysis["overall_sentiment"] = self._calculate_overall_sentiment(analysis)
        
        return analysis
    
    async def _analyze_text(self, text: str) -> dict:
        """Analyze text content"""
        prompt = f"""
        Analyze the following text content:
        Text: {text}
        
        Provide:
        1. Sentiment analysis (positive, negative, neutral)
        2. Key topics mentioned
        3. Emotional tone
        4. Overall summary
        
        Return as JSON.
        """
        
        response = await self.llm_service.generate_completion(prompt)
        # Parse and return analysis
        pass
    
    async def _analyze_images(self, images: List[str]) -> dict:
        """Analyze image content"""
        # Use image analysis service
        pass
    
    async def _analyze_videos(self, videos: List[str]) -> dict:
        """Analyze video content"""
        # Use video analysis service
        pass
    
    def _calculate_overall_sentiment(self, analysis: dict) -> str:
        """Calculate overall sentiment from all analyses"""
        # Implement sentiment calculation logic
        pass
```

### Phase 3: QueryEngine Migration (Weeks 5-6)

#### Migration Strategy

##### 1. Query Optimization
```python
# backend/engines/query/query_optimizer.py
from typing import List, Dict, Any
from datetime import datetime

from backend.services.llm_service import LLMService
from backend.models.query import QueryOptimizationConfig

class QueryOptimizer:
    def __init__(self, config: QueryOptimizationConfig):
        self.config = config
        self.llm_service = LLMService(config.llmProvider)
    
    async def optimize_query(self, original_query: str, context: dict = None) -> List[str]:
        """Optimize query for better search results"""
        prompt = f"""
        Optimize the following search query for precise information retrieval:
        Original Query: {original_query}
        Context: {context or 'No specific context'}
        
        Provide 3-5 optimized queries that will yield the most relevant and precise results.
        Consider:
        1. Different phrasing and synonyms
        2. Specific technical terms
        3. Temporal aspects
        4. Geographic considerations
        5. Domain-specific terminology
        
        Return as a JSON array of strings.
        """
        
        response = await self.llm_service.generate_completion(prompt)
        # Parse and return optimized queries
        pass
    
    async def rank_results(self, query: str, results: List[dict]) -> List[dict]:
        """Rank search results by relevance"""
        prompt = f"""
        Rank the following search results by relevance to the query:
        Query: {query}
        Results: {results}
        
        Consider:
        1. Direct relevance to query
        2. Information quality and accuracy
        3. Source credibility
        4. Recency and timeliness
        5. Comprehensiveness
        
        Return as a JSON array with relevance scores (0-1).
        """
        
        response = await self.llm_service.generate_completion(prompt)
        # Parse and return ranked results
        pass
```

### Phase 4: ReportEngine Migration (Weeks 7-8)

#### Migration Strategy

##### 1. Report Generation
```python
# backend/engines/report/report_generator.py
from typing import List, Dict, Any
from datetime import datetime

from backend.services.llm_service import LLMService
from backend.services.template_service import TemplateService
from backend.services.pdf_service import PDFService
from backend.models.report import ReportConfig

class ReportGenerator:
    def __init__(self, config: ReportConfig):
        self.config = config
        self.llm_service = LLMService(config.llmProvider)
        self.template_service = TemplateService()
        self.pdf_service = PDFService()
    
    async def generate_report(self, task_id: str, analysis_results: Dict[str, Any]) -> dict:
        """Generate comprehensive report from analysis results"""
        # Select appropriate template
        template = await self._select_template(analysis_results)
        
        # Generate report structure
        report_structure = await self._generate_structure(analysis_results, template)
        
        # Generate content for each section
        report_content = await self._generate_content(report_structure, analysis_results)
        
        # Create intermediate representation
        ir = await self._create_intermediate_representation(report_content)
        
        # Render HTML report
        html_report = await self._render_html_report(ir, template)
        
        # Generate PDF if requested
        pdf_report = await self._generate_pdf_report(html_report) if self.config.generatePdf else None
        
        # Save report to database
        report = await self._save_report(task_id, {
            "template": template,
            "structure": report_structure,
            "content": report_content,
            "ir": ir,
            "html": html_report,
            "pdf": pdf_report
        })
        
        return report
    
    async def _select_template(self, analysis_results: Dict[str, Any]) -> str:
        """Select appropriate report template based on analysis results"""
        prompt = f"""
        Select the most appropriate report template for the following analysis results:
        Analysis Results: {analysis_results}
        
        Available Templates:
        1. executive_summary - For business executives
        2. technical_analysis - For technical teams
        3. public_opinion - For public opinion analysis
        4. market_research - For market research reports
        5. crisis_management - For crisis situations
        
        Consider the content type, audience, and purpose.
        Return the template name as a string.
        """
        
        response = await self.llm_service.generate_completion(prompt)
        return response.content.strip()
    
    async def _generate_structure(self, analysis_results: Dict[str, Any], template: str) -> dict:
        """Generate report structure based on template and analysis results"""
        # Get template structure
        template_structure = await self.template_service.get_template_structure(template)
        
        # Customize structure based on analysis results
        # Add or remove sections as needed
        
        return template_structure
    
    async def _generate_content(self, structure: dict, analysis_results: Dict[str, Any]) -> dict:
        """Generate content for each report section"""
        content = {}
        
        for section in structure["sections"]:
            section_content = await self._generate_section_content(section, analysis_results)
            content[section["id"]] = section_content
        
        return content
    
    async def _generate_section_content(self, section: dict, analysis_results: Dict[str, Any]) -> str:
        """Generate content for a specific section"""
        prompt = f"""
        Generate content for the following report section:
        Section: {section}
        Analysis Results: {analysis_results}
        
        Follow these guidelines:
        1. Be comprehensive and detailed
        2. Use data from the analysis results
        3. Provide insights and interpretations
        4. Maintain professional tone
        5. Include relevant statistics and metrics
        
        Return as markdown content.
        """
        
        response = await self.llm_service.generate_completion(prompt)
        return response.content
    
    async def _create_intermediate_representation(self, content: dict) -> dict:
        """Create intermediate representation for rendering"""
        ir = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "version": "1.0",
                "format": "ir_v1"
            },
            "content": content
        }
        
        return ir
    
    async def _render_html_report(self, ir: dict, template: str) -> str:
        """Render HTML report from intermediate representation"""
        # Use template service to render HTML
        return await self.template_service.render_html(ir, template)
    
    async def _generate_pdf_report(self, html_report: str) -> bytes:
        """Generate PDF report from HTML"""
        return await self.pdf_service.generate_pdf(html_report)
    
    async def _save_report(self, task_id: str, report_data: dict) -> dict:
        """Save report to database"""
        # Use Prisma to save report
        pass
```

## Migration Timeline

### Week 1-2: InsightEngine
- Database layer migration
- Agent implementation
- API integration
- Testing and validation

### Week 3-4: MediaEngine
- Web search integration
- Multimodal analysis
- API integration
- Testing and validation

### Week 5-6: QueryEngine
- Query optimization
- Result ranking
- API integration
- Testing and validation

### Week 7-8: ReportEngine
- Report generation
- Template system
- PDF generation
- Testing and validation

## Testing Strategy

### Unit Testing
- Test each engine component independently
- Mock external dependencies
- Validate data transformations

### Integration Testing
- Test engine interactions with database
- Test WebSocket communication
- Test API endpoints

### End-to-End Testing
- Test complete analysis workflows
- Test report generation
- Test real-time updates

## Rollback Strategy

### Immediate Rollback
- Switch back to Flask system if critical issues arise
- Preserve data consistency
- Minimize downtime

### Gradual Rollback
- Roll back specific engines while keeping others
- Maintain partial functionality
- Address issues incrementally

## Performance Monitoring

### Metrics to Track
- Response times
- Error rates
- Resource usage
- User satisfaction

### Alerting
- Set up alerts for critical issues
- Monitor system health
- Automated rollback triggers

This migration strategy ensures a smooth transition from Flask to FastAPI while maintaining system functionality and improving performance throughout the process.