"""
Configuration management module for the Media Engine (pydantic_settings style).
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Literal


# Calculate .env priority: prioritize current working directory, then project root
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
CWD_ENV: Path = Path.cwd() / ".env"
ENV_FILE: str = str(CWD_ENV if CWD_ENV.exists() else (PROJECT_ROOT / ".env"))

class Settings(BaseSettings):
    """
    Global configuration; supports automatic loading of .env and environment variables.
    Variable names are consistent with the original config.py in uppercase for smooth transition.
    """
    # ====================== Database Configuration ======================
    DB_HOST: str = Field("your_db_host", description="Database host, e.g., localhost or 127.0.0.1. We also provide convenient cloud database resource configuration for 100k+ daily data, free application available, contact us: 670939375@qq.com NOTE: For data compliance review and service upgrade, cloud database will suspend new application acceptance from October 1, 2025")
    DB_PORT: int = Field(3306, description="Database port number, default is 3306")
    DB_USER: str = Field("your_db_user", description="Database username")
    DB_PASSWORD: str = Field("your_db_password", description="Database password")
    DB_NAME: str = Field("your_db_name", description="Database name")
    DB_CHARSET: str = Field("utf8mb4", description="Database character set, recommended utf8mb4 for emoji compatibility")
    DB_DIALECT: str = Field("mysql", description="Database type, e.g., 'mysql' or 'postgresql'. Used to support multiple database backends (such as SQLAlchemy, please configure together with connection information)")

    # ======================= LLM Related =======================
    INSIGHT_ENGINE_API_KEY: str = Field(None, description="Insight Agent (recommended Kimi, https://platform.moonshot.cn/) API key, used for main LLM. You can change the API used by each LLM part, 🚩as long as it's compatible with OpenAI request format, you can use it normally by defining KEY, BASE_URL and MODEL_NAME. Important reminder: we strongly recommend you first apply for API using the recommended configuration, get it working before making your changes!")
    INSIGHT_ENGINE_BASE_URL: Optional[str] = Field("https://api.moonshot.cn/v1", description="Insight Agent LLM interface BaseUrl, customizable vendor API")
    INSIGHT_ENGINE_MODEL_NAME: str = Field("kimi-k2-0711-preview", description="Insight Agent LLM model name, e.g., kimi-k2-0711-preview")
    
    MEDIA_ENGINE_API_KEY: str = Field(None, description="Media Agent (recommended Gemini, I used a relay vendor here, you can also replace it with your own, application address: https://www.chataiapi.com/) API key")
    MEDIA_ENGINE_BASE_URL: Optional[str] = Field("https://www.chataiapi.com/v1", description="Media Agent LLM interface BaseUrl")
    MEDIA_ENGINE_MODEL_NAME: str = Field("gemini-2.5-pro", description="Media Agent LLM model name, e.g., gemini-2.5-pro")
    
    BOCHA_WEB_SEARCH_API_KEY: Optional[str] = Field(None, description="Bocha Web Search API Key")
    BOCHA_API_KEY: Optional[str] = Field(None, description="Bocha compatibility key (alias)")
    
    SEARCH_TIMEOUT: int = Field(240, description="Search timeout (seconds)")
    SEARCH_CONTENT_MAX_LENGTH: int = Field(20000, description="Maximum content length for prompts")
    MAX_REFLECTIONS: int = Field(2, description="Maximum reflection rounds")
    MAX_PARAGRAPHS: int = Field(5, description="Maximum paragraph count")
    
    MINDSPIDER_API_KEY: Optional[str] = Field(None, description="MindSpider API key")
    MINDSPIDER_BASE_URL: Optional[str] = Field("https://api.deepseek.com", description="MindSpider LLM interface BaseUrl")
    MINDSPIDER_MODEL_NAME: str = Field("deepseek-reasoner", description="MindSpider LLM model name, e.g., deepseek-reasoner")
    
    OUTPUT_DIR: str = Field("reports", description="Output directory")
    SAVE_INTERMEDIATE_STATES: bool = Field(True, description="Whether to save intermediate states")

    
    QUERY_ENGINE_API_KEY: str = Field(None, description="Query Agent (recommended DeepSeek, https://www.deepseek.com/) API key")
    QUERY_ENGINE_BASE_URL: Optional[str] = Field("https://api.deepseek.com", description="Query Agent LLM interface BaseUrl")
    QUERY_ENGINE_MODEL_NAME: str = Field("deepseek-reasoner", description="Query Agent LLM model, e.g., deepseek-reasoner")
    
    REPORT_ENGINE_API_KEY: str = Field(None, description="Report Agent (recommended Gemini, I used a relay vendor here, you can also replace it with your own, application address: https://www.chataiapi.com/) API key")
    REPORT_ENGINE_BASE_URL: Optional[str] = Field("https://www.chataiapi.com/v1", description="Report Agent LLM interface BaseUrl")
    REPORT_ENGINE_MODEL_NAME: str = Field("gemini-2.5-pro", description="Report Agent LLM model name, e.g., gemini-2.5-pro")
    
    FORUM_HOST_API_KEY: str = Field(None, description="Forum Host (Qwen3 latest model, I used the SiliconFlow platform here, application address: https://cloud.siliconflow.cn/) API key")
    FORUM_HOST_BASE_URL: Optional[str] = Field("https://api.siliconflow.cn/v1", description="Forum Host LLM BaseUrl")
    FORUM_HOST_MODEL_NAME: str = Field("Qwen/Qwen3-235B-A22B-Instruct-2507", description="Forum Host LLM model name, e.g., Qwen/Qwen3-235B-A22B-Instruct-2507")
    
    KEYWORD_OPTIMIZER_API_KEY: str = Field(None, description="SQL keyword Optimizer (small parameter Qwen3 model, I used the SiliconFlow platform here, application address: https://cloud.siliconflow.cn/) API key")
    KEYWORD_OPTIMIZER_BASE_URL: Optional[str] = Field("https://api.siliconflow.cn/v1", description="Keyword Optimizer BaseUrl")
    KEYWORD_OPTIMIZER_MODEL_NAME: str = Field("Qwen/Qwen3-30B-A3B-Instruct-2507", description="Keyword Optimizer LLM model name, e.g., Qwen/Qwen3-30B-A3B-Instruct-2507")

    # ================== Network Tool Configuration ====================
    TAVILY_API_KEY: str = Field(None, description="Tavily API (application address: https://www.tavily.com/) API key, used for Tavily web search")
    
    SEARCH_TOOL_TYPE: Literal["AnspireAPI", "BochaAPI"] = Field("AnspireAPI", description="Web search tool type, supports BochaAPI or AnspireAPI, default is AnspireAPI")
    BOCHA_BASE_URL: Optional[str] = Field("https://api.bochaai.com/v1/ai-search", description="Bocha AI search BaseUrl or Bocha web search BaseUrl")
    BOCHA_WEB_SEARCH_API_KEY: Optional[str] = Field(None, description="Bocha API (application address: https://open.bochaai.com/) API key, used for Bocha search")
    # Anspire AI Search API (application address: https://open.anspire.cn/)
    ANSPIRE_BASE_URL: Optional[str] = Field("https://plugin.anspire.cn/api/ntsearch/search", description="Anspire AI search BaseUrl")
    ANSPIRE_API_KEY: Optional[str] = Field(None, description="Anspire AI Search API (application address: https://open.anspire.cn/) API key, used for Anspire search")

    class Config:
        env_file = ENV_FILE
        env_prefix = ""
        case_sensitive = False
        extra = "allow"


settings = Settings()
