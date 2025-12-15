"""
Use the latest chapter JSON to rebind and render HTML reports.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from loguru import logger

# Ensure project modules can be found
sys.path.insert(0, str(Path(__file__).parent))

from ReportEngine.core import ChapterStorage, DocumentComposer
from ReportEngine.ir import IRValidator
from ReportEngine.renderers import HTMLRenderer
from ReportEngine.utils.config import settings


def find_latest_run_dir(chapter_root: Path):
    """
    Locate the latest run output directory under the chapter root directory.

    Scan all subdirectories under `chapter_root`, filter candidates containing `manifest.json`,
    sort by modification time in descending order and take the latest one. If directory does not exist
    or has no valid manifest, will log error and return None.

    Args:
        chapter_root: Chapter output root directory (usually settings.CHAPTER_OUTPUT_DIR)

    Returns:
        Path | None: Latest run directory path; None if not found.
    """
    if not chapter_root.exists():
        logger.error(f"Chapter directory does not exist: {chapter_root}")
        return None

    run_dirs = []
    for candidate in chapter_root.iterdir():
        if not candidate.is_dir():
            continue
        manifest_path = candidate / "manifest.json"
        if manifest_path.exists():
            run_dirs.append((candidate, manifest_path.stat().st_mtime))

    if not run_dirs:
        logger.error("No chapter directory with manifest.json found")
        return None

    latest_dir = sorted(run_dirs, key=lambda item: item[1], reverse=True)[0][0]
    logger.info(f"Found latest run directory: {latest_dir.name}")
    return latest_dir


def load_manifest(run_dir: Path):
    """
    Read manifest.json within a single run directory.

    On success, returns reportId and metadata dictionary; on read or parse failure
    will log error and return (None, None) to allow early termination by upper layer.

    Args:
        run_dir: Chapter output directory containing manifest.json

    Returns:
        tuple[str | None, dict | None]: (report_id, metadata)
    """
    manifest_path = run_dir / "manifest.json"
    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
        report_id = manifest.get("reportId") or run_dir.name
        metadata = manifest.get("metadata") or {}
        logger.info(f"Report ID: {report_id}")
        if manifest.get("createdAt"):
            logger.info(f"Creation time: {manifest['createdAt']}")
        return report_id, metadata
    except Exception as exc:
        logger.error(f"Failed to read manifest: {exc}")
        return None, None


def load_chapters(run_dir: Path):
    """
    Read all chapter JSON under the specified run directory.

    Will reuse ChapterStorage's load_chapters capability, automatically sort by order.
    After reading, print chapter count to confirm completeness.

    Args:
        run_dir: Single report's chapter directory

    Returns:
        list[dict]: Chapter JSON list (empty list if directory is empty)
    """
    storage = ChapterStorage(settings.CHAPTER_OUTPUT_DIR)
    chapters = storage.load_chapters(run_dir)
    logger.info(f"加载章节数: {len(chapters)}")
    return chapters


def validate_chapters(chapters):
    """
    Perform quick validation of chapter structure using IRValidator.

    Only log failed chapters and first three errors, will not interrupt process; purpose is to
    discover potential structural issues before rebinding.

    Args:
        chapters: Chapter JSON list
    """
    validator = IRValidator()
    invalid = []
    for chapter in chapters:
        ok, errors = validator.validate_chapter(chapter)
        if not ok:
            invalid.append((chapter.get("chapterId") or "unknown", errors))

    if invalid:
        logger.warning(f"There are {len(invalid)} chapters that failed structure validation, will continue rebinding:")
        for chapter_id, errors in invalid:
            preview = "; ".join(errors[:3])
            logger.warning(f"  - {chapter_id}: {preview}")
    else:
        logger.info("Chapter structure validation passed")


def stitch_document(report_id, metadata, chapters):
    """
    Stitch each chapter with metadata into a complete Document IR.

    Use DocumentComposer to uniformly handle chapter order, global metadata, etc., and print
    the number of completed chapters and charts.

    Args:
        report_id: Report ID (from manifest or directory name)
        metadata: Global metadata from manifest
        chapters: Loaded chapter list

    Returns:
        dict: Complete Document IR object
    """
    composer = DocumentComposer()
    document_ir = composer.build_document(report_id, metadata, chapters)
    logger.info(
        f"Rebinding completed: {len(document_ir.get('chapters', []))} chapters, "
        f"{count_charts(document_ir)} charts"
    )
    return document_ir


def count_charts(document_ir):
    """
    Count the total number of Chart.js charts in the entire Document IR.

    Will traverse blocks of each chapter, recursively find widget types starting with `chart.js`
    components, to quickly perceive chart scale.

    Args:
        document_ir: Complete Document IR

    Returns:
        int: Total chart count
    """
    chart_count = 0
    for chapter in document_ir.get("chapters", []):
        blocks = chapter.get("blocks", [])
        chart_count += _count_chart_blocks(blocks)
    return chart_count


def _count_chart_blocks(blocks):
    """
    Recursively count Chart.js components in block list.

    Compatible with nested blocks/list/table structure, ensuring all level charts are counted.

    Args:
        blocks: Block list at any level

    Returns:
        int: Counted chart.js chart quantity
    """
    count = 0
    for block in blocks:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "widget" and str(block.get("widgetType", "")).startswith("chart.js"):
            count += 1
        nested = block.get("blocks")
        if isinstance(nested, list):
            count += _count_chart_blocks(nested)
        if block.get("type") == "list":
            for item in block.get("items", []):
                if isinstance(item, list):
                    count += _count_chart_blocks(item)
        if block.get("type") == "table":
            for row in block.get("rows", []):
                for cell in row.get("cells", []):
                    if isinstance(cell, dict):
                        cell_blocks = cell.get("blocks", [])
                        if isinstance(cell_blocks, list):
                            count += _count_chart_blocks(cell_blocks)
    return count


def save_document_ir(document_ir, base_name, timestamp):
    """
    Save the rebound complete Document IR to disk.

    Write with `report_ir_{slug}_{timestamp}_regen.json` filename to
    `settings.DOCUMENT_IR_OUTPUT_DIR`, ensure directory exists and return save path.

    Args:
        document_ir: Rebound complete IR
        base_name: Safe file name fragment generated from topic/title
        timestamp: Timestamp string, used to distinguish multiple regenerations

    Returns:
        Path: Saved IR file path
    """
    output_dir = Path(settings.DOCUMENT_IR_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    ir_filename = f"report_ir_{base_name}_{timestamp}_regen.json"
    ir_path = output_dir / ir_filename
    ir_path.write_text(json.dumps(document_ir, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"IR已保存: {ir_path}")
    return ir_path


def render_html(document_ir, base_name, timestamp):
    """
    Use HTMLRenderer to render Document IR to HTML and save.

    After rendering, save to `final_reports/html`, print chart validation statistics, to facilitate
    observation of Chart.js data repair/failure situations.

    Args:
        document_ir: Rebound complete IR
        base_name: File name fragment (from report topic/title)
        timestamp: Timestamp string

    Returns:
        Path: Generated HTML file path
    """
    renderer = HTMLRenderer()
    html_content = renderer.render(document_ir)

    output_dir = Path(settings.OUTPUT_DIR) / "html"
    output_dir.mkdir(parents=True, exist_ok=True)
    html_filename = f"report_html_{base_name}_{timestamp}.html"
    html_path = output_dir / html_filename
    html_path.write_text(html_content, encoding="utf-8")

    file_size_mb = html_path.stat().st_size / (1024 * 1024)
    logger.info(f"HTML生成成功: {html_path} ({file_size_mb:.2f} MB)")
    logger.info(
        "图表验证统计: "
        f"total={renderer.chart_validation_stats.get('total', 0)}, "
        f"valid={renderer.chart_validation_stats.get('valid', 0)}, "
        f"repaired={renderer.chart_validation_stats.get('repaired_locally', 0) + renderer.chart_validation_stats.get('repaired_api', 0)}, "
        f"failed={renderer.chart_validation_stats.get('failed', 0)}"
    )
    return html_path


def build_slug(text):
    """
    Convert topic/title to file system safe fragment.

    Only retain letters/numbers/space/underscore/hyphen characters, unify spaces to underscores, and limit
    to maximum 60 characters to avoid overly long filenames.

    Args:
        text: Original topic or title

    Returns:
        str: Cleaned safe string
    """
    text = str(text or "report")
    sanitized = "".join(c for c in text if c.isalnum() or c in (" ", "-", "_")).strip()
    sanitized = sanitized.replace(" ", "_")
    return sanitized[:60] or "report"


def main():
    """
    Main entry point: read latest chapters, rebind IR and render HTML.

    Process:
        1) Find latest chapter run directory and read manifest;
        2) Load chapters and perform structure validation (warning only);
        3) Rebind complete IR, save IR copy;
        4) Render HTML and output paths with statistics.

    Returns:
        int: 0 for success, others for failure.
    """
    logger.info("🚀 Rebind and render HTML using latest LLM chapters")

    chapter_root = Path(settings.CHAPTER_OUTPUT_DIR)
    latest_run = find_latest_run_dir(chapter_root)
    if not latest_run:
        return 1

    report_id, metadata = load_manifest(latest_run)
    if not report_id or metadata is None:
        return 1

    chapters = load_chapters(latest_run)
    if not chapters:
        logger.error("No chapter JSON found, cannot rebind")
        return 1

    validate_chapters(chapters)

    document_ir = stitch_document(report_id, metadata, chapters)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = build_slug(
        metadata.get("query") or metadata.get("title") or metadata.get("reportId") or report_id
    )

    ir_path = save_document_ir(document_ir, base_name, timestamp)
    html_path = render_html(document_ir, base_name, timestamp)

    logger.info("")
    logger.info("🎉 HTML rebind and render complete")
    logger.info(f"IR file: {ir_path.resolve()}")
    logger.info(f"HTML file: {html_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
