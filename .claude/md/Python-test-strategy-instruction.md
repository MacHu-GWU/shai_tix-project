# Test Strategy

## Unit Test File Organization

Each Python file in your project's source directory has a corresponding unit test file in the `tests/` directory. For example, source code at `shai_tix/<subpackage>/<module>.py` has its test file at `tests/<subpackage>/test_<subpackage>_<module>.py`. The test file name includes the full relative path to prevent naming collisions.

**Example:**

- Source: `shai_tix/math/operations/calculator.py`
- Test: `tests/math/operations/test_math_operations_calculator.py`

## Package Test Directory Structure

Each Python package (directory containing `__init__.py`) has a corresponding test directory in `tests/`. For example, the package at `shai_tix/<subpackage>/` has its test directory at `tests/<subpackage>/`. Each test directory contains an `all.py` file that runs code coverage tests for all modules in that package.

**Example:**

- Package: `shai_tix/math/operations/`
- Test directory: `tests/math/operations/`
- Test for entire package: `tests/math/operations/all.py`

## Running Code Coverage Tests for Individual Files

Each test file can be run directly to generate a coverage report:

```bash
.venv/bin/python tests/<subpackage>/test_<subpackage>_<module>.py
```

**Example:**
```bash
.venv/bin/python tests/math/operations/test_math_operations_calculator.py
```

This will:

1. Run all unit tests for the specific module
2. Generate a code coverage HTML report at `htmlcov/${random_hash}_<module>_py.html`
3. Show covered and uncovered lines in the HTML report

This is the most important workflow since 90% of development involves editing a single source file and running its corresponding test to meet coverage goals.

## Running Code Coverage Tests for All Files

Each source code directory has a corresponding `all.py` test script. Running `tests/all.py` executes code coverage tests for the entire Python package:

```bash
.venv/bin/python tests/all.py
```

You can also run coverage tests for a specific package:

```bash
.venv/bin/python tests/shai_tix/all.py
```

**Example:**
```bash
.venv/bin/python tests/math/all.py
```

## Code Coverage Configuration

The `.coveragerc` file in the root directory configures the coverage tool, specifying which files to exclude from coverage reports in the `omit` section.

## Viewing Coverage Reports

After running tests, open the generated HTML file to see:

- Green lines: Code executed during tests
- Red lines: Code not covered by tests  
- Line-by-line coverage details

## Coverage Goals

- Target 95%+ code coverage for all implementation files
- Use `# pragma: no cover` for untestable code (e.g., platform-specific code when testing on different platforms)

## Public API and Testing

The package always includes a `api.py` file that exposes all public APIs for package users. Each line in this file defines a Python class, function, or variable.

**Example for a project named `shai_tix`:**
```python
# In shai_tix/api.py
from .math.operations import add_numbers
from .math.operations import subtract_numbers
```

We follow this pattern (one import per line):

```python
from .my_module import my_func_1
from .my_module import my_func_2
```

We avoid this pattern (multiple imports per line):

```python
from .my_module import my_func_1, my_func_2
```

The corresponding test file is located at `tests/test_api.py`. This test file imports all public API objects from `api.py` to establish a test baseline, ensuring that any changes to the public API in `api.py` are caught by unit tests.

Example `tests/test_api.py` for `shai_tix`:
```python
from shai_tix import api

def test():
    _ = api
    _ = api.my_func_1
    _ = api.my_func_2
```

---

*Note: Throughout this guide, `<subpackage>`, and `<module>` are placeholders that should be replaced with your actual project structure. The examples using `shai_tix` demonstrate how these concepts apply to a real project.*
