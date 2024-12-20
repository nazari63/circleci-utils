import requests
import os
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any


class GitHubActionsAudit:
    def __init__(self, token: str, org: str):
        """
        Initialize the GitHub Actions auditor.

        Args:
            token (str): GitHub personal access token
            org (str): GitHub organization name
        """
        self.token = token
        self.org = org
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'

    def get_repositories(self) -> List[Dict[str, Any]]:
        """Get all repositories in the organization."""
        repos = []
        page = 1
        while True:
            url = f'{self.base_url}/orgs/{self.org}/repos'
            params = {'page': page, 'per_page': 100}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            batch = response.json()
            if not batch:
                break
            repos.extend(batch)
            page += 1

        return repos

    def get_workflow_count(self, repo_name: str) -> int:
        """Get the number of workflows in a repository."""
        url = f'{self.base_url}/repos/{self.org}/{repo_name}/actions/workflows'
        response = requests.get(url, headers=self.headers)

        if response.status_code == 404:
            return 0

        response.raise_for_status()
        return response.json()['total_count']

    def check_actions_enabled(self, repo_name: str) -> bool:
        """Check if GitHub Actions are enabled for the repository."""
        url = f'{self.base_url}/repos/{self.org}/{repo_name}'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return not response.json().get('disabled_actions', False)

    def audit_repositories(self) -> pd.DataFrame:
        """Audit all repositories and return results as a DataFrame."""
        repositories = self.get_repositories()
        results = []

        for repo in repositories:
            workflow_count = self.get_workflow_count(repo['name'])
            actions_enabled = self.check_actions_enabled(repo['name'])

            results.append({
                'repository': repo['name'],
                'visibility': 'private' if repo['private'] else 'public',
                'archived': repo['archived'],
                'disabled': repo['disabled'],
                'fork': repo['fork'],
                'created_at': repo['created_at'],
                'updated_at': repo['updated_at'],
                'actions_enabled': actions_enabled,
                'workflow_count': workflow_count,
                'default_branch': repo['default_branch'],
                'url': repo['html_url']
            })

        return pd.DataFrame(results)


def main():
    # Get GitHub token from environment variable
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("Please set the GITHUB_TOKEN environment variable")

    # Get organization name from command line or environment
    org_name = os.getenv('GITHUB_ORG')
    if not org_name:
        org_name = input("Enter GitHub organization name: ")

    # Initialize and run audit
    auditor = GitHubActionsAudit(github_token, org_name)

    try:
        print(f"Starting audit of {org_name}...")
        results_df = auditor.audit_repositories()

        # Save results to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'github_actions_audit_{org_name}_{timestamp}.csv'
        results_df.to_csv(filename, index=False)

        # Print summary
        total_repos = len(results_df)
        repos_with_actions = len(results_df[results_df['workflow_count'] > 0])

        print("\nAudit Summary:")
        print(f"Total repositories: {total_repos}")
        print(f"Repositories with workflows: {repos_with_actions}")
        print(f"Results saved to: {filename}")

        # Print repositories with workflows
        if repos_with_actions > 0:
            print("\nRepositories with GitHub Actions:")
            action_repos = results_df[results_df['workflow_count'] > 0]
            for _, repo in action_repos.iterrows():
                print(f"- {repo['repository']}: {repo['workflow_count']} workflows "
                      f"({'enabled' if repo['actions_enabled'] else 'disabled'})")

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
