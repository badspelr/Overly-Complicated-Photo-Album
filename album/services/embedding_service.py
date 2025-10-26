from sentence_transformers import SentenceTransformer
from PIL import Image, ImageFile
import torch
import logging
import numpy as np

# Get a logger
logger = logging.getLogger(__name__)

# Allow loading of truncated images to prevent hangs on corrupted files
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Load the pre-trained CLIP model
try:
    model = SentenceTransformer('clip-ViT-B-32-multilingual-v1')
    logger.info("Successfully loaded SentenceTransformer model.")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer model: {e}")
    model = None

def generate_image_embedding(image_path):
    """
    Generates a vector embedding for a given image by first converting it to a NumPy array.
    
    Args:
        image_path (str): The absolute path to the image file.
        
    Returns:
        list[float]: A 512-dimension vector embedding of the image, or None on failure.
    """
    if model is None:
        logger.error("Embedding model is not loaded. Cannot generate embedding.")
        return None

    try:
        # 1. Load the image with Pillow
        pil_image = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        logger.warning(f"Image file not found: {image_path}")
        return None
    except Exception as e:
        logger.error(f"Pillow error for image {image_path}: {e}")
        return None

    try:
        # 2. Convert the Pillow image to a NumPy array (THE CRITICAL STEP)
        numpy_image = np.array(pil_image)

        # 3. Generate the embedding from the NumPy array
        embeddings = model.encode([numpy_image], convert_to_tensor=True, show_progress_bar=False)

        # 4. Validate and process the output tensor
        if not isinstance(embeddings, torch.Tensor) or embeddings.ndim != 2 or embeddings.shape[0] != 1:
            logger.error(f"Model returned unexpected output for {image_path}. Shape: {embeddings.shape}, Type: {type(embeddings)}")
            return None
            
        embedding_vector = embeddings[0].cpu().numpy()
        return embedding_vector.tolist()

    except Exception as e:
        logger.error(f"Model encoding error for {image_path}: {e}")
        return None


def generate_text_embedding(text):
    """
    Generates a vector embedding for a given text query.
    
    Args:
        text (str): The text to embed.
        
    Returns:
        list[float]: A 512-dimension vector embedding of the text.
    """
    try:
        # Generate the embedding for the text
        embedding = model.encode(text, convert_to_tensor=True)
        
        # Move embedding to CPU and convert to a list of floats
        return embedding.cpu().numpy().tolist()
        
    except Exception as e:
        print(f"An error occurred during text embedding generation: {e}")
        return None

