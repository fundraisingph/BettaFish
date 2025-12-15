#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindSpider - AI crawler project main program
Integrates BroadTopicExtraction and DeepSentimentCrawling two core modules
"""

import os
import sys
import argparse
from datetime import date, datetime
from pathlib import Path
import subprocess
import asyncio
import pymysql
from pymysql.cursors import DictCursor
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import inspect, text
from config import settings
from loguru import logger
from urllib.parse import quote_plus

# Add project root directory to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    import config
except ImportError:
    logger.error("Error: Unable to import config.py configuration file")
    logger.error("Please ensure config.py file exists in project root directory and contains database and API configuration information")
    sys.exit(1)

class MindSpider:
    """MindSpider main program"""
    
    def __init__(self):
        """Initialize MindSpider"""
        self.project_root = project_root
        self.broad_topic_path = self.project_root / "BroadTopicExtraction"
        self.deep_sentiment_path = self.project_root / "DeepSentimentCrawling"
        self.schema_path = self.project_root / "schema"
        
        logger.info("MindSpider AI crawler project")
        logger.info(f"Project path: {self.project_root}")
    
    def check_config(self) -> bool:
        """Check basic configuration"""
        logger.info("Checking basic configuration...")
        
        # Check settings configuration items
        required_configs = [
            'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_CHARSET',
            'MINDSPIDER_API_KEY', 'MINDSPIDER_BASE_URL', 'MINDSPIDER_MODEL_NAME'
        ]
        
        missing_configs = []
        for config_name in required_configs:
            if not hasattr(settings, config_name) or not getattr(settings, config_name):
                missing_configs.append(config_name)
        
        if missing_configs:
            logger.error(f"Missing configuration: {', '.join(missing_configs)}")
            logger.error("Please check environment variable configuration information in .env file")
            return False
        
        logger.info("Basic configuration check passed")
        return True
    
    def check_database_connection(self) -> bool:
        """Check database connection"""
        logger.info("Checking database connection...")
        
        def build_async_url() -> str:
            dialect = (settings.DB_DIALECT or "mysql").lower()
            if dialect == "postgresql":
                return f"postgresql+asyncpg://{settings.DB_USER}:{quote_plus(settings.DB_PASSWORD)}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
            # Default to use mysql async driver asyncmy
            return (
                f"mysql+asyncmy://{settings.DB_USER}:{quote_plus(settings.DB_PASSWORD)}"
                f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset={settings.DB_CHARSET}"
            )

        async def _test_connection(db_url: str) -> None:
            engine: AsyncEngine = create_async_engine(db_url, pool_pre_ping=True)
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
            finally:
                await engine.dispose()

        try:
            db_url: str = build_async_url()
            asyncio.run(_test_connection(db_url))
            logger.info("Database connection normal")
            return True
        except Exception as e:
            logger.exception(f"Database connection failed: {e}")
            return False
    
    def check_database_tables(self) -> bool:
        """Check if database tables exist"""
        logger.info("Checking database tables...")
        
        def build_async_url() -> str:
            dialect = (settings.DB_DIALECT or "mysql").lower()
            if dialect == "postgresql":
                return f"postgresql+asyncpg://{settings.DB_USER}:{quote_plus(settings.DB_PASSWORD)}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
            return (
                f"mysql+asyncmy://{settings.DB_USER}:{quote_plus(settings.DB_PASSWORD)}"
                f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset={settings.DB_CHARSET}"
            )

        async def _check_tables(db_url: str) -> list[str]:
            engine: AsyncEngine = create_async_engine(db_url, pool_pre_ping=True)
            try:
                async with engine.connect() as conn:
                    def _get_tables(sync_conn):
                        return inspect(sync_conn).get_table_names()
                    tables = await conn.run_sync(_get_tables)
                    return tables
            finally:
                await engine.dispose()

        try:
            db_url: str = build_async_url()
            existing_tables = asyncio.run(_check_tables(db_url))
            required_tables = ['daily_news', 'daily_topics']
            missing_tables = [t for t in required_tables if t not in existing_tables]
            if missing_tables:
                logger.error(f"Missing database tables: {', '.join(missing_tables)}")
                return False
            logger.info("Database table check passed")
            return True
        except Exception as e:
            logger.exception(f"Database table check failed: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """Initialize database"""
        logger.info("Initializing database...")
        
        try:
            # Run database initialization script
            init_script = self.schema_path / "init_database.py"
            if not init_script.exists():
                logger.error("Error: Database initialization script not found")
                return False
            
            result = subprocess.run(
                [sys.executable, str(init_script)],
                cwd=self.schema_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("数据库初始化成功")
                return True
            else:
                logger.error(f"数据库初始化失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.exception(f"数据库初始化异常: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check dependency environment"""
        logger.info("Checking dependency environment...")
        
        # Check Python packages
        required_packages = ['pymysql', 'requests', 'playwright']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing Python packages: {', '.join(missing_packages)}")
            logger.info("Please run: pip install -r requirements.txt")
            return False
        
        # Check MediaCrawler dependency
        mediacrawler_path = self.deep_sentiment_path / "MediaCrawler"
        if not mediacrawler_path.exists():
            logger.error("Error: MediaCrawler directory not found")
            return False
        
        logger.info("Dependency environment check passed")
        return True
    
    def run_broad_topic_extraction(self, extract_date: date = None, keywords_count: int = 100) -> bool:
        """Run BroadTopicExtraction module"""
        logger.info("Running BroadTopicExtraction module...")
        
        if not extract_date:
            extract_date = date.today()
        
        try:
            cmd = [
                sys.executable, "main.py",
                "--keywords", str(keywords_count)
            ]
            
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.broad_topic_path,
                timeout=1800  # 30 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("BroadTopicExtraction模块执行成功")
                return True
            else:
                logger.error(f"BroadTopicExtraction模块执行失败，返回码: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("BroadTopicExtraction模块执行超时")
            return False
        except Exception as e:
            logger.exception(f"BroadTopicExtraction模块执行异常: {e}")
            return False
    
    def run_deep_sentiment_crawling(self, target_date: date = None, platforms: list = None,
                                   max_keywords: int = 50, max_notes: int = 50,
                                   test_mode: bool = False) -> bool:
        """运行DeepSentimentCrawling模块"""
        logger.info("运行DeepSentimentCrawling模块...")
        
        if not target_date:
            target_date = date.today()
        
        try:
            cmd = [sys.executable, "main.py"]
            
            if target_date:
                cmd.extend(["--date", target_date.strftime("%Y-%m-%d")])
            
            if platforms:
                cmd.extend(["--platforms"] + platforms)
            
            cmd.extend([
                "--max-keywords", str(max_keywords),
                "--max-notes", str(max_notes)
            ])
            
            if test_mode:
                cmd.append("--test")
            
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.deep_sentiment_path,
                timeout=3600  # 60 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("DeepSentimentCrawling模块执行成功")
                return True
            else:
                logger.error(f"DeepSentimentCrawling模块执行失败，返回码: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("DeepSentimentCrawling模块执行超时")
            return False
        except Exception as e:
            logger.exception(f"DeepSentimentCrawling模块执行异常: {e}")
            return False
    
    def run_complete_workflow(self, target_date: date = None, platforms: list = None,
                             keywords_count: int = 100, max_keywords: int = 50,
                             max_notes: int = 50, test_mode: bool = False) -> bool:
        """运行完整工作流程"""
        logger.info("开始完整的MindSpider工作流程")
        
        if not target_date:
            target_date = date.today()
        
        logger.info(f"Target date: {target_date}")
        logger.info(f"Platform list: {platforms if platforms else 'All supported platforms'}")
        logger.info(f"Test mode: {'Yes' if test_mode else 'No'}")
        
        # Step 1: Run topic extraction
        logger.info("=== Step 1: Topic Extraction ===")
        if not self.run_broad_topic_extraction(target_date, keywords_count):
            logger.error("Topic extraction failed, terminating process")
            return False
        
        # Step 2: Run sentiment crawling
        logger.info("=== Step 2: Sentiment Crawling ===")
        if not self.run_deep_sentiment_crawling(target_date, platforms, max_keywords, max_notes, test_mode):
            logger.error("Sentiment crawling failed, but topic extraction completed")
            return False
        
        logger.info("Complete workflow execution successful!")
        return True
    
    def show_status(self):
        """Display project status"""
        logger.info("MindSpider project status:")
        logger.info(f"Project path: {self.project_root}")
        
        # Configuration status
        config_ok = self.check_config()
        logger.info(f"Configuration status: {'Normal' if config_ok else 'Abnormal'}")
        
        # Database status
        if config_ok:
            db_conn_ok = self.check_database_connection()
            logger.info(f"Database connection: {'Normal' if db_conn_ok else 'Abnormal'}")
            
            if db_conn_ok:
                db_tables_ok = self.check_database_tables()
                logger.info(f"Database tables: {'Normal' if db_tables_ok else 'Need initialization'}")
        
        # Dependency status
        deps_ok = self.check_dependencies()
        logger.info(f"Dependency environment: {'Normal' if deps_ok else 'Abnormal'}")
        
        # Module status
        broad_topic_exists = self.broad_topic_path.exists()
        deep_sentiment_exists = self.deep_sentiment_path.exists()
        logger.info(f"BroadTopicExtraction module: {'Exists' if broad_topic_exists else 'Missing'}")
        logger.info(f"DeepSentimentCrawling module: {'Exists' if deep_sentiment_exists else 'Missing'}")
    
    def setup_project(self) -> bool:
        """Project initialization setup"""
        logger.info("Starting MindSpider project initialization...")
        
        # 1. Check configuration
        if not self.check_config():
            return False
        
        # 2. Check dependencies
        if not self.check_dependencies():
            return False
        
        # 3. Check database connection
        if not self.check_database_connection():
            return False
        
        # 4. Check and initialize database tables
        if not self.check_database_tables():
            logger.info("Need to initialize database tables...")
            if not self.initialize_database():
                return False
        
        logger.info("MindSpider project initialization completed!")
        return True

def main():
    """Command line entry point"""
    parser = argparse.ArgumentParser(description="MindSpider - AI crawler project main program")
    
    # Basic operations
    parser.add_argument("--setup", action="store_true", help="Initialize project setup")
    parser.add_argument("--status", action="store_true", help="Display project status")
    parser.add_argument("--init-db", action="store_true", help="Initialize database")
    
    # Module execution
    parser.add_argument("--broad-topic", action="store_true", help="Run only topic extraction module")
    parser.add_argument("--deep-sentiment", action="store_true", help="Run only sentiment crawling module")
    parser.add_argument("--complete", action="store_true", help="Run complete workflow")
    
    # Parameter configuration
    parser.add_argument("--date", type=str, help="Target date (YYYY-MM-DD), default is today")
    parser.add_argument("--platforms", type=str, nargs='+',
                       choices=['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu'],
                       help="Specify crawling platforms")
    parser.add_argument("--keywords-count", type=int, default=100, help="Number of keywords for topic extraction")
    parser.add_argument("--max-keywords", type=int, default=50, help="Maximum number of keywords per platform")
    parser.add_argument("--max-notes", type=int, default=50, help="Maximum number of content to crawl per keyword")
    parser.add_argument("--test", action="store_true", help="Test mode (small amount of data)")
    
    args = parser.parse_args()
    
    # 解析日期
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            logger.error("Error: Date format incorrect, please use YYYY-MM-DD format")
            return
    
    # 创建MindSpider实例
    spider = MindSpider()
    
    try:
        # 显示状态
        if args.status:
            spider.show_status()
            return
        
        # Project setup
        if args.setup:
            if spider.setup_project():
                logger.info("Project setup completed, can start using MindSpider!")
            else:
                logger.error("Project setup failed, please check configuration and environment")
            return
        
        # Initialize database
        if args.init_db:
            if spider.initialize_database():
                logger.info("Database initialization successful")
            else:
                logger.error("Database initialization failed")
            return
        
        # Run modules
        if args.broad_topic:
            spider.run_broad_topic_extraction(target_date, args.keywords_count)
        elif args.deep_sentiment:
            spider.run_deep_sentiment_crawling(
                target_date, args.platforms, args.max_keywords, args.max_notes, args.test
            )
        elif args.complete:
            spider.run_complete_workflow(
                target_date, args.platforms, args.keywords_count,
                args.max_keywords, args.max_notes, args.test
            )
        else:
            # Default to run complete workflow
            logger.info("Running complete MindSpider workflow...")
            spider.run_complete_workflow(
                target_date, args.platforms, args.keywords_count,
                args.max_keywords, args.max_notes, args.test
            )
    
    except KeyboardInterrupt:
        logger.info("User interrupted operation")
    except Exception as e:
        logger.exception(f"Execution error: {e}")

if __name__ == "__main__":
    main()
