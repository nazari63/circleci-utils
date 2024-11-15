import requests
import datetime
import os
from dateutil.parser import parse as parse_date
from datetime import datetime, timezone
from pprint import pprint
import argparse

# Configuration
# Parse command line arguments
parser = argparse.ArgumentParser(description="Check for stale issues and PRs.")
parser.add_argument("--github-token", default=os.getenv("GITHUB_TOKEN"),
                    help="GitHub token for authentication")
parser.add_argument("--repo", default=os.getenv("REPO"),
                    help="GitHub repository in the format 'owner/repo'")
parser.add_argument("--stale-pr-message", default=os.getenv("STALE_PR_MESSAGE",
                    "This PR is stale because it has been open 14 days with no activity. Remove stale label or comment or this will be closed in 5 days."), help="Message to post on stale PRs")
parser.add_argument("--stale-issue-label", default=os.getenv(
    "STALE_ISSUE_LABEL", "S-stale"), help="Label to mark stale issues/PRs")
parser.add_argument("--exempt-pr-labels", default=os.getenv("EXEMPT_PR_LABELS", "S-exempt-stale"),
                    help="Comma-separated list of labels to exempt PRs from being marked as stale")
parser.add_argument("--days-before-issue-stale", type=int, default=int(os.getenv(
    "DAYS_BEFORE_ISSUE_STALE", 999)), help="Number of days before an issue is considered stale")
parser.add_argument("--days-before-pr-stale", type=int, default=int(os.getenv(
    "DAYS_BEFORE_PR_STALE", 14)), help="Number of days before a PR is considered stale")
parser.add_argument("--days-before-close", type=int, default=int(os.getenv(
    "DAYS_BEFORE_CLOSE", 5)), help="Number of days before a stale issue/PR is closed")
args = parser.parse_args()

# Configuration
GITHUB_TOKEN = args.github_token
REPO = args.repo
STALE_PR_MESSAGE = args.stale_pr_message
STALE_ISSUE_LABEL = args.stale_issue_label
EXEMPT_PR_LABELS = args.exempt_pr_labels.split(",")
DAYS_BEFORE_ISSUE_STALE = args.days_before_issue_stale
DAYS_BEFORE_PR_STALE = args.days_before_pr_stale
DAYS_BEFORE_CLOSE = args.days_before_close

# GitHub API setup
API_URL = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def get_open_issues_and_prs():
    """Retrieve open issues and pull requests from the repository."""
    url = f"{API_URL}/issues"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def is_stale(issue, days_before_stale):
    """Determine if the issue or PR is stale based on the last update date."""
    last_updated = parse_date(issue["updated_at"])
    days_since_update = (datetime.now(timezone.utc) - last_updated).days
    return days_since_update >= days_before_stale


def label_stale(issue):
    """Label the issue or PR as stale."""
    issue_number = issue["number"]
    url = f"{API_URL}/issues/{issue_number}/labels"
    data = {"labels": [STALE_ISSUE_LABEL]}
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    print(f"Labeled issue/PR #{issue_number} as stale.")


def close_stale(issue):
    """Close the stale issue or PR."""
    issue_number = issue["number"]
    url = f"{API_URL}/issues/{issue_number}"
    data = {"state": "closed"}
    response = requests.patch(url, json=data, headers=HEADERS)
    response.raise_for_status()
    print(f"Closed stale issue/PR #{issue_number}.")


def process_issues_and_prs():
    """Main function to process issues and PRs."""
    issues = get_open_issues_and_prs()
    print(f"Processing {len(issues)} issues and PRs...")
    for issue in issues:
        try:
            # Skip if the issue/PR has the exempt label
            if any(label["name"] in EXEMPT_PR_LABELS for label in issue.get("labels", [])):
                print(f"Skipping exempt issue/PR #{issue['number']}.")
                continue

            # Determine if the item is a PR or an issue
            is_pull_request = "pull_request" in issue

            # Set the stale period based on whether it is a PR or issue
            days_before_stale = DAYS_BEFORE_PR_STALE if is_pull_request else DAYS_BEFORE_ISSUE_STALE
            print(f"days_before_stale: {days_before_stale}")
            print(f"Processing {'PR' if is_pull_request else 'issue'} #{issue['number']}...")

            # Check if the issue or PR is stale
            if is_stale(issue, days_before_stale):
                if STALE_ISSUE_LABEL not in [label["name"] for label in issue.get("labels", [])]:
                    print(f"Stale issue/PR #{issue['number']} detected.")
                    label_stale(issue)
                elif is_stale(issue, DAYS_BEFORE_CLOSE):
                    print(f"Stale issue/PR #{issue['number']} closing.")
                    close_stale(issue)
            else:
                print(f"Issue/PR #{issue['number']} is not stale.")
        except Exception as e:
            print(f"Error processing issue/PR #{issue['number']}")
            continue


if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        exit(1)

    try:
        process_issues_and_prs()
        print("Stale check completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
