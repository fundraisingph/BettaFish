# ReportEngine - Intelligent Report Generation

## Package Identity
ReportEngine is the intelligent report generation component of BettaFish multi-agent system. It aggregates outputs from all analysis agents, performs template-based report generation, and renders interactive HTML and PDF reports with charts and visualizations.

Primary tech/framework: Python with Flask interface, WeasyPrint for PDF generation, Plotly for charts, and IR (Intermediate Representation) for content management.

## Setup & Run
```bash
# Start ReportEngine standalone
python report_engine_only.py --query "Your analysis topic"

# Or start via main system (integrated mode)
python app.py  # ReportEngine is automatically integrated
```

## Patterns & Conventions

### File Organization
- `agent.py` - Main ReportAgent implementation
- `flask_interface.py` - Flask API endpoints for report generation
- `core/` - Core functionality (template parser, chapter storage, document stitching)
- `ir/` - Intermediate Representation schema and validation
- `nodes/` - Report generation pipeline nodes
- `renderers/` - HTML and PDF rendering engines
- `report_template/` - Markdown template library
- `utils/` - Configuration, JSON parsing, chart validation

### Report Generation Pipeline
✅ DO: Follow the structured report generation pipeline:
```python
class ReportAgent:
    def __init__(self):
        self.template_selector = TemplateSelectionNode()
        self.layout_designer = DocumentLayoutNode()
        self.chapter_generator = ChapterGenerationNode()
        self.html_renderer = HTMLRenderer()
        self.pdf_renderer = PDFRenderer()
    
    def generate_report(self, agent_outputs, forum_logs):
        # 1. Select appropriate template
        template = self.template_selector.select(agent_outputs)
        
        # 2. Design document layout
        layout = self.layout_designer.design(template, agent_outputs)
        
        # 3. Generate chapters
        chapters = self.chapter_generator.generate(layout, agent_outputs)
        
        # 4. Create IR (Intermediate Representation)
        ir = self.create_ir(chapters, layout)
        
        # 5. Render to HTML/PDF
        html_report = self.html_renderer.render(ir)
        pdf_report = self.pdf_renderer.render(html_report)
        
        return html_report, pdf_report
```

❌ DON'T: Generate reports without structured templates:
```python
# Avoid this pattern
def generate_simple_report(self, content):
    # Direct HTML generation without template system
    html = f"<html><body>{content}</body></html>"
    return html
```

### Template Usage
✅ DO: Use template system for consistent report structure:
```python
from ReportEngine.core.template_parser import TemplateParser

# Example from ReportEngine/core/template_parser.py
parser = TemplateParser()
template = parser.parse_template("企业品牌声誉分析报告.md")
sections = parser.extract_sections(template)
layout = parser.generate_layout(sections)
```

### IR (Intermediate Representation) Management
✅ DO: Use IR for content-rendering decoupling:
```python
from ReportEngine.ir.schema import BlockType, IRBlock
from ReportEngine.ir.validator import IRValidator

# Create IR structure
ir_blocks = [
    IRBlock(type=BlockType.HEADING, content="Report Title"),
    IRBlock(type=BlockType.TEXT, content="Report content..."),
    IRBlock(type=BlockType.CHART, content=chart_data)
]

# Validate IR before rendering
validator = IRValidator()
if validator.validate(ir_blocks):
    # Safe to render
    html = renderer.render(ir_blocks)
```

## Touch Points / Key Files

- Report agent: `agent.py` - Main ReportAgent class
- Flask interface: `flask_interface.py` - API endpoints for report generation
- Template parser: `core/template_parser.py` - Markdown template processing
- Chapter storage: `core/chapter_storage.py` - Chapter content management
- Document stitching: `core/stitcher.py` - IR assembly and metadata
- HTML renderer: `renderers/html_renderer.py` - Interactive HTML generation
- PDF renderer: `renderers/pdf_renderer.py` - PDF export with layout optimization
- IR schema: `ir/schema.py` - IR structure definitions
- Configuration: `utils/config.py` - Engine-specific settings

## JIT Index Hints

- Find report generation pipeline: `rg -n "class.*Node" nodes/`
- Find template implementations: `rg -n "\.md$" report_template/`
- Find rendering engines: `rg -n "class.*Renderer" renderers/`
- Find IR schema: `rg -n "BlockType\|IRBlock" ir/schema.py`
- Find Flask endpoints: `rg -n "@.*route" flask_interface.py`
- Find chart generation: `rg -n "plotly\|chart\|visualization" renderers/`
- Find PDF optimization: `rg -n "layout\|weasyprint\|css" renderers/pdf_layout_optimizer.py`

## Common Gotchas

- Report generation requires all agent outputs to be complete
- Templates must follow specific Markdown structure for proper parsing
- IR validation is mandatory before rendering to prevent errors
- PDF generation requires WeasyPrint system dependencies
- Large reports need chunked processing to avoid memory issues
- Chart data must be properly formatted for Plotly integration

## Pre-PR Checks

```bash
# Run ReportEngine tests
python -m pytest tests/test_report_engine.py -v

# Test template parsing
python -c "from ReportEngine.core.template_parser import TemplateParser; TemplateParser().test_templates()"

# Validate IR system
python -c "from ReportEngine.ir.validator import IRValidator; IRValidator().test_validation()"

# Test PDF generation
python -c "from ReportEngine.renderers.pdf_renderer import PDFRenderer; PDFRenderer().test_dependencies()"