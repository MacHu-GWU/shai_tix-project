# shai_tix Project Guide

## Project Overview

See @README.rst for complete project overview.

## Core Development Guides

See @./docs/source/design.md for solution design.

### Python Development Standards

- **Virtual Environment**: @./.claude/md/Python-virtual-environment-setup-instruction.md
- **Testing Strategy**: @./.claude/md/Python-test-strategy-instruction.md
- **Docstring Guide**: @./.claude/md/Python-docstring-guide.md
- **API Documentation**: @./.claude/md/Python-cross-reference-api-doc-guide.md
- **Documentation Structure**: @./.claude/md/Python-documentation-structure-guide.md

## Essential Commands

- **All Operations**: @./Makefile (run `make help` for full command list)
- **Python Execution**: Use `.venv/bin/python` for all Python scripts in:
  - `debug/**/*.py` - Debug utilities
  - `scripts/**/*.py` - Automation scripts
  - `config/**/*.py` - Configuration deployment
  - `tests/**/*.py` - Unit and integration tests

## Quick Start Workflow

1. **Setup**: `make venv-create && make install-all`
2. **Update Dependencies**: ``make poetry-lock && make poetry-export && make install``
3. **Development**: Edit code in ``shai_tix/**/*.py`` → Run tests ``.venv/bin/python tests/**/*.py``
4. **Testing**: `make test` or `make cov` for coverage
5. **Build Document**: `make build-doc && make view-doc` for build sphinx docs and open local html doc site in web browser
