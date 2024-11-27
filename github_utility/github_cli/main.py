import typer
from github import Github
from typing import Optional  # Import Optional for type hinting
from commands import (
    post_pr_comment,
    delete_pr_comment,
    process_issues,
    process_pull_requests,
    get_comments_ids,
    get_pr_base_sha,
)
app = typer.Typer(help="CLI tool for GitHub operations.")


@app.command("post-pr-comment")
def cli_post_pr_comment(
    github_token: str = typer.Option(...,
                                     help="GitHub token with permissions to comment."),
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
        github = Github(github_token)
        result = post_pr_comment(
            github, repo, pr_number, comment_body, comment_id)
        typer.echo(result)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("delete-pr-comment")
def cli_delete_pr_comment(
    github_token: str = typer.Option(...,
                                     help="GitHub token with permissions to comment."),
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
        github = Github(github_token)
        result = delete_pr_comment(
            github, repo, pr_number, comment_id)
        typer.echo(result)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("process-stale-issues")
def cli_process_issues(
    github_token: str = typer.Option(...,
                                     help="GitHub token for authentication."),
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
        github = Github(github_token)
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
    github_token: str = typer.Option(...,
                                     help="GitHub token for authentication."),
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
        github = Github(github_token)
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
    github_token: str = typer.Option(...,
                                     help="GitHub token for authentication."),
    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    pr_number: int = typer.Option(..., help="Pull request number."),
    message_substring: str = typer.Option(...,
                                          help="Substring to search in comments."),
    user_type: str = typer.Option(
        ..., help="User type to filter comments. Can be 'User' or 'Bot'."),
):
    try:
        github = Github(github_token)
        comment_ids = get_comments_ids(
            github, repo, pr_number, message_substring, user_type)
        typer.echo(",".join(map(str, comment_ids)))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("get-pr-base-sha")
def cli_get_pr_base_sha(
    github_token: str = typer.Option(...,
                                     help="GitHub token for authentication."),
    repo: str = typer.Option(...,
                             help="GitHub repository in the format 'owner/repo'."),
    pr_number: int = typer.Option(..., help="Pull request number."),
):
    """
    Get the base commit SHA of a pull request.
    """
    try:
        github = Github(github_token)
        base_sha = get_pr_base_sha(github, repo, pr_number)
        typer.echo(f"{base_sha}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
