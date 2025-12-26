# Python Cross-Reference Guide for Sphinx Documentation

This guide explains how to properly reference Python objects (modules, classes, methods, functions) in both `.py` docstrings and `.rst` documentation files using Sphinx cross-reference syntax.

## Overview

Sphinx provides role directives that create clickable links between documentation elements. These references work in both Python docstrings and reStructuredText files, enabling rich interconnected documentation.

## Project Structure Example

For this guide, we'll use this example project structure:

```
shai_tix-project/
├── shai_tix/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── users.py          # Contains User class, authenticate() function
│   │   └── permissions.py    # Contains Role class, check_permission() function
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py         # Contains BaseModel class
│   │   └── connection.py     # Contains Database class, connect() function
│   └── utils/
│       ├── __init__.py
│       └── helpers.py        # Contains format_date() function
└── docs/
    └── source/
        ├── 01-Getting-Started/
        │   └── index.rst
        ├── 02-API-Reference/
        │   └── index.rst
        └── 03-Advanced-Usage/
            └── index.rst
```

## Example File Contents

### shai_tix/auth/users.py

```python
class User:
    """User account management."""
    
    def __init__(self, username: str):
        self.username = username
    
    def get_profile(self) -> dict:
        """Get user profile data."""
        pass

def authenticate(username: str, password: str) -> bool:
    """Authenticate user credentials."""
    pass
```

### shai_tix/auth/permissions.py

```python
class Role:
    """User role and permission management."""
    pass

def check_permission(user: str, action: str) -> bool:
    """Check if user has permission for action."""
    pass
```

### shai_tix/database/models.py

```python
class BaseModel:
    """Base class for all database models."""
    
    def save(self) -> None:
        """Save model to database."""
        pass
```

### shai_tix/database/connection.py

```python
class Database:
    """Database connection manager."""
    
    def query(self, sql: str) -> list:
        """Execute SQL query."""
        pass

def connect(url: str) -> Database:
    """Create database connection."""
    pass
```

## Cross-Reference Rules

### 1. Referencing Elements in Different Modules

Use full import paths for elements outside the current module:

#### Classes

```python
# Syntax: :class:`~full.module.path.ClassName`
# The ~ hides the full path, showing only the class name to users

def process_user():
    """
    Process user data using authentication.
    
    Creates a :class:`~shai_tix.auth.users.User` instance and validates
    permissions through :class:`~shai_tix.auth.permissions.Role`.
    """
    pass
```

**Rendered as**: Creates a `User` instance and validates permissions through `Role`.

#### Methods

```python
# Syntax: :meth:`ClassName.method_name <full.module.path.ClassName.method_name>`
# Shows only ClassName.method_name to users

def update_profile():
    """
    Update user profile information.
    
    Uses :meth:`User.get_profile <shai_tix.auth.users.User.get_profile>` 
    to retrieve current data before updating.
    """
    pass
```

**Rendered as**: Uses `User.get_profile` to retrieve current data.

#### Functions

```python
# Syntax: :func:`~full.module.path.function_name`
# The ~ hides the full path, showing only the function name

def login_user():
    """
    Handle user login process.
    
    Calls :func:`~shai_tix.auth.users.authenticate` to verify credentials
    and :func:`~shai_tix.auth.permissions.check_permission` for authorization.
    """
    pass
```

**Rendered as**: Calls `authenticate` to verify credentials and `check_permission` for authorization.

#### Modules

```python
# Syntax: :mod:`full.module.path`
# Shows the full module path (no ~ used for modules)

def setup_auth():
    """
    Initialize authentication system.
    
    Configures components from :mod:`shai_tix.auth.users` and 
    :mod:`shai_tix.auth.permissions` modules.
    """
    pass
```

**Rendered as**: Configures components from `shai_tix.auth.users` and `shai_tix.auth.permissions` modules.

### 2. Referencing Elements Within the Same Module

Use short paths when referencing elements in the same Python file:

#### Example: shai_tix/auth/users.py

```python
class User:
    """
    User account management.
    
    Uses :func:`authenticate` for credential validation.
    """
    
    def get_profile(self) -> dict:
        """
        Get user profile data.
        
        This method works with :class:`User` instances created through
        the :func:`authenticate` function.
        """
        pass

def authenticate(username: str, password: str) -> bool:
    """
    Authenticate user credentials.
    
    Returns a :class:`User` instance if authentication succeeds.
    Call :meth:`User.get_profile` after successful authentication.
    """
    pass
```

#### Syntax Summary for Same Module

- **Class**: `:class:`ClassName``
- **Method**: `:meth:`ClassName.method_name``  
- **Function**: `:func:`function_name``

### 3. Referencing Documentation Sections

Reference specific `.rst` documents using labels:

#### Setting Up Labels in .rst Files

**docs/source/01-Getting-Started/index.rst**:

```rst
.. _getting-started:

Getting Started
===============

This section covers basic setup and configuration.

.. _installation-guide:

Installation
------------

Step-by-step installation instructions.
```

**docs/source/02-API-Reference/index.rst**:

```rst
.. _api-reference:

API Reference
=============

Complete API documentation.

.. _authentication-api:

Authentication API  
------------------

User authentication functions and classes.
```

#### Using References in Docstrings
```python
def setup_project():
    """
    Initialize a new project.
    
    Follow the :ref:`getting-started` guide for complete setup instructions.
    See :ref:`authentication-api` for security configuration details.
    
    For installation help, check the :ref:`installation section <installation-guide>`.
    """
    pass
```

#### Using References in .rst Files
```rst
Database Models
===============

The database layer provides several key components. Start with the
:ref:`getting-started` guide, then review the :class:`~shai_tix.database.models.BaseModel`
class documentation.

For connection management, see :func:`~shai_tix.database.connection.connect`
and the :ref:`Advanced Usage Guide <advanced-usage>`.
```

## Complete Example: Cross-Module References

### shai_tix/database/models.py
```python
"""
Database model definitions.

This module provides base classes for all database operations. Models inherit
from :class:`BaseModel` and use connections created by 
:func:`~shai_tix.database.connection.connect`.

See the :ref:`api-reference` documentation for complete usage examples.
"""

from typing import Optional

class BaseModel:
    """
    Base class for all database models.
    
    Provides common functionality for database operations. Subclasses should
    implement their own validation logic while using the connection established
    through :func:`~shai_tix.database.connection.connect`.
    
    Integration with authentication is handled through 
    :class:`~shai_tix.auth.users.User` instances. User permissions are
    validated using :func:`~shai_tix.auth.permissions.check_permission`.
    
    :param table_name: Database table name for this model
    :param connection: Database connection instance
    
    Example:
        Creating a model with authentication::
        
            user = User("john_doe") 
            if check_permission(user.username, "read"):
                model = BaseModel("users", db_connection)
                profile = user.get_profile()
    
    .. note::
        See :ref:`getting-started` for setup instructions and 
        :ref:`authentication-api` for security best practices.
    """
    
    def __init__(self, table_name: str, connection):
        self.table_name = table_name
        self.connection = connection
    
    def save(self) -> None:
        """
        Save model instance to database.
        
        Uses the connection established by :func:`~shai_tix.database.connection.connect`.
        Requires authentication through :func:`~shai_tix.auth.users.authenticate`.
        """
        pass
    
    def find_by_id(self, record_id: int) -> Optional[dict]:
        """
        Find record by primary key.
        
        :param record_id: Primary key value to search for
        
        :returns: Record data if found, None otherwise
        
        .. seealso::
            :meth:`save` for creating new records and 
            :func:`~shai_tix.database.connection.Database.query` for custom queries.
        """
        pass
```

## Best Practices

### 1. Consistency Rules

- **Always use `~`** for classes and functions from other modules (hides full path)
- **Never use `~`** for modules (users need to see full module path)
- **Use descriptive text** with angle brackets when the default text isn't clear

### 2. Reference Documentation Sections
```python
def complex_operation():
    """
    Perform complex database operation.
    
    This function requires understanding of several concepts:
    
    - Basic setup: :ref:`getting-started`
    - Database configuration: :ref:`database-setup-guide` 
    - Security considerations: :ref:`authentication and authorization <auth-guide>`
    """
    pass
```

### 3. Group Related References
```python
class UserManager:
    """
    Comprehensive user management system.
    
    **Core Components:**
    
    - User creation: :class:`~shai_tix.auth.users.User`
    - Authentication: :func:`~shai_tix.auth.users.authenticate`
    - Authorization: :func:`~shai_tix.auth.permissions.check_permission`
    - Data persistence: :class:`~shai_tix.database.models.BaseModel`
    
    **Related Documentation:**
    
    - Setup guide: :ref:`getting-started`
    - API reference: :ref:`authentication-api`
    - Advanced patterns: :ref:`user-management-patterns`
    """
    pass
```

### 4. Error Prevention
```python
# ❌ Wrong - missing backticks
:class:User

# ❌ Wrong - unnecessary ~ for same module  
:class:`~User`

# ❌ Wrong - missing ~ for external module
:class:`shai_tix.auth.users.User`

# ✅ Correct - same module
:class:`User`

# ✅ Correct - external module with ~
:class:`~shai_tix.auth.users.User`
```

## Quick Reference Table

| Element Type | Same Module | Different Module | Display Result |
|--------------|-------------|------------------|----------------|
| **Class** | :class:`User` | :class:`~package.module.User` | `User` |
| **Method** | :meth:`User.save` | :meth:`User.save <package.module.User.save>` | `User.save` |
| **Function** | :func:`authenticate` | :func:`~package.module.authenticate` | `authenticate` |
| **Module** | N/A | :mod:`package.module` | `package.module` |
| **Documentation** | :ref:`section-label` | :ref:`Custom Text <section-label>` | `section-label` or `Custom Text` |

This cross-reference system creates rich, navigable documentation that helps users understand relationships between code components and find relevant information quickly.