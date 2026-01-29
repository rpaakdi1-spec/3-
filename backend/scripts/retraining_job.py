#!/usr/bin/env python3
"""
Scheduled job for automatic model retraining.

This script should be run periodically (e.g., via cron) to check
and retrain ML models as needed.

Usage:
    python retraining_job.py [--force] [--model-type prophet|lstm]

Examples:
    # Normal check and retrain if needed
    python retraining_job.py
    
    # Force retraining
    python retraining_job.py --force
    
    # Check specific model
    python retraining_job.py --model-type lstm

Cron examples:
    # Run daily at 2 AM
    0 2 * * * cd /path/to/backend && python retraining_job.py
    
    # Run weekly on Sunday at 3 AM
    0 3 * * 0 cd /path/to/backend && python retraining_job.py --force
"""
import sys
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.ml.pipelines.retraining_pipeline import RetrainingPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/retraining_job.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automatic ML model retraining job'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retraining regardless of conditions'
    )
    parser.add_argument(
        '--model-type',
        type=str,
        default='prophet',
        choices=['prophet', 'lstm', 'all'],
        help='Model type to check/retrain (default: prophet)'
    )
    parser.add_argument(
        '--use-sample-data',
        action='store_true',
        help='Use synthetic sample data for testing'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info(f"Retraining job started at {datetime.utcnow().isoformat()}")
    logger.info(f"Force: {args.force}")
    logger.info(f"Model type: {args.model_type}")
    logger.info(f"Use sample data: {args.use_sample_data}")
    logger.info("=" * 80)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize retraining pipeline
        pipeline = RetrainingPipeline(db)
        
        # Determine which models to check
        if args.model_type == 'all':
            model_types = ['prophet', 'lstm']
        else:
            model_types = [args.model_type]
        
        # Check and retrain each model
        results = {}
        for model_type in model_types:
            logger.info(f"\n{'='*60}")
            logger.info(f"Checking {model_type} model...")
            logger.info(f"{'='*60}")
            
            result = pipeline.check_and_retrain(
                model_type=model_type,
                force=args.force,
                use_sample_data=args.use_sample_data
            )
            
            results[model_type] = result
            
            logger.info(f"\nResult for {model_type}:")
            logger.info(f"  Status: {result['status']}")
            
            if result['status'] == 'skipped':
                logger.info(f"  Reason: {result['reason']}")
            elif result['status'] == 'success':
                logger.info(f"  Reason: {result.get('reason', 'N/A')}")
                logger.info(f"  Training duration: {result.get('training_duration_seconds', 0):.1f}s")
                if 'metrics' in result:
                    metrics = result['metrics']
                    logger.info(f"  Metrics:")
                    logger.info(f"    - MAE: {metrics.get('mae', 0):.2f}")
                    logger.info(f"    - RMSE: {metrics.get('rmse', 0):.2f}")
                    logger.info(f"    - R²: {metrics.get('r2_score', 0):.3f}")
            elif result['status'] == 'error':
                logger.error(f"  Error: {result.get('error', 'Unknown error')}")
        
        # Print summary
        logger.info(f"\n{'='*80}")
        logger.info("SUMMARY")
        logger.info(f"{'='*80}")
        
        for model_type, result in results.items():
            status_emoji = {
                'success': '✅',
                'skipped': '⏭️',
                'error': '❌'
            }.get(result['status'], '❓')
            
            logger.info(f"{status_emoji} {model_type}: {result['status'].upper()}")
        
        logger.info(f"\nJob completed at {datetime.utcnow().isoformat()}")
        logger.info("=" * 80)
        
        # Exit code based on results
        if any(r['status'] == 'error' for r in results.values()):
            sys.exit(1)  # Error occurred
        else:
            sys.exit(0)  # Success
            
    except Exception as e:
        logger.error(f"Fatal error in retraining job: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        db.close()


if __name__ == '__main__':
    main()
