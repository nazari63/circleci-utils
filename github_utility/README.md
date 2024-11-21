# GitHub CLI Tool

A command-line interface (CLI) tool for performing common GitHub operations, such as posting comments on pull requests, using [PyGitHub](https://pygithub.readthedocs.io/) and [Typer](https://typer.tiangolo.com/).

## Features

- Post comments on GitHub pull requests.
- Expandable to include other GitHub operations.
- Pythonic CLI using Typer for a clean, user-friendly experience.

## Installation

### Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/)

### Steps

1. Clone the repository:

```bash
   git clone git@github.com:ethereum-optimism/circleci-utils.git
   cd github_utility/github_cli
```

2. Install dependencies using Poetry:

```bash
   poetry install
```

   This will:
   - Create a virtual environment for the project.
   - Install all required dependencies from `pyproject.toml`.
   - Set up CLI scripts for the project.

3. Activate the virtual environment:

```bash
   poetry shell
```
   Alternatively, you can run commands directly using `poetry run`.

---

## Usage

The CLI tool is accessible via `github-cli`. Below is a list of available commands and examples.

### Post a Comment on a Pull Request

```bash
poetry run post-pr-comment "${REPO}" "${PR_NUMBER}" "${COMMENT_BODY}" "${GITHUB_TOKEN}"
```

#### Parameters:
- `repo`: GitHub repository in the format `owner/repo` (e.g., `octocat/Hello-World`).
- `pr_number`: The pull request number.
- `comment_body`: The text of the comment to post.
- `github_token`: A GitHub token with permission to comment on the repository.

#### Example:

```bash
github-cli post-pr-comment octocat/Hello-World 123 "This is a test comment" ghp_YourPersonalAccessToken
```

### Running Without Installing Globally

If you don't want to install the CLI globally, you can use `poetry run`:

```bash
poetry run github-cli post-pr-comment octocat/Hello-World 123 "Hello, World!" ghp_YourPersonalAccessToken
```

---

## Project Structure

github_cli/  
├── __init__.py        # Module initializer  
├── commands.py        # Implementation of GitHub operations  
├── main.py            # Typer CLI entry point  
pyproject.toml         # Poetry configuration file  

---

## Development

### Adding New Commands

1. Define the new command in `github_cli/commands.py` or another module.
2. Register the command in `main.py` using `@app.command`.

### Installing New Dependencies

To add a new dependency, use:

```bash
poetry add <package-name>
```

For development-only dependencies, use:

```bash
poetry add --dev <package-name>
```

### Running the Tool Locally

Run the tool using:

```bash
poetry run github-cli <command>
```
---
