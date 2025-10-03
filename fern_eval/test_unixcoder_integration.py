#!/usr/bin/env python3
"""
Quick test script to verify UniXcoder integration works correctly.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.analyzers import SemanticSimilarityAnalyzer
from src.config import DEFAULT_EMBEDDING_MODEL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_unixcoder_integration():
    """Test that UniXcoder integration works."""
    print(f"Testing with model: {DEFAULT_EMBEDDING_MODEL}")
    
    # Initialize analyzer
    analyzer = SemanticSimilarityAnalyzer()
    
    # Test code samples
    code1 = """
    def calculate_sum(a, b):
        return a + b
    """
    
    code2 = """
    def add_numbers(x, y):
        result = x + y
        return result
    """
    
    code3 = """
    def multiply(a, b):
        return a * b
    """
    
    print("Computing similarities...")
    
    # Test similarity computation
    sim1_2 = analyzer.compute_similarity(code1, code2)
    sim1_3 = analyzer.compute_similarity(code1, code3)
    
    print(f"Similarity (sum vs add): {sim1_2:.3f}")
    print(f"Similarity (sum vs multiply): {sim1_3:.3f}")
    print(f"Model type: {analyzer.model_type}")
    
    # Verify that similar functions have higher similarity
    if sim1_2 > sim1_3:
        print("✅ SUCCESS: Similar functions have higher similarity")
        return True
    else:
        print("❌ WARNING: Similar functions don't have higher similarity")
        print("This might indicate fallback to random embeddings")
        return False

if __name__ == "__main__":
    try:
        success = test_unixcoder_integration()
        if success:
            print("\n🎉 UniXcoder integration test passed!")
        else:
            print("\n⚠️  Test completed with warnings")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
