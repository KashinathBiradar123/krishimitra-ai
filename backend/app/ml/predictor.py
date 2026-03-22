# predictor
import json
import tensorflow as tf
import numpy as np
import os
import logging
from typing import Dict, Any, Optional
from .preprocessing import preprocess_image, validate_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models/plant_disease_model/model.h5")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "models/plant_disease_model/labels.json")

# Mock data for when model is not available
MOCK_DISEASES = [
    "Tomato Late Blight",
    "Tomato Early Blight",
    "Tomato Healthy",
    "Potato Late Blight",
    "Potato Early Blight",
    "Potato Healthy",
    "Rice Blast",
    "Rice Brown Spot",
    "Rice Healthy",
    "Wheat Yellow Rust",
    "Wheat Brown Rust",
    "Wheat Healthy",
    "Corn Northern Leaf Blight",
    "Corn Common Rust",
    "Corn Healthy"
]

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.85,
    "medium": 0.70,
    "low": 0.50
}

class DiseasePredictor:
    """
    Plant Disease Prediction Model Handler
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize the predictor
        
        Args:
            use_mock: If True, use mock predictions (for development)
        """
        self.model = None
        self.labels = None
        self.use_mock = use_mock
        self.model_loaded = False
        
        # Try to load model if not in mock mode
        if not use_mock:
            self._load_model()
    
    def _load_model(self) -> bool:
        """
        Load the trained model and labels
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Check if model file exists
            if not os.path.exists(MODEL_PATH):
                logger.warning(f"Model file not found at {MODEL_PATH}")
                return False
            
            # Load model
            logger.info(f"Loading model from {MODEL_PATH}")
            self.model = tf.keras.models.load_model(MODEL_PATH)
            logger.info("Model loaded successfully")
            
            # Load labels
            if os.path.exists(LABELS_PATH):
                with open(LABELS_PATH, 'r') as f:
                    self.labels = json.load(f)
                logger.info(f"Labels loaded: {len(self.labels)} classes")
            else:
                logger.warning(f"Labels file not found at {LABELS_PATH}")
                # Create default labels
                self.labels = {str(i): f"Disease_{i}" for i in range(10)}
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model_loaded = False
            return False
    
    def predict(self, image_file, crop_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Predict disease from image
        
        Args:
            image_file: Uploaded image file
            crop_type: Optional crop type for better accuracy
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Validate image first
            validate_image(image_file)
            
            # Preprocess image
            logger.info("Preprocessing image...")
            image_tensor = preprocess_image(image_file)
            
            # Make prediction
            if self.model_loaded and not self.use_mock:
                return self._predict_with_model(image_tensor, crop_type)
            else:
                return self._predict_mock(image_tensor, crop_type)
                
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "disease": "Unknown",
                "confidence": 0.0,
                "severity": "unknown",
                "message": f"Prediction failed: {str(e)}"
            }
    
    def _predict_with_model(self, image_tensor: np.ndarray, crop_type: Optional[str]) -> Dict[str, Any]:
        """
        Make prediction using actual model
        """
        # Get model prediction
        predictions = self.model.predict(image_tensor, verbose=0)
        
        # Get top prediction
        top_indices = np.argsort(predictions[0])[-3:][::-1]  # Top 3
        top_confidences = predictions[0][top_indices]
        
        # Get primary prediction
        primary_idx = top_indices[0]
        primary_confidence = float(top_confidences[0])
        
        # Get disease name
        if self.labels and str(primary_idx) in self.labels:
            disease_name = self.labels[str(primary_idx)]
        else:
            disease_name = f"Disease_{primary_idx}"
        
        # Determine severity based on confidence
        severity = self._get_severity(primary_confidence)
        
        # Get alternative predictions
        alternatives = []
        for i in range(1, min(3, len(top_indices))):
            idx = top_indices[i]
            conf = float(top_confidences[i])
            name = self.labels.get(str(idx), f"Disease_{idx}") if self.labels else f"Disease_{idx}"
            alternatives.append({
                "disease": name,
                "confidence": conf
            })
        
        return {
            "success": True,
            "disease": disease_name,
            "confidence": primary_confidence,
            "severity": severity,
            "alternatives": alternatives,
            "model_used": "trained",
            "crop_type": crop_type
        }
    
    def _predict_mock(self, image_tensor: np.ndarray, crop_type: Optional[str]) -> Dict[str, Any]:
        """
        Generate mock predictions for development
        """
        import random
        
        logger.info("Using mock predictions (model not loaded)")
        
        # Filter diseases based on crop type if provided
        available_diseases = MOCK_DISEASES
        if crop_type:
            filtered = [d for d in MOCK_DISEASES if d.lower().startswith(crop_type.lower())]
            if filtered:
                available_diseases = filtered
        
        # Generate random prediction
        disease = random.choice(available_diseases)
        confidence = random.uniform(0.65, 0.98)
        severity = self._get_severity(confidence)
        
        # Generate alternative predictions
        alternatives = []
        for _ in range(2):
            alt_disease = random.choice([d for d in available_diseases if d != disease])
            alt_confidence = random.uniform(0.3, 0.6)
            alternatives.append({
                "disease": alt_disease,
                "confidence": alt_confidence
            })
        
        return {
            "success": True,
            "disease": disease,
            "confidence": round(confidence, 3),
            "severity": severity,
            "alternatives": alternatives,
            "model_used": "mock",
            "crop_type": crop_type,
            "message": "Using mock predictions - train model for production"
        }
    
    def _get_severity(self, confidence: float) -> str:
        """
        Determine severity based on confidence
        """
        if confidence >= CONFIDENCE_THRESHOLDS["high"]:
            return "high"
        elif confidence >= CONFIDENCE_THRESHOLDS["medium"]:
            return "moderate"
        elif confidence >= CONFIDENCE_THRESHOLDS["low"]:
            return "low"
        else:
            return "uncertain"
    
    def batch_predict(self, image_files: list) -> list:
        """
        Predict diseases for multiple images
        """
        results = []
        for image_file in image_files:
            result = self.predict(image_file)
            results.append(result)
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        """
        if self.model_loaded and self.model:
            return {
                "loaded": True,
                "input_shape": self.model.input_shape,
                "output_shape": self.model.output_shape,
                "num_classes": len(self.labels) if self.labels else 0,
                "layers": len(self.model.layers)
            }
        else:
            return {
                "loaded": False,
                "mode": "mock" if self.use_mock else "not loaded",
                "message": "Model not loaded, using mock predictions"
            }


# Singleton instance for reuse
_predictor_instance = None

def get_predictor(use_mock: bool = False) -> DiseasePredictor:
    """
    Get or create predictor singleton
    """
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DiseasePredictor(use_mock=use_mock)
    return _predictor_instance


# Simple function version for backward compatibility
def predict_disease(image_file, use_mock: bool = False):
    """
    Simple function to predict disease from image
    
    Args:
        image_file: Uploaded image file
        use_mock: If True, use mock predictions
    
    Returns:
        Dictionary with prediction results
    """
    predictor = get_predictor(use_mock=use_mock)
    return predictor.predict(image_file)


# Batch prediction function
def predict_diseases_batch(image_files: list):
    """
    Predict diseases for multiple images
    """
    predictor = get_predictor()
    return predictor.batch_predict(image_files)


# Get model info
def get_model_status():
    """
    Get current model status
    """
    predictor = get_predictor()
    return predictor.get_model_info()