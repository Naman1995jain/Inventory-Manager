#!/usr/bin/env python3
"""
Setup Recommendation System

This script:
1. Downloads the sentence-transformers model locally
2. Generates embeddings for all scraped products 
3. Converts data to NumPy format for fast recommendations
4. Caches embeddings for quick startup

Run this script after adding new products to the database or during initial setup.
"""

import sys
import os
from pathlib import Path
import logging
import time

# Add the parent directory to sys.path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal, create_tables
from app.services.recommendation_service import get_recommendation_engine
from app.models.models import ScrapData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_recommendation_system():
    """
    Set up the recommendation system by downloading models and generating embeddings.
    """
    logger.info("Starting recommendation system setup...")
    
    try:
        # Ensure database tables exist
        logger.info("Creating database tables if they don't exist...")
        create_tables()
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Check if we have any scraped data
            product_count = db.query(ScrapData).count()
            logger.info(f"Found {product_count} products in database")
            
            if product_count == 0:
                logger.warning("No products found in database. Run scrape_and_store.py first.")
                return False
            
            # Get recommendation engine
            logger.info("Initializing recommendation engine...")
            rec_engine = get_recommendation_engine()
            
            # Generate embeddings (this will download the model if needed)
            logger.info("Generating embeddings (this may take a few minutes on first run)...")
            start_time = time.time()
            
            rec_engine.generate_embeddings(db, force_regenerate=True)
            
            end_time = time.time()
            logger.info(f"Embeddings generated successfully in {end_time - start_time:.2f} seconds")
            
            # Test the recommendation system
            logger.info("Testing recommendation system...")
            
            # Get a sample product for testing
            sample_product = db.query(ScrapData).first()
            if sample_product:
                logger.info(f"Testing with product: {sample_product.product_name}")
                
                # Test different recommendation types
                test_cases = [
                    ("price", rec_engine.get_price_based_recommendations),
                    ("category", rec_engine.get_category_based_recommendations),
                    ("description", rec_engine.get_description_based_recommendations),
                    ("hybrid", rec_engine.get_hybrid_recommendations)
                ]
                
                for test_name, test_func in test_cases:
                    try:
                        recommendations = test_func(sample_product.id, limit=3)
                        logger.info(f"{test_name} recommendations: {len(recommendations)} found")
                    except Exception as e:
                        logger.error(f"Error testing {test_name} recommendations: {e}")
                        return False
                
                logger.info("All recommendation types working correctly!")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error setting up recommendation system: {e}")
        return False


def print_system_info():
    """Print information about the recommendation system setup."""
    rec_engine = get_recommendation_engine()
    
    print("\n" + "="*60)
    print("RECOMMENDATION SYSTEM SETUP COMPLETE")
    print("="*60)
    print(f"Model: {rec_engine.model_name}")
    print(f"Cache directory: {rec_engine.embeddings_cache_dir}")
    print(f"Embeddings file: {rec_engine.embeddings_file}")
    print(f"Metadata file: {rec_engine.metadata_file}")
    
    # Check file sizes
    if rec_engine.embeddings_file.exists():
        size_mb = rec_engine.embeddings_file.stat().st_size / (1024 * 1024)
        print(f"Embeddings file size: {size_mb:.2f} MB")
    
    print("\nAvailable API endpoints:")
    print("- POST /api/v1/recommendations/generate-embeddings")
    print("- GET  /api/v1/recommendations/{product_id}")
    print("- GET  /api/v1/recommendations/by-name/{product_name}")
    print("- GET  /api/v1/recommendations/search/similar")
    print("- GET  /api/v1/recommendations/status")
    
    print("\nRecommendation types:")
    print("- price: Find products with similar prices")
    print("- category: Find products in the same category")
    print("- description: Find products with similar descriptions (AI-powered)")
    print("- hybrid: Combine all methods with configurable weights")
    
    print("\nExample usage:")
    print("curl 'http://localhost:8000/api/v1/recommendations/1?recommendation_type=hybrid&limit=5'")
    print("curl 'http://localhost:8000/api/v1/recommendations/by-name/book?recommendation_type=description'")
    print("="*60)


if __name__ == "__main__":
    print("Setting up recommendation system...")
    
    success = setup_recommendation_system()
    
    if success:
        print_system_info()
        logger.info("Recommendation system setup completed successfully!")
    else:
        logger.error("Recommendation system setup failed!")
        sys.exit(1)