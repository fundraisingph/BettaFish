"""
Text processing utilities for InsightEngine
"""

from typing import List, Dict, Any


def format_search_results_for_prompt(search_results: List[Dict[str, Any]], max_content_length: int = 500000) -> str:
    """
    Format search results for LLM prompt with content length limit
    
    Args:
        search_results: List of search results
        max_content_length: Maximum total content length
        
    Returns:
        Formatted string for LLM prompt
    """
    if not search_results:
        return "没有找到相关搜索结果。"
    
    formatted_results = []
    total_length = 0
    
    for i, result in enumerate(search_results, 1):
        title = result.get('title', '')
        content = result.get('content', '')
        url = result.get('url', '')
        platform = result.get('platform', '')
        author = result.get('author', '')
        published_date = result.get('published_date', '')
        
        # Format individual result
        result_text = f"""
{i}. 标题: {title}
   内容: {content}
   平台: {platform}
   作者: {author}
   发布时间: {published_date}
   链接: {url}
---
"""
        
        # Check if adding this result would exceed the limit
        if total_length + len(result_text) > max_content_length:
            # If we can't fit the full result, try to truncate it
            remaining_space = max_content_length - total_length - 100  # Leave some buffer
            if remaining_space > 200:  # Only include if we have meaningful space
                truncated_content = content[:remaining_space] + "...\n[内容因长度限制被截断]"
                result_text = f"""
{i}. 标题: {title}
   内容: {truncated_content}
   平台: {platform}
   作者: {author}
   发布时间: {published_date}
   链接: {url}
---
"""
                formatted_results.append(result_text)
            break
        
        formatted_results.append(result_text)
        total_length += len(result_text)
    
    return "\n".join(formatted_results)


def remove_reasoning_from_output(text: str) -> str:
    """
    Remove reasoning sections from LLM output
    
    Args:
        text: Raw LLM output
        
    Returns:
        Cleaned text
    """
    # Look for common reasoning patterns and remove them
    reasoning_patterns = [
        r'```json\s* reasoning.*?```',
        r'```reasoning.*?```',
        r'推理：.*?(?=\n\n|\n#|\n##)',
        r'Reasoning:.*?(?=\n\n|\n#|\n##)',
        r'思考过程：.*?(?=\n\n|\n#|\n##)',
        r'Thinking process:.*?(?=\n\n|\n#|\n##)',
    ]
    
    import re
    for pattern in reasoning_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE | re.MULTILINE)
    
    return text.strip()


def clean_json_tags(text: str) -> str:
    """
    Clean JSON tags from text
    
    Args:
        text: Text with potential JSON tags
        
    Returns:
        Cleaned text
    """
    import re
    
    # Remove ```json and ``` tags
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    
    # Remove any extra markdown formatting
    text = re.sub(r'^\s*[-*]\s*', '', text, flags=re.MULTILINE)
    
    return text.strip()


def extract_clean_response(text: str) -> Dict[str, Any]:
    """
    Extract clean JSON response from potentially messy text
    
    Args:
        text: Potentially messy LLM output
        
    Returns:
        Parsed JSON dict or error dict
    """
    import json
    import re
    
    try:
        # Try direct JSON parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from the text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # If no valid JSON found, return error
    return {"error": "Could not extract valid JSON from response", "raw_text": text}


def fix_incomplete_json(text: str) -> str:
    """
    Attempt to fix incomplete JSON
    
    Args:
        text: Incomplete JSON string
        
    Returns:
        Fixed JSON string or empty string
    """
    import re
    
    # Count braces
    open_braces = text.count('{')
    close_braces = text.count('}')
    
    # Add missing closing braces
    if open_braces > close_braces:
        text += '}' * (open_braces - close_braces)
    
    # Fix common JSON issues
    # Remove trailing commas
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    
    # Fix unescaped quotes in strings (basic attempt)
    # This is a simplified fix - more complex cases might need more sophisticated handling
    text = re.sub(r'(?<!\\)"(?=[^,:}\]\s*$)', r'\\"', text)
    
    return text


def truncate_content(content: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate content to specified length with suffix
    
    Args:
        content: Content to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated content
    """
    if len(content) <= max_length:
        return content
    
    return content[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text (simple implementation)
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords
        
    Returns:
        List of keywords
    """
    import re
    from collections import Counter
    
    # Simple keyword extraction - remove common words and count remaining
    common_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    
    # Extract Chinese characters and words
    words = re.findall(r'[\u4e00-\u9fff]+', text)
    
    # Filter out common words
    filtered_words = [word for word in words if len(word) > 1 and word not in common_words]
    
    # Count and return most common
    word_counts = Counter(filtered_words)
    return [word for word, count in word_counts.most_common(max_keywords)]