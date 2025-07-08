#!/usr/bin/env python3
"""
Boiler Temperature Classification Training Script

This script trains a machine learning model to classify boiler temperature
from images using the boiler dataset.
"""

import os
import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(data_path: str) -> tuple:
    """
    Load and prepare the boiler dataset.
    
    Args:
        data_path: Path to the data directory
        
    Returns:
        Tuple of (X, y) where X is features and y is labels
    """
    logger.info(f"Loading data from: {data_path}")
    
    # Load JSONL file
    jsonl_path = os.path.join(data_path, "boiler_dataset.jsonl")
    if not os.path.exists(jsonl_path):
        raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")
    
    data = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    
    logger.info(f"Loaded {len(data)} samples")
    
    # Extract features and labels
    X = []
    y = []
    
    for item in data:
        # Extract image path
        image_path = item['relative_path']
        label = item['label']
        temperature_value = float(item['temperature_value'])
        
        # For now, we'll use temperature value as a feature
        # In a real scenario, you'd extract features from the images
        X.append([temperature_value])
        y.append(label)
    
    return np.array(X), np.array(y)


def train_model(X_train: np.ndarray, y_train: np.ndarray, 
                X_test: np.ndarray, y_test: np.ndarray,
                output_dir: str, **kwargs) -> dict:
    """
    Train a machine learning model.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        output_dir: Directory to save the model
        **kwargs: Additional training parameters
        
    Returns:
        Dictionary containing training results
    """
    logger.info("Training Random Forest model...")
    
    # Initialize model
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    
    # Train model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    # Save model
    model_path = os.path.join(output_dir, "boiler_classifier.joblib")
    joblib.dump(model, model_path)
    logger.info(f"Model saved to: {model_path}")
    
    # Save metrics
    metrics_path = os.path.join(output_dir, "metrics.json")
    metrics = {
        "accuracy": accuracy,
        "classification_report": report,
        "feature_importance": model.feature_importances_.tolist()
    }
    
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"Metrics saved to: {metrics_path}")
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Train boiler temperature classifier")
    parser.add_argument("--data-path", required=True, help="Path to data directory")
    parser.add_argument("--output-dir", required=True, help="Output directory for model")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set size")
    parser.add_argument("--random-state", type=int, default=42, help="Random state")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load data
    X, y = load_data(args.data_path)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )
    
    logger.info(f"Training set size: {len(X_train)}")
    logger.info(f"Test set size: {len(X_test)}")
    
    # Train model
    metrics = train_model(X_train, y_train, X_test, y_test, args.output_dir)
    
    # Print results
    logger.info(f"Model accuracy: {metrics['accuracy']:.4f}")
    logger.info("Training completed successfully!")


if __name__ == "__main__":
    main() 