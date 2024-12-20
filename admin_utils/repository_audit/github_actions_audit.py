import requests
import os
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any
import base64
import argparse
from pprint import pprint


class GitHubActionsAudit:
    def __init__(self, token: str, org: str):
        self.token = token
        self.org = org
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'

    def get_repository(self, repo_name: str) -> Dict[str, Any]:
        """Get a single repository's information."""
        url = f'{self.base_url}/repos/{self.org}/{repo_name}'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

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

    def get_workflow_files(self, repo_name: str, default_branch: str) -> List[Dict[str, Any]]:
        """Get workflow files from .github/workflows directory."""
        workflows = []
        url = f'{
            self.base_url}/repos/{self.org}/{repo_name}/contents/.github/workflows'
        params = {'ref': default_branch}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 404:
                return []

            response.raise_for_status()
            contents = response.json()

            workflows = [
                content for content in contents
                if content['name'].endswith(('.yml', '.yaml'))
            ]

            verified_workflows = []
            for workflow in workflows:
                try:
                    file_response = requests.get(
                        workflow['url'], headers=self.headers)
                    file_response.raise_for_status()
                    file_content = file_response.json()

                    content = base64.b64decode(
                        file_content['content']).decode('utf-8')

                    if 'on:' in content or 'jobs:' in content:
                        workflow['content'] = content
                        verified_workflows.append(workflow)
                except Exception as e:
                    print(f"Error reading workflow file {
                          workflow['name']}: {e}")
                    continue

            return verified_workflows

        except requests.exceptions.RequestException as e:
            print(f"Error checking workflows for {repo_name}: {e}")
            return []

    def check_actions_enabled(self, repo_name: str) -> Dict[str, Any]:
        """Check GitHub Actions permissions and settings for the repository."""
        # First get basic repo info to check if it's a fork
        repo_url = f'{self.base_url}/repos/{self.org}/{repo_name}'
        repo_response = requests.get(repo_url, headers=self.headers)
        repo_response.raise_for_status()
        repo_data = repo_response.json()

        # Check if it's a fork
        is_fork = repo_data.get('fork', False)

        result = {
            'is_fork': is_fork,
            'fork_status': 'N/A',
            'enabled': False,
            'allowed_actions': 'none',
            'status': 'disabled'
        }

        # If it's a fork, check the specific fork settings endpoint
        if is_fork:
            fork_settings_url = f'{
                self.base_url}/repos/{self.org}/{repo_name}/actions/permissions'
            settings_response = requests.get(
                fork_settings_url, headers=self.headers)

            if settings_response.status_code == 200:
                settings_data = settings_response.json()
                workflows_enabled = settings_data.get('enabled', False)

                # Check for fork-specific workflows state
                fork_settings_url = f'{self.base_url}/repos/{self.org}/{
                    repo_name}/actions/permissions/workflows/fork-pull-requests'
                fork_response = requests.get(
                    fork_settings_url, headers=self.headers)

                if fork_response.status_code == 200:
                    fork_data = fork_response.json()
                    fork_workflows_enabled = fork_data.get('enabled', False)
                    result.update({
                        'enabled': workflows_enabled and fork_workflows_enabled,
                        'status': 'enabled' if (workflows_enabled and fork_workflows_enabled) else 'disabled',
                        'fork_status': 'workflows enabled' if fork_workflows_enabled else 'workflows disabled (fork)',
                        'allowed_actions': settings_data.get('allowed_actions', 'none')
                    })
                else:
                    result['fork_status'] = 'workflows disabled (fork)'
                    result['enabled'] = False
                    result['status'] = 'disabled'
        else:
            # Not a fork, use regular permissions endpoint
            actions_url = f'{
                self.base_url}/repos/{self.org}/{repo_name}/actions/permissions'
            actions_response = requests.get(actions_url, headers=self.headers)

            if actions_response.status_code == 200:
                actions_data = actions_response.json()
                result.update({
                    'enabled': actions_data.get('enabled', False),
                    'allowed_actions': actions_data.get('allowed_actions', 'none'),
                    'status': 'enabled' if actions_data.get('enabled', False) else 'disabled'
                })

        # Get additional workflow permissions if actions are enabled
        if result['enabled']:
            workflow_url = f'{
                self.base_url}/repos/{self.org}/{repo_name}/actions/permissions/workflow'
            workflow_response = requests.get(
                workflow_url, headers=self.headers)
            if workflow_response.status_code == 200:
                workflow_data = workflow_response.json()
                result.update({
                    'default_workflow_permissions': workflow_data.get('default_workflow_permissions'),
                    'can_approve_pull_request_reviews': workflow_data.get('can_approve_pull_request_reviews', False)
                })

        return result

    def audit_single_repository(self, repo_name: str) -> pd.DataFrame:
        """Audit a single repository and return results as a DataFrame."""
        try:
            repo = self.get_repository(repo_name)
            return self.process_repositories([repo])
        except requests.exceptions.RequestException as e:
            print(f"Error accessing repository {repo_name}: {e}")
            return pd.DataFrame()

    def audit_all_repositories(self) -> pd.DataFrame:
        """Audit all repositories in the organization."""
        repositories = self.get_repositories()
        return self.process_repositories(repositories)

    def process_repositories(self, repositories: List[Dict[str, Any]]) -> pd.DataFrame:
        """Process repository data and return results as a DataFrame."""
        results = []

        for repo in repositories:
            print(f"\nChecking repository: {repo['name']}")
            workflow_files = self.get_workflow_files(
                repo['name'], repo['default_branch'])
            actions_status = self.check_actions_enabled(repo['name'])

            workflow_names = [w['name'] for w in workflow_files]

            print(f"Is fork: {actions_status['is_fork']}")
            print(f"Fork workflow status: {actions_status['fork_status']}")
            print(f"Actions enabled: {actions_status['enabled']}")
            print(f"Actions status: {actions_status['status']}")
            print(f"Allowed actions: {actions_status['allowed_actions']}")
            print(f"Workflow files found: {', '.join(
                workflow_names) if workflow_names else 'None'}")

            results.append({
                'repository': repo['name'],
                'visibility': 'private' if repo['private'] else 'public',
                'archived': repo['archived'],
                'disabled': repo['disabled'],
                'fork': actions_status['is_fork'],
                'fork_workflow_status': actions_status['fork_status'],
                'created_at': repo['created_at'],
                'updated_at': repo['updated_at'],
                'actions_enabled': actions_status['enabled'],
                'actions_status': actions_status['status'],
                'allowed_actions': actions_status['allowed_actions'],
                'default_workflow_permissions': actions_status.get('default_workflow_permissions', 'N/A'),
                'can_approve_pull_request_reviews': actions_status.get('can_approve_pull_request_reviews', 'N/A'),
                'workflow_count': len(workflow_files),
                'workflow_files': ', '.join(workflow_names) if workflow_names else None,
                'default_branch': repo['default_branch'],
                'url': repo['html_url']
            })

        return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description='Audit GitHub Actions in repositories')
    parser.add_argument('--org', help='GitHub organization name',
                        default=os.getenv('GITHUB_ORG'))
    parser.add_argument(
        '--repo', help='Specific repository to audit (optional)')
    parser.add_argument('--token', help='GitHub token',
                        default=os.getenv('GITHUB_TOKEN'))
    args = parser.parse_args()

    if not args.token:
        raise ValueError(
            "GitHub token is required. Set GITHUB_TOKEN or use --token")
    if not args.org:
        raise ValueError(
            "Organization name is required. Set GITHUB_ORG or use --org")

    auditor = GitHubActionsAudit(args.token, args.org)

    try:
        print(f"Starting audit for organization: {args.org}")
        if args.repo:
            print(f"Auditing single repository: {args.repo}")
            results_df = auditor.audit_single_repository(args.repo)
        else:
            print("Auditing all repositories...")
            results_df = auditor.audit_all_repositories()

        if not results_df.empty:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            repo_part = f"_{args.repo}" if args.repo else ""
            filename = f'github_actions_audit_{
                args.org}{repo_part}_{timestamp}.csv'
            results_df.to_csv(filename, index=False)
            print(f"\nResults saved to: {filename}")

    except Exception as e:
        print(f"Error during audit: {e}")


if __name__ == "__main__":
    main()
