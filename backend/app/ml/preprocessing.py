# backend/app/ml/preprocessing.py

import numpy as np
from PIL import Image
import io
import logging
from typing import Tuple, Optional, Union
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenCV, but don't fail if it's not available
try:
    import cv2
    CV2_AVAILABLE = True
    logger.info("OpenCV loaded successfully")
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Using PIL-only mode.")


def preprocess_image(image_file, target_size=(224, 224), normalize=True):
    """
    Simple function to preprocess image
    
    Args:
        image_file: Uploaded image file
        target_size: Target size tuple (width, height)
        normalize: Whether to normalize to [0,1]
    
    Returns:
        Preprocessed image as numpy array with batch dimension
    """
    try:
        # Open image
        if isinstance(image_file, str):
            image = Image.open(image_file)
        else:
            # Reset file pointer
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
            image = Image.open(io.BytesIO(image_file.read()))
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        image_array = np.array(image, dtype=np.float32)
        
        # Normalize
        if normalize:
            image_array = image_array / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise ValueError(f"Error preprocessing image: {str(e)}")


def validate_image(image_file, max_size_mb: int = 5) -> bool:
    """
    Validate image file
    
    Args:
        image_file: Uploaded image file
        max_size_mb: Maximum file size in MB
    
    Returns:
        True if valid, raises exception if invalid
    """
    # Check file size
    if hasattr(image_file, 'size') and image_file.size > max_size_mb * 1024 * 1024:
        raise ValueError(f"Image too large. Maximum size is {max_size_mb}MB")
    
    # Check file type
    allowed_formats = ['jpg', 'jpeg', 'png', 'webp', 'gif']
    
    if hasattr(image_file, 'filename'):
        ext = image_file.filename.split('.')[-1].lower()
        if ext not in allowed_formats:
            raise ValueError(f"Unsupported file format. Allowed: {', '.join(allowed_formats)}")
    
    # Try to open the image to verify it's valid
    try:
        if isinstance(image_file, str):
            img = Image.open(image_file)
        else:
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
            img = Image.open(io.BytesIO(image_file.read()))
            # Reset file pointer for later use
            image_file.seek(0)
        img.verify()  # Verify it's a valid image
        logger.info(f"Image validation passed: {img.format}, {img.size}")
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")
    
    return True


def get_image_hash(image_array: np.ndarray) -> str:
    """
    Generate a hash for image to detect duplicates
    """
    import hashlib
    return hashlib.md5(image_array.tobytes()).hexdigest()


def get_image_info(image_file) -> dict:
    """
    Extract metadata from image
    
    Args:
        image_file: Uploaded image file
    
    Returns:
        Dictionary with image metadata
    """
    try:
        # Save file position if it's a file-like object
        file_pos = None
        if hasattr(image_file, 'tell'):
            file_pos = image_file.tell()
        
        # Load image
        if isinstance(image_file, str):
            image = Image.open(image_file)
        else:
            # Reset file pointer
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
            image = Image.open(io.BytesIO(image_file.read()))
        
        info = {
            'format': image.format or 'unknown',
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'has_exif': hasattr(image, '_getexif') and image._getexif() is not None
        }
        
        # Add file size if available
        if hasattr(image_file, 'size'):
            info['file_size_bytes'] = image_file.size
            info['file_size_kb'] = round(image_file.size / 1024, 2)
        
        # Add filename if available
        if hasattr(image_file, 'filename'):
            info['filename'] = image_file.filename
        
        # Restore file position if needed
        if file_pos is not None and hasattr(image_file, 'seek'):
            image_file.seek(file_pos)
        
        logger.info(f"Image info extracted: {info['width']}x{info['height']}, {info['format']}")
        return info
        
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return {
            'error': str(e),
            'format': 'unknown',
            'size': (0, 0),
            'width': 0,
            'height': 0
        }


def resize_image(image, target_size=(224, 224)):
    """
    Resize image to target size
    """
    if isinstance(image, np.ndarray):
        # If numpy array, convert to PIL
        image = Image.fromarray(image)
    
    return image.resize(target_size, Image.Resampling.LANCZOS)


def normalize_image(image_array):
    """
    Normalize image array to [0, 1]
    """
    if image_array.max() > 1.0:
        image_array = image_array / 255.0
    return image_array


def batch_preprocess(image_files, target_size=(224, 224)):
    """
    Preprocess multiple images
    """
    batch = []
    for file in image_files:
        img_array = preprocess_image(file, target_size, normalize=True)
        batch.append(img_array[0])  # Remove batch dimension
    
    return np.array(batch)


# Class-based preprocessor for advanced use
class ImagePreprocessor:
    """Advanced image preprocessor with configurable options"""
    
    def __init__(self, target_size=(224, 224), normalize=True):
        self.target_size = target_size
        self.normalize = normalize
    
    def process(self, image_file):
        return preprocess_image(image_file, self.target_size, self.normalize)
    
    def process_batch(self, image_files):
        return batch_preprocess(image_files, self.target_size)


# Test the module when run directly
if __name__ == "__main__":
    print("Testing Image Preprocessor Module")
    print(f"OpenCV Available: {CV2_AVAILABLE}")
    
    # Create a test image
    test_img = Image.new('RGB', (100, 100), color='green')
    img_bytes = io.BytesIO()
    test_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    class TestFile:
        def read(self):
            return img_bytes.getvalue()
        def seek(self, offset):
            img_bytes.seek(offset)
        def tell(self):
            return img_bytes.tell()
        size = 1024
        filename = "test.jpg"
    
    test_file = TestFile()
    
    # Test functions
    try:
        # Test validate_image
        validate_image(test_file)
        print("✅ validate_image passed")
        
        # Test get_image_info
        info = get_image_info(test_file)
        print(f"✅ get_image_info: {info}")
        
        # Test preprocess_image
        img_array = preprocess_image(test_file)
        print(f"✅ preprocess_image: shape={img_array.shape}")
        
        # Test get_image_hash
        img_hash = get_image_hash(img_array)
        print(f"✅ get_image_hash: {img_hash[:8]}...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")