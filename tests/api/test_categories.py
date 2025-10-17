"""
Tests for category-related endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestCategoriesEndpoints:
    """Test suite for category endpoints."""
    
    def test_get_categories(self, test_client: TestClient):
        """
        Test GET /api/categories endpoint.
        
        Should return:
        - Status code 200
        - CategoryList response model
        - List of categories ordered by name
        """
        # TODO: Implement test
        pass
    
    def test_get_categories_returns_correct_schema(self, test_client: TestClient):
        """
        Test that categories endpoint returns data matching CategoryList schema.
        
        Validates:
        - Response has 'categories' and 'total' fields
        - Each category has 'id' and 'name' fields
        - Categories are ordered alphabetically
        """
        # TODO: Implement test
        pass
    
    def test_get_categories_cache_behavior(self, test_client: TestClient):
        """
        Test that categories endpoint caching works correctly.
        
        Validates:
        - Cached responses are returned
        - Cache duration is 1 hour
        """
        # TODO: Implement test
        pass
