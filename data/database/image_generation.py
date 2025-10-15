"""
Azure OpenAI GPT-Image-1 Image Generation Script using direct HTTP requests
Generates images for products in product_data.json and updates the JSON with image file paths.
Uses API key for authentication.
"""

import base64
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

# Load environment variables from same directory only
script_dir = Path(__file__).parent.parent.parent
env_path = script_dir / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class GptImageGenerator:
    def __init__(self):
        """Initialize the GPT-Image-1 generator with direct HTTP requests and API key authentication."""
        # You will need to set these environment variables
        self.endpoint = os.getenv('AZURE_IMAGE_ENDPOINT')
        self.api_key = os.getenv('AZURE_IMAGE_APIKEY')
        self.api_version = os.getenv('OPENAI_API_VERSION', '2025-04-01-preview')
        self.deployment = os.getenv('DEPLOYMENT_NAME', 'gpt-image-1')

        if not self.endpoint:
            raise ValueError("Missing AZURE_IMAGE_ENDPOINT in environment variables")
        
        if not self.api_key:
            raise ValueError("Missing AZURE_IMAGE_APIKEY in environment variables")
        
        # Build the full API URL (ensure no double slashes)
        endpoint = self.endpoint.rstrip('/')
        self.api_url = f"{endpoint}/openai/deployments/{self.deployment}/images/generations?api-version={self.api_version}"        # Paths - relative to script location
        script_dir = Path(__file__).parent
        self.product_data_path = script_dir / "product_data.json"
        self.images_dir = Path("/workspace/images")

        # Ensure images directory exists
        self.images_dir.mkdir(exist_ok=True)

        # Load product data
        self.product_data = self.load_product_data()

    def load_product_data(self) -> Dict[str, Any]:
        """Load product data from JSON file."""
        try:
            with open(self.product_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Product data file not found: {self.product_data_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in product data file: {e}")

    def save_product_data(self):
        """Save updated product data back to JSON file."""
        try:
            with open(self.product_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.product_data, f, indent=2, ensure_ascii=False)
            print(f"Product data saved to {self.product_data_path}")
        except Exception as e:
            print(f"Error saving product data: {e}")

    def create_safe_filename(self, product_name: str, category: str, subcategory: str) -> str:
        """Create a safe, unique filename for the image."""
        # Remove special characters and spaces, replace with underscores (but keep &)
        safe_category = re.sub(r'[^\w\s\-&]', '', category.lower())
        safe_category = re.sub(r'[-\s]+', '_', safe_category)
        
        safe_subcategory = re.sub(r'[^\w\s\-&]', '', subcategory.lower())
        safe_subcategory = re.sub(r'[-\s]+', '_', safe_subcategory)
        
        safe_name = re.sub(r'[^\w\s\-&]', '', product_name.lower())
        safe_name = re.sub(r'[-\s]+', '_', safe_name)

        # Create unique filename with category, subcategory, product name and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{safe_category}_{safe_subcategory}_{safe_name}_{timestamp}.png"

    def get_api_key(self) -> str:
        """Get API key from environment variables."""
        if not self.api_key:
            raise RuntimeError("API key not found in environment variables")
        return self.api_key

    def generate_image(self, product: Dict[str, Any], category: str, subcategory: str) -> Optional[str]:
        """Generate an image using GPT-Image-1 for a specific product."""

        image_prompt = f"""A simple realistic image of a "{product['description']}", isolated on a white background, centered, with no shadows."""

        try:
            print(f"Generating image for: {product['name']}")
            
            # Get API key
            api_key = self.get_api_key()
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # Prepare request payload
            payload = {
                "prompt": image_prompt,
                "size": "1024x1024",
                "quality": "medium",
                "output_compression": 100,
                "output_format": "png",
                "n": 1
            }
            
            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Extract base64 image data
                    if 'data' in result and len(result['data']) > 0 and 'b64_json' in result['data'][0]:
                        b64_image = result['data'][0]['b64_json']
                        
                        # Create filename and save image
                        filename = self.create_safe_filename(
                            product['name'], category, subcategory)
                        image_path = self.images_dir / filename
                        
                        # Decode base64 and save image
                        image_data = base64.b64decode(b64_image)
                        with open(image_path, 'wb') as f:
                            f.write(image_data)
                        
                        print(f"Image saved: {filename}")
                        # Return relative path for JSON storage
                        return f"images/{filename}"
                    else:
                        print(f"No image data found in response. Response structure: {list(result.keys()) if result else 'Empty response'}")
                        return None
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON response: {e}")
                    print(f"Response content: {response.text[:500]}...")
                    return None
            else:
                print(f"API request failed with status {response.status_code}: {response.text[:500]}...")
                return None

        except Exception as e:
            print(f"Error generating image for {product['name']}: {e}")
            return None

    def needs_image(self, product: Dict[str, Any]) -> bool:
        """Check if a product needs an image generated."""
        return 'image_path' not in product or not product.get('image_path')

    def process_products(self, limit: Optional[int] = None, delay: float = 1.0):
        """
        Process all products and generate images where needed.

        Args:
            limit: Maximum number of images to generate (None for no limit)
            delay: Delay between API calls in seconds
        """
        generated_count = 0
        total_products = 0
        products_needing_images = 0

        print("Starting image generation process...")
        print(f"Images will be saved to: {self.images_dir.absolute()}")

        # Count total products and those needing images
        for category_name, category_data in self.product_data['main_categories'].items():
            for subcategory_name, products in category_data.items():
                if isinstance(products, list) and products:
                    for product in products:
                        if isinstance(product, dict) and 'name' in product:
                            total_products += 1
                            if self.needs_image(product):
                                products_needing_images += 1

        print(f"Total products: {total_products}")
        print(f"Products needing images: {products_needing_images}")

        if limit:
            print(f"Generation limit: {limit} images")

        # Process each category and subcategory
        for category_name, category_data in self.product_data['main_categories'].items():
            print(f"\nProcessing category: {category_name}")

            for subcategory_name, products in category_data.items():
                # Skip non-product data (like seasonal multipliers)
                if not isinstance(products, list) or not products:
                    continue

                print(f"  Processing subcategory: {subcategory_name}")

                for i, product in enumerate(products):
                    # Skip if not a valid product
                    if not isinstance(product, dict) or 'name' not in product:
                        continue

                    # Check if limit reached
                    if limit and generated_count >= limit:
                        print(f"Reached generation limit of {limit} images")
                        self.save_product_data()
                        return

                    # Check if product needs an image
                    if not self.needs_image(product):
                        print(
                            f"    Skipping {product['name']} (already has image)")
                        continue

                    # Generate image
                    print(f"    Generating image for: {product['name']}")
                    image_path = self.generate_image(
                        product, category_name, subcategory_name)

                    if image_path:
                        # Update product with image path
                        product['image_path'] = image_path
                        generated_count += 1
                        print(
                            f"    ✓ Generated image {generated_count}: {image_path}")

                        # Save progress after each image
                        self.save_product_data()

                        # Add delay to avoid rate limiting
                        if delay > 0:
                            time.sleep(delay)
                    else:
                        print(
                            f"    ✗ Failed to generate image for: {product['name']}")
                        time.sleep(delay)

        print("\n🎉 Image generation complete!")
        print(f"Generated {generated_count} new images")
        print(f"All images saved to: {self.images_dir.absolute()}")

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about products and images."""
        stats = {
            'total_products': 0,
            'products_with_images': 0,
            'products_without_images': 0
        }

        for category_name, category_data in self.product_data['main_categories'].items():
            for subcategory_name, products in category_data.items():
                if isinstance(products, list) and products:
                    for product in products:
                        if isinstance(product, dict) and 'name' in product:
                            stats['total_products'] += 1
                            if 'image_path' in product and product.get('image_path'):
                                stats['products_with_images'] += 1
                            else:
                                stats['products_without_images'] += 1

        return stats


def main():
    """Main function to run the image generation process."""
    try:
        generator = GptImageGenerator()

        # Show initial statistics
        stats = generator.get_statistics()
        print("📊 Initial Statistics:")
        print(f"  Total products: {stats['total_products']}")
        print(f"  Products with images: {stats['products_with_images']}")
        print(f"  Products without images: {stats['products_without_images']}")

        if stats['products_without_images'] == 0:
            print("\n✅ All products already have images!")
            return None

        # Ask user for preferences
        print("\n" + "="*50)
        print("GPT-Image-1 Image Generation Options:")
        print("="*50)

        # Get user input for generation limit
        try:
            limit_input = input(
                f"Enter max images to generate (Enter for all {stats['products_without_images']}): ").strip()
            limit = int(limit_input) if limit_input else None
        except ValueError:
            limit = None

        # Get user input for delay
        try:
            delay_input = input(
                "Enter delay between API calls in seconds (default 1.0): ").strip()
            delay = float(delay_input) if delay_input else 1.0
        except ValueError:
            delay = 1.0

        print("\nStarting generation with:")
        print(f"  Limit: {limit if limit else 'No limit'}")
        print(f"  Delay: {delay} seconds")
        print(f"  Rate: ~{3600/delay:.0f} images per hour" if delay >
              0 else "  Rate: Maximum")

        confirm = input("\nProceed? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Generation cancelled.")
            return None

        # Start generation
        generator.process_products(limit=limit, delay=delay)

        # Show final statistics
        final_stats = generator.get_statistics()
        print("\n📊 Final Statistics:")
        print(f"  Total products: {final_stats['total_products']}")
        print(f"  Products with images: {final_stats['products_with_images']}")
        print(
            f"  Products without images: {final_stats['products_without_images']}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        print("Progress has been saved automatically.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
