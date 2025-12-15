# ForumEngine Log Parsing Tests

This test suite is used to test the log parsing functionality in `ForumEngine/monitor.py`, verifying its correctness under different log formats.

## Test Data

`forum_log_test_data.py` contains minimal examples of various log formats (forum log test data):

### Old Format ([HH:MM:SS])
- `OLD_FORMAT_SINGLE_LINE_JSON`: Single-line JSON
- `OLD_FORMAT_MULTILINE_JSON`: Multi-line JSON
- `OLD_FORMAT_FIRST_SUMMARY`: Log containing FirstSummaryNode
- `OLD_FORMAT_REFLECTION_SUMMARY`: Log containing ReflectionSummaryNode

### New Format (loguru default format)
- `NEW_FORMAT_SINGLE_LINE_JSON`: Single-line JSON
- `NEW_FORMAT_MULTILINE_JSON`: Multi-line JSON
- `NEW_FORMAT_FIRST_SUMMARY`: Log containing FirstSummaryNode
- `NEW_FORMAT_REFLECTION_SUMMARY`: Log containing ReflectionSummaryNode

### Complex Examples
- `COMPLEX_JSON_WITH_UPDATED`: JSON containing updated_paragraph_latest_state
- `COMPLEX_JSON_WITH_PARAGRAPH`: JSON with only paragraph_latest_state
- `MIXED_FORMAT_LINES`: Mixed format log lines

## Running Tests

### Using pytest (recommended)

```bash
# Install pytest (if not already installed)
pip install pytest

# Run all tests
pytest tests/test_monitor.py -v

# Run specific test
pytest tests/test_monitor.py::TestLogMonitor::test_extract_json_content_new_format_multiline -v
```

### Direct Run

```bash
python tests/test_monitor.py
```

## Test Coverage

Tests cover the following functions:

1. **is_target_log_line**: Identify target node log lines
2. **is_json_start_line**: Identify JSON start lines
3. **is_json_end_line**: Identify JSON end lines
4. **extract_json_content**: Extract JSON content (single and multi-line)
5. **format_json_content**: Format JSON content (prioritize extracting updated_paragraph_latest_state)
6. **extract_node_content**: Extract node content
7. **process_lines_for_json**: Complete processing flow
8. **is_valuable_content**: Judge whether content is valuable

## Expected Issues

Current code may not correctly handle loguru new format, main issues are:

1. **Timestamp Removal**: The regex `r'^\[\d{2}:\d{2}:\d{2}\]\s*'` in `extract_json_content()` can only match `[HH:MM:SS]` format, cannot match loguru's `YYYY-MM-DD HH:mm:ss.SSS` format

2. **Timestamp Matching**: The regex `r'\[\d{2}:\d{2}:\d{2}\]\s*(.+)'` in `extract_node_content()` also can only match old format

These tests will help identify these issues and guide subsequent code fixes.

