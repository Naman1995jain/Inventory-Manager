"""
Unit tests for the recommendation service.

Tests all recommendation types and edge cases.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from app.services.recommendation_service import RecommendationEngine
from app.models.models import ScrapData


class TestRecommendationEngine:
    """Test cases for the RecommendationEngine class."""
    
    @pytest.fixture
    def mock_products(self):
        """Create mock product data for testing."""
        products = [
            Mock(
                id=1,
                product_name="Python Programming Book",
                product_description="Learn Python programming with this comprehensive guide",
                category="Programming",
                price=Decimal("29.99"),
                rating="4.5",
                image_url="http://example.com/python.jpg",
                product_page_url="http://example.com/python"
            ),
            Mock(
                id=2,
                product_name="JavaScript Guide",
                product_description="Master JavaScript with practical examples",
                category="Programming",
                price=Decimal("34.99"),
                rating="4.2",
                image_url="http://example.com/js.jpg",
                product_page_url="http://example.com/js"
            ),
            Mock(
                id=3,
                product_name="Cooking Basics",
                product_description="Essential cooking techniques for beginners",
                category="Cooking",
                price=Decimal("19.99"),
                rating="4.8",
                image_url="http://example.com/cooking.jpg",
                product_page_url="http://example.com/cooking"
            ),
            Mock(
                id=4,
                product_name="Advanced Python",
                product_description="Advanced Python techniques and best practices",
                category="Programming",
                price=Decimal("45.99"),
                rating="4.7",
                image_url="http://example.com/advanced-python.jpg",
                product_page_url="http://example.com/advanced-python"
            )
        ]
        return products
    
    @pytest.fixture
    def recommendation_engine(self):
        """Create a recommendation engine instance for testing."""
        engine = RecommendationEngine("sentence-transformers/all-MiniLM-L6-v2")
        return engine
    
    def test_create_text_for_embedding(self, recommendation_engine, mock_products):
        """Test text creation for embeddings."""
        product = mock_products[0]
        text = recommendation_engine._create_text_for_embedding(product)
        
        expected_parts = [
            "Title: Python Programming Book",
            "Category: Programming", 
            "Description: Learn Python programming with this comprehensive guide",
            "Price: $29.99"
        ]
        
        for part in expected_parts:
            assert part in text
    
    def test_create_text_for_embedding_missing_fields(self, recommendation_engine):
        """Test text creation when some fields are missing."""
        product = Mock(
            product_name="Test Book",
            product_description=None,
            category=None,
            price=None
        )
        
        text = recommendation_engine._create_text_for_embedding(product)
        assert "Title: Test Book" in text
        assert "Category:" not in text
        assert "Description:" not in text
        assert "Price:" not in text
    
    @patch('app.services.recommendation_service.SentenceTransformer')
    def test_load_model(self, mock_sentence_transformer, recommendation_engine):
        """Test model loading."""
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        model = recommendation_engine._load_model()
        
        assert model == mock_model
        mock_sentence_transformer.assert_called_once_with("sentence-transformers/all-MiniLM-L6-v2")
    
    def test_find_product_index(self, recommendation_engine):
        """Test finding product index in metadata cache."""
        recommendation_engine._metadata_cache = [
            {'id': 1, 'product_name': 'Product 1'},
            {'id': 2, 'product_name': 'Product 2'},
            {'id': 3, 'product_name': 'Product 3'}
        ]
        
        # Test existing product
        assert recommendation_engine._find_product_index(2) == 1
        
        # Test non-existing product
        assert recommendation_engine._find_product_index(999) is None
        
        # Test with no cache
        recommendation_engine._metadata_cache = None
        assert recommendation_engine._find_product_index(1) is None
    
    def test_price_based_recommendations(self, recommendation_engine):
        """Test price-based recommendations."""
        # Set up mock metadata
        recommendation_engine._metadata_cache = [
            {'id': 1, 'product_name': 'Product 1', 'price': 30.0, 'category': 'Books'},
            {'id': 2, 'product_name': 'Product 2', 'price': 35.0, 'category': 'Books'},  # Within range
            {'id': 3, 'product_name': 'Product 3', 'price': 25.0, 'category': 'Books'},  # Within range
            {'id': 4, 'product_name': 'Product 4', 'price': 60.0, 'category': 'Books'},  # Outside range
        ]
        
        recommendations = recommendation_engine.get_price_based_recommendations(
            product_id=1, 
            price_tolerance=0.2,  # ±20% of $30 = $24-$36
            limit=10
        )
        
        # Should recommend products 2 and 3 (within price range)
        assert len(recommendations) == 2
        assert recommendations[0]['id'] in [2, 3]
        assert recommendations[1]['id'] in [2, 3]
        
        # Check similarity scores
        for rec in recommendations:
            assert 0 <= rec['similarity_score'] <= 1
            assert rec['recommendation_type'] == 'price_based'
    
    def test_category_based_recommendations(self, recommendation_engine):
        """Test category-based recommendations."""
        # Set up mock metadata
        recommendation_engine._metadata_cache = [
            {'id': 1, 'product_name': 'Product 1', 'category': 'Programming', 'price': 30.0},
            {'id': 2, 'product_name': 'Product 2', 'category': 'Programming', 'price': 35.0},  # Same category
            {'id': 3, 'product_name': 'Product 3', 'category': 'Cooking', 'price': 25.0},     # Different category
            {'id': 4, 'product_name': 'Product 4', 'category': 'Programming', 'price': 40.0}, # Same category
        ]
        
        recommendations = recommendation_engine.get_category_based_recommendations(
            product_id=1,
            limit=10
        )
        
        # Should recommend products 2 and 4 (same category)
        assert len(recommendations) == 2
        assert recommendations[0]['id'] in [2, 4]
        assert recommendations[1]['id'] in [2, 4]
        
        # Check similarity scores (should be 1.0 for perfect category match)
        for rec in recommendations:
            assert rec['similarity_score'] == 1.0
            assert rec['recommendation_type'] == 'category_based'
            assert rec['category'] == 'Programming'
    
    @patch('app.services.recommendation_service.cosine_similarity')
    def test_description_based_recommendations(self, mock_cosine_similarity, recommendation_engine):
        """Test description-based recommendations using embeddings."""
        # Set up mock data
        recommendation_engine._embeddings_cache = np.array([
            [0.1, 0.2, 0.3],  # Product 1 embedding
            [0.2, 0.3, 0.4],  # Product 2 embedding
            [0.8, 0.9, 0.7],  # Product 3 embedding (very different)
        ])
        
        recommendation_engine._metadata_cache = [
            {'id': 1, 'product_name': 'Product 1'},
            {'id': 2, 'product_name': 'Product 2'},
            {'id': 3, 'product_name': 'Product 3'},
        ]
        
        # Mock cosine similarity to return known values
        mock_cosine_similarity.return_value = np.array([[0.95, 0.85, 0.2]])
        
        recommendations = recommendation_engine.get_description_based_recommendations(
            product_id=1,
            limit=10
        )
        
        # Should recommend products 2 and 3, sorted by similarity
        assert len(recommendations) == 2
        assert recommendations[0]['id'] == 2  # Higher similarity (0.85)
        assert recommendations[1]['id'] == 3  # Lower similarity (0.2)
        
        # Check similarity scores
        assert recommendations[0]['similarity_score'] == 0.85
        assert recommendations[1]['similarity_score'] == 0.2
        
        for rec in recommendations:
            assert rec['recommendation_type'] == 'description_based'
    
    def test_recommendations_by_name(self, recommendation_engine):
        """Test getting recommendations by product name."""
        # Set up mock metadata
        recommendation_engine._metadata_cache = [
            {'id': 1, 'product_name': 'Python Programming Book', 'category': 'Programming', 'price': 30.0},
            {'id': 2, 'product_name': 'JavaScript Guide', 'category': 'Programming', 'price': 35.0},
            {'id': 3, 'product_name': 'Cooking Basics', 'category': 'Cooking', 'price': 25.0},
        ]
        
        # Mock the category-based recommendations method
        recommendation_engine.get_category_based_recommendations = Mock(return_value=[
            {'id': 2, 'product_name': 'JavaScript Guide', 'similarity_score': 1.0}
        ])
        
        recommendations = recommendation_engine.get_recommendations_by_name(
            product_name="python",  # Should match "Python Programming Book"
            recommendation_type="category",
            limit=10
        )
        
        # Should call category-based recommendations for product 1
        recommendation_engine.get_category_based_recommendations.assert_called_once_with(1, limit=10)
        assert len(recommendations) == 1
        assert recommendations[0]['id'] == 2
    
    def test_recommendations_by_name_not_found(self, recommendation_engine):
        """Test getting recommendations by product name when product not found."""
        recommendation_engine._metadata_cache = [
            {'id': 1, 'product_name': 'Python Programming Book'},
        ]
        
        recommendations = recommendation_engine.get_recommendations_by_name(
            product_name="nonexistent",
            recommendation_type="category",
            limit=10
        )
        
        assert len(recommendations) == 0
    
    def test_hybrid_recommendations(self, recommendation_engine):
        """Test hybrid recommendations combining multiple methods."""
        # Mock the individual recommendation methods
        recommendation_engine.get_price_based_recommendations = Mock(return_value=[
            {'id': 2, 'similarity_score': 0.8, 'product_name': 'Product 2'},
            {'id': 3, 'similarity_score': 0.6, 'product_name': 'Product 3'},
        ])
        
        recommendation_engine.get_category_based_recommendations = Mock(return_value=[
            {'id': 2, 'similarity_score': 1.0, 'product_name': 'Product 2'},
            {'id': 4, 'similarity_score': 1.0, 'product_name': 'Product 4'},
        ])
        
        recommendation_engine.get_description_based_recommendations = Mock(return_value=[
            {'id': 2, 'similarity_score': 0.9, 'product_name': 'Product 2'},
            {'id': 5, 'similarity_score': 0.7, 'product_name': 'Product 5'},
        ])
        
        weights = {
            'price_based': 0.3,
            'category_based': 0.3,
            'description_based': 0.4
        }
        
        recommendations = recommendation_engine.get_hybrid_recommendations(
            product_id=1,
            weights=weights,
            limit=10
        )
        
        # Product 2 should have the highest combined score:
        # 0.8 * 0.3 + 1.0 * 0.3 + 0.9 * 0.4 = 0.24 + 0.3 + 0.36 = 0.9
        assert len(recommendations) >= 1
        assert recommendations[0]['id'] == 2
        assert recommendations[0]['recommendation_type'] == 'hybrid'
        
        # Check that all methods were called
        recommendation_engine.get_price_based_recommendations.assert_called_once()
        recommendation_engine.get_category_based_recommendations.assert_called_once()
        recommendation_engine.get_description_based_recommendations.assert_called_once()


@pytest.mark.asyncio
class TestRecommendationAPI:
    """Test cases for the recommendation API endpoints."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        db = Mock()
        return db
    
    @pytest.fixture
    def mock_recommendation_engine(self):
        """Create a mock recommendation engine."""
        engine = Mock()
        engine.generate_embeddings = Mock()
        engine.get_price_based_recommendations = Mock(return_value=[])
        engine.get_category_based_recommendations = Mock(return_value=[])
        engine.get_description_based_recommendations = Mock(return_value=[])
        engine.get_hybrid_recommendations = Mock(return_value=[])
        engine.get_recommendations_by_name = Mock(return_value=[])
        return engine
    
    def test_recommendation_types_enum(self):
        """Test that all recommendation types are properly defined."""
        from app.api.recommendations import RecommendationType
        
        assert RecommendationType.PRICE == "price"
        assert RecommendationType.CATEGORY == "category"
        assert RecommendationType.DESCRIPTION == "description"
        assert RecommendationType.HYBRID == "hybrid"
