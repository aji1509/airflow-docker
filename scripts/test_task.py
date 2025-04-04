#!/usr/bin/env python
"""
Simple test script to verify Python environment and module availability
"""
import os
import sys

def main():
    """Test key imports and print environment information"""
    print("=== Python Environment Test ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Test imports of critical modules
    print("\n=== Testing Critical Imports ===")
    
    try:
        import airflow
        print(f"✅ Airflow imported successfully (version: {airflow.__version__})")
    except ImportError as e:
        print(f"❌ Failed to import airflow: {e}")
    
    try:
        import celery
        print(f"✅ Celery imported successfully (version: {celery.__version__})")
    except ImportError as e:
        print(f"❌ Failed to import celery: {e}")
    
    try:
        import redis
        print(f"✅ Redis imported successfully (version: {redis.__version__})")
    except ImportError as e:
        print(f"❌ Failed to import redis: {e}")
    
    # Print current PYTHONPATH
    print("\n=== PYTHONPATH ===")
    pythonpath = os.environ.get('PYTHONPATH', '')
    if pythonpath:
        paths = pythonpath.split(':')
        for i, path in enumerate(paths):
            print(f"{i+1}. {path} (exists: {os.path.exists(path)})")
    else:
        print("PYTHONPATH not set")
    
    # Print sys.path
    print("\n=== sys.path ===")
    for i, path in enumerate(sys.path):
        if path:  # Skip empty strings
            print(f"{i+1}. {path} (exists: {os.path.exists(path)})")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 