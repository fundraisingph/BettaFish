# MindSpider - Social Media Crawling System

## Package Identity
MindSpider is the social media crawling system of BettaFish multi-agent platform. It extracts trending topics from news sources and performs deep sentiment crawling across 30+ social media platforms including Weibo, Douyin, Xiaohongshu, Bilibili, Zhihu, and Tieba.

Primary tech/framework: Python with Playwright for browser automation, SQLAlchemy for database operations, and platform-specific crawlers with configurable parameters.

## Setup & Run
```bash
# Initialize MindSpider
cd MindSpider
python main.py --setup

# Run topic extraction (get hot topics from news)
python main.py --broad-topic

# Run complete crawling workflow
python main.py --complete --date 2024-01-20

# Run specific platforms only
python main.py --deep-sentiment --platforms xhs dy wb
```

## Patterns & Conventions

### File Organization
- `main.py` - Main entry point with CLI interface
- `config.py.example` - Configuration template for crawling parameters
- `BroadTopicExtraction/` - Topic extraction from news sources
- `DeepSentimentCrawling/` - Deep sentiment analysis crawling
- `DeepSentimentCrawling/MediaCrawler/` - Core crawler implementation
- `schema/` - Database models and schema definitions

### Crawling Architecture
✅ DO: Use structured crawling approach:
```python
# Example from MindSpider/DeepSentimentCrawling/platform_crawler.py
class PlatformCrawler:
    def __init__(self, platform_config):
        self.config = platform_config
        self.browser = None
        self.data_extractor = DataExtractor()
    
    def crawl_platform(self, keywords: list, date_range: str):
        # 1. Initialize browser with proper settings
        self.initialize_browser()
        
        # 2. Search for content using keywords
        search_results = self.search_content(keywords)
        
        # 3. Extract structured data
        structured_data = self.data_extractor.extract(search_results)
        
        # 4. Store to database
        self.store_to_database(structured_data)
        
        # 5. Clean up resources
        self.cleanup()
        
        return structured_data
```

❌ DON'T: Use direct HTTP requests without browser automation:
```python
# Avoid this pattern
def simple_crawl(self, url):
    # Direct requests without proper browser handling
    response = requests.get(url)
    return response.text
```

### Platform-Specific Configuration
✅ DO: Use platform-specific configurations:
```python
# Example from MindSpider/DeepSentimentCrawling/MediaCrawler/config/weibo_config.py
class WeiboConfig:
    PLATFORM_NAME = "weibo"
    BASE_URL = "https://s.weibo.com"
    SEARCH_URL = "https://s.weibo.com/weibo"
    
    # Browser settings
    HEADLESS = True
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Crawling limits
    MAX_PAGES = 10
    MAX_COMMENTS_PER_POST = 100
    
    # Selectors for data extraction
    SELECTORS = {
        'post_container': '.card-wrap',
        'post_content': '.content',
        'post_time': '.time',
        'comments': '.comment-list'
    }
```

### Database Integration
✅ DO: Use SQLAlchemy models for data persistence:
```python
# Example from MindSpider/schema/models_sa.py
class DailyTopic(Base):
    __tablename__ = 'daily_topics'
    
    id = Column(Integer, primary_key=True)
    topic = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    platform = Column(String(50), nullable=False)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Usage in crawler
def store_topic_data(self, topic_data):
    with get_db_session() as session:
        topic = DailyTopic(
            topic=topic_data['topic'],
            date=topic_data['date'],
            platform=topic_data['platform'],
            sentiment_score=topic_data['sentiment']
        )
        session.add(topic)
        session.commit()
```

## Touch Points / Key Files

- Main entry point: `main.py` - CLI interface and workflow orchestration
- Platform crawler: `DeepSentimentCrawling/platform_crawler.py` - Multi-platform crawling logic
- Topic extraction: `BroadTopicExtraction/topic_extractor.py` - News topic extraction
- Database models: `schema/models_sa.py` - SQLAlchemy ORM models
- Platform configs: `DeepSentimentCrawling/MediaCrawler/config/` - Platform-specific settings
- Database manager: `schema/db_manager.py` - Database connection and operations

## JIT Index Hints

- Find crawler implementations: `rg -n "class.*Crawler" DeepSentimentCrawling/MediaCrawler/media_platform/`
- Find platform configurations: `rg -n "class.*Config" DeepSentimentCrawling/MediaCrawler/config/`
- Find database models: `rg -n "class.*\(.*Base\)" schema/`
- Find topic extraction: `rg -n "extract.*topic\|topic.*extract" BroadTopicExtraction/`
- Find CLI commands: `rg -n "def.*main\|argparse\|click" main.py`
- Find data extraction: `rg -n "extract.*data\|parse.*content" DeepSentimentCrawling/`

## Common Gotchas

- Browser automation requires proper Playwright installation: `playwright install chromium`
- Platform-specific selectors may break when websites update
- Rate limiting is essential to avoid being blocked by platforms
- Database connections must be properly managed with context sessions
- Crawling parameters should be configurable per platform
- Large-scale crawling requires proper resource management and cleanup

## Pre-PR Checks

```bash
# Test MindSpider setup
cd MindSpider && python main.py --setup

# Test topic extraction
python main.py --broad-topic --test

# Test database connectivity
python -c "from MindSpider.schema.db_manager import test_connection; test_connection()"

# Validate platform configurations
python -c "from MindSpider.DeepSentimentCrawling.platform_crawler import validate_configs; validate_configs()"