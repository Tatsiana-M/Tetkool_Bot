import json
import os

def get_courses(category: str = None, search_query: str = None):
    """
    Retrieves courses from the knowledge base.
    
    Args:
        category (str, optional): The category of courses to retrieve (e.g., 'IT', 'Кулинария', 'Языки', 'Бизнес').
        search_query (str, optional): A keyword to search for in course titles or descriptions.
        
    Returns:
        str: A JSON string containing the list of matching courses or a message if none found.
    """
    kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge_base.json')
    
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return "Error: Knowledge base not found."
    except json.JSONDecodeError:
        return "Error: Invalid knowledge base format."

    results = []

    # If a category is specified, look only in that category
    if category:
        # Case-insensitive match for category keys
        category_key = None
        for key in data.keys():
            if key.lower() == category.lower():
                category_key = key
                break
        
        if category_key:
            results.extend(data[category_key])
    else:
        # If no category, look in all categories
        for courses in data.values():
            results.extend(courses)

    # Filter by search query if provided
    if search_query:
        query = search_query.lower()
        results = [
            course for course in results
            if query in course['name'].lower() or query in course['description'].lower()
        ]

    if not results:
        return "К сожалению, по вашему запросу ничего не найдено."

    return json.dumps(results, ensure_ascii=False, indent=2)

# Tool definition for OpenAI
tool_definition = {
    "type": "function",
    "function": {
        "name": "get_courses",
        "description": "Get a list of courses regarding their prices, duration, start dates, and detailed descriptions. Use this tool to answer questions about course costs, schedule, and content.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "The category of the course, e.g. 'IT', 'Culinary', 'Languages', 'Business'."
                },
                "search_query": {
                    "type": "string",
                    "description": "A keyword to search for in the course title or description."
                }
            },
            "required": []
        }
    }
}
