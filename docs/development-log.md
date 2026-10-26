# Development log

This log records completed work, checks, and important project decisions.

## Milestone 1: Project foundation

Status: In progress

Branch: codex/project-setup

### Changes

- Documented the project purpose and planned first version in README.md.
- Added ignore rules for virtual environments, Python caches,
  local application data, environment files, and test output.
- Documented the first-version requirements and completion checks.
- Created this development log.

### Checks performed

- Confirmed the repository has an origin remote configured for GitHub.
- Confirmed work is on the codex/project-setup branch.
- Confirmed Git ignores the .venv directory.

### Decisions

- Build the application incrementally from the small-order-book starter.
- Use Python, Flask, HTML, CSS, and SQLite.
- Keep the first version local and intended for one seller.
- Keep local order data and environment files out of Git.
- Review changes through pull requests before merging into main.

### Remaining work

- Review and commit the foundation files.
- Push the setup branch to GitHub.
- Open and review a pull request.
- Merge the pull request and update the local main branch.