import socket
from transformers import pipeline
import warnings

# Lazy load classifier
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        try:
            print("Loading zero-shot classifier (distilbert)...")
            
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(60) 
            
            try:
                _classifier = pipeline(
                    "zero-shot-classification",
                    model="typeform/distilbert-base-uncased-mnli"
                )
                print("Classifier loaded.")
            finally:
                socket.setdefaulttimeout(original_timeout)
                
        except Exception as e:
            print(f"Error loading classifier: {e}")
            return None
    return _classifier

LABELS = [
    "Non Disclosure Agreement",
    "Employment Contract",
    "Service Agreement",
    "Lease Agreement"
]

def classify_contract(text: str):
    classifier = get_classifier()
    if not classifier:
        return {"contract_type": "Unknown", "confidence": 0.0}
        
    try:
        # Use first 1500 chars for classification
        result = classifier(text[:1500], LABELS)
        return {
            "contract_type": result["labels"][0],
            "confidence": round(float(result["scores"][0]), 2)
        }
    except Exception as e:
        print(f"Classification error: {e}")
        return {"contract_type": "Unknown", "confidence": 0.0}
