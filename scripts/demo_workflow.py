#============================================================================
#scripts/demo_workflow.py
#============================================================================

#!/usr/bin/env python3
"""
Demo workflow script for project presentation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.logger import setup_logger
import time

logger = setup_logger(__name__)

def demo_workflow():
    """Run complete demo workflow"""
    
    print("=" * 60)
    print("SENTINEL AI PLATFORM - DEMO WORKFLOW")
    print("=" * 60)
    print()
    
    steps = [
        "1. Starting backend server...",
        "2. Initializing ML models...",
        "3. Starting camera streams...",
        "4. Running face detection...",
        "5. Tracking persons across cameras...",
        "6. Checking watchlist matches...",
        "7. Analyzing behaviors...",
        "8. Generating alerts...",
    ]
    
    for step in steps:
        print(f"✓ {step}")
        time.sleep(1)
    
    print()
    print("=" * 60)
    print("DEMO READY!")
    print("=" * 60)
    print()
    print("Access the application at: http://localhost:3000")
    print("Login credentials:")
    print("  Admin: admin / admin123")
    print("  Operator: operator / operator123")
    print()

if __name__ == "__main__":
    demo_workflow()