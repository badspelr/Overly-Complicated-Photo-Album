"""
AI image analysis service for generating descriptions and tags.
"""
import logging
import requests
from django.conf import settings
import os

logger = logging.getLogger(__name__)

class AIAnalysisService:
    """Service for analyzing images with AI to generate descriptions and tags."""

    def __init__(self):
        # Start with API/fallback approach, don't load heavy models immediately
        self.use_local = False
        self.local_model_attempted = False
        self.api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
        self.headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"} if hasattr(settings, 'HF_TOKEN') and settings.HF_TOKEN else {}
        
        # We'll try to load local models only when needed
        self.processor = None
        self.model = None
        
        logger.info("Initialized AI Analysis Service with fallback approach.")
    
    def analyze_image(self, image_path):
        """
        Analyze an image and generate description and tags.

        Args:
            image_path (str): Path to the image file

        Returns:
            dict: {
                'description': str,
                'tags': list,
                'confidence': float
            }
        """
        # Try local analysis first (but only load model if needed)
        if not self.local_model_attempted:
            try:
                self._load_local_model()
                if self.use_local:
                    return self._analyze_image_local(image_path)
            except Exception as e:
                logger.error(f"Failed to load local model: {e}")
                self.local_model_attempted = True
                self.use_local = False
        elif self.use_local:
            try:
                return self._analyze_image_local(image_path)
            except Exception as e:
                logger.error(f"Local analysis failed for {image_path}: {e}")
                # Fall through to API or fallback
        
        # Try API if available
        if hasattr(settings, 'HF_TOKEN') and settings.HF_TOKEN:
            try:
                return self._analyze_image_api(image_path)
            except Exception as e:
                logger.error(f"API analysis failed for {image_path}: {e}")
        
        # Fallback to basic analysis
        return self._analyze_image_fallback(image_path)
    
    def _load_local_model(self):
        """Try to load local BLIP model on demand."""
        try:
            import torch
            from transformers import BlipProcessor, BlipForConditionalGeneration
            
            # Determine device (GPU if available, otherwise CPU)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Loading local BLIP model on {self.device} (this may take a while on first run)...")
            
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=False)
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Move model to GPU if available
            self.model = self.model.to(self.device)
            
            self.use_local = True
            self.local_model_attempted = True
            logger.info(f"Successfully loaded local BLIP model on {self.device}.")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            self.use_local = False
            self.local_model_attempted = True
            raise
    
    def _analyze_image_local(self, image_path):
        """Analyze image using local BLIP model."""
        from PIL import Image
        
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        
        # Generate caption with GPU acceleration
        inputs = self.processor(image, return_tensors="pt")
        
        # Move inputs to the same device as model
        if hasattr(self, 'device'):
            inputs = {key: val.to(self.device) for key, val in inputs.items()}
        
        out = self.model.generate(
            **inputs, 
            max_length=50, 
            num_beams=5,
            no_repeat_ngram_size=3,  # Prevent repetition
            do_sample=True,
            temperature=0.7
        )
        description = self.processor.decode(out[0], skip_special_tokens=True)
        
        # Extract tags from description
        tags = self._extract_tags_from_description(description)
        
        return {
            'description': description,
            'tags': tags,
            'confidence': 0.9
        }
    
    def _analyze_image_api(self, image_path):
        """Analyze image using Hugging Face API."""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            response = requests.post(self.api_url, headers=self.headers, data=image_data, timeout=30)
            response.raise_for_status()

            result = response.json()
            if isinstance(result, list) and result:
                description = result[0].get('generated_text', '')
            else:
                description = result.get('generated_text', '') if isinstance(result, dict) else ''

            # Extract tags from description
            tags = self._extract_tags_from_description(description)

            return {
                'description': description,
                'tags': tags,
                'confidence': 0.8
            }
        except requests.RequestException as e:
            logger.error(f"Error calling Hugging Face API for {image_path}: {e}")
            raise
    
    def _analyze_image_fallback(self, image_path):
        """Fallback analysis when no AI is available."""
        # Basic analysis based on filename and simple heuristics
        filename = os.path.basename(image_path).lower()
        
        # Basic tags based on common patterns
        basic_tags = ['photo']
        
        if any(word in filename for word in ['img', 'photo', 'pic']):
            basic_tags.append('image')
        
        # Try to get image dimensions for basic classification
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                width, height = img.size
                if width > height * 1.3:
                    basic_tags.append('landscape')
                elif height > width * 1.3:
                    basic_tags.append('portrait')
                else:
                    basic_tags.append('square')
                    
                if width >= 1920 or height >= 1920:
                    basic_tags.append('high_resolution')
        except Exception:
            pass
        
        return {
            'description': 'A digital photograph',
            'tags': basic_tags,
            'confidence': 0.3
        }
    
    def _extract_tags_from_description(self, description):
        """
        Extract relevant tags from the generated description.
        
        Args:
            description (str): Generated image description
            
        Returns:
            list: List of tags
        """
        if not description:
            return []
        
        # Common objects and concepts to extract as tags
        tag_keywords = {
            'water': ['water', 'pool', 'swimming', 'lake', 'ocean', 'sea', 'river'],
            'people': ['person', 'people', 'man', 'woman', 'child', 'boy', 'girl'],
            'animals': ['dog', 'cat', 'bird', 'animal', 'pet'],
            'nature': ['tree', 'grass', 'flower', 'garden', 'park', 'forest'],
            'buildings': ['house', 'building', 'home', 'room', 'kitchen', 'bathroom'],
            'vehicles': ['car', 'truck', 'bike', 'bicycle', 'vehicle'],
            'sports': ['ball', 'game', 'sport', 'playing'],
            'food': ['food', 'eating', 'meal', 'kitchen'],
            'outdoor': ['outdoor', 'outside', 'sky', 'cloud', 'sun'],
            'indoor': ['indoor', 'inside', 'room'],
        }
        
        description_lower = description.lower()
        tags = []
        
        for category, keywords in tag_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    if keyword not in tags:
                        tags.append(keyword)
                    if category not in tags and len([t for t in tags if t in keywords]) >= 1:
                        tags.append(category)
        
        # Also add individual significant words as tags
        words = description.lower().split()
        significant_words = []
        
        # Filter out common words
        stop_words = {'a', 'an', 'the', 'is', 'are', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'under', 'over'}
        
        for word in words:
            if len(word) > 3 and word not in stop_words and word not in tags:
                significant_words.append(word)
        
        # Add up to 3 significant words
        tags.extend(significant_words[:3])
        
        return tags[:10]  # Limit to 10 tags
    
    def is_available(self):
        """Check if the AI analysis service is available."""
        # Always return True since we have fallback methods
        # Local model > API > Fallback analysis
        return True


# Global instance
ai_analysis_service = AIAnalysisService()


def analyze_image(image_path):
    """
    Convenience function to analyze an image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Analysis results with description, tags, and confidence
    """
    return ai_analysis_service.analyze_image(image_path)


def is_ai_analysis_available():
    """Check if AI analysis is available."""
    return ai_analysis_service.is_available()