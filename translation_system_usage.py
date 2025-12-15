#!/usr/bin/env python3
"""
Translation System Usage Examples and Testing

This script demonstrates how to use the automated Chinese-to-English
translation system for the BettaFish codebase.
"""

import os
import sys
from pathlib import Path
from chinese_translation_system import TranslationEngine, TranslationStats
from translation_config import load_config

def example_single_file_translation():
    """Example: Translate a single Python file"""
    print("=== Single File Translation Example ===")
    
    # Initialize translation engine
    engine = TranslationEngine(".")
    
    # Translate a specific file
    file_path = "MediaEngine/utils/config.py"
    if os.path.exists(file_path):
        results = engine.translate_file(file_path)
        print(f"Translated {file_path}")
        print(f"Found {len(results)} Chinese elements")
        for result in results:
            print(f"  Line {result.line_number}: {result.original_text} -> {result.translated_text}")
    else:
        print(f"File not found: {file_path}")

def example_directory_translation():
    """Example: Translate an entire directory"""
    print("\n=== Directory Translation Example ===")
    
    # Initialize translation engine
    engine = TranslationEngine(".")
    
    # Translate MediaEngine directory
    directory_path = "MediaEngine"
    if os.path.exists(directory_path):
        results = engine.translate_directory(directory_path, recursive=True)
        print(f"Processed {len(results)} files in {directory_path}")
        
        total_translations = sum(len(file_results) for file_results in results.values())
        print(f"Total Chinese elements translated: {total_translations}")
        
        # Generate report
        report_path = engine.generate_report()
        print(f"Translation report generated: {report_path}")
    else:
        print(f"Directory not found: {directory_path}")

def example_selective_translation():
    """Example: Translate specific file patterns"""
    print("\n=== Selective Translation Example ===")
    
    # Initialize translation engine
    engine = TranslationEngine(".")
    
    # Translate only Python and Markdown files
    file_patterns = ["*.py", "*.md"]
    results = engine.translate_directory(".", recursive=True, file_patterns=file_patterns)
    
    print(f"Processed files matching patterns: {file_patterns}")
    for file_path, file_results in results.items():
        if file_results:
            print(f"  {file_path}: {len(file_results)} translations")

def example_backup_and_rollback():
    """Example: Demonstrate backup and rollback functionality"""
    print("\n=== Backup and Rollback Example ===")
    
    # Create a test file with Chinese content
    test_file = "test_translation.py"
    test_content = '''# 测试文件
def 测试函数():
    """这是一个测试函数"""
    print("测试消息")
    return "测试结果"
'''
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Initialize translation engine
    engine = TranslationEngine(".")
    
    # Translate with backup
    results = engine.translate_file(test_file, create_backup=True)
    print(f"Translated {test_file} with backup")
    
    # Show backup files
    backup_dir = Path("translation_backups")
    if backup_dir.exists():
        backup_files = list(backup_dir.glob("*_backup*"))
        print(f"Created backups: {[f.name for f in backup_files]}")
    
    # Clean up
    os.remove(test_file)

def example_configuration_usage():
    """Example: Use custom configuration"""
    print("\n=== Configuration Usage Example ===")
    
    # Load custom configuration
    config = load_config("translation_config.json")
    
    # Initialize engine with custom settings
    engine = TranslationEngine(".", config)
    
    # Apply configuration-based translation
    print("Translation engine initialized with custom configuration:")
    print(f"  Source language: {config['translation_settings']['source_language']}")
    print(f"  Target language: {config['translation_settings']['target_language']}")
    print(f"  Create backups: {config['translation_settings']['create_backups']}")

def example_batch_processing():
    """Example: Batch processing with performance monitoring"""
    print("\n=== Batch Processing Example ===")
    
    # Initialize translation engine
    engine = TranslationEngine(".")
    
    # Process files in batches
    batch_size = 5
    processed_files = 0
    
    # Get all Python files
    python_files = list(Path(".").rglob("*.py"))
    total_files = len(python_files)
    
    print(f"Processing {total_files} Python files in batches of {batch_size}")
    
    for i in range(0, total_files, batch_size):
        batch = python_files[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} ({len(batch)} files)")
        
        for file_path in batch:
            results = engine.translate_file(str(file_path))
            processed_files += 1
            if results:
                print(f"  {file_path.name}: {len(results)} translations")
        
        print(f"Progress: {processed_files}/{total_files} files")
    
    print("Batch processing completed")

def example_edge_case_handling():
    """Example: Handle edge cases and mixed-language strings"""
    print("\n=== Edge Case Handling Example ===")
    
    # Create test file with edge cases
    edge_case_file = "edge_cases.py"
    edge_case_content = '''# Edge case examples
def mixed_language_function():
    """函数描述 with English and 中文 mixed"""
    # This comment has English and 中文 mixed
    message = "Error: 错误 occurred in process"
    url = "https://example.com/路径/参数"
    return message

# Cultural idiom example
def cultural_example():
    """这个函数处理"一石二鸟"的情况"""
    # Handle "一石二鸟" (kill two birds with one stone)
    return "multi_task_handling"
'''
    
    with open(edge_case_file, 'w', encoding='utf-8') as f:
        f.write(edge_case_content)
    
    # Initialize translation engine
    engine = TranslationEngine(".")
    
    # Translate edge cases
    results = engine.translate_file(edge_case_file)
    print(f"Processed edge cases in {edge_case_file}")
    
    for result in results:
        if result.requires_manual_review:
            print(f"  REVIEW NEEDED - Line {result.line_number}:")
            print(f"    Original: {result.original_text}")
            print(f"    Translated: {result.translated_text}")
            print(f"    Type: {result.translation_type}")
        else:
            print(f"  Auto-translated - Line {result.line_number}: {result.original_text}")
    
    # Clean up
    os.remove(edge_case_file)

def example_quality_assessment():
    """Example: Assess translation quality"""
    print("\n=== Quality Assessment Example ===")
    
    # Initialize translation engine
    engine = TranslationEngine(".")
    
    # Translate a file and assess quality
    test_file = "MediaEngine/utils/config.py"
    if os.path.exists(test_file):
        results = engine.translate_file(test_file)
        
        # Calculate quality metrics
        total_translations = len(results)
        high_confidence = sum(1 for r in results if r.confidence > 0.8)
        manual_review_required = sum(1 for r in results if r.requires_manual_review)
        
        print(f"Quality Assessment for {test_file}:")
        print(f"  Total translations: {total_translations}")
        print(f"  High confidence (>0.8): {high_confidence} ({high_confidence/total_translations*100:.1f}%)")
        print(f"  Manual review required: {manual_review_required} ({manual_review_required/total_translations*100:.1f}%)")
        
        # Show translation types
        type_counts = {}
        for result in results:
            type_counts[result.translation_type] = type_counts.get(result.translation_type, 0) + 1
        
        print(f"  Translation types:")
        for translation_type, count in type_counts.items():
            print(f"    {translation_type}: {count}")

def main():
    """Run all examples"""
    print("BettaFish Chinese-to-English Translation System Examples")
    print("=" * 60)
    
    try:
        example_single_file_translation()
        example_directory_translation()
        example_selective_translation()
        example_backup_and_rollback()
        example_configuration_usage()
        example_batch_processing()
        example_edge_case_handling()
        example_quality_assessment()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()