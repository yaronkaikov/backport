#!/usr/bin/env python3

import os
import re
import shutil
import tempfile
import logging

from github import Github, GithubException
from git import Repo, GitCommandError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

github_token = os.getenv("GITHUB_TOKEN")
repo_name = 'yaronkaikov/backport'
promoted_to_master_label = 'promoted-to-master'
backport_label_pattern = re.compile(r'backport/\d+\.\d+$')

g = Github(github_token)
repo = g.get_repo(repo_name)
closed_prs = repo.get_pulls(state='closed', base='master')


def create_pull_request(repo, new_branch_name, base_branch_name, pr_title, pr_body, pr_number, commit_sha, author, is_draft=True):
    """Create a pull request on GitHub."""
    new_pr_body = f"{pr_body}\n\n- (cherry picked from commit {commit_sha})\n\nParent PR: #{pr_number}"
    try:
        pr = repo.create_pull(
            title=pr_title,
            body=new_pr_body,
            head=f'{repo.owner.login}:{new_branch_name}',
            base=base_branch_name,
            draft=is_draft
        )
        pr.add_to_assignees(author)
        logging.info(f"Assigned PR to original author: {author}")
        logging.info(f"Pull request created: {pr.html_url}")
    except GithubException as e:
        logging.error(f"Failed to create PR: {e}")
    return pr


def get_pr_commit(pr):
    """Get the commit that closed or merged the pull request."""
    if pr.merged:
        return pr.merge_commit_sha
    elif pr.closed_at:
        events = pr.get_issue_events()
        for event in events:
            if event.event == 'closed':
                return event.commit_id
    return None


def main():
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

                logging.info(f"Found PR #{pr.number} with commit {commit_sha}")

                with tempfile.TemporaryDirectory() as local_repo_path:
                    try:
                        Repo.clone_from(f'https://github.com/{repo_name}.git', local_repo_path)
                        repo_local = Repo(local_repo_path)
                        repo_local.git.checkout(backport_base_branch)
                        repo_local.git.checkout(b=new_branch_name)
                        repo_local.git.cherry_pick(commit_sha, '-m 1')
                        repo_local.git.push('origin', new_branch_name, force=True)
                        create_pull_request(repo, new_branch_name, backport_base_branch, backport_pr_title, pr.body, pr.number, commit_sha, pr.user.login)
                    except GitCommandError as e:
                        logging.error(f"Git command failed: {e}")
                        repo_local.git.add(A=True)
                        repo_local.git.commit('--no-edit')
                        repo_local.git.push('origin', new_branch_name, force=True)
                        create_pull_request(repo, new_branch_name, backport_base_branch, backport_pr_title, pr.body, pr.number, commit_sha, pr.user.login, is_draft=True)
                    except Exception as e:
                        logging.error(f"Failed to process PR #{pr.number}: {e}")


if __name__ == "__main__":
    main()
