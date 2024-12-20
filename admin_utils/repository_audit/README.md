# GitHub Actions Repository Audit

A tool to audit GitHub Actions usage across repositories. It can analyze either a single repository or all repositories in an organization, providing detailed information about Actions configuration and workflow files.

## Features

- Audit single repository or entire organization
- Detailed Actions permissions and settings
- Workflow file detection and validation
- Repository status information (visibility, archive status, etc.)
- CSV export of results
- Detailed console output during audit

## Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token with permissions:
  - `repo` (Full access to repositories)
  - `workflow` (Access to Actions and workflows)
  - `read:org` (Read organization data)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ethereum-optimism/circleci-utils
cd admin_utils/repository_audit
```

2. Set up environment variables (optional):
```bash
export GITHUB_TOKEN=your-token-here
export GITHUB_ORG=your-org-name
```

3. Install dependencies:
```bash
make setup
```

## Usage

### Command Line Options

```bash
python github_actions_audit.py --help
```

Available options:
- `--org`: GitHub organization name
- `--repo`: Specific repository to audit (optional)
- `--token`: GitHub token (if not set in environment)

### Using Make Commands

1. Audit all repositories in an organization:
```bash
# Using environment variables
make run

# Specifying organization
make run ORG=your-org-name
```

2. Audit a single repository:
```bash
# Using environment variables
make run-single REPO=repository-name

# Specifying both org and repo
make run-single ORG=your-org-name REPO=repository-name
```

3. Clean up generated files:
```bash
make clean
```

## Output

### Console Output
The tool provides real-time feedback during the audit:
- Repository being checked
- Actions status and permissions
- Workflow files found
- Any errors or issues encountered

### CSV Output
Generated CSV file includes:
- Repository information (name, visibility, status)
- Actions configuration details
- Workflow file information
- Timestamps and URLs

File naming format:
- All repositories: `github_actions_audit_<org>_<timestamp>.csv`
- Single repository: `github_actions_audit_<org>_<repo>_<timestamp>.csv`

## CSV Columns

| Column | Description |
|--------|-------------|
| repository | Repository name |
| visibility | Public or private |
| archived | Repository archive status |
| actions_enabled | Whether Actions are enabled |
| actions_status | Current Actions status |
| allowed_actions | Types of actions allowed |
| workflow_count | Number of workflow files |
| workflow_files | Names of workflow files |
| default_branch | Default branch name |
| url | Repository URL |

## Development

1. Install development dependencies:
```bash
make dev-setup
```

2. Run linting:
```bash
make lint
```

## Troubleshooting

Common issues:

1. Authentication Errors:
- Ensure GITHUB_TOKEN is set and has required permissions
- Token should be a valid PAT (Personal Access Token)

2. Access Issues:
- Verify organization membership
- Check repository access permissions
- Ensure token has necessary scopes

3. Rate Limiting:
- Tool respects GitHub API rate limits
- For large organizations, audit may take longer

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Submit a pull request

## License

[MIT License](LICENSE)