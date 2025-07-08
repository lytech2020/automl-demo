#!/usr/bin/env python3
"""
JSON to JSONL Converter

This script converts JSON files to JSONL (JSON Lines) format.
Supports various input formats:
- Single JSON object
- JSON array of objects
- Multiple JSON objects (one per line)
- Multiple JSON objects (concatenated)

Usage:
    python json2jsonl.py input.json output.jsonl
    python json2jsonl.py input.json output.jsonl --pretty
    python json2jsonl.py input.json output.jsonl --indent 2
"""

import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Union


def parse_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse JSON file and return a list of objects.
    Handles various JSON formats:
    - Single object
    - Array of objects
    - Multiple objects (one per line)
    - Multiple objects (concatenated)
    """
    objects = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # Try parsing as a single JSON object
        try:
            obj = json.loads(content)
            if isinstance(obj, dict):
                objects.append(obj)
                return objects
        except json.JSONDecodeError:
            pass
        
        # Try parsing as JSON array
        try:
            obj = json.loads(content)
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict):
                        objects.append(item)
                return objects
        except json.JSONDecodeError:
            pass
        
        # Try parsing as multiple JSON objects (one per line)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        objects.append(obj)
                except json.JSONDecodeError:
                    continue
        
        # If we found objects, return them
        if objects:
            return objects
        
        # Try parsing as concatenated JSON objects
        # This is a more complex case - we'll try to split by closing braces
        try:
            # Find all complete JSON objects
            brace_count = 0
            start_pos = 0
            for i, char in enumerate(content):
                if char == '{':
                    if brace_count == 0:
                        start_pos = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # We have a complete object
                        obj_str = content[start_pos:i+1]
                        try:
                            obj = json.loads(obj_str)
                            if isinstance(obj, dict):
                                objects.append(obj)
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)
    
    return objects


def write_jsonl_file(objects: List[Dict[str, Any]], output_path: str, 
                    pretty: bool = False, indent: int = None) -> None:
    """
    Write objects to JSONL file.
    
    Args:
        objects: List of dictionaries to write
        output_path: Output file path
        pretty: Whether to pretty-print JSON
        indent: Indentation level for pretty printing
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for obj in objects:
                if pretty:
                    json_str = json.dumps(obj, ensure_ascii=False, indent=indent)
                else:
                    json_str = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
                f.write(json_str + '\n')
        
        print(f"Successfully converted {len(objects)} objects to '{output_path}'")
        
    except Exception as e:
        print(f"Error writing to '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSON file to JSONL format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python json2jsonl.py input.json output.jsonl
  python json2jsonl.py input.json output.jsonl --pretty
  python json2jsonl.py input.json output.jsonl --indent 2
        """
    )
    
    parser.add_argument('input', help='Input JSON file path')
    parser.add_argument('output', help='Output JSONL file path')
    parser.add_argument('--pretty', action='store_true', 
                       help='Pretty-print JSON objects (one per line)')
    parser.add_argument('--indent', type=int, default=2,
                       help='Indentation level for pretty printing (default: 2)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Parse JSON file
    if args.verbose:
        print(f"Parsing JSON file: {args.input}")
    
    objects = parse_json_file(args.input)
    
    if not objects:
        print("Error: No valid JSON objects found in the input file.", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Found {len(objects)} JSON objects")
    
    # Write JSONL file
    write_jsonl_file(objects, args.output, args.pretty, args.indent if args.pretty else None)


if __name__ == '__main__':
    main()
