#!/usr/bin/env python3

import os
import re
import shutil

from github import Github, GithubException
from git import Repo
from git import GitCommandError


def create_pull_request(repo, new_branch_name, base_branch_name, pr_title, pr_body, pr_number, commit_sha, author, is_draft=False):
    """Create a pull request on GitHub."""
    # Format the new PR body with original body and list of commits
    new_pr_body = f"{pr_body}\n\n"
    new_pr_body += f"\n- (cherry picked from commit {commit_sha})"
    new_pr_body += f'\n\nParent PR: #{pr_number}'
    print(repo.full_name)
    print(base_branch_name)
    print(f'{repo.full_name}:{new_branch_name}')
    pr = repo.create_pull(
        title=pr_title,
        body=new_pr_body,
        head=f'{repo.full_name}:{new_branch_name}',
        base=base_branch_name,
    )
    try:
        pr.add_to_assignees(author)
        print(f"Assigned PR to original author: {author}")
    except Exception as e:
        print(f"Failed to assign PR to {author}: {e}")
    print(f"Pull request created: {pr.html_url}")
    return pr


def get_pr_commit(pr):
    """Get the commit that closed or merged the pull request."""
    if pr.merged:
        return pr.merge_commit_sha
    elif pr.closed_at:
        # Check events to find the commit that closed the PR
        events = pr.get_issue_events()
        for event in events:
            if event.event == 'closed':
                # Return the commit that closed the PR
                return event.commit_id
    return None


def main():
    # GitHub access token
    github_token = os.environ["GITHUB_TOKEN"]
    repo_name = 'yaronkaikov/backport'
    is_draft = False
    # Initialize GitHub and repository objects
    g = Github(github_token)
    repo = g.get_repo(repo_name)

    # Get closed PRs with specific labels
    closed_prs = repo.get_pulls(state='closed', base='master')

    promoted_to_master_label = 'promoted-to-master'
    backport_label_pattern = re.compile(r'backport/\d+\.\d+$')

    for pr in closed_prs:
        labels = [label.name for label in pr.labels]
        backport_labels = [label for label in labels if backport_label_pattern.match(label)]

        if promoted_to_master_label in labels and backport_labels:
            for backport_label in backport_labels:
                version = backport_label.replace('backport/', '')
                backport_base_branch = f'branch-{version}'
                new_branch_name = f'backport/{pr.number}/to-{version}'
                backport_pr_title = f'[Backport {version}] {pr.title}'

                commit_sha = get_pr_commit(pr)
                print(f"Found PR #{pr.number} with commit {commit_sha}")

                # Clone the repository
                local_repo_path = '/tmp/backport'
                if os.path.exists(local_repo_path):
                    shutil.rmtree(local_repo_path)

                Repo.clone_from(f'https://github.com/{repo_name}.git', local_repo_path)
                repo_local = Repo(local_repo_path)
                repo_local.git.checkout('master')
                repo_local.git.checkout(backport_base_branch)
                repo_local.git.checkout(b=new_branch_name)
                # Cherry-pick the commit
                try:
                    print(1)
                    repo_local.git.cherry_pick(commit_sha)
                    print(f"Cherry-picked commit {commit_sha} to branch {new_branch_name}")
                    repo_local.git.push('origin', new_branch_name, force=True)
                    # user = g.get_user(pr.user.login)
                    # repo.add_to_collaborators(user.login, permission="push")
                    create_pull_request(repo, new_branch_name, backport_base_branch, backport_pr_title, pr.body, pr.number, commit_sha, pr.user.login)
                except GitCommandError as e:
                    print(2)
                    print(e)
                    repo_local.git.add(A=True)
                    # repo_local.git.commit('--no-edit')
                    repo_local.git.push('origin', new_branch_name, force=True)
                    is_draft = True
                    create_pull_request(repo, new_branch_name, backport_base_branch, backport_pr_title, pr.body, pr.number, commit_sha, pr.user.login)


if __name__ == "__main__":
    main()

