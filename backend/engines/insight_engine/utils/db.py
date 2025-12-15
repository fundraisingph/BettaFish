"""
Database utilities for InsightEngine
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Literal
import logging
logger = logging.getLogger(__name__)
import asyncpg

from core.database import db_manager
from ..models.schemas import QueryResult


class InsightDatabaseManager:
    """Database manager for InsightEngine with async PostgreSQL support"""
    
    # Engagement weights
    W_LIKE = 1.0
    W_COMMENT = 5.0
    W_SHARE = 10.0  # Share/forward/favorite/coin high-value interactions
    W_VIEW = 0.1
    W_DANMAKU = 0.5

    def __init__(self):
        """Initialize database manager"""
        self.db_manager = db_manager

    async def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute database query with error handling"""
        try:
            conn = await self.db_manager.get_connection()
            if params:
                result = await conn.fetch(query, *params)
            else:
                result = await conn.fetch(query)
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            return []

    @staticmethod
    def _to_datetime(ts: Any) -> Optional[datetime]:
        """Convert timestamp to datetime"""
        if not ts: 
            return None
        try:
            if isinstance(ts, datetime): 
                return ts
            if isinstance(ts, str):
                return datetime.fromisoformat(ts.split('+')[0].strip())
            if isinstance(ts, (int, float)) or str(ts).isdigit():
                val = float(ts)
                return datetime.fromtimestamp(val / 1000 if val > 1_000_000_000_000 else val)
        except (ValueError, TypeError): 
            return None

    async def _get_table_columns(self, table_name: str) -> List[str]:
        """Get table columns from database"""
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
        result = await self._execute_query(query)
        return [row['column_name'] for row in result] if result else []

    def _extract_engagement(self, row: Dict[str, Any]) -> Dict[str, int]:
        """Extract and unify engagement metrics from data row"""
        engagement = {}
        mapping = {
            'likes': ['liked_count', 'like_count', 'voteup_count', 'comment_like_count'],
            'comments': ['video_comment', 'comments_count', 'comment_count', 'total_replay_num', 'sub_comment_count'],
            'shares': ['video_share_count', 'shared_count', 'share_count', 'total_forwards'],
            'views': ['video_play_count', 'viewd_count'],
            'favorites': ['video_favorite_count', 'collected_count'],
            'coins': ['video_coin_count'],
            'danmaku': ['video_danmaku'],
        }
        
        for key, potential_cols in mapping.items():
            for col in potential_cols:
                if col in row and row[col] is not None:
                    try:
                        engagement[key] = int(row[col])
                    except (ValueError, TypeError):
                        engagement[key] = 0
                    break
        return engagement

    async def search_hot_content(
        self,
        time_period: Literal['24h', 'week', 'year'] = 'week',
        limit: int = 50
    ) -> List[QueryResult]:
        """Search for hot content within specified time period"""
        now = datetime.now()
        start_time = now - timedelta(days={'24h': 1, 'week': 7}.get(time_period, 365))

        # Define hotness calculation SQL for different platforms
        hotness_formulas = {
            'bilibili_video': f"(COALESCE(liked_count, 0) * {self.W_LIKE} + COALESCE(video_comment, 0) * {self.W_COMMENT} + COALESCE(video_share_count, 0) * {self.W_SHARE} + COALESCE(video_favorite_count, 0) * {self.W_SHARE} + COALESCE(video_coin_count, 0) * {self.W_SHARE} + COALESCE(video_danmaku, 0) * {self.W_DANMAKU} + COALESCE(video_play_count, 0) * {self.W_VIEW})",
            'douyin_aweme': f"(COALESCE(liked_count, 0) * {self.W_LIKE} + COALESCE(comment_count, 0) * {self.W_COMMENT} + COALESCE(share_count, 0) * {self.W_SHARE} + COALESCE(collected_count, 0) * {self.W_SHARE})",
            'weibo_note': f"(COALESCE(liked_count, 0) * {self.W_LIKE} + COALESCE(comments_count, 0) * {self.W_COMMENT} + COALESCE(shared_count, 0) * {self.W_SHARE})",
            'xhs_note': f"(COALESCE(liked_count, 0) * {self.W_LIKE} + COALESCE(comment_count, 0) * {self.W_COMMENT} + COALESCE(share_count, 0) * {self.W_SHARE} + COALESCE(collected_count, 0) * {self.W_SHARE})",
            'kuaishou_video': f"(COALESCE(liked_count, 0) * {self.W_LIKE} + COALESCE(viewd_count, 0) * {self.W_VIEW})",
            'zhihu_content': f"(COALESCE(voteup_count, 0) * {self.W_LIKE} + COALESCE(comment_count, 0) * {self.W_COMMENT})",
        }

        all_queries = []
        params = []
        
        for table, formula in hotness_formulas.items():
            time_filter_sql = ""
            time_param = None
            
            if table == 'weibo_note':
                time_filter_sql = "create_date_time >= %s"
                time_param = start_time.strftime('%Y-%m-%d %H:%M:%S')
            elif table in ['kuaishou_video', 'xhs_note', 'douyin_aweme']:
                time_col = 'time' if table == 'xhs_note' else 'create_time'
                time_filter_sql = f"{time_col} >= %s"
                time_param = str(int(start_time.timestamp() * 1000))
            elif table == 'zhihu_content':
                time_filter_sql = "CAST(created_time AS BIGINT) >= %s"
                time_param = str(int(start_time.timestamp()))
            else:  # bilibili_video
                time_filter_sql = "create_time >= %s"
                time_param = str(int(start_time.timestamp()))

            content_type = 'note' if table in ['weibo_note', 'xhs_note'] else 'content' if table == 'zhihu_content' else 'video'
            
            query_template = f"""
            SELECT '{table.split('_')[0]}' as platform, 
                   '{content_type}' as content_type, 
                   title as title_or_content,
                   nickname as author_nickname,
                   video_url as url,
                   create_time as publish_time,
                   {formula} as hotness_score,
                   source_keyword,
                   '{table}' as source_table,
                   liked_count, video_comment, video_share_count, video_favorite_count, video_coin_count, video_danmaku, video_play_count
            FROM {table}
            WHERE {time_filter_sql}
            """
            
            all_queries.append(query_template)
            params.append(time_param)

        final_query = f"{' UNION ALL '.join(all_queries)} ORDER BY hotness_score DESC LIMIT %s"
        params.append(limit)
        
        raw_results = await self._execute_query(final_query, tuple(params))
        
        formatted_results = []
        for r in raw_results:
            formatted_results.append(QueryResult(
                platform=r['platform'],
                content_type=r['content_type'],
                title_or_content=r['title_or_content'],
                author_nickname=r['author_nickname'],
                url=r['url'],
                publish_time=self._to_datetime(r['publish_time']),
                engagement=self._extract_engagement(r),
                hotness_score=r.get('hotness_score', 0.0),
                source_keyword=r.get('source_keyword'),
                source_table=r['source_table']
            ))
        
        return formatted_results

    async def search_topic_globally(self, topic: str, limit_per_table: int = 100) -> List[QueryResult]:
        """Global topic search across all platforms"""
        search_term = f"%{topic}%"
        search_configs = {
            'bilibili_video': {'fields': ['title', 'desc', 'source_keyword'], 'type': 'video'},
            'bilibili_video_comment': {'fields': ['content'], 'type': 'comment'},
            'douyin_aweme': {'fields': ['title', 'desc', 'source_keyword'], 'type': 'video'},
            'douyin_aweme_comment': {'fields': ['content'], 'type': 'comment'},
            'kuaishou_video': {'fields': ['title', 'desc', 'source_keyword'], 'type': 'video'},
            'kuaishou_video_comment': {'fields': ['content'], 'type': 'comment'},
            'weibo_note': {'fields': ['content', 'source_keyword'], 'type': 'note'},
            'weibo_note_comment': {'fields': ['content'], 'type': 'comment'},
            'xhs_note': {'fields': ['title', 'desc', 'tag_list', 'source_keyword'], 'type': 'note'},
            'xhs_note_comment': {'fields': ['content'], 'type': 'comment'},
            'zhihu_content': {'fields': ['title', 'desc', 'content_text', 'source_keyword'], 'type': 'content'},
            'zhihu_comment': {'fields': ['content'], 'type': 'comment'},
            'tieba_note': {'fields': ['title', 'desc', 'source_keyword'], 'type': 'note'},
            'tieba_comment': {'fields': ['content'], 'type': 'comment'},
            'daily_news': {'fields': ['title'], 'type': 'news'},
        }
        
        all_results = []
        
        for table, config in search_configs.items():
            where_clauses = []
            params = []
            
            for idx, field in enumerate(config['fields']):
                where_clauses.append(f"{field} LIKE ${idx + 1}")
                params.append(search_term)
            
            params.append(limit_per_table)
            where_clause = " OR ".join(where_clauses)
            
            query = f"""
            SELECT * FROM {table} 
            WHERE {where_clause} 
            ORDER BY id DESC 
            LIMIT ${len(params)}
            """
            
            raw_results = await self._execute_query(query, tuple(params))
            
            for row in raw_results:
                content = (row.get('title') or row.get('content') or row.get('desc') or row.get('content_text', ''))
                time_key = row.get('create_time') or row.get('time') or row.get('created_time') or row.get('publish_time') or row.get('crawl_date')
                
                all_results.append(QueryResult(
                    platform=table.split('_')[0],
                    content_type=config['type'],
                    title_or_content=content if content else '',
                    author_nickname=row.get('nickname') or row.get('user_nickname') or row.get('user_name'),
                    url=row.get('video_url') or row.get('note_url') or row.get('content_url') or row.get('url') or row.get('aweme_url'),
                    publish_time=self._to_datetime(time_key),
                    engagement=self._extract_engagement(row),
                    source_keyword=row.get('source_keyword'),
                    source_table=table
                ))
        
        return all_results

    async def search_topic_by_date(self, topic: str, start_date: str, end_date: str, limit_per_table: int = 100) -> List[QueryResult]:
        """Search topic by date range"""
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            logger.error("Invalid date format, should be YYYY-MM-DD")
            return []
        
        search_term = f"%{topic}%"
        search_configs = {
            'bilibili_video': {'fields': ['title', 'desc', 'source_keyword'], 'type': 'video', 'time_col': 'create_time', 'time_type': 'sec'},
            'douyin_aweme': {'fields': ['title', 'desc', 'source_keyword'], 'type': 'video', 'time_col': 'create_time', 'time_type': 'ms'},
            'kuaishou_video': {'fields': ['title', 'desc', 'source_keyword'], 'type': 'video', 'time_col': 'create_time', 'time_type': 'ms'},
            'weibo_note': {'fields': ['content', 'source_keyword'], 'type': 'note', 'time_col': 'create_date_time', 'time_type': 'str'},
            'xhs_note': {'fields': ['title', 'desc', 'tag_list', 'source_keyword'], 'type': 'note', 'time_col': 'time', 'time_type': 'ms'},
            'zhihu_content': {'fields': ['title', 'desc', 'content_text', 'source_keyword'], 'type': 'content', 'time_col': 'created_time', 'time_type': 'sec_str'},
            'tieba_note': {'fields': ['title', 'desc', 'source_keyword'], 'type': 'note', 'time_col': 'publish_time', 'time_type': 'str'},
            'daily_news': {'fields': ['title'], 'type': 'news', 'time_col': 'crawl_date', 'time_type': 'date_str'},
        }
        
        all_results = []
        
        for table, config in search_configs.items():
            where_clauses = []
            params = []
            
            for idx, field in enumerate(config['fields']):
                where_clauses.append(f"{field} LIKE ${idx + 1}")
                params.append(search_term)
            
            # Add time filter
            time_col = config['time_col']
            time_type = config['time_type']
            
            if time_type == 'sec':
                time_filter = f"({time_col} >= ${len(params) + 1} AND {time_col} < ${len(params) + 2})"
                params.extend([int(start_dt.timestamp()), int(end_dt.timestamp())])
            elif time_type == 'ms':
                time_filter = f"({time_col} >= ${len(params) + 1} AND {time_col} < ${len(params) + 2})"
                params.extend([int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000)])
            elif time_type in ['str', 'date_str']:
                time_filter = f"({time_col} >= ${len(params) + 1} AND {time_col} < ${len(params) + 2})"
                params.extend([start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d')])
            
            where_clauses.append(time_filter)
            params.append(limit_per_table)
            
            query = f"""
            SELECT * FROM {table} 
            WHERE ({' OR '.join(where_clauses[:len(config['fields'])])}) AND {time_filter}
            ORDER BY id DESC 
            LIMIT ${len(params)}
            """
            
            raw_results = await self._execute_query(query, tuple(params))
            
            for row in raw_results:
                content = (row.get('title') or row.get('content') or row.get('desc') or row.get('content_text', ''))
                time_key = config.get('time_col') and row.get(config.get('time_col'))
                
                all_results.append(QueryResult(
                    platform=table.split('_')[0],
                    content_type=config['type'],
                    title_or_content=content if content else '',
                    author_nickname=row.get('nickname') or row.get('user_nickname') or row.get('user_name'),
                    url=row.get('video_url') or row.get('note_url') or row.get('content_url') or row.get('url') or row.get('aweme_url'),
                    publish_time=self._to_datetime(time_key),
                    engagement=self._extract_engagement(row),
                    source_keyword=row.get('source_keyword'),
                    source_table=table
                ))
        
        return all_results

    async def get_comments_for_topic(self, topic: str, limit: int = 500) -> List[QueryResult]:
        """Get comments for a specific topic"""
        search_term = f"%{topic}%"
        comment_tables = ['bilibili_video_comment', 'douyin_aweme_comment', 'kuaishou_video_comment', 'weibo_note_comment', 'xhs_note_comment', 'zhihu_comment', 'tieba_comment']
        
        all_queries = []
        params = []
        
        for table in comment_tables:
            # Get table columns dynamically
            cols = await self._get_table_columns(table)
            author_col = 'user_nickname' if 'user_nickname' in cols else 'nickname'
            like_col = 'comment_like_count' if 'comment_like_count' in cols else 'like_count' if 'like_count' in cols else None
            time_col = 'publish_time' if 'publish_time' in cols else 'create_date_time' if 'create_date_time' in cols else 'create_time'
            like_select = f"{like_col} as likes" if like_col else "'0' as likes"
            
            query = f"""
            SELECT '{table.split('_')[0]}' as platform,
                   content as title_or_content,
                   {author_col} as author_nickname,
                   {time_col} as publish_time,
                   {like_select},
                   '{table}' as source_table
            FROM {table}
            WHERE content LIKE ${len(all_queries) + 1}
            """
            
            all_queries.append(query)
            params.append(search_term)

        final_query = f"{' UNION ALL '.join(all_queries)} ORDER BY publish_time DESC LIMIT ${len(params) + 1}"
        params.append(limit)
        
        raw_results = await self._execute_query(final_query, tuple(params))
        
        formatted_results = []
        for r in raw_results:
            engagement = {'likes': int(r['likes']) if str(r['likes']).isdigit() else 0}
            formatted_results.append(QueryResult(
                platform=r['platform'],
                content_type='comment',
                title_or_content=r['title_or_content'],
                author_nickname=r['author_nickname'],
                publish_time=self._to_datetime(r['publish_time']),
                engagement=engagement,
                source_table=r['source_table']
            ))
        
        return formatted_results

    async def search_topic_on_platform(
        self,
        platform: Literal['bilibili', 'weibo', 'douyin', 'kuaishou', 'xhs', 'zhihu', 'tieba'],
        topic: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20
    ) -> List[QueryResult]:
        """Search topic on specific platform"""
        all_configs = {
            'bilibili': [
                {'table': 'bilibili_video', 'fields': ['title', 'desc', 'source_keyword'], 'type': 'video', 'time_col': 'create_time', 'time_type': 'sec'},
                {'table': 'bilibili_video_comment', 'fields': ['content'], 'type': 'comment'}
            ],
            'douyin': [
                {'table': 'douyin_aweme', 'fields': ['title', 'desc', 'source_keyword'], 'type': 'video', 'time_col': 'create_time', 'time_type': 'ms'},
                {'table': 'douyin_aweme_comment', 'fields': ['content'], 'type': 'comment'}
            ],
            'kuaishou': [
                {'table': 'kuaishou_video', 'fields': ['title', 'desc', 'source_keyword'], 'type': 'video', 'time_col': 'create_time', 'time_type': 'ms'},
                {'table': 'kuaishou_video_comment', 'fields': ['content'], 'type': 'comment'}
            ],
            'weibo': [
                {'table': 'weibo_note', 'fields': ['content', 'source_keyword'], 'type': 'note', 'time_col': 'create_date_time', 'time_type': 'str'},
                {'table': 'weibo_note_comment', 'fields': ['content'], 'type': 'comment'}
            ],
            'xhs': [
                {'table': 'xhs_note', 'fields': ['title', 'desc', 'tag_list', 'source_keyword'], 'type': 'note', 'time_col': 'time', 'time_type': 'ms'},
                {'table': 'xhs_note_comment', 'fields': ['content'], 'type': 'comment'}
            ],
            'zhihu': [
                {'table': 'zhihu_content', 'fields': ['title', 'desc', 'content_text', 'source_keyword'], 'type': 'content', 'time_col': 'created_time', 'time_type': 'sec_str'},
                {'table': 'zhihu_comment', 'fields': ['content'], 'type': 'comment'}
            ],
            'tieba': [
                {'table': 'tieba_note', 'fields': ['title', 'desc', 'source_keyword'], 'type': 'note', 'time_col': 'publish_time', 'time_type': 'str'},
                {'table': 'tieba_comment', 'fields': ['content'], 'type': 'comment'}
            ]
        }
        
        if platform not in all_configs:
            logger.error(f"Unsupported platform: {platform}")
            return []
        
        search_term = f"%{topic}%"
        platform_configs = all_configs[platform]
        all_results = []
        
        # Parse dates if provided
        start_dt = None
        end_dt = None
        if start_date and end_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            except ValueError:
                logger.error("Invalid date format, should be YYYY-MM-DD")
                return []
        
        for config in platform_configs:
            table = config['table']
            topic_clauses = [f"{field} LIKE ${idx + 1}" for idx, field in enumerate(config['fields'])]
            query = f"SELECT * FROM {table} WHERE {' OR '.join(topic_clauses)}"
            params = [search_term] * len(config['fields'])
            
            # Add time filter if dates are provided
            if start_dt and end_dt and 'time_col' in config:
                time_col = config['time_col']
                time_type = config['time_type']
                
                if time_type == 'sec':
                    t_params = (int(start_dt.timestamp()), int(end_dt.timestamp()))
                    time_filter = f"({time_col} >= ${len(params) + 1} AND {time_col} < ${len(params) + 2})"
                elif time_type == 'ms':
                    t_params = (int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000))
                    time_filter = f"({time_col} >= ${len(params) + 1} AND {time_col} < ${len(params) + 2})"
                elif time_type in ['str', 'date_str']:
                    t_params = (start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'))
                    time_filter = f"({time_col} >= ${len(params) + 1} AND {time_col} < ${len(params) + 2})"
                else:
                    t_params = (str(int(start_dt.timestamp())), str(int(end_dt.timestamp())))
                    time_filter = f"({time_col} >= ${len(params) + 1} AND {time_col} < ${len(params) + 2})"
                
                if table == 'zhihu_content':
                    time_filter = f"(CAST({time_col} AS BIGINT) >= ${len(params) + 1} AND CAST({time_col} AS BIGINT) < ${len(params) + 2})"
                
                query += f" AND {time_filter}"
                params.extend(t_params)
            
            query += f" ORDER BY id DESC LIMIT ${len(params) + 1}"
            params.append(limit)
            
            raw_results = await self._execute_query(query, tuple(params))
            
            for row in raw_results:
                content = (row.get('title') or row.get('content') or row.get('desc') or row.get('content_text', ''))
                time_key = config.get('time_col') and row.get(config.get('time_col'))
                
                all_results.append(QueryResult(
                    platform=platform,
                    content_type=config['type'],
                    title_or_content=content if content else '',
                    author_nickname=row.get('nickname') or row.get('user_nickname'),
                    url=row.get('video_url') or row.get('note_url') or row.get('content_url') or row.get('url') or row.get('aweme_url'),
                    publish_time=self._to_datetime(time_key),
                    engagement=self._extract_engagement(row),
                    source_keyword=row.get('source_keyword'),
                    source_table=table
                ))
        
        return all_results


# Global instance
db_manager = InsightDatabaseManager()