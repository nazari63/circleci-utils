import typer
import re  # For regular expressions
from github import Github, GithubIntegration, GithubException
from typing import Optional  # Import Optional for type hinting
from pathlib import Path  # For file operations
from pprint import pprint  # For pretty printing
from commands import (
    post_pr_comment,
    delete_pr_comment,
    process_issues,
    process_pull_requests,
    get_comments_ids,
    get_pr_base_sha,
    create_issue_from_string,
)
app = typer.Typer(help="CLI tool for GitHub operations.",
                  pretty_exceptions_show_locals=False)


def fix_pem_string(content: str) -> str:
    """
    Fix the formatting of a PEM string by replacing spaces in the body with newlines.
    """
    content = re.sub(r"(-----BEGIN [A-Z ]+-----)\s+",
                     r"\1\n", content)  # Fix BEGIN line
    content = re.sub(r"\s+(-----END [A-Z ]+-----)",
                     r"\n\1", content)    # Fix END line

    # Replace spaces in the body with newlines
    fixed_content = re.sub(r"(?<=-----\n)(.+?)(?=\n-----)",
                           lambda match: match.group(0).replace(" ", "\n"),
                           content, flags=re.S)
    return fixed_content


def get_github_client(
    github_token: Optional[str] = None
) -> Github:
    """
    Create a GitHub client using either a GitHub token

    :param github_token: Personal GitHub token.
    :return: Authenticated GitHub client.
    """
    if github_token:
        return Github(github_token)
    else:
        typer.echo(
            f"Provide a GitHub token to authenticate with GitHub.", err=True)
        raise typer.Exit(code=1)


@app.command("get-github-access-token")
def get_github_acces_token(
    app_id: Optional[int] = None,
    private_key_path: Optional[Path] = None,
    private_key_str: Optional[str] = None,
    repo: Optional[str] = None,
) -> str:
    """
    Create a GitHub client using either a GitHub token or GitHub App credentials.

    :param github_token: Personal GitHub token.
    :param app_id: GitHub App ID.
    :param private_key_path: Path to the GitHub App private key file.
    :param private_key_str: Private key as a string.
    :param repo: Repository in the format 'owner/repo', required for GitHub App.
    :return: access token.
    """
    if app_id and (private_key_path or private_key_str) and repo:
        # Read private key from file or use the provided string
        private_key = None
        if private_key_path:
            if not private_key_path.exists() or not private_key_path.is_file():
                raise FileNotFoundError(f"Private key file '{
                                        private_key_path}' does not exist.")
            with private_key_path.open("r") as key_file:
                private_key = key_file.read()
        elif private_key_str:
            private_key = private_key_str

        if not private_key:
            raise ValueError(
                "A valid private key must be provided as a file or string.")

        private_key = fix_pem_string(private_key)
        # Authenticate using GitHub App
        integration = GithubIntegration(app_id, private_key)

        try:
            owner, repo_name = repo.split("/")
            installation = integration.get_repo_installation(owner, repo_name)
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"GitHub App is not installed on the repository '{
                    repo}' or the credentials are invalid.")
            raise e
        access_token = integration.get_access_token(installation.id).token
        typer.echo(f"{access_token}")
    else:
        typer.echo(
            f"Provide GitHub App credentials (app_id, private_key, and repo).", err=True)
        raise typer.Exit(code=1)


@app.command("create-issue-from-file")
def cli_create_issue_from_file(
    github_token: Optional[str] = typer.Option(
        None, help="GitHub token with permissions to create issues."),
    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    file_path: Path = typer.Option(...,
                                   help="Path to the file containing issue content."),
    issue_title: str = typer.Option(..., help="Title of the issue to create."),
    issue_labels: Optional[str] = typer.Option(
        None, help="Comma-separated list of labels for the issue."),
    assignees: Optional[str] = typer.Option(
        None, help="Comma-separated list of GitHub usernames to assign."),
):
    """
    Create an issue from a file, with optional labels and assignees.
    """
    try:
        # Read file content
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(
                f"The file '{file_path}' does not exist or is not a valid file.")

        with file_path.open("r") as file:
            issue_body = file.read().strip()

        if not issue_body:
            raise ValueError(
                "The file is empty. Provide a file with valid issue content.")

        # Connect to GitHub
        github = get_github_client(github_token)

        issue = create_issue_from_string(
            github, repo, issue_title, issue_body, issue_labels, assignees)

        typer.echo(f"Issue #{issue.number} created successfully: {
                   issue.html_url}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("create-issue-from-string")
def cli_create_issue_from_string(
    github_token: Optional[str] = typer.Option(
        None, help="GitHub token with permissions to create issues."),

    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    issue_body: str = typer.Option(..., help="Content of the issue."),
    issue_title: str = typer.Option(..., help="Title of the issue to create."),
    issue_labels: Optional[str] = typer.Option(
        None, help="Comma-separated list of labels for the issue."),
    assignees: Optional[str] = typer.Option(
        None, help="Comma-separated list of GitHub usernames to assign."),
):
    """
    Create an issue from a string, with optional labels and assignees.
    """
    try:
        # Connect to GitHub
        github = get_github_client(github_token)

        issue = create_issue_from_string(
            github, repo, issue_title, issue_body, issue_labels, assignees)

        typer.echo(f"Issue #{issue.number} created successfully: {
                   issue.html_url}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("post-pr-comment")
def cli_post_pr_comment(
    github_token: Optional[str] = typer.Option(
        None, help="GitHub token with permissions to create issues."),

    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    pr_number: int = typer.Option(..., help="Pull request number."),
    comment_body: str = typer.Option(..., help="The comment text."),
    comment_id: Optional[int] = typer.Option(
        None,
        "--comment-id",
        help="ID of the comment to update. If not provided, a new comment will be created."
    ),
):
    """Post or update a comment on a pull request."""
    try:
        github = get_github_client(github_token)

        result = post_pr_comment(
            github, repo, pr_number, comment_body, comment_id)
        typer.echo(result)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("delete-pr-comment")
def cli_delete_pr_comment(
    github_token: Optional[str] = typer.Option(
        None, help="GitHub token with permissions to create issues."),

    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    pr_number: int = typer.Option(..., help="Pull request number."),
    comment_id: int = typer.Option(
        None,
        "--comment-id",
        help="ID of the comment to delete."
    ),
):
    """Delete a comment with provided comment id on a pull request."""
    try:
        github = get_github_client(github_token)

        result = delete_pr_comment(
            github, repo, pr_number, comment_id)
        typer.echo(result)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("process-stale-issues")
def cli_process_issues(
    github_token: Optional[str] = typer.Option(
        None, help="GitHub token with permissions to create issues."),

    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    stale_issue_label: str = typer.Option(
        "S-stale", help="Label to mark stale issues."),
    days_before_stale: int = typer.Option(
        999, help="Number of days before an issue is considered stale."),
    days_before_close: int = typer.Option(
        5, help="Number of days before a stale issue is closed."),
):
    """Process stale issues."""
    try:
        github = get_github_client(github_token)

        process_issues(
            github,
            repo,
            stale_issue_label,
            days_before_stale,
            days_before_close,
        )
        typer.echo("Stale issue check completed successfully.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("process-stale-prs")
def cli_process_pull_requests(
    github_token: Optional[str] = typer.Option(
        None, help="GitHub token with permissions to create issues."),

    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    stale_pr_message: str = typer.Option(
        "This PR is stale because it has been open 14 days with no activity. Remove stale label or comment or this will be closed in 5 days.",
        help="Message to post on stale PRs."
    ),
    stale_issue_label: str = typer.Option(
        "S-stale", help="Label to mark stale PRs."),
    exempt_labels: str = typer.Option(
        "S-exempt-stale", help="Comma-separated exempt labels."),
    days_before_stale: int = typer.Option(
        14, help="Number of days before a PR is considered stale."),
    days_before_close: int = typer.Option(
        5, help="Number of days before a stale PR is closed."),
):
    """Process stale pull requests."""
    try:
        github = get_github_client(github_token)

        process_pull_requests(
            github,
            repo,
            stale_pr_message,
            stale_issue_label,
            exempt_labels.split(","),
            days_before_stale,
            days_before_close,
        )
        typer.echo("Stale PR check completed successfully.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("get-pr-comments")
def cli_get_pr_comments(
    github_token: Optional[str] = typer.Option(
        None, help="GitHub token with permissions to create issues."),

    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    pr_number: int = typer.Option(..., help="Pull request number."),
    message_substring: str = typer.Option(...,
                                          help="Substring to search in comments."),
    user_type: str = typer.Option(
        ..., help="User type to filter comments. Can be 'User' or 'Bot'."),
):
    try:
        github = get_github_client(github_token)

        comment_ids = get_comments_ids(
            github, repo, pr_number, message_substring, user_type)
        typer.echo(",".join(map(str, comment_ids)))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("get-pr-base-sha")
def cli_get_pr_base_sha(
    github_token: Optional[str] = typer.Option(
        None, help="GitHub token with permissions to create issues."),

    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    pr_number: int = typer.Option(..., help="Pull request number."),
):
    """
    Get the base commit SHA of a pull request.
    """
    try:
        github = get_github_client(github_token)

        base_sha = get_pr_base_sha(github, repo, pr_number)
        typer.echo(f"{base_sha}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
