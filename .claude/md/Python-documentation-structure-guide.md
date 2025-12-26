# Sphinx Documentation Structure Guide

This guide establishes a universal documentation structure standard for Sphinx projects using the autotoctree plugin.

## Directory Structure

All documentation lives in `docs/source/` following this pattern:

```
docs/source/
├── 01-Introduction/
│   └── index.rst
├── 02-Configuration/
│   └── index.rst
├── 03-User-Guide/
│   └── index.rst
└── 04-Developer-Guide/
    ├── index.rst
    ├── 01-Architecture-Overview/
    │   └── index.rst
    └── 02-Testing-Strategy/
        └── index.rst
```

## Naming Convention

```
${sequence-number}-${short-title}/index.rst
```

- **Sequence Number**: Two digits (01, 02, 03...) for ordering
- **Short Title**: Title-Case-With-Hyphens, no articles or prepositions
- **Always Directory**: Never standalone `.rst` files (required for autotoctree)

## Document Header Format

Every `index.rst` must start with:

```rst
.. _${reference-label}:

${Document Title}
==============================================================================
*Optional subtitle*

Content starts here...
```

### Rules:

1. **Reference Label**: Lowercase slugified title (permanent, unique)
2. **Title Underline**: 79 equals signs, or match title length if >79 chars
3. **Required Elements**: Reference label, title, underline

### Examples:

```rst
.. _user-authentication:

User Authentication and Authorization
==============================================================================
*Comprehensive guide to security implementation*
```

```rst
.. _api-reference:

API Reference
==============================================================================
```

## Cross-References

Link between documents using reference labels:

```rst
See :ref:`user-authentication` for security details.
```

## Integration

Works automatically with Sphinx autotoctree:

```rst
.. autotoctree::
    :maxdepth: 1
```

This structure ensures consistent, maintainable documentation across all projects using Sphinx with autotoctree.