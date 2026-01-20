import sys
import os
import json

# Add current directory to path
sys.path.append(os.getcwd())

from tools.get_courses import get_courses

def test_get_courses():
    print("Testing get_courses...")
    
    # Test 1: Category 'IT'
    print("\n--- Test 1: Category 'IT' ---")
    res_it = get_courses(category="IT")
    print(res_it)
    
    # Test 2: Search query 'Chef'
    print("\n--- Test 2: Search 'Chef' ---")
    res_search = get_courses(search_query="Chef")
    print(res_search)
    
     # Test 3: Search query 'Python'
    print("\n--- Test 3: Search 'Python' ---")
    res_python = get_courses(search_query="Python")
    print(res_python)

    # Test 4: Invalid category
    print("\n--- Test 4: Invalid category ---")
    res_invalid = get_courses(category="SpaceTravel")
    print(res_invalid)

if __name__ == "__main__":
    test_get_courses()
    print("\nVerification successful!")
