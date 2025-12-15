# BettaFish System Architecture

## System Architecture

BettaFish is built as a multi-agent public opinion analysis system with a Flask-based orchestration layer. The architecture prioritizes modularity, real-time communication, and scalable agent coordination.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   Multi-Agent    │    │   External      │
│   (Orchestrator) │◄──►│   System         │◄──►│   Services      │
│   Port: 5000    │    │   (4 Engines)     │    │   (OpenAI, etc) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Report Engine  │    │   MindSpider     │
│   Database      │    │   (Aggregator)   │    │   (Crawler)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Flask Orchestrator (app.py)
- **Main Application**: Flask server with SocketIO for real-time communication
- **Process Management**: Manages lifecycle of Streamlit applications for each agent
- **API Gateway**: RESTful endpoints for system control and configuration
- **Real-time Updates**: WebSocket-based streaming of logs and progress

### 2. Multi-Agent System

#### InsightEngine
- **Purpose**: Private database mining and sentiment analysis
- **Agent Class**: `DeepSearchAgent` in `InsightEngine/agent.py`
- **Key Capabilities**:
  - Database search across multiple platforms
  - Keyword optimization with Qwen middleware
  - Multilingual sentiment analysis (22 languages)
  - Clustering and sampling of search results
  - Reflection-based iterative research

#### MediaEngine
- **Purpose**: Multimodal content analysis with web search
- **Agent Class**: `DeepSearchAgent` in `MediaEngine/agent.py`
- **Key Capabilities**:
  - BochaMultimodalSearch for comprehensive web search
  - AnspireAISearch for alternative search capabilities
  - Structured data extraction
  - Time-based search (24 hours, weekly)

#### QueryEngine
- **Purpose**: Precise information search and query optimization
- **Agent Class**: Similar structure to other engines
- **Key Capabilities**:
  - Advanced search query formulation
  - Result ranking and filtering
  - Cross-platform information synthesis

#### ReportEngine
- **Purpose**: Intelligent report generation from all agent outputs
- **Agent Class**: `ReportAgent` in `ReportEngine/agent.py`
- **Key Capabilities**:
  - Template selection and slicing
  - Document layout design
  - Chapter-by-chapter generation with streaming
  - HTML and PDF rendering
  - IR (Intermediate Representation) management

### 3. ForumEngine
- **Purpose**: Agent collaboration mechanism
- **Location**: `ForumEngine/monitor.py`
- **Key Capabilities**:
  - Real-time log monitoring from all agents
  - Host-guided discussions using LLM
  - Speech synthesis and moderation
  - Multi-turn conversation management

### 4. MindSpider
- **Purpose**: Social media crawling system
- **Location**: `MindSpider/main.py`
- **Key Capabilities**:
  - Broad topic extraction from news
  - Deep sentiment crawling across platforms
  - Support for 30+ social media platforms
  - Configurable crawling parameters

## Data Flow Architecture

### Analysis Workflow
1. **User Query** → Flask App receives search request
2. **Parallel Execution** → All 3 agents (Insight, Media, Query) start simultaneously
3. **Initial Research** → Each agent performs first search and summary
4. **Forum Collaboration** → ForumEngine monitors and facilitates agent discussion
5. **Iterative Deepening** → Agents perform reflection-based research cycles
6. **Report Generation** → ReportEngine aggregates all outputs and forum logs
7. **Final Output** → Interactive HTML report with optional PDF export

### Data Storage
- **PostgreSQL Database**: Stores crawled social media data
  - Tables: daily_news, daily_topics, platform-specific content
  - Managed by SQLAlchemy ORM
- **File Storage**: Markdown reports from each engine
- **Log Storage**: Real-time logs in `/logs` directory
- **Report Storage**: Final HTML/PDF reports in `/final_reports`

## Component Relationships

### Agent Communication
- **ForumEngine**: Acts as central coordinator, monitoring all agent logs
- **Shared State**: Each agent maintains independent state but shares outputs
- **Log-based Integration**: Agents communicate through structured log outputs
- **Real-time Streaming**: SocketIO enables live progress monitoring

### Report Generation Pipeline
1. **Input Collection**: Gathers Markdown outputs from all 3 engines
2. **Template Selection**: LLM chooses appropriate report template
3. **Content Structuring**: Generates document layout and chapter plan
4. **Chapter Generation**: Sequential LLM generation with streaming support
5. **IR Assembly**: Creates intermediate representation for rendering
6. **Final Rendering**: HTML generation with PDF export capability

## Technical Architecture Patterns

### Multi-Agent Coordination
- **Loose Coupling**: Agents operate independently with minimal direct dependencies
- **Event-Driven Communication**: ForumEngine monitors log events for coordination
- **Fault Tolerance**: Each agent can fail independently without affecting others

### Streaming Architecture
- **Real-time Progress**: SocketIO streams agent outputs to frontend
- **Chunked Processing**: Large reports generated in streaming fashion
- **Backpressure Handling**: Queue-based event management prevents overload

### Modular Design
- **Plugin Architecture**: Each engine is a self-contained module
- **Shared Interfaces**: Common patterns for LLM integration and state management
- **Extensible Framework**: New agents can be added following established patterns

## Key Technical Decisions

### Flask + Streamlit Architecture
- **Rationale**: Combines Flask's API capabilities with Streamlit's rich UI
- **Process Isolation**: Each agent runs in separate Streamlit process
- **Central Orchestration**: Flask app manages lifecycle and communication

### Forum-Based Collaboration
- **Innovation**: Uses log monitoring and LLM host for agent coordination
- **Scalability**: Supports dynamic agent addition/removal
- **Transparency**: All agent discussions are logged and observable

### Intermediate Representation (IR)
- **Purpose**: Decouples content generation from rendering
- **Flexibility**: Enables multiple output formats (HTML, PDF)
- **Debuggability**: Preserves generation metadata for troubleshooting

## Security Architecture

### Authentication & Authorization
- **API Key Management**: Secure storage of LLM provider credentials
- **Multi-tenancy**: User data isolation through separate databases
- **Input Validation**: Comprehensive validation using structured schemas

### Data Protection
- **Encryption**: Sensitive data encrypted at rest
- **Audit Logging**: Complete activity tracking for compliance
- **Error Handling**: Graceful degradation with detailed error reporting

## Deployment Architecture

### Containerization
- **Docker Support**: Multi-stage builds for optimization
- **Docker Compose**: Orchestrates application and database services
- **Environment Configuration**: Flexible configuration through environment variables

### Scalability Considerations
- **Horizontal Scaling**: Stateless design enables multiple instances
- **Database Optimization**: Connection pooling and query optimization
- **Resource Management**: Configurable limits for API usage and processing