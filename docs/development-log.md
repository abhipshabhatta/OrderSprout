# Development log

This log records completed work, checks, and important project decisions.

## Milestone 1: Project foundation

Status: Merged into main through pull request #1

Branch: codex/project-setup

### Changes

- Documented the project purpose and planned first version.
- Added ignore rules for virtual environments, Python caches,
  local application data, environment files, and test output.
- Documented requirements and completion checks.
- Created this development log.

### Validation

- Confirmed the GitHub remote configuration.
- Confirmed Git ignores the .venv directory.
- Passed whitespace checks.

## Milestone 2: Local order management application

Status: Implementation and local checks complete; awaiting PR review

Branch: codex/add-order-book

Pull request: #2

### Changes

- Adapted the small-order-book starter into OrderSprout.
- Added Flask application logic and SQLite storage.
- Added forms for creating and editing orders.
- Added server-side validation and form security tokens.
- Added dashboard totals and remaining-balance calculations.
- Added responsive styling for the dashboard and order form.
- Documented local setup and test instructions.
- Added 19 automated tests using temporary databases.

### Manual validation

- Created an order totaling EUR 40.00 with EUR 10.00 paid.
- Confirmed EUR 30.00 remained.
- Updated the payment to EUR 40.00 and status to Ready.
- Confirmed EUR 0.00 remained.
- Restarted the application and confirmed the order persisted.
- Checked that summary cards stack on a narrow screen.
- Checked that the orders table scrolls horizontally.
- Checked that form fields stack and the save button remains visible.

### Automated validation

- Python syntax check passed.
- Whitespace checks passed before previous commits.
- Local pytest result: 19 passed.

### Decisions

- Keep the first version local and intended for one seller.
- Store money as whole cents.
- Keep local order data and environment files out of Git.
- Use port 5002 locally because port 5001 was occupied.
- Keep related implementation commits in one milestone branch.
- Introduce CI and deployment in separate milestones.

### Remaining work

- Commit and push the updated documentation.
- Review the final pull request changes and available GitHub checks.
- Mark the draft pull request ready for review.
- Merge after review and update the local main branch.