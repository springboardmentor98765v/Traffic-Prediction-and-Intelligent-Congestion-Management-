# Day 4 — CI Automated Tests on Pull Requests

## Project
TrafficVision AI — Milestone 1

## Role
Intern 5 — DevOps

## Objective
Ensure the TrafficVision AI CI workflow executes the automated API test suite whenever a Pull Request is created or updated.

## Required Checks

1. Checkout the repository.
2. Set up the required Python environment.
3. Install API test dependencies.
4. Run the automated API test suite with pytest.
5. Execute configured backend quality checks.
6. Execute frontend lint/build checks when available.
7. Report the CI result on the Pull Request.
8. Do not include a deployment stage in Milestone 1.

## API Test Command

```bash
pytest -q
```

The command discovers and executes tests according to the API testing skeleton configuration.

## Pull Request Flow

```text
Pull Request Created / Updated
              ↓
       GitHub Actions
              ↓
      Checkout Repository
              ↓
       Setup Python 3.11
              ↓
     Install Test Dependencies
              ↓
          pytest -q
              ↓
        PASS / FAIL
```

## Expected Result

- A Pull Request starts the CI workflow.
- Automated API tests are executed by the API-test job.
- If pytest reports a test failure, the CI job fails.
- The CI result is visible on the Pull Request.
- No deployment is performed.

## Environment Dependency

The API test suite requires a reachable Authentication and Traffic Monitoring service. Until those live services are available, the API tests cannot be truthfully marked as Passed or Failed.

The CI configuration is prepared so the automated API suite can be executed when the services are available.

## Milestone 1 Boundary

No deployment stage is included. CI is used for quality validation, lint/build checks, and automated testing only.

## Final Status

**CI CONFIGURED — LIVE API EXECUTION PENDING SERVICE AVAILABILITY**
