"""
Regenerate PDF of latest report using new SVG vector chart functionality
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

from ReportEngine.renderers import PDFRenderer

def find_latest_report():
    """
    Find the latest report IR JSON in `final_reports/ir`.

    Select the first one in descending order by modification time, log error and return None if directory or file is missing.

    Returns:
        Path | None: Latest IR file path; None if not found.
    """
    ir_dir = Path("final_reports/ir")

    if not ir_dir.exists():
        logger.error(f"Report directory does not exist: {ir_dir}")
        return None

    # Get all JSON files and sort by modification time
    json_files = sorted(ir_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not json_files:
        logger.error("No report files found")
        return None

    latest_file = json_files[0]
    logger.info(f"Found latest report: {latest_file.name}")

    return latest_file

def load_document_ir(file_path):
    """
    Read Document IR JSON from specified path and count chapters/charts.

    Return None on parse failure; on success will print chapter and chart counts to confirm
    the scale of the input report.

    Args:
        file_path: IR file path

    Returns:
        dict | None: Parsed Document IR; None on failure.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            document_ir = json.load(f)

        logger.info(f"Successfully loaded report: {file_path.name}")

        # Count chart quantity
        chart_count = 0
        chapters = document_ir.get('chapters', [])

        def count_charts(blocks):
            """Recursively count Chart.js charts in block list"""
            count = 0
            for block in blocks:
                if isinstance(block, dict):
                    if block.get('type') == 'widget' and block.get('widgetType', '').startswith('chart.js'):
                        count += 1
                    # Recursively handle nested blocks
                    nested = block.get('blocks')
                    if isinstance(nested, list):
                        count += count_charts(nested)
            return count

        for chapter in chapters:
            blocks = chapter.get('blocks', [])
            chart_count += count_charts(blocks)

        logger.info(f"Report contains {len(chapters)} chapters, {chart_count} charts")

        return document_ir

    except Exception as e:
        logger.error(f"Failed to load report: {e}")
        return None

def generate_pdf_with_vector_charts(document_ir, output_path):
    """
    Use PDFRenderer to render Document IR to PDF containing SVG vector charts.

    Enable layout optimization, output file size and success message after generation; return None on exception.

    Args:
        document_ir: Complete Document IR
        output_path: Target PDF path

    Returns:
        Path | None: Generated PDF path on success, None on failure.
    """
    try:
        logger.info("=" * 60)
        logger.info("Starting PDF generation (with vector charts)")
        logger.info("=" * 60)

        # Create PDF renderer
        renderer = PDFRenderer()

        # Render PDF
        result_path = renderer.render_to_pdf(
            document_ir,
            output_path,
            optimize_layout=True
        )

        logger.info("=" * 60)
        logger.info(f"✓ PDF generation successful: {result_path}")
        logger.info("=" * 60)

        # Display file size
        file_size = result_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        logger.info(f"File size: {size_mb:.2f} MB")

        return result_path

    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        return None

def main():
    """
    Main entry point: regenerate vector PDF of latest report.

    Steps:
        1) Find latest IR file;
        2) Read and count report structure;
        3) Construct output filename and ensure directory exists;
        4) Call render function to generate PDF, output path and feature description.

    Returns:
        int: 0 for success, non-zero for failure.
    """
    logger.info("🚀 Regenerate latest report PDF using SVG vector charts")
    logger.info("")

    # 1. Find latest report
    latest_report = find_latest_report()
    if not latest_report:
        logger.error("No report file found")
        return 1

    # 2. Load report data
    document_ir = load_document_ir(latest_report)
    if not document_ir:
        logger.error("Failed to load report")
        return 1

    # 3. Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = latest_report.stem.replace("report_ir_", "")
    output_filename = f"report_vector_{report_name}_{timestamp}.pdf"
    output_path = Path("final_reports/pdf") / output_filename

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output path: {output_path}")
    logger.info("")

    # 4. Generate PDF
    result = generate_pdf_with_vector_charts(document_ir, output_path)

    if result:
        logger.info("")
        logger.info("🎉 PDF generation complete!")
        logger.info("")
        logger.info("Feature description:")
        logger.info("  ✓ Charts rendered in SVG vector format")
        logger.info("  ✓ Supports infinite scaling without distortion")
        logger.info("  ✓ Preserves complete chart visual effects")
        logger.info("  ✓ Line charts, bar charts, pie charts are all vector curves")
        logger.info("")
        logger.info(f"PDF file location: {result.absolute()}")
        return 0
    else:
        logger.error("❌ PDF generation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
