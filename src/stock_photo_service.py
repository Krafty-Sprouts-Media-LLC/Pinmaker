import requests
import random
from typing import Optional, List, Dict, Any
import os
import asyncio
from datetime import datetime, timedelta
import json


class StockPhotoService:
    def __init__(self):
        # API keys (should be set via environment variables)
        self.pixabay_key = os.getenv("PIXABAY_API_KEY", "")
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
        self.pexels_key = os.getenv("PEXELS_API_KEY", "")

        # Cache for API responses
        self.cache = {}
        self.cache_duration = timedelta(hours=1)

        # Fallback image categories for random selection
        self.image_categories = [
            "business",
            "technology",
            "nature",
            "food",
            "travel",
            "lifestyle",
            "abstract",
            "minimal",
            "design",
            "workspace",
        ]

        # Fallback placeholder images (free to use)
        self.fallback_images = [
            "https://picsum.photos/800/600?random=1",
            "https://picsum.photos/800/600?random=2",
            "https://picsum.photos/800/600?random=3",
            "https://picsum.photos/800/600?random=4",
            "https://picsum.photos/800/600?random=5",
        ]

    async def get_random_image(
        self, width: int = 800, height: int = 600, category: str = None
    ) -> Optional[str]:
        """Get random stock image URL with specified dimensions"""
        try:
            # Try different APIs in order of preference
            apis = ["unsplash", "pexels", "pixabay"]

            for api in apis:
                try:
                    image_url = await self._get_image_from_api(
                        api, width, height, category
                    )
                    if image_url:
                        return image_url
                except Exception as e:
                    print(f"Error with {api} API: {e}")
                    continue

            # Fallback to Lorem Picsum
            return await self._get_fallback_image(width, height)

        except Exception as e:
            print(f"Error getting stock image: {e}")
            return None

    async def _get_image_from_api(
        self, api: str, width: int, height: int, category: str = None
    ) -> Optional[str]:
        """Get image from specific API"""
        if api == "unsplash" and self.unsplash_key:
            return await self._get_unsplash_image(width, height, category)
        elif api == "pexels" and self.pexels_key:
            return await self._get_pexels_image(width, height, category)
        elif api == "pixabay" and self.pixabay_key:
            return await self._get_pixabay_image(width, height, category)
        else:
            return None

    async def _get_unsplash_image(
        self, width: int, height: int, category: str = None
    ) -> Optional[str]:
        """Get image from Unsplash API"""
        try:
            # Select random category if none provided
            if not category:
                category = random.choice(self.image_categories)

            # Check cache first
            cache_key = f"unsplash_{category}_{width}x{height}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["url"]

            # API request
            url = "https://api.unsplash.com/photos/random"
            headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
            params = {"query": category, "w": width, "h": height, "fit": "crop"}

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                image_url = data.get("urls", {}).get("custom") or data.get(
                    "urls", {}
                ).get("regular")

                if image_url:
                    # Add dimensions to URL
                    image_url = f"{image_url}&w={width}&h={height}&fit=crop"

                    # Cache the result
                    self.cache[cache_key] = {
                        "url": image_url,
                        "timestamp": datetime.now(),
                    }

                    return image_url

            return None

        except Exception as e:
            print(f"Unsplash API error: {e}")
            return None

    async def _get_pexels_image(
        self, width: int, height: int, category: str = None
    ) -> Optional[str]:
        """Get image from Pexels API"""
        try:
            # Select random category if none provided
            if not category:
                category = random.choice(self.image_categories)

            # Check cache first
            cache_key = f"pexels_{category}_{width}x{height}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["url"]

            # API request
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_key}
            params = {"query": category, "per_page": 20, "page": random.randint(1, 5)}

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])

                if photos:
                    # Select random photo
                    photo = random.choice(photos)

                    # Get appropriate size or original
                    image_url = photo.get("src", {}).get("large") or photo.get(
                        "src", {}
                    ).get("original")

                    if image_url:
                        # Cache the result
                        self.cache[cache_key] = {
                            "url": image_url,
                            "timestamp": datetime.now(),
                        }

                        return image_url

            return None

        except Exception as e:
            print(f"Pexels API error: {e}")
            return None

    async def _get_pixabay_image(
        self, width: int, height: int, category: str = None
    ) -> Optional[str]:
        """Get image from Pixabay API"""
        try:
            # Select random category if none provided
            if not category:
                category = random.choice(self.image_categories)

            # Check cache first
            cache_key = f"pixabay_{category}_{width}x{height}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["url"]

            # API request
            url = "https://pixabay.com/api/"
            params = {
                "key": self.pixabay_key,
                "q": category,
                "image_type": "photo",
                "orientation": "all",
                "min_width": min(width, 640),
                "min_height": min(height, 480),
                "per_page": 20,
                "page": random.randint(1, 5),
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])

                if hits:
                    # Select random image
                    image = random.choice(hits)

                    # Get appropriate size
                    image_url = image.get("webformatURL") or image.get("largeImageURL")

                    if image_url:
                        # Cache the result
                        self.cache[cache_key] = {
                            "url": image_url,
                            "timestamp": datetime.now(),
                        }

                        return image_url

            return None

        except Exception as e:
            print(f"Pixabay API error: {e}")
            return None

    async def _get_fallback_image(self, width: int, height: int) -> str:
        """Get fallback placeholder image"""
        try:
            # Use Lorem Picsum as fallback
            random_seed = random.randint(1, 1000)
            return f"https://picsum.photos/{width}/{height}?random={random_seed}"

        except Exception:
            # Ultimate fallback
            return random.choice(self.fallback_images)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.cache:
            return False

        cached_time = self.cache[cache_key]["timestamp"]
        return datetime.now() - cached_time < self.cache_duration

    async def get_themed_image(
        self, theme: str, width: int = 800, height: int = 600
    ) -> Optional[str]:
        """Get image based on specific theme"""
        # Map themes to search terms
        theme_mapping = {
            "business": ["business", "office", "professional", "corporate"],
            "technology": ["technology", "computer", "digital", "innovation"],
            "lifestyle": ["lifestyle", "people", "daily life", "modern"],
            "nature": ["nature", "landscape", "outdoor", "environment"],
            "food": ["food", "cooking", "restaurant", "cuisine"],
            "travel": ["travel", "vacation", "destination", "adventure"],
            "abstract": ["abstract", "pattern", "geometric", "minimal"],
            "workspace": ["workspace", "desk", "office", "productivity"],
        }

        search_terms = theme_mapping.get(theme.lower(), [theme])
        selected_term = random.choice(search_terms)

        return await self.get_random_image(width, height, selected_term)

    def clear_cache(self):
        """Clear the image cache"""
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        valid_entries = sum(1 for key in self.cache.keys() if self._is_cache_valid(key))

        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.cache) - valid_entries,
            "cache_duration_hours": self.cache_duration.total_seconds() / 3600,
        }

    async def test_apis(self) -> Dict[str, bool]:
        """Test which APIs are working"""
        results = {
            "unsplash": False,
            "pexels": False,
            "pixabay": False,
            "fallback": False,
        }

        # Test Unsplash
        if self.unsplash_key:
            try:
                url = await self._get_unsplash_image(400, 300, "test")
                results["unsplash"] = url is not None
            except:
                pass

        # Test Pexels
        if self.pexels_key:
            try:
                url = await self._get_pexels_image(400, 300, "test")
                results["pexels"] = url is not None
            except:
                pass

        # Test Pixabay
        if self.pixabay_key:
            try:
                url = await self._get_pixabay_image(400, 300, "test")
                results["pixabay"] = url is not None
            except:
                pass

        # Test fallback
        try:
            url = await self._get_fallback_image(400, 300)
            results["fallback"] = url is not None
        except:
            pass

        return results
