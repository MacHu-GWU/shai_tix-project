# Virtual Environment Setup

We create the Python virtual environment in the `.venv` directory at the project root. Key tools include:

- `.venv/bin/python`: Virtual environment Python interpreter, use this for running all Python scripts in:
    - `debug/**/*.py`: Debug utilities
    - `scripts/**/*.py`: Automation scripts
    - `config/**/*.py`: Configuration deployment
    - `tests/**/*.py`: Unit tests
    - `tests_int/**/*.py`: Integration tests
    - `manual_tests/**/*.py`: Manual tests
- `.venv/bin/pip`: pip package manager for installing ad-hoc Python packages. For predefined packages in `pyproject.toml`, we primarily use the global `poetry` 2.x command
- `.venv/bin/pytest`: pytest test runner for executing unit tests
