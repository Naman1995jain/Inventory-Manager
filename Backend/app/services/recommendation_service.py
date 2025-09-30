"""
Recommendation Service Module

This module provides product recommendation functionality using multiple approaches:
1. Price-based recommendations
2. Category-based recommendations  
3. Description-based recommendations using LLM embeddings
4. Hybrid recommendations combining multiple methods

Uses sentence-transformers for semantic similarity and caches embeddings as NumPy arrays.
"""

import os
import pickle
import logging
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.models.models import ScrapData
from app.schemas.schemas import ScrapData as ScrapDataSchema

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Main recommendation engine that handles multiple recommendation types
    and manages LLM model loading and embedding generation.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the recommendation engine.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.embeddings_cache_dir = Path("data/embeddings")
        self.embeddings_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache files
        self.embeddings_file = self.embeddings_cache_dir / "product_embeddings.npy"
        self.metadata_file = self.embeddings_cache_dir / "product_metadata.pkl"
        self.price_features_file = self.embeddings_cache_dir / "price_features.npy"
        
        # In-memory cache
        self._embeddings_cache = None
        self._metadata_cache = None
        self._price_features_cache = None
        self._price_scaler = StandardScaler()
        
    def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading model: {self.model_name}")
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                raise
        return self.model
    
    def _create_text_for_embedding(self, product: ScrapData) -> str:
        """
        Create a combined text representation for embedding generation.
        
        Args:
            product: ScrapData model instance
            
        Returns:
            Combined text string for embedding
        """
        text_parts = []
        
        if product.product_name:
            text_parts.append(f"Title: {product.product_name}")
            
        if product.category:
            text_parts.append(f"Category: {product.category}")
            
        if product.product_description:
            # Limit description length to avoid token limits
            desc = product.product_description[:500] if len(product.product_description) > 500 else product.product_description
            text_parts.append(f"Description: {desc}")
            
        if product.price:
            text_parts.append(f"Price: ${product.price}")
            
        return " | ".join(text_parts)
    
    def generate_embeddings(self, db: Session, force_regenerate: bool = False) -> None:
        """
        Generate and cache embeddings for all products in the database.
        
        Args:
            db: Database session
            force_regenerate: Force regeneration even if cache exists
        """
        if not force_regenerate and self._embeddings_cache is not None:
            logger.info("Using cached embeddings")
            return
            
        if not force_regenerate and self.embeddings_file.exists() and self.metadata_file.exists():
            logger.info("Loading embeddings from cache files")
            self._load_cached_embeddings()
            return
            
        logger.info("Generating new embeddings")
        model = self._load_model()
        
        # Get all products from database
        products = db.query(ScrapData).all()
        
        if not products:
            logger.warning("No products found in database")
            return
            
        # Prepare texts and metadata
        texts = []
        metadata = []
        price_features = []
        
        for product in products:
            text = self._create_text_for_embedding(product)
            texts.append(text)
            
            # Store metadata for later retrieval
            metadata.append({
                'id': product.id,
                'product_name': product.product_name,
                'category': product.category,
                'price': float(product.price) if product.price else 0.0,
                'rating': product.rating,
                'image_url': product.image_url,
                'product_page_url': product.product_page_url
            })
            
            # Prepare price features for price-based recommendations
            price_features.append([
                float(product.price) if product.price else 0.0,
                len(product.product_name) if product.product_name else 0,
                len(product.product_description) if product.product_description else 0
            ])
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} products")
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # Normalize price features
        price_features_array = np.array(price_features)
        normalized_price_features = self._price_scaler.fit_transform(price_features_array)
        
        # Cache in memory
        self._embeddings_cache = embeddings
        self._metadata_cache = metadata
        self._price_features_cache = normalized_price_features
        
        # Save to disk
        np.save(self.embeddings_file, embeddings)
        np.save(self.price_features_file, normalized_price_features)
        
        with open(self.metadata_file, 'wb') as f:
            pickle.dump({
                'metadata': metadata,
                'price_scaler': self._price_scaler
            }, f)
            
        logger.info("Embeddings generated and cached successfully")
    
    def _load_cached_embeddings(self) -> None:
        """Load embeddings and metadata from cache files."""
        try:
            self._embeddings_cache = np.load(self.embeddings_file)
            self._price_features_cache = np.load(self.price_features_file)
            
            with open(self.metadata_file, 'rb') as f:
                cache_data = pickle.load(f)
                self._metadata_cache = cache_data['metadata']
                self._price_scaler = cache_data['price_scaler']
                
            logger.info("Successfully loaded cached embeddings")
        except Exception as e:
            logger.error(f"Error loading cached embeddings: {e}")
            raise
    
    def _find_product_index(self, product_id: int) -> Optional[int]:
        """Find the index of a product in the cached metadata."""
        if self._metadata_cache is None:
            return None
            
        for idx, metadata in enumerate(self._metadata_cache):
            if metadata['id'] == product_id:
                return idx
        return None
    
    def get_price_based_recommendations(
        self, 
        product_id: int, 
        price_tolerance: float = 0.2,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on price similarity.
        
        Args:
            product_id: ID of the product to find recommendations for
            price_tolerance: Percentage tolerance for price matching (0.2 = ±20%)
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended products with similarity scores
        """
        if self._metadata_cache is None:
            return []
            
        product_idx = self._find_product_index(product_id)
        if product_idx is None:
            return []
            
        target_product = self._metadata_cache[product_idx]
        target_price = target_product['price']
        
        if target_price == 0:
            return []
            
        # Find products within price range
        recommendations = []
        price_min = target_price * (1 - price_tolerance)
        price_max = target_price * (1 + price_tolerance)
        
        for idx, metadata in enumerate(self._metadata_cache):
            if idx == product_idx:  # Skip the same product
                continue
                
            product_price = metadata['price']
            if price_min <= product_price <= price_max:
                # Calculate price similarity (closer = higher score)
                price_diff = abs(target_price - product_price) / target_price
                similarity_score = 1.0 - price_diff
                
                recommendations.append({
                    **metadata,
                    'similarity_score': similarity_score,
                    'recommendation_type': 'price_based'
                })
        
        # Sort by similarity score and limit results
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        return recommendations[:limit]
    
    def get_category_based_recommendations(
        self, 
        product_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on category matching.
        
        Args:
            product_id: ID of the product to find recommendations for
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended products from the same category
        """
        if self._metadata_cache is None:
            return []
            
        product_idx = self._find_product_index(product_id)
        if product_idx is None:
            return []
            
        target_product = self._metadata_cache[product_idx]
        target_category = target_product['category']
        
        if not target_category:
            return []
            
        # Find products in the same category
        recommendations = []
        for idx, metadata in enumerate(self._metadata_cache):
            if idx == product_idx:  # Skip the same product
                continue
                
            if metadata['category'] == target_category:
                recommendations.append({
                    **metadata,
                    'similarity_score': 1.0,  # Perfect category match
                    'recommendation_type': 'category_based'
                })
        
        # Limit results
        return recommendations[:limit]
    
    def get_description_based_recommendations(
        self, 
        product_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on description similarity using LLM embeddings.
        
        Args:
            product_id: ID of the product to find recommendations for
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended products with cosine similarity scores
        """
        if self._embeddings_cache is None or self._metadata_cache is None:
            return []
            
        product_idx = self._find_product_index(product_id)
        if product_idx is None:
            return []
            
        # Get target product embedding
        target_embedding = self._embeddings_cache[product_idx].reshape(1, -1)
        
        # Calculate cosine similarity with all other products
        similarities = cosine_similarity(target_embedding, self._embeddings_cache)[0]
        
        # Create recommendations list (excluding the same product)
        recommendations = []
        for idx, similarity in enumerate(similarities):
            if idx == product_idx:  # Skip the same product
                continue
                
            recommendations.append({
                **self._metadata_cache[idx],
                'similarity_score': float(similarity),
                'recommendation_type': 'description_based'
            })
        
        # Sort by similarity score and limit results
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        return recommendations[:limit]
    
    def get_hybrid_recommendations(
        self, 
        product_id: int, 
        weights: Optional[Dict[str, float]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get hybrid recommendations combining multiple methods.
        
        Args:
            product_id: ID of the product to find recommendations for
            weights: Dictionary of weights for each recommendation type
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended products with combined scores
        """
        if weights is None:
            weights = {
                'price_based': 0.3,
                'category_based': 0.3,
                'description_based': 0.4
            }
        
        # Get recommendations from each method
        price_recs = self.get_price_based_recommendations(product_id, limit=limit*2)
        category_recs = self.get_category_based_recommendations(product_id, limit=limit*2)
        description_recs = self.get_description_based_recommendations(product_id, limit=limit*2)
        
        # Combine and weight scores
        combined_scores = {}
        
        # Process each recommendation type
        for recs, weight in [
            (price_recs, weights.get('price_based', 0)),
            (category_recs, weights.get('category_based', 0)),
            (description_recs, weights.get('description_based', 0))
        ]:
            for rec in recs:
                product_id_key = rec['id']
                if product_id_key not in combined_scores:
                    combined_scores[product_id_key] = {
                        **rec,
                        'combined_score': 0.0,
                        'recommendation_type': 'hybrid'
                    }
                
                combined_scores[product_id_key]['combined_score'] += rec['similarity_score'] * weight
        
        # Convert to list and sort
        recommendations = list(combined_scores.values())
        recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Update similarity_score to reflect combined score
        for rec in recommendations:
            rec['similarity_score'] = rec['combined_score']
            del rec['combined_score']
        
        return recommendations[:limit]
    
    def get_recommendations_by_name(
        self,
        product_name: str,
        recommendation_type: str = "hybrid",
        limit: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations for a product by name instead of ID.
        
        Args:
            product_name: Name of the product to find recommendations for
            recommendation_type: Type of recommendation ('price', 'category', 'description', 'hybrid')
            limit: Maximum number of recommendations to return
            **kwargs: Additional arguments passed to specific recommendation methods
            
        Returns:
            List of recommended products
        """
        if self._metadata_cache is None:
            return []
        
        # Find product by name (case-insensitive partial match)
        product_idx = None
        target_product_name = product_name.lower()
        
        for idx, metadata in enumerate(self._metadata_cache):
            if target_product_name in metadata['product_name'].lower():
                product_idx = idx
                break
        
        if product_idx is None:
            return []
        
        product_id = self._metadata_cache[product_idx]['id']
        
        # Call appropriate recommendation method
        if recommendation_type == "price":
            return self.get_price_based_recommendations(product_id, limit=limit, **kwargs)
        elif recommendation_type == "category":
            return self.get_category_based_recommendations(product_id, limit=limit)
        elif recommendation_type == "description":
            return self.get_description_based_recommendations(product_id, limit=limit)
        else:  # hybrid
            return self.get_hybrid_recommendations(product_id, limit=limit, **kwargs)


# Global instance
recommendation_engine = RecommendationEngine()


def get_recommendation_engine() -> RecommendationEngine:
    """Get the global recommendation engine instance."""
    return recommendation_engine