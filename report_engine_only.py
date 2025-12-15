#!/usr/bin/env python
"""
Report Engine Command Line Version

This is a command-line report generation program that doesn't require a frontend.
Main process:
1. Check PDF dependencies
2. Get latest log, md files
3. Directly call Report Engine to generate reports (skip file addition review)
4. Automatically save HTML and PDF (if dependencies available) to final_reports/

Usage:
    python report_engine_only.py [options]

Options:
    --query QUERY     Specify report topic (optional, default extracted from filename)
    --skip-pdf        Skip PDF generation (even if dependencies available)
    --verbose         Show detailed logs
    --help            Show help information
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from loguru import logger

# Global configuration
VERBOSE = False

# Configure logging
def setup_logger(verbose: bool = False):
    """Set up logging configuration"""
    global VERBOSE
    VERBOSE = verbose

    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="DEBUG" if verbose else "INFO"
    )


def check_dependencies() -> tuple[bool, Optional[str]]:
    """
    Check system dependencies required for PDF generation

    Returns:
        tuple: (is_available: bool, message: str)
            - is_available: Whether PDF functionality is available
            - message: Dependency check result message
    """
    logger.info("=" * 70)
    logger.info("Step 1/4: Check system dependencies")
    logger.info("=" * 70)

    try:
        from ReportEngine.utils.dependency_check import check_pango_available
        is_available, message = check_pango_available()

        if is_available:
            logger.success("✓ PDF dependency check passed, will generate both HTML and PDF files")
        else:
            logger.warning("⚠ PDF dependencies missing, will generate HTML files only")
            logger.info("\n" + message)

        return is_available, message
    except Exception as e:
        logger.error(f"Dependency check failed: {e}")
        return False, str(e)


def get_latest_engine_reports() -> Dict[str, str]:
    """
    Get latest report files from three engine directories

    Returns:
        Dict[str, str]: Mapping from engine name to file path
    """
    logger.info("\n" + "=" * 70)
    logger.info("Step 2/4: Get latest analysis engine reports")
    logger.info("=" * 70)

    # Define three engine directories
    directories = {
        'insight': 'insight_engine_streamlit_reports',
        'media': 'media_engine_streamlit_reports',
        'query': 'query_engine_streamlit_reports'
    }

    latest_files = {}

    for engine, directory in directories.items():
        if not os.path.exists(directory):
            logger.warning(f"⚠ {engine.capitalize()} Engine directory does not exist: {directory}")
            continue

        # Get all .md files
        md_files = [f for f in os.listdir(directory) if f.endswith('.md')]

        if not md_files:
            logger.warning(f"⚠ No .md files found in {engine.capitalize()} Engine directory")
            continue

        # Get latest file
        latest_file = max(
            md_files,
            key=lambda x: os.path.getmtime(os.path.join(directory, x))
        )
        latest_path = os.path.join(directory, latest_file)
        latest_files[engine] = latest_path

        logger.info(f"✓ Found {engine.capitalize()} Engine latest report")

    if not latest_files:
        logger.error("❌ No engine report files found, please run analysis engines first to generate reports")
        sys.exit(1)

    logger.info(f"\nFound {len(latest_files)} latest reports from engines")

    return latest_files


def confirm_file_selection(latest_files: Dict[str, str]) -> bool:
    """
    Confirm with user whether selected files are correct

    Args:
        latest_files: Mapping from engine name to file path

    Returns:
        bool: Return True if user confirms, otherwise False
    """
    logger.info("\n" + "=" * 70)
    logger.info("Please confirm the following selected files:")
    logger.info("=" * 70)

    for engine, file_path in latest_files.items():
        filename = os.path.basename(file_path)
        # Get file modification time
        mtime = os.path.getmtime(file_path)
        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

        logger.info(f"  {engine.capitalize()} Engine:")
        logger.info(f"    Filename: {filename}")
        logger.info(f"    Path: {file_path}")
        logger.info(f"    Modified time: {mtime_str}")
        logger.info("")

    logger.info("=" * 70)

    # Prompt user for confirmation
    try:
        response = input("Use above files to generate report? [Y/n]: ").strip().lower()

        # Default is y, so empty input or y both mean confirmation
        if response == '' or response == 'y' or response == 'yes':
            logger.success("✓ User confirmed, continuing report generation")
            return True
        else:
            logger.warning("✗ User cancelled operation")
            return False
    except (KeyboardInterrupt, EOFError):
        logger.warning("\n✗ User cancelled operation")
        return False


def load_engine_reports(latest_files: Dict[str, str]) -> list[str]:
    """
    Load engine report content

    Args:
        latest_files: Mapping from engine name to file path

    Returns:
        list[str]: Report content list
    """
    reports = []

    for engine, file_path in latest_files.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                reports.append(content)
                logger.debug(f"Loaded {engine} report, length: {len(content)} characters")
        except Exception as e:
            logger.error(f"Failed to load {engine} report: {e}")

    return reports


def extract_query_from_reports(latest_files: Dict[str, str]) -> str:
    """
    Extract query topic from report filenames

    Args:
        latest_files: Mapping from engine name to file path

    Returns:
        str: Extracted query topic
    """
    # Try to extract topic from filename
    for engine, file_path in latest_files.items():
        filename = os.path.basename(file_path)
        # Assume filename format is: report_topic_timestamp.md
        if '_' in filename:
            parts = filename.replace('.md', '').split('_')
            if len(parts) >= 2:
                # Extract middle part as topic
                topic = '_'.join(parts[1:-1]) if len(parts) > 2 else parts[1]
                if topic:
                    return topic

    # If extraction fails, return default value
    return "Comprehensive Analysis Report"


def generate_report(reports: list[str], query: str, pdf_available: bool) -> Dict[str, Any]:
    """
    Call Report Engine to generate report

    Args:
        reports: Report content list
        query: Report topic
        pdf_available: Whether PDF functionality is available

    Returns:
        Dict[str, Any]: Dictionary containing generation results
    """
    logger.info("\n" + "=" * 70)
    logger.info("Step 3/4: Generate comprehensive report")
    logger.info("=" * 70)
    logger.info(f"Report topic: {query}")
    logger.info(f"Input report count: {len(reports)}")

    try:
        from ReportEngine.agent import ReportAgent

        # Initialize Report Agent
        logger.info("Initializing Report Engine...")
        agent = ReportAgent()

        # Define streaming event handler
        def stream_handler(event_type: str, payload: Dict[str, Any]):
            """Handle Report Engine's streaming events"""
            if event_type == 'stage':
                stage = payload.get('stage', '')
                if stage == 'agent_start':
                    logger.info(f"Starting report generation: {payload.get('report_id', '')}")
                elif stage == 'template_selected':
                    logger.info(f"✓ Template selected: {payload.get('template', '')}")
                elif stage == 'template_sliced':
                    logger.info(f"✓ Template parsing complete, {payload.get('section_count', 0)} sections total")
                elif stage == 'layout_designed':
                    logger.info(f"✓ Document layout design complete")
                    logger.info(f"  Title: {payload.get('title', '')}")
                elif stage == 'word_plan_ready':
                    logger.info(f"✓ Word count planning complete, target chapter count: {payload.get('chapter_targets', 0)}")
                elif stage == 'chapters_compiled':
                    logger.info(f"✓ Chapter generation complete, {payload.get('chapter_count', 0)} chapters total")
                elif stage == 'html_rendered':
                    logger.info(f"✓ HTML rendering complete")
                elif stage == 'report_saved':
                    logger.info(f"✓ Report saved")
            elif event_type == 'chapter_status':
                chapter_id = payload.get('chapterId', '')
                title = payload.get('title', '')
                status = payload.get('status', '')
                if status == 'generating':
                    logger.info(f"  Generating chapter: {title}")
                elif status == 'completed':
                    attempt = payload.get('attempt', 1)
                    warning = payload.get('warning', '')
                    if warning:
                        logger.warning(f"  ✓ Chapter complete: {title} (attempt {attempt}, {payload.get('warningMessage', '')})")
                    else:
                        logger.success(f"  ✓ Chapter complete: {title}")
            elif event_type == 'error':
                logger.error(f"Error: {payload.get('message', '')}")

        # Generate report
        logger.info("Starting report generation, this may take several minutes...")
        result = agent.generate_report(
            query=query,
            reports=reports,
            forum_logs="",  # Do not use forum logs
            custom_template="",  # Use automatic template selection
            save_report=True,  # Automatically save report
            stream_handler=stream_handler
        )

        logger.success("✓ Report generation successful!")
        return result

    except Exception as e:
        logger.exception(f"❌ Report generation failed: {e}")
        sys.exit(1)


def save_pdf(document_ir_path: str, query: str) -> Optional[str]:
    """
    Generate and save PDF from IR file

    Args:
        document_ir_path: Document IR file path
        query: Report topic

    Returns:
        Optional[str]: PDF file path, None if failed
    """
    logger.info("\nGenerating PDF file...")

    try:
        # Read IR data
        with open(document_ir_path, 'r', encoding='utf-8') as f:
            document_ir = json.load(f)

        # Create PDF renderer
        from ReportEngine.renderers import PDFRenderer
        renderer = PDFRenderer()

        # Prepare output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = "".join(
            c for c in query if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        query_safe = query_safe.replace(" ", "_")[:30] or "report"

        pdf_dir = Path("final_reports") / "pdf"
        pdf_dir.mkdir(parents=True, exist_ok=True)

        pdf_filename = f"final_report_{query_safe}_{timestamp}.pdf"
        pdf_path = pdf_dir / pdf_filename

        # Use render_to_pdf method to directly generate PDF file (consistent with regenerate_latest_pdf.py)
        logger.info(f"Starting PDF rendering: {pdf_path}")
        result_path = renderer.render_to_pdf(
            document_ir,
            pdf_path,
            optimize_layout=True
        )

        # Display file size
        file_size = result_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        logger.success(f"✓ PDF 已保存: {pdf_path}")
        logger.info(f"  文件大小: {size_mb:.2f} MB")

        return str(result_path)

    except Exception as e:
        logger.exception(f"❌ PDF generation failed: {e}")
        return None


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Report Engine Command Line Version - Frontend-free report generation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python report_engine_only.py
  python report_engine_only.py --query "Civil Engineering Industry Analysis"
  python report_engine_only.py --skip-pdf --verbose

Note:
  The program will automatically get the latest report files from three engine directories,
  does not perform file addition review, directly generates comprehensive reports.
        """
    )

    parser.add_argument(
        '--query',
        type=str,
        default=None,
        help='Specify report topic (default auto-extracted from filename)'
    )

    parser.add_argument(
        '--skip-pdf',
        action='store_true',
        help='Skip PDF generation (even if system supports it)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed log information'
    )

    return parser.parse_args()


def main():
    """Main function"""
    # Parse command line arguments
    args = parse_arguments()

    # Set up logging
    setup_logger(verbose=args.verbose)

    logger.info("\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " " * 20 + "Report Engine Command Line Version" + " " * 24 + "║")
    logger.info("╚" + "═" * 68 + "╝")
    logger.info("\n")

    # Step 1: Check dependencies
    pdf_available, _ = check_dependencies()

    # If user specifies skip PDF, disable PDF generation
    if args.skip_pdf:
        logger.info("User specified --skip-pdf, will skip PDF generation")
        pdf_available = False

    # Step 2: Get latest files
    latest_files = get_latest_engine_reports()

    # Confirm file selection
    if not confirm_file_selection(latest_files):
        logger.info("\nProgram exited")
        sys.exit(0)

    # Load report content
    reports = load_engine_reports(latest_files)

    if not reports:
        logger.error("❌ 未能加载任何报告内容")
        sys.exit(1)

    # Extract or use specified query topic
    query = args.query if args.query else extract_query_from_reports(latest_files)
    logger.info(f"Using report topic: {query}")

    # Step 3: Generate report
    result = generate_report(reports, query, pdf_available)

    # Step 4: Save files
    logger.info("\n" + "=" * 70)
    logger.info("Step 4/4: Save generated files")
    logger.info("=" * 70)

    # HTML has been automatically saved in generate_report
    html_path = result.get('report_filepath', '')
    if html_path:
        logger.success(f"✓ HTML 已保存: {result.get('report_relative_path', html_path)}")

    # If PDF dependencies available, generate and save PDF
    if pdf_available:
        ir_path = result.get('ir_filepath', '')
        if ir_path and os.path.exists(ir_path):
            pdf_path = save_pdf(ir_path, query)
        else:
            logger.warning("⚠ IR file not found, cannot generate PDF")
    else:
        logger.info("⚠ Skipping PDF generation (missing system dependencies or user specified skip)")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.success("✓ Report generation complete!")
    logger.info("=" * 70)
    logger.info(f"Report ID: {result.get('report_id', 'N/A')}")
    logger.info(f"HTML file: {result.get('report_relative_path', 'N/A')}")
    if pdf_available:
        logger.info(f"PDF file: in final_reports/pdf/ directory")
    logger.info("=" * 70)
    logger.info("\nProgram ended")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\nUser interrupted program")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"\nProgram exited abnormally: {e}")
        sys.exit(1)
