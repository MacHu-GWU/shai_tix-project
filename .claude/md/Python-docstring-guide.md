# Python Docstring Standard Guide

This guide establishes consistent docstring standards for functions, methods, classes, and modules to ensure clear, maintainable documentation.

## General Principles

- **Concise but Complete**: Brief summary followed by detailed explanation when needed
- **No Type Duplication**: Don't repeat type information already in type hints
- **Structured Format**: Consistent order of sections across all docstrings
- **Sphinx Compatible**: Use reStructuredText syntax for proper rendering

## Function/Method Docstrings

### Structure

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of what the function does.

    Optional detailed explanation of WHY (not HOW) when logic is complex
    or there are special design decisions that need clarification.

    Optional usage examples when parameters are complex or when Union types
    make usage unclear.

    :param param1: Description of first parameter
    :param param2: Description of second parameter

    :returns: Description of return value

    .. note::
        Optional special notes, warnings, or additional information
    """
```

### Example

```python
def format_currency(amount: float, currency: str, precision: int = 2) -> str:
    """
    Format a numeric amount as a currency string.

    Handles locale-specific formatting and currency symbols. Uses banker's
    rounding for financial accuracy when precision requires rounding.

    Examples:
        >>> format_currency(1234.567, "USD", 2)
        '$1,234.57'
        >>> format_currency(999.99, "EUR", 0)
        '€1,000'

    :param amount: Numeric amount to format
    :param currency: ISO currency code (USD, EUR, GBP, etc.)
    :param precision: Number of decimal places to display

    :returns: Formatted currency string with symbol and locale formatting

    .. note::
        Uses banker's rounding (round half to even) for financial accuracy
    """
```

## Class Docstrings

Class docstrings document the constructor parameters regardless of whether you're using raw classes, dataclasses, attrs, or Pydantic. The `:param` entries describe the fields/attributes that will be set during instance creation.

### Structure

```python
@dataclass
class ClassName:
    """
    Brief description of the class purpose.

    Detailed explanation of what the class represents and how it fits
    into the larger system when necessary.

    :param field1: Description of constructor parameter/field
    :param field2: Description of constructor parameter/field

    **Examples**:
        Usage example with JSON/dict representation::

            {
                "field1": "value1",
                "field2": ["item1", "item2"]
            }

    .. note::
        Special notes about validation, constraints, or behavior
    """

    field1: Type1
    field2: Type2 = default_value
```

### Example

```python
@dataclass
class UserProfile:
    """
    User profile information for account management.

    Stores core user data with validation and formatting capabilities.
    Supports both individual users and organizational accounts.

    :param username: Unique identifier for user login
    :param email: Primary contact email address
    :param full_name: User's complete name for display purposes
    :param is_active: Whether the account is currently enabled
    :param tags: Optional labels for categorization and filtering

    **Examples**:
        Individual user account::

            {
                "username": "john_doe",
                "email": "john@example.com", 
                "full_name": "John Doe",
                "is_active": true,
                "tags": ["premium", "beta_tester"]
            }

    .. note::
        Username must be unique across the entire system and cannot be changed
        after account creation.
    """

    username: str
    email: str
    full_name: str
    is_active: bool = True
    tags: list[str] = field(default_factory=list)
```

## Module Docstrings

### Structure

```python
"""
Module Title

Brief description of what this module contains and its primary purpose.
If there's a specific design pattern used, describe it in one paragraph.
"""
```

### Example

```python
"""
User Authentication and Authorization

This module provides authentication mechanisms and role-based access control
for web applications. Supports multiple authentication backends including
OAuth, LDAP, and local database authentication.

The module follows the adapter pattern to allow pluggable authentication
providers while maintaining a consistent interface for application code.
"""
```

## Section Guidelines

### When to Include Each Section

**WHY Explanation**: Include when:
- Logic is complex or non-obvious
- Special design decisions were made
- Performance considerations exist
- Security implications are present

**Usage Examples**: Include when:
- Function has many parameters
- Union types make usage unclear
- Complex data structures are involved
- Configuration examples help understanding

**Special Notes**: Use for:
- `.. note::` - Important information
- `.. warning::` - Potential issues or gotchas
- `.. seealso::` - Related functions or documentation

### Parameter Descriptions

- **Be Specific**: Describe what the parameter represents, not just its type
- **Include Constraints**: Mention valid ranges, formats, or patterns
- **Explain Relationships**: How parameters interact with each other
- **Default Behavior**: What happens when optional parameters are omitted

### Return Descriptions

- **Describe Content**: What the return value contains, not just its type
- **Explain Format**: Structure of complex return types
- **Error Conditions**: When None or empty values might be returned

## Best Practices

1. **First Line**: Always a brief, complete sentence ending with period
2. **Present Tense**: Use present tense ("Returns..." not "Will return...")
3. **Active Voice**: Prefer active over passive voice
4. **Consistent Terminology**: Use same terms throughout codebase
5. **Avoid Redundancy**: Don't repeat information from type hints
6. **Link Related Items**: Use `:class:`, `:func:`, `:meth:` for cross-references
7. **Code Examples**: Use double backticks for inline code, code blocks for multi-line

## Common Patterns

### For Factory Functions
```python
def parse_config_file(file_path: str, format: str = "json") -> dict:
    """
    Parse configuration file into dictionary.

    :param file_path: Path to configuration file
    :param format: File format (json, yaml, toml)

    :returns: Parsed configuration dictionary

    :raises FileNotFoundError: If configuration file doesn't exist
    :raises ValueError: If file format is unsupported
    """
```

### For Configuration Classes
```python
@dataclass
class ServerConfig:
    """
    Web server configuration settings.

    :param host: Server hostname or IP address to bind to
    :param port: TCP port number for incoming connections
    :param workers: Number of worker processes to spawn
    :param debug: Enable debug mode with detailed error messages

    Example:
        Production configuration::

            {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 4,
                "debug": false
            }
    """

    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    debug: bool = False
```

This standard ensures consistent, helpful documentation across all Python code while avoiding redundancy with type hints and maintaining readability.