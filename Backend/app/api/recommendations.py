"""
Recommendations API endpoints

Provides product recommendation functionality with multiple recommendation types:
- Price-based recommendations
- Category-based recommendations  
- Description-based recommendations (using LLM embeddings)
- Hybrid recommendations (combining multiple methods)

Supports both product ID and product name-based queries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from enum import Enum

from app.core.database import get_database
from app.services.recommendation_service import get_recommendation_engine, RecommendationEngine
from app.models.models import ScrapData

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


class RecommendationType(str, Enum):
    """Available recommendation types"""
    PRICE = "price"
    CATEGORY = "category" 
    DESCRIPTION = "description"
    HYBRID = "hybrid"


@router.post("/generate-embeddings")
async def generate_embeddings(
    force_regenerate: bool = Query(False, description="Force regeneration of embeddings"),
    db: Session = Depends(get_database),
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """
    Generate or regenerate product embeddings.
    This should be called after adding new products to the database.
    """
    try:
        rec_engine.generate_embeddings(db, force_regenerate=force_regenerate)
        return {
            "message": "Embeddings generated successfully",
            "force_regenerate": force_regenerate
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating embeddings: {str(e)}"
        )


@router.get("/{product_id}")
async def get_recommendations_by_id(
    product_id: int,
    recommendation_type: RecommendationType = Query(
        RecommendationType.HYBRID,
        description="Type of recommendation to generate"
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
    price_tolerance: float = Query(
        0.2, 
        ge=0.1, 
        le=1.0, 
        description="Price tolerance for price-based recommendations (0.2 = ±20%)"
    ),
    price_weight: float = Query(
        0.3, 
        ge=0.0, 
        le=1.0, 
        description="Weight for price-based scoring in hybrid mode"
    ),
    category_weight: float = Query(
        0.3, 
        ge=0.0, 
        le=1.0, 
        description="Weight for category-based scoring in hybrid mode"
    ),
    description_weight: float = Query(
        0.4, 
        ge=0.0, 
        le=1.0, 
        description="Weight for description-based scoring in hybrid mode"
    ),
    db: Session = Depends(get_database),
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """
    Get product recommendations based on product ID.
    
    Supports multiple recommendation types:
    - price: Find products with similar prices
    - category: Find products in the same category
    - description: Find products with similar descriptions (using AI)
    - hybrid: Combine all methods with configurable weights
    """
    # Verify product exists
    product = db.query(ScrapData).filter(ScrapData.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Ensure embeddings are generated
    try:
        rec_engine.generate_embeddings(db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error preparing recommendation engine: {str(e)}"
        )
    
    # Get recommendations based on type
    try:
        if recommendation_type == RecommendationType.PRICE:
            recommendations = rec_engine.get_price_based_recommendations(
                product_id=product_id,
                price_tolerance=price_tolerance,
                limit=limit
            )
        elif recommendation_type == RecommendationType.CATEGORY:
            recommendations = rec_engine.get_category_based_recommendations(
                product_id=product_id,
                limit=limit
            )
        elif recommendation_type == RecommendationType.DESCRIPTION:
            recommendations = rec_engine.get_description_based_recommendations(
                product_id=product_id,
                limit=limit
            )
        else:  # HYBRID
            # Normalize weights to sum to 1
            total_weight = price_weight + category_weight + description_weight
            if total_weight == 0:
                total_weight = 1
                
            weights = {
                'price_based': price_weight / total_weight,
                'category_based': category_weight / total_weight,
                'description_based': description_weight / total_weight
            }
            
            recommendations = rec_engine.get_hybrid_recommendations(
                product_id=product_id,
                weights=weights,
                limit=limit
            )
        
        return {
            "product_id": product_id,
            "product_name": product.product_name,
            "recommendation_type": recommendation_type,
            "recommendations": recommendations,
            "total_found": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/by-name/{product_name}")
async def get_recommendations_by_name(
    product_name: str,
    recommendation_type: RecommendationType = Query(
        RecommendationType.HYBRID,
        description="Type of recommendation to generate"
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
    price_tolerance: float = Query(
        0.2, 
        ge=0.1, 
        le=1.0, 
        description="Price tolerance for price-based recommendations (0.2 = ±20%)"
    ),
    price_weight: float = Query(
        0.3, 
        ge=0.0, 
        le=1.0, 
        description="Weight for price-based scoring in hybrid mode"
    ),
    category_weight: float = Query(
        0.3, 
        ge=0.0, 
        le=1.0, 
        description="Weight for category-based scoring in hybrid mode"
    ),
    description_weight: float = Query(
        0.4, 
        ge=0.0, 
        le=1.0, 
        description="Weight for description-based scoring in hybrid mode"
    ),
    db: Session = Depends(get_database),
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """
    Get product recommendations based on product name.
    
    This endpoint allows users to search by product name and get recommendations.
    It performs a partial, case-insensitive match on product names.
    """
    # Ensure embeddings are generated
    try:
        rec_engine.generate_embeddings(db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error preparing recommendation engine: {str(e)}"
        )
    
    # Get recommendations based on type
    try:
        kwargs = {}
        weights = None
        
        if recommendation_type == RecommendationType.PRICE:
            kwargs['price_tolerance'] = price_tolerance
        elif recommendation_type == RecommendationType.HYBRID:
            # Normalize weights to sum to 1
            total_weight = price_weight + category_weight + description_weight
            if total_weight == 0:
                total_weight = 1
                
            weights = {
                'price_based': price_weight / total_weight,
                'category_based': category_weight / total_weight,
                'description_based': description_weight / total_weight
            }
            kwargs['weights'] = weights
        
        recommendations = rec_engine.get_recommendations_by_name(
            product_name=product_name,
            recommendation_type=recommendation_type.value,
            limit=limit,
            **kwargs
        )
        
        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"No product found matching name: {product_name}"
            )
        
        return {
            "searched_product_name": product_name,
            "recommendation_type": recommendation_type,
            "recommendations": recommendations,
            "total_found": len(recommendations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/search/similar")
async def search_similar_products(
    query: str = Query(..., description="Search query for finding similar products"),
    recommendation_type: RecommendationType = Query(
        RecommendationType.DESCRIPTION,
        description="Type of similarity to use"
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    min_similarity: float = Query(
        0.1, 
        ge=0.0, 
        le=1.0, 
        description="Minimum similarity score threshold"
    ),
    db: Session = Depends(get_database),
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """
    Search for products similar to a text query.
    
    This endpoint allows users to input any text description and find
    similar products in the database using AI-powered semantic search.
    """
    try:
        # Ensure embeddings are generated
        rec_engine.generate_embeddings(db)
        
        # Load the model and generate embedding for query
        model = rec_engine._load_model()
        query_embedding = model.encode([query])
        
        # Get all embeddings and metadata
        if rec_engine._embeddings_cache is None or rec_engine._metadata_cache is None:
            raise HTTPException(
                status_code=500,
                detail="Embeddings not available. Please generate embeddings first."
            )
        
        # Calculate similarities
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(query_embedding, rec_engine._embeddings_cache)[0]
        
        # Create results list
        results = []
        for idx, similarity in enumerate(similarities):
            if similarity >= min_similarity:
                result = {
                    **rec_engine._metadata_cache[idx],
                    'similarity_score': float(similarity),
                    'recommendation_type': 'query_based'
                }
                results.append(result)
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return {
            "query": query,
            "recommendation_type": recommendation_type,
            "min_similarity": min_similarity,
            "results": results[:limit],
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching similar products: {str(e)}"
        )


@router.get("/status")
async def get_recommendation_status(
    rec_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """
    Get the status of the recommendation engine.
    
    Returns information about cached embeddings and model status.
    """
    try:
        status = {
            "model_loaded": rec_engine.model is not None,
            "embeddings_cached": rec_engine._embeddings_cache is not None,
            "metadata_cached": rec_engine._metadata_cache is not None,
            "embeddings_file_exists": rec_engine.embeddings_file.exists(),
            "metadata_file_exists": rec_engine.metadata_file.exists(),
            "model_name": rec_engine.model_name
        }
        
        if rec_engine._metadata_cache:
            status["total_products"] = len(rec_engine._metadata_cache)
            
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendation status: {str(e)}"
        )