# GitHub Actions Repository Audit

This tool audits GitHub Actions usage across all repositories in a GitHub organization. It provides information about each repository's status, including whether Actions are enabled and how many workflow files exist.

## Features

- Lists all repositories in an organization
- Shows repository visibility (public/private)
- Indicates if repositories are archived or disabled
- Counts GitHub Actions workflow files
- Checks if Actions are enabled for each repository
- Exports results to CSV
- Provides summary statistics

## Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token with the following permissions:
  - `repo` (Full access to private repositories)
  - `workflow` (Update GitHub Action workflows)
  - `read:org` (Read organization data)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ethereum-optimism/circleci-utils
   cd admin_utils/repository_audit
   ```

2. Create and configure the environment file:
   ```bash
   echo "GITHUB_TOKEN=your-token-here" > .env
   echo "GITHUB_ORG=your-org-name" >> .env
   ```

3. Set up the virtual environment and install dependencies:
   ```bash
   make setup
   ```

## Usage

1. Run the script:
   ```bash
   make run
   ```

   Or manually activate the virtual environment and run:
   ```bash
   source venv/bin/activate
   python github_actions_audit.py
   ```

2. If the `GITHUB_ORG` environment variable is not set, you will be prompted to enter the organization name.

3. The script will generate a CSV file with the naming format: `github_actions_audit_<org-name>_<timestamp>.csv`

## Output

The tool generates two types of output:

1. Console output showing:
   - Total number of repositories
   - Number of repositories with workflows
   - List of repositories that have GitHub Actions configured

2. CSV file with detailed information including:
   - Repository name
   - Visibility status
   - Archive status
   - Actions enabled/disabled
   - Workflow count
   - Creation and last update dates
   - Default branch
   - Repository URL

## Maintenance

To clean up the environment and generated files:
```bash
make clean
```

This will:
- Remove the virtual environment
- Delete all generated CSV files
- Clean up Python cache files

## Error Handling

The script includes error handling for:
- GitHub API request failures
- Authentication issues
- Missing environment variables
- Invalid organization names

If any errors occur, they will be displayed in the console with appropriate error messages.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[MIT License](LICENSE)