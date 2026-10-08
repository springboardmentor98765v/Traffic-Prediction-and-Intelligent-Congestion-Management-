# QA Quality Gates and Testing Workflow

## Quality Gates

- All changed code must pass lint and formatting checks.
- Unit tests must pass for impacted modules.
- Integration tests must pass for cross-service and data pipeline flows.
- No critical or high-severity defects remain open for the release candidate.
- Security and privacy review completed for data handling changes.
- Release owner signs off before deployment approval.

## Workflow

1. Developer implements and tests code locally.
2. PR submitted with required checklist and linked issues.
3. CI executes lint, format, and automated test checks.
4. QA runs smoke/regression validation for affected features.
5. Defects are logged, triaged, and retested.
6. Release manager approves only after all gates are satisfied.

## Release Readiness Rule

A build may proceed to production only when all mandatory quality gates are green and the release checklist is signed by QA and engineering.
