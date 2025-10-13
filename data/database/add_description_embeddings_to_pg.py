#!/usr/bin/env python3
"""
Script to add description embeddings from product_data.json to PostgreSQL database.
This script reads the embeddings from the JSON file and inserts them into the 
retail.product_description_embeddings table.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import asyncpg
from dotenv import load_dotenv

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
# Try to load .env from script directory first, then parent directories
env_paths = [
    os.path.join(script_dir, '.env'),
    os.path.join(script_dir, '..', '..', '.env'),  # Up to workspace root
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break
else:
    # Fallback to default behavior
    load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PostgreSQL connection configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_DB_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_DB_PORT', 5432)),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password'),
    'database': os.getenv('POSTGRES_DB', 'zava')
}

SCHEMA_NAME = 'retail'


class DescriptionEmbeddingLoader:
    def __init__(self, data_directory_path: str):
        """
        Initialize the description embedding loader.
        
        Args:
            data_directory_path: Path to the data directory containing product_data.json
        """
        self.data_directory_path = Path(data_directory_path)
        self.json_file_path = self.data_directory_path / "product_data.json"
        self.conn: Optional[asyncpg.Connection] = None
    
    async def connect_to_database(self) -> None:
        """Establish connection to PostgreSQL database."""
        try:
            self.conn = await asyncpg.connect(
                host=POSTGRES_CONFIG['host'],
                port=POSTGRES_CONFIG['port'],
                user=POSTGRES_CONFIG['user'],
                password=POSTGRES_CONFIG['password'],
                database=POSTGRES_CONFIG['database']
            )
            logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def close_connection(self) -> None:
        """Close database connection."""
        if self.conn:
            await self.conn.close()
            logger.info("Database connection closed")
    
    def load_product_data(self) -> Dict:
        """Load the product data from JSON file."""
        try:
            with self.json_file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded product data from {self.json_file_path}")
            return data
        except FileNotFoundError:
            logger.error(f"Could not find {self.json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file: {e}")
            raise
    
    def extract_products_with_description_embeddings(self, product_data: Dict) -> List[Tuple[str, List[float]]]:
        """
        Extract products with description embeddings from the JSON structure.
        
        Args:
            product_data: The loaded product data dictionary
            
        Returns:
            List of tuples: (sku, description_embedding)
        """
        products_with_embeddings = []
        
        for category_name, category_data in product_data.get('main_categories', {}).items():
            logger.info(f"Processing category: {category_name}")
            
            for product_type, products in category_data.items():
                # Skip non-product keys like seasonal multipliers
                if not isinstance(products, list):
                    continue
                    
                logger.info(f"  Processing product type: {product_type} ({len(products)} products)")
                
                for product in products:
                    if isinstance(product, dict):
                        sku = product.get('sku')
                        description_embedding = product.get('description_embedding')
                        
                        if sku and description_embedding:
                            products_with_embeddings.append((sku, description_embedding))
                        else:
                            logger.debug(f"Skipping product with missing data: SKU={sku}, has_embedding={bool(description_embedding)}")
        
        logger.info(f"Found {len(products_with_embeddings)} products with description embeddings")
        return products_with_embeddings
    
    async def get_product_id_by_sku(self, sku: str) -> Optional[int]:
        """
        Get product_id for a given SKU.
        
        Args:
            sku: The product SKU
            
        Returns:
            product_id if found, None otherwise
        """
        try:
            result = await self.conn.fetchval(
                f"SELECT product_id FROM {SCHEMA_NAME}.products WHERE sku = $1",
                sku
            )
            return result
        except Exception as e:
            logger.error(f"Error fetching product_id for SKU {sku}: {e}")
            return None
    
    async def embedding_exists(self, product_id: int) -> bool:
        """
        Check if embedding already exists for a product.
        
        Args:
            product_id: The product ID
            
        Returns:
            True if embedding exists, False otherwise
        """
        try:
            result = await self.conn.fetchval(
                f"SELECT COUNT(*) FROM {SCHEMA_NAME}.product_description_embeddings WHERE product_id = $1",
                product_id
            )
            return result > 0
        except Exception as e:
            logger.error(f"Error checking embedding existence for product_id {product_id}: {e}")
            return False
    
    async def insert_product_description_embedding(
        self, 
        product_id: int, 
        description_embedding: List[float]
    ) -> bool:
        """
        Insert a product description embedding record.
        
        Args:
            product_id: The product ID
            description_embedding: List of embedding values
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert the embedding list to a vector string format for PostgreSQL
            embedding_str = f"[{','.join([str(x) for x in description_embedding])}]"
            
            await self.conn.execute(
                f"""
                INSERT INTO {SCHEMA_NAME}.product_description_embeddings 
                (product_id, description_embedding) 
                VALUES ($1, $2::vector)
                """,
                product_id,
                embedding_str
            )
            return True
        except Exception as e:
            logger.error(f"Error inserting embedding for product_id {product_id}: {e}")
            return False
    
    async def process_embeddings(self) -> None:
        """Process all embeddings and insert them into the database."""
        # Load product data
        product_data = self.load_product_data()
        
        # Extract products with embeddings
        products_with_embeddings = self.extract_products_with_description_embeddings(product_data)
        
        if not products_with_embeddings:
            logger.warning("No products with description embeddings found in the JSON file")
            return
        
        # Connect to database
        await self.connect_to_database()
        
        # Process each product
        total_products = len(products_with_embeddings)
        processed = 0
        skipped = 0
        failed = 0
        
        logger.info(f"Starting to process {total_products} products with embeddings...")
        
        try:
            for sku, embedding in products_with_embeddings:
                # Get product_id for this SKU
                product_id = await self.get_product_id_by_sku(sku)
                
                if product_id is None:
                    logger.warning(f"Product not found in database for SKU: {sku}")
                    failed += 1
                    continue
                
                # Check if embedding already exists
                if await self.embedding_exists(product_id):
                    logger.debug(f"Embedding already exists for SKU {sku} (product_id: {product_id})")
                    skipped += 1
                    continue
                
                # Insert the embedding
                success = await self.insert_product_description_embedding(product_id, embedding)
                
                if success:
                    processed += 1
                    logger.info(f"✓ Inserted embedding for SKU {sku} (product_id: {product_id}) - {processed}/{total_products}")
                else:
                    failed += 1
                    logger.error(f"✗ Failed to insert embedding for SKU {sku} (product_id: {product_id})")
                
                # Progress update every 10 items
                if (processed + skipped + failed) % 10 == 0:
                    logger.info(f"Progress: {processed} inserted, {skipped} skipped, {failed} failed")
        
        finally:
            await self.close_connection()
        
        # Print summary
        logger.info("=" * 60)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total products with embeddings: {total_products}")
        logger.info(f"Successfully inserted: {processed}")
        logger.info(f"Skipped (already exists): {skipped}")
        logger.info(f"Failed: {failed}")
        
        if failed > 0:
            logger.warning("Some embeddings failed to process. Check the logs above for details.")
        else:
            logger.info("All embeddings processed successfully!")


async def main():
    """Main function to run the description embedding loader."""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    logger.info("Description Embedding Loader for PostgreSQL")
    logger.info("=" * 60)
    logger.info(f"Working directory: {script_dir}")
    logger.info(f"Database: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}")
    
    # Verify we're in the right directory and file exists
    json_file = script_dir / "product_data.json"
    if not json_file.exists():
        logger.error("Error: product_data.json not found in current directory")
        logger.error("Please run this script from the data/database directory")
        sys.exit(1)
    
    try:
        # Create loader and run
        loader = DescriptionEmbeddingLoader(str(script_dir))
        await loader.process_embeddings()
        
    except KeyboardInterrupt:
        logger.info("\n\nProcess interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
