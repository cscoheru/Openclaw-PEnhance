"""
Code Templates for PEnhance
Provides high-quality code templates for different programming scenarios
"""

# Programming language templates
LANGUAGE_TEMPLATES = {
    "python": {
        "function_template": '''def {name}({params}) -> {return_type}:
    """
    {description}

    Args:
        {args_doc}

    Returns:
        {return_doc}
    """
    # Implementation
    pass''',
        "class_template": '''class {name}:
    """
    {description}
    """

    def __init__(self, {init_params}):
        """Initialize {name}."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(...)"''',
        "error_handling": '''try:
    {operation}
except {exception_type} as e:
    logger.error(f"Failed to {operation_desc}: {e}")
    raise''',
    },
    "javascript": {
        "function_template": '''/**
 * {description}
 * @param {params_doc}
 * @returns {return_doc}
 */
function {name}({params}) {{
    // Implementation
}}''',
        "class_template": '''class {name} {{
    /**
     * {description}
     */
    constructor({init_params}) {{
        // Initialize
    }}
}}''',
    },
    "typescript": {
        "function_template": '''/**
 * {description}
 */
function {name}({params}): {return_type} {{
    // Implementation
}}''',
        "interface_template": '''interface {name} {{
    {properties}
}}''',
    },
}

# Code quality prompts
QUALITY_PROMPTS = {
    "type_hints": """
[QUALITY REQUIREMENT] Always include type hints/annotations in your code:
- Function parameters must have type annotations
- Return types must be specified
- Use Optional[T] for optional parameters
- Use Union[T1, T2] for multiple possible types
""",
    "error_handling": """
[QUALITY REQUIREMENT] Include proper error handling:
- Validate input parameters
- Handle edge cases explicitly
- Use specific exception types
- Include meaningful error messages
- Consider using custom exceptions for domain errors
""",
    "testing": """
[QUALITY REQUIREMENT] Consider testability:
- Write pure functions when possible
- Avoid hidden dependencies
- Make functions deterministic
- Include example test cases in comments if requested
""",
    "documentation": """
[QUALITY REQUIREMENT] Include documentation:
- Docstrings for public functions and classes
- Comments for complex logic
- Type hints as documentation
- Example usage in docstrings
""",
}

# Algorithm templates
ALGORITHM_TEMPLATES = {
    "sorting": {
        "prompt": """
[ALGORITHM CONTEXT] For sorting problems, consider:
- Time complexity: O(n log n) is typical for efficient sorting
- Space complexity: In-place vs. out-of-place
- Stability: Whether equal elements maintain order
- Use built-in sort() when possible for production code
""",
    },
    "search": {
        "prompt": """
[ALGORITHM CONTEXT] For search problems, consider:
- Binary search for sorted data: O(log n)
- Hash tables for O(1) lookup
- Linear search for unsorted small data
- Consider using Python's `in` operator or `dict` for lookups
""",
    },
    "graph": {
        "prompt": """
[ALGORITHM CONTEXT] For graph problems, consider:
- BFS for shortest path in unweighted graphs
- Dijkstra for weighted graphs with non-negative weights
- DFS for connectivity, cycle detection, topological sort
- Consider using adjacency list representation
""",
    },
    "dynamic_programming": {
        "prompt": """
[ALGORITHM CONTEXT] For DP problems, consider:
- Identify overlapping subproblems
- Define recurrence relation
- Choose memoization (top-down) or tabulation (bottom-up)
- Space optimization opportunities
""",
    },
}

# Best practices by category
BEST_PRACTICES = {
    "general": [
        "Follow DRY (Don't Repeat Yourself) principle",
        "Use meaningful variable and function names",
        "Keep functions small and focused (single responsibility)",
        "Avoid premature optimization",
    ],
    "python": [
        "Follow PEP 8 style guide",
        "Use list comprehensions for simple transformations",
        "Use context managers (with statements) for resources",
        "Prefer pathlib over os.path for file operations",
        "Use dataclasses for simple data containers",
        "Use type hints for better code clarity",
    ],
    "javascript": [
        "Use const/let instead of var",
        "Prefer arrow functions for callbacks",
        "Use async/await over .then() chains",
        "Destructure objects and arrays",
    ],
    "security": [
        "Never hardcode credentials",
        "Validate and sanitize user input",
        "Use parameterized queries for database operations",
        "Keep dependencies updated",
        "Use environment variables for configuration",
    ],
}

# Code review checklist
REVIEW_CHECKLIST = """
[CODE REVIEW CHECKLIST]
Before finalizing code, verify:
□ Type hints are present and correct
□ Error handling covers edge cases
□ Functions have clear single responsibilities
□ Variable names are descriptive
□ No hardcoded values (use constants/config)
□ Comments explain "why", not "what"
□ No commented-out code
□ Imports are organized and unused ones removed
□ Code follows project style guide
"""


def get_template(language: str, template_type: str) -> str:
    """Get a code template for the specified language and type."""
    lang_templates = LANGUAGE_TEMPLATES.get(language, LANGUAGE_TEMPLATES["python"])
    return lang_templates.get(template_type, "")


def get_quality_prompt(category: str) -> str:
    """Get a quality requirement prompt."""
    return QUALITY_PROMPTS.get(category, "")


def get_algorithm_prompt(algorithm_type: str) -> str:
    """Get an algorithm context prompt."""
    algo = ALGORITHM_TEMPLATES.get(algorithm_type, {})
    return algo.get("prompt", "")


def get_best_practices(language: str = "general") -> list:
    """Get best practices for a language."""
    practices = BEST_PRACTICES.get("general", [])
    practices.extend(BEST_PRACTICES.get(language, []))
    return practices
