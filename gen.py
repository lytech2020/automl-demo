#!/usr/bin/env python3
"""
Boiler Dataset JSONL Generator

This script generates a JSONL file from the boiler_dataset directory,
combining image file paths with their corresponding labels from the CSV file.
"""

import os
import json
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL (Pillow) not available. Image dimensions will be 'unknown'.")
    print("Install with: pip install Pillow")


def load_labels_from_csv(csv_path: str) -> Dict[str, Dict[str, str]]:
    """
    Load labels from CSV file and return a dictionary mapping image paths to label info.
    
    Args:
        csv_path: Path to the CSV file containing labels
        
    Returns:
        Dictionary mapping image_path to label information
    """
    labels = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_path = row['image_path']
                labels[image_path] = {
                    'temperature_class': row['temperature_class'],
                    'temperature_value': row['temperature_value'],
                    'timestamp': row['timestamp']
                }
    except FileNotFoundError:
        print(f"Warning: CSV file '{csv_path}' not found. Will generate entries without labels.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        
    return labels


def get_image_details(image_path: str, dataset_dir: str = "") -> Dict[str, str]:
    """
    Get image details from file extension and actual dimensions.
    
    Args:
        image_path: Path to the image file
        dataset_dir: Dataset directory path for constructing full path
        
    Returns:
        Dictionary with image format and actual dimensions
    """
    file_ext = Path(image_path).suffix.lower()
    format_map = {
        '.png': 'png',
        '.jpg': 'jpeg',
        '.jpeg': 'jpeg',
        '.gif': 'gif',
        '.bmp': 'bmp',
        '.tiff': 'tiff',
        '.tif': 'tiff'
    }
    
    image_format = format_map.get(file_ext, 'unknown')
    width = "unknown"
    height = "unknown"
    
    # Try to get actual image dimensions if PIL is available
    if PIL_AVAILABLE and dataset_dir:
        try:
            full_path = os.path.join(dataset_dir, image_path)
            with Image.open(full_path) as img:
                width = str(img.width)
                height = str(img.height)
        except Exception as e:
            # If we can't read the image, keep width/height as "unknown"
            pass
    
    return {
        "format": image_format,
        "width": f"{width}px",
        "height": f"{height}px"
    }


def scan_dataset_directory(dataset_dir: str) -> List[Tuple[str, str]]:
    """
    Scan the dataset directory and return list of (subdir, filename) tuples.
    
    Args:
        dataset_dir: Path to the dataset directory
        
    Returns:
        List of tuples containing (subdirectory, filename)
    """
    files = []
    
    try:
        for subdir in os.listdir(dataset_dir):
            subdir_path = os.path.join(dataset_dir, subdir)
            if os.path.isdir(subdir_path) and not subdir.startswith('.'):
                for filename in os.listdir(subdir_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
                        files.append((subdir, filename))
    except Exception as e:
        print(f"Error scanning dataset directory: {e}")
        
    return files


def generate_jsonl_entries(files: List[Tuple[str, str]], 
                          labels: Dict[str, Dict[str, str]], 
                          base_url: str, dataset_dir: str) -> List[Dict]:
    """
    Generate JSONL entries for all files.
    
    Args:
        files: List of (subdir, filename) tuples
        labels: Dictionary of label information
        base_url: Base URL for image paths
        dataset_dir: Dataset directory path for image processing
        
    Returns:
        List of dictionaries representing JSONL entries
    """
    entries = []
    
    for subdir, filename in files:
        # Create relative path as used in CSV
        relative_path = f"{subdir}/{filename}"
        
        # Create full Azure ML URL
        image_url = f"{base_url}boiler_dataset/{relative_path}"
        
        # Get label information
        label_info = labels.get(relative_path, {})
        temperature_class = label_info.get('temperature_class', 'unknown')
        temperature_value = label_info.get('temperature_value', '0.0')
        timestamp = label_info.get('timestamp', '')
        
        # Get image details with actual dimensions
        image_details = get_image_details(relative_path, dataset_dir)
        
        # Create entry
        entry = {
            "image_url": image_url,
            "image_details": image_details,
            "label": temperature_class,
            "temperature_value": temperature_value,
            "timestamp": timestamp,
            "relative_path": relative_path
        }
        
        entries.append(entry)
    
    return entries


def write_jsonl_file(entries: List[Dict], output_path: str, pretty: bool = False) -> None:
    """
    Write entries to JSONL file.
    
    Args:
        entries: List of dictionaries to write
        output_path: Output file path
        pretty: Whether to pretty-print JSON
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                if pretty:
                    json_str = json.dumps(entry, ensure_ascii=False, indent=2)
                else:
                    json_str = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))
                f.write(json_str + '\n')
        
        print(f"Successfully generated {len(entries)} entries to '{output_path}'")
        
    except Exception as e:
        print(f"Error writing to '{output_path}': {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate JSONL file from boiler dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 gen.py --output boiler_dataset.jsonl
  python3 gen.py --output boiler_dataset.jsonl --pretty
  python3 gen.py --output boiler_dataset.jsonl --base-url "custom://base/path/"
        """
    )
    
    parser.add_argument('--dataset-dir', default='boiler_dataset',
                       help='Dataset directory path (default: boiler_dataset)')
    parser.add_argument('--csv-file', default='boiler_dataset/boiler_labels_100.csv',
                       help='CSV file with labels (default: boiler_dataset/boiler_labels_100.csv)')
    parser.add_argument('--output', required=True,
                       help='Output JSONL file path')
    parser.add_argument('--base-url', 
                       default='azureml://subscriptions/4e3d915a-bc68-42e8-8bc1-af28dd4f8d91/resourcegroups/lytech-rg/workspaces/lytech-machine-learning-workspace/datastores/workspaceblobstore/paths/LocalUpload/aeafb12c43181b9788690d5db006e885/',
                       help='Base URL for image paths')
    parser.add_argument('--pretty', action='store_true',
                       help='Pretty-print JSON objects (one per line)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate dataset directory
    if not os.path.exists(args.dataset_dir):
        print(f"Error: Dataset directory '{args.dataset_dir}' does not exist.")
        return 1
    
    # Load labels from CSV
    if args.verbose:
        print(f"Loading labels from: {args.csv_file}")
    
    labels = load_labels_from_csv(args.csv_file)
    
    if args.verbose:
        print(f"Loaded {len(labels)} label entries")
    
    # Scan dataset directory
    if args.verbose:
        print(f"Scanning dataset directory: {args.dataset_dir}")
    
    files = scan_dataset_directory(args.dataset_dir)
    
    if not files:
        print("Error: No image files found in dataset directory.")
        return 1
    
    if args.verbose:
        print(f"Found {len(files)} image files")
    
    # Generate JSONL entries
    if args.verbose:
        print("Generating JSONL entries...")
    
    entries = generate_jsonl_entries(files, labels, args.base_url, args.dataset_dir)
    
    # Write JSONL file
    write_jsonl_file(entries, args.output, args.pretty)
    
    # Print summary
    print(f"\nSummary:")
    print(f"- Total files processed: {len(entries)}")
    print(f"- Files with labels: {sum(1 for e in entries if e['label'] != 'unknown')}")
    print(f"- Files without labels: {sum(1 for e in entries if e['label'] == 'unknown')}")
    
    # Count by temperature class
    class_counts = {}
    for entry in entries:
        label = entry['label']
        class_counts[label] = class_counts.get(label, 0) + 1
    
    print(f"\nTemperature class distribution:")
    for label, count in sorted(class_counts.items()):
        print(f"- {label}: {count}")
    
    return 0


if __name__ == '__main__':
    exit(main())
