"""
Test log parsing functions in ForumEngine/monitor.py

Test parsing capabilities under various log formats, including:
1. Old format: [HH:MM:SS]
2. New format: loguru default format (YYYY-MM-DD HH:mm:ss.SSS | LEVEL | ...)
3. Should only receive outputs from SummaryNodes like FirstSummaryNode, ReflectionSummaryNode, etc., not from SearchNode
"""

import sys
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ForumEngine.monitor import LogMonitor
from tests import forum_log_test_data as test_data


class TestLogMonitor:
    """Test log parsing functionality of LogMonitor"""
    
    def setup_method(self):
        """Initialization before each test method"""
        self.monitor = LogMonitor(log_dir="tests/test_logs")
    
    def test_is_target_log_line_old_format(self):
        """Test target node identification in old format"""
        # Should identify lines containing FirstSummaryNode
        assert self.monitor.is_target_log_line(test_data.OLD_FORMAT_FIRST_SUMMARY) == True
        # Should identify lines containing ReflectionSummaryNode
        assert self.monitor.is_target_log_line(test_data.OLD_FORMAT_REFLECTION_SUMMARY) == True
        # Should not identify non-target nodes
        assert self.monitor.is_target_log_line(test_data.OLD_FORMAT_NON_TARGET) == False
    
    def test_is_target_log_line_new_format(self):
        """Test target node identification in new format"""
        # Should identify lines containing FirstSummaryNode
        assert self.monitor.is_target_log_line(test_data.NEW_FORMAT_FIRST_SUMMARY) == True
        # Should identify lines containing ReflectionSummaryNode
        assert self.monitor.is_target_log_line(test_data.NEW_FORMAT_REFLECTION_SUMMARY) == True
        # Should not identify non-target nodes
        assert self.monitor.is_target_log_line(test_data.NEW_FORMAT_NON_TARGET) == False
    
    def test_is_json_start_line_old_format(self):
        """Test JSON start line identification in old format"""
        assert self.monitor.is_json_start_line(test_data.OLD_FORMAT_SINGLE_LINE_JSON) == True
        assert self.monitor.is_json_start_line(test_data.OLD_FORMAT_MULTILINE_JSON[0]) == True
        assert self.monitor.is_json_start_line(test_data.OLD_FORMAT_NON_TARGET) == False
    
    def test_is_json_start_line_new_format(self):
        """Test JSON start line identification in new format"""
        assert self.monitor.is_json_start_line(test_data.NEW_FORMAT_SINGLE_LINE_JSON) == True
        assert self.monitor.is_json_start_line(test_data.NEW_FORMAT_MULTILINE_JSON[0]) == True
        assert self.monitor.is_json_start_line(test_data.NEW_FORMAT_NON_TARGET) == False
    
    def test_is_json_end_line(self):
        """测试JSON结束行识别"""
        assert self.monitor.is_json_end_line("}") == True
        assert self.monitor.is_json_end_line("] }") == True
        assert self.monitor.is_json_end_line("[17:42:31] }") == False  # 需要先清理时间戳
        assert self.monitor.is_json_end_line("2025-11-05 17:42:31.289 | INFO | module:function:133 - }") == False  # 需要先清理时间戳
    
    def test_extract_json_content_old_format_single_line(self):
        """Test old format single-line JSON extraction"""
        lines = [test_data.OLD_FORMAT_SINGLE_LINE_JSON]
        result = self.monitor.extract_json_content(lines)
        assert result is not None
        assert "This is first summary content" in result
    
    def test_extract_json_content_new_format_single_line(self):
        """Test new format single-line JSON extraction"""
        lines = [test_data.NEW_FORMAT_SINGLE_LINE_JSON]
        result = self.monitor.extract_json_content(lines)
        assert result is not None
        assert "This is first summary content" in result
    
    def test_extract_json_content_old_format_multiline(self):
        """Test old format multi-line JSON extraction"""
        result = self.monitor.extract_json_content(test_data.OLD_FORMAT_MULTILINE_JSON)
        assert result is not None
        assert "multiline" in result
        assert "JSON content" in result
    
    def test_extract_json_content_new_format_multiline(self):
        """Test new format multi-line JSON extraction (supports loguru format timestamp removal)"""
        result = self.monitor.extract_json_content(test_data.NEW_FORMAT_MULTILINE_JSON)
        assert result is not None
        assert "multiline" in result
        assert "JSON content" in result
    
    def test_extract_json_content_updated_priority(self):
        """Test priority extraction of updated_paragraph_latest_state"""
        result = self.monitor.extract_json_content(test_data.COMPLEX_JSON_WITH_UPDATED)
        assert result is not None
        assert "updated version" in result
        assert "key findings" in result
    
    def test_extract_json_content_paragraph_only(self):
        """Test case with only paragraph_latest_state"""
        result = self.monitor.extract_json_content(test_data.COMPLEX_JSON_WITH_PARAGRAPH)
        assert result is not None
        assert "first summary" in result or "key findings" in result
    
    def test_format_json_content(self):
        """Test JSON content formatting"""
        # Test updated_paragraph_latest_state priority
        json_obj = {
            "updated_paragraph_latest_state": "updated content",
            "paragraph_latest_state": "first content"
        }
        result = self.monitor.format_json_content(json_obj)
        assert result == "updated content"
        
        # Test only paragraph_latest_state
        json_obj = {
            "paragraph_latest_state": "first content"
        }
        result = self.monitor.format_json_content(json_obj)
        assert result == "first content"
        
        # Test case with neither
        json_obj = {"other_field": "other content"}
        result = self.monitor.format_json_content(json_obj)
        assert "cleaned output" in result
    
    def test_extract_node_content_old_format(self):
        """Test node content extraction in old format"""
        line = "[17:42:31] [INSIGHT] [FirstSummaryNode] cleaned output: This is test content"
        result = self.monitor.extract_node_content(line)
        assert result is not None
        assert "test content" in result
    
    def test_extract_node_content_new_format(self):
        """Test node content extraction in new format"""
        line = "2025-11-05 17:42:31.287 | INFO | InsightEngine.nodes.summary_node:process_output:131 - FirstSummaryNode cleaned output: This is test content"
        result = self.monitor.extract_node_content(line)
        assert result is not None
        assert "test content" in result
    
    def test_process_lines_for_json_old_format(self):
        """Test complete processing flow in old format"""
        lines = [
            test_data.OLD_FORMAT_NON_TARGET,  # Should be ignored
            test_data.OLD_FORMAT_MULTILINE_JSON[0],
            test_data.OLD_FORMAT_MULTILINE_JSON[1],
            test_data.OLD_FORMAT_MULTILINE_JSON[2],
        ]
        result = self.monitor.process_lines_for_json(lines, "insight")
        assert len(result) > 0
        assert any("multiline" in content for content in result)
    
    def test_process_lines_for_json_new_format(self):
        """Test complete processing flow in new format"""
        lines = [
            test_data.NEW_FORMAT_NON_TARGET,  # Should be ignored
            test_data.NEW_FORMAT_MULTILINE_JSON[0],
            test_data.NEW_FORMAT_MULTILINE_JSON[1],
            test_data.NEW_FORMAT_MULTILINE_JSON[2],
        ]
        result = self.monitor.process_lines_for_json(lines, "insight")
        assert len(result) > 0
        assert any("multiline" in content for content in result)
        assert any("JSON content" in content for content in result)
    
    def test_process_lines_for_json_mixed_format(self):
        """Test mixed format processing"""
        result = self.monitor.process_lines_for_json(test_data.MIXED_FORMAT_LINES, "insight")
        assert len(result) > 0
        assert any("mixed format content" in content for content in result)
    
    def test_is_valuable_content(self):
        """Test valuable content judgment"""
        # Content containing "cleaned output" should be valuable
        assert self.monitor.is_valuable_content(test_data.OLD_FORMAT_SINGLE_LINE_JSON) == True
        
        # Exclude short prompt messages
        assert self.monitor.is_valuable_content("JSON parsing successful") == False
        assert self.monitor.is_valuable_content("Successfully generated") == False
        
        # Empty lines should be filtered
        assert self.monitor.is_valuable_content("") == False
    
    def test_extract_json_content_real_query_engine(self):
        """Test QueryEngine actual production environment log extraction"""
        result = self.monitor.extract_json_content(test_data.REAL_QUERY_ENGINE_REFLECTION)
        assert result is not None
        assert "Luoyang Luanchuan Molybdenum Group" in result
        assert "CMOC" in result
        assert "updated_paragraph_latest_state" not in result  # Should have extracted content, not field name
    
    def test_extract_json_content_real_insight_engine(self):
        """Test InsightEngine actual production environment log extraction (including identifier lines)"""
        # First test if identifier lines can be recognized
        assert self.monitor.is_target_log_line(test_data.REAL_INSIGHT_ENGINE_REFLECTION[0]) == True  # Contains "generating reflection summary"
        assert self.monitor.is_target_log_line(test_data.REAL_INSIGHT_ENGINE_REFLECTION[1]) == True  # Contains nodes.summary_node
        
        # Test JSON extraction (start from second line, because first line is identifier line)
        json_lines = test_data.REAL_INSIGHT_ENGINE_REFLECTION[1:]  # Skip identifier line
        result = self.monitor.extract_json_content(json_lines)
        assert result is not None
        assert "key findings" in result
        assert "updated version" in result
        assert "Luoyang Molybdenum 2025 Q3" in result
    
    def test_extract_json_content_real_media_engine(self):
        """Test MediaEngine actual production environment log extraction (single-line JSON)"""
        # MediaEngine is single-line JSON format, need to split into lines first
        lines = test_data.REAL_MEDIA_ENGINE_REFLECTION.split('\n')
        
        # Test if identifier lines can be recognized
        assert self.monitor.is_target_log_line(lines[0]) == True  # Contains "generating reflection summary"
        assert self.monitor.is_target_log_line(lines[1]) == True  # Contains nodes.summary_node and "cleaned output"
        
        # Test JSON extraction (start from line containing JSON)
        json_line = lines[1]  # Second line contains complete single-line JSON
        result = self.monitor.extract_json_content([json_line])
        assert result is not None
        assert "comprehensive information overview" in result
        assert "Luoyang Molybdenum" in result
        assert "updated_paragraph_latest_state" not in result  # Should have extracted content
    
    def test_process_lines_for_json_real_query_engine(self):
        """Test complete processing flow of QueryEngine actual logs"""
        result = self.monitor.process_lines_for_json(test_data.REAL_QUERY_ENGINE_REFLECTION, "query")
        assert len(result) > 0
        assert any("Luoyang Luanchuan Molybdenum Group" in content for content in result)
    
    def test_process_lines_for_json_real_insight_engine(self):
        """Test complete processing flow of InsightEngine actual logs (including identifier lines)"""
        result = self.monitor.process_lines_for_json(test_data.REAL_INSIGHT_ENGINE_REFLECTION, "insight")
        assert len(result) > 0
        assert any("key findings" in content for content in result)
        assert any("updated version" in content for content in result)
    
    def test_process_lines_for_json_real_media_engine(self):
        """Test complete processing flow of MediaEngine actual logs (single-line JSON)"""
        # Split single-line string into multiple lines
        lines = test_data.REAL_MEDIA_ENGINE_REFLECTION.split('\n')
        result = self.monitor.process_lines_for_json(lines, "media")
        assert len(result) > 0
        assert any("comprehensive information overview" in content for content in result)
        assert any("Luoyang Molybdenum" in content for content in result)
    
    def test_filter_search_node_output(self):
        """Test filtering SearchNode output (Important: SearchNode should not enter forum)"""
        # SearchNode output contains "cleaned output: {", but does not contain target node pattern
        search_lines = test_data.SEARCH_NODE_FIRST_SEARCH
        result = self.monitor.process_lines_for_json(search_lines, "insight")
        # SearchNode output should be filtered, should not be captured
        assert len(result) == 0
    
    def test_filter_search_node_output_single_line(self):
        """Test filtering SearchNode single-line JSON output"""
        # SearchNode single-line JSON format
        search_line = test_data.SEARCH_NODE_REFLECTION_SEARCH
        result = self.monitor.process_lines_for_json([search_line], "insight")
        # SearchNode output should be filtered
        assert len(result) == 0
    
    def test_search_node_vs_summary_node_mixed(self):
        """Test mixed scenario: SearchNode and SummaryNode exist simultaneously, only capture SummaryNode"""
        lines = [
            # SearchNode output (should be filtered)
            "[11:16:35] 2025-11-06 11:16:35.567 | INFO | InsightEngine.nodes.search_node:process_output:97 - cleaned output: {",
            "[11:16:35] \"search_query\": \"test query\"",
            "[11:16:35] }",
            # SummaryNode output (should be captured)
            "[11:17:05] 2025-11-06 11:17:05.547 | INFO | InsightEngine.nodes.summary_node:process_output:131 - cleaned output: {",
            "[11:17:05] \"paragraph_latest_state\": \"This is summary content\"",
            "[11:17:05] }",
        ]
        result = self.monitor.process_lines_for_json(lines, "insight")
        # Should only capture SummaryNode output, not include SearchNode output
        assert len(result) > 0
        assert any("summary content" in content for content in result)
        # Ensure search query content is not included
        assert not any("search_query" in content for content in result)
        assert not any("test query" in content for content in result)
    
    def test_filter_error_logs_from_summary_node(self):
        """Test filtering SummaryNode error logs (Important: error logs should not enter forum)"""
        # JSON parsing failed error log
        assert self.monitor.is_target_log_line(test_data.SUMMARY_NODE_JSON_ERROR) == False
        
        # JSON repair failed error log
        assert self.monitor.is_target_log_line(test_data.SUMMARY_NODE_JSON_FIX_ERROR) == False
        
        # ERROR level log
        assert self.monitor.is_target_log_line(test_data.SUMMARY_NODE_ERROR_LOG) == False
        
        # Traceback error log
        for line in test_data.SUMMARY_NODE_TRACEBACK.split('\n'):
            assert self.monitor.is_target_log_line(line) == False
    
    def test_error_logs_not_captured(self):
        """Test error logs are not captured to forum"""
        error_lines = [
            test_data.SUMMARY_NODE_JSON_ERROR,
            test_data.SUMMARY_NODE_JSON_FIX_ERROR,
            test_data.SUMMARY_NODE_ERROR_LOG,
        ]
        
        for line in error_lines:
            result = self.monitor.process_lines_for_json([line], "media")
            # Error logs should not be captured
            assert len(result) == 0
    
    def test_mixed_valid_and_error_logs(self):
        """Test mixed scenario: valid logs and error logs exist simultaneously, only capture valid logs"""
        lines = [
            # Error logs (should be filtered)
            test_data.SUMMARY_NODE_JSON_ERROR,
            test_data.SUMMARY_NODE_JSON_FIX_ERROR,
            # Valid SummaryNode output (should be captured)
            "[11:55:31] 2025-11-06 11:55:31.762 | INFO | MediaEngine.nodes.summary_node:process_output:134 - cleaned output: {",
            "[11:55:31] \"paragraph_latest_state\": \"This is valid summary content\"",
            "[11:55:31] }",
        ]
        result = self.monitor.process_lines_for_json(lines, "media")
        # Should only capture valid logs, not include error logs
        assert len(result) > 0
        assert any("valid summary content" in content for content in result)
        # Ensure error information is not included
        assert not any("JSON parsing failed" in content for content in result)
        assert not any("JSON repair failed" in content for content in result)


def run_tests():
    """Run all tests"""
    import pytest
    
    # Run tests
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()

