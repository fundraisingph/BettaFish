# BettaFish Technology Stack

## Backend Technologies

### Core Framework
- **Flask 2.3.3**: Web framework with SocketIO for real-time communication
- **Python 3.9+**: Runtime environment
- **Eventlet 0.33.3**: Async WSGI server for SocketIO

### Database & Storage
- **PostgreSQL 15+**: Primary relational database
- **SQLAlchemy 2.0.35**: Database ORM with async support
- **AsyncPG 0.29.0**: PostgreSQL async driver
- **PyMySQL 1.1.0**: MySQL driver (alternative)
- **Cryptography 42.0.7**: Security and encryption

### AI Integration
- **OpenAI SDK 1.3.0+**: OpenAI API integration for AI functionality
- **Multiple LLM Providers**: Support for various AI providers through OpenAI-compatible APIs
- **Sentiment Analysis Models**: Multiple fine-tuned models for emotion detection

### Web & Network
- **Requests 2.31.0**: HTTP client library
- **HTTPX 0.28.1**: Async HTTP client
- **Playwright 1.45.0**: Browser automation for web crawling
- **BeautifulSoup4 4.12.0**: HTML parsing
- **SocksIO 1.0.0**: SOCKS proxy support
- **Aiofiles 23.2.1**: Async file operations
- **Aiohttp 3.8.0+**: Async HTTP server/client

### Data Processing
- **Pandas 2.0.0+**: Data manipulation and analysis
- **NumPy 1.24.0+**: Numerical computing
- **Jieba 0.42.1**: Chinese text segmentation
- **Regex 2023.8.8**: Advanced regex operations
- **Sentence-Transformers 2.2.2+**: Text embeddings and similarity
- **Scikit-learn 1.3.0+**: Machine learning algorithms

### Visualization & Reports
- **Plotly 5.17.0+**: Interactive charts and graphs
- **Matplotlib 3.9.0**: Static plotting
- **WordCloud 1.9.3**: Text visualization
- **WeasyPrint 60.0+**: HTML to PDF conversion

### Machine Learning
- **Torch 2.0.0+**: Deep learning framework (CPU version)
- **Transformers 4.30.0+**: Hugging Face transformers library
- **XGBoost 2.0.0+**: Gradient boosting framework

### Search APIs
- **Tavily Python 0.3.0+**: Web search API
- **Bocha AI Search**: Multimodal search capabilities
- **Anspire AI Search**: Alternative search provider

### Development & Deployment
- **Docker**: Container platform with multi-stage builds
- **Docker Compose**: Multi-service orchestration
- **Loguru 0.7.0+**: Structured logging
- **Pydantic 2.5.2+**: Data validation and settings management
- **Pydantic-Settings 2.2.1+**: Environment-based configuration
- **JSON-Repair 0.53.0+**: JSON parsing and repair

### Testing & Quality
- **Pytest 7.4.0+**: Testing framework
- **Black 23.0.0+**: Code formatting
- **Flake8 6.0.0+**: Linting and code quality

## Frontend Technologies

### Web Framework
- **Streamlit 1.28.1**: UI framework for agent applications
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Client-side interactivity

### UI Components
- **Custom Components**: Built with Streamlit widgets
- **Real-time Updates**: SocketIO integration for live updates
- **Responsive Design**: Mobile-friendly interface

## Infrastructure & DevOps

### Containerization
- **Multi-stage Docker builds**: Optimized image sizes
- **Python 3.11-slim**: Base image for production
- **Health checks**: Application health monitoring
- **Volume mounting**: Persistent data storage

### Database Management
- **Connection pooling**: Efficient database connections
- **Migrations**: Database schema versioning
- **Backup strategies**: Automated data backups

### Monitoring & Observability
- **Structured logging**: JSON-formatted logs with levels
- **Real-time monitoring**: Live agent status tracking
- **Error tracking**: Comprehensive error reporting
- **Performance metrics**: Resource usage monitoring

## System Architecture Patterns

### Multi-Agent System
- **Independent Processes**: Each agent runs in separate Streamlit process
- **Inter-process Communication**: SocketIO-based messaging
- **State Management**: Independent state per agent with shared coordination
- **Fault Isolation**: Agent failures don't affect other components

### Data Flow Architecture
- **Event-driven**: Real-time event propagation
- **Streaming Responses**: Progressive result delivery
- **Async Processing**: Non-blocking operations throughout
- **Queue Management**: Task queuing and load balancing

### Search & Analysis Pipeline
- **Parallel Execution**: Multiple agents work simultaneously
- **Result Aggregation**: Centralized result collection
- **Iterative Refinement**: Multi-round analysis with feedback
- **Cross-validation**: Multiple source verification

## Security & Compliance

### Data Protection
- **Encryption at rest**: Sensitive data encryption
- **Secure API communication**: HTTPS/TLS for all external calls
- **Input validation**: Comprehensive data validation
- **SQL Injection prevention**: Parameterized queries via ORM

### Authentication & Authorization
- **API Key Management**: Secure credential storage
- **Multi-tenancy**: User data isolation
- **Session Management**: Secure session handling
- **Access controls**: Role-based permissions

## Performance & Scalability

### Optimization Strategies
- **Caching**: Multi-level caching for frequently accessed data
- **Connection pooling**: Database connection optimization
- **Async operations**: Non-blocking I/O throughout the system
- **Resource limits**: Configurable limits for API usage

### Scalability Design
- **Horizontal scaling**: Stateless design enables multiple instances
- **Load balancing**: Request distribution across instances
- **Microservices architecture**: Loosely coupled services
- **Resource management**: Memory and CPU optimization

## Development Workflow

### Version Control
- **Git**: Source code management with GitHub integration
- **Branching strategy**: Feature branch development
- **Pull requests**: Code review and collaboration
- **Release management**: Tagged releases with changelogs

### Code Quality
- **Type hints**: Comprehensive type annotations
- **Documentation**: Inline and separate documentation
- **Testing**: Unit tests and integration tests
- **Code formatting**: Automated code formatting and linting

## External Integrations

### AI/LLM Providers
- **OpenAI**: GPT models and Assistant API
- **Moonshot**: Kimi models (recommended for Insight)
- **DeepSeek**: DeepSeek models (recommended for Query)
- **Google/Anspire**: Gemini models (recommended for Media)
- **SiliconFlow**: Qwen models (recommended for Forum)

### Search Services
- **Tavily**: Web search API
- **Bocha**: Multimodal search with structured data
- **Anspire**: Alternative web search provider

### Social Media Platforms
- **Weibo**: Chinese microblogging platform
- **Douyin**: Chinese short video platform
- **Xiaohongshu**: Chinese lifestyle platform
- **Bilibili**: Chinese video sharing platform
- **Zhihu**: Chinese Q&A platform
- **Tieba**: Baidu forum platform
- **30+ platforms**: Comprehensive social media coverage