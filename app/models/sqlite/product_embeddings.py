"""
Product Embedding models for SQLite
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class ProductDescriptionEmbedding(Base):
    """Represents a product description embedding vector"""
    
    __tablename__ = "product_description_embeddings"
    
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    description_embedding = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="description_embedding")
    
    def __repr__(self):
        return f"<ProductDescriptionEmbedding(product_id={self.product_id})>"


class ProductImageEmbedding(Base):
    """Represents a product image embedding vector"""
    
    __tablename__ = "product_image_embeddings"
    
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    image_url = Column(String, primary_key=True)
    image_embedding = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="image_embeddings")
    
    def __repr__(self):
        return f"<ProductImageEmbedding(product_id={self.product_id}, url='{self.image_url}')>"
