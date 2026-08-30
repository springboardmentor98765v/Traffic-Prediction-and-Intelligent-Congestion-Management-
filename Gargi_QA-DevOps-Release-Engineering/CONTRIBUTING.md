# QA Contribution Guidelines

## Before Committing

Run the following checks from the `Gargi_QA-DevOps-Release-Engineering` directory.

### 1. Run Tests

```bash
pytest -v
```

All tests should pass before committing.

### 2. Check Code Formatting

```bash
black --check tests
```

The command should complete without formatting errors.

### 3. Run Linting

```bash
flake8 tests
```

The command should complete without errors.

## Development Workflow

1. Pull the latest changes from the `Team-3` branch.
2. Make your changes.
3. Run the QA checks.
4. Fix any failed tests or code-quality issues.
5. Commit your changes with a meaningful commit message.
6. Push the changes to the `Team-3` branch.
7. Verify that the GitHub Actions QA CI workflow passes.

## Test Failure Handling

If a test fails:

1. Reproduce the failure.
2. Determine whether the issue is caused by the test or application code.
3. Record application defects in the QA defect tracker.
4. Fix or assign the defect.
5. Run the test again after the fix.
6. Confirm that existing tests still pass.

## Code Quality

Python test code should follow the project's Black and Flake8 configuration.

Generated files such as Python cache files and pytest cache files must not be committed.
