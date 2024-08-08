#!/usr/bin/env python3

import os
import re
import shutil
import tempfile
import logging

<<<<<<< HEAD
from github import Github, GithubException, InputGitAuthor
=======
from github import Github, GithubException
>>>>>>> ae51704 (Merge 'test2: Update README' from Yaron Kaikov)
from git import Repo, GitCommandError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

<<<<<<< HEAD
github_token = os.getenv("GITHUB_TOKEN")
repo_name = 'yaronkaikov/backport'
promoted_to_master_label = 'promoted-to-master'
backport_label_pattern = re.compile(r'backport/\d+\.\d+$')

g = Github(github_token)
repo = g.get_repo(repo_name)
closed_prs = repo.get_pulls(state='closed', base='master')


def create_pull_request(repo, new_branch_name, base_branch_name, pr_title, pr_body, pr_number, commit_sha, author, is_draft=True):
=======

def create_pull_request(repo, new_branch_name, base_branch_name, pr_title, pr_body, pr_number, commit_sha, author, is_draft=False):
>>>>>>> ae51704 (Merge 'test2: Update README' from Yaron Kaikov)
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
<<<<<<< HEAD
        return pr
    except GithubException as e:
        logging.error(f"Failed to create PR: {e}")
=======
    except GithubException as e:
        logging.error(f"Failed to create PR: {e}")
    return pr
>>>>>>> ae51704 (Merge 'test2: Update README' from Yaron Kaikov)


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


<<<<<<< HEAD
def cherry_pick_commits(pr, repo, commit_sha, base_branch_name, temp_branch_name):
    """Cherry-pick commits and push them to a temporary branch."""
    base_branch = repo.get_branch(base_branch_name)
    print(base_branch)
    base_commit = base_branch.commit
    print(base_commit)
    print(temp_branch_name)
    print(base_branch_name)
    try:
        ref = repo.create_git_ref(ref=f"refs/heads/{temp_branch_name}", sha=base_commit.sha)
    except GithubException as e:
        print(f"Failed to create temp branch {temp_branch_name}: {e}")
        raise

    commit = repo.get_commit(commit_sha)
    print(commit)
    author = InputGitAuthor(
        name="github-actions[bot]",
        email="41898282+github-actions[bot]@users.noreply.github.com"
    )
    new_tree = commit.commit.tree
    new_commit = repo.create_git_commit(
        message=f"Cherry-picked: {commit.commit.message}",
        author=author,
        tree=new_tree,
        parents=[base_commit.commit]
    )

    # Update the temp branch to point to the new commit
    try:
        ref.edit(sha=new_commit.sha)
        print(f"Successfully cherry-picked commit {commit_sha} to {temp_branch_name}")
    except GithubException as e:
        print(f"Failed to update temp branch {temp_branch_name}: {e}")
        raise

    return new_commit.sha, [f"- (cherry picked from commit {commit_sha})"]


def main():
=======
def main():
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = 'yaronkaikov/backport'
    promoted_to_master_label = 'promoted-to-master'
    backport_label_pattern = re.compile(r'backport/\d+\.\d+$')

    g = Github(github_token)
    repo = g.get_repo(repo_name)
    closed_prs = repo.get_pulls(state='closed', base='master')

>>>>>>> ae51704 (Merge 'test2: Update README' from Yaron Kaikov)
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
<<<<<<< HEAD
                        try:
                            repo_local.git.cherry_pick(commit_sha, '-m 1')
                        except GitCommandError as e:
                            logging.warning(f"Cherry-pick conflict: {e}")
                            repo_local.git.cherry_pick(commit_sha, '--strategy=recursive', '-X', 'ours')
                            logging.info("Resolved conflicts using 'ours' strategy")

=======
                        repo_local.git.cherry_pick(commit_sha)
>>>>>>> ae51704 (Merge 'test2: Update README' from Yaron Kaikov)
                        repo_local.git.push('origin', new_branch_name, force=True)
                        create_pull_request(repo, new_branch_name, backport_base_branch, backport_pr_title, pr.body, pr.number, commit_sha, pr.user.login)
                    except GitCommandError as e:
                        logging.error(f"Git command failed: {e}")
<<<<<<< HEAD
                        is_draft = True
                        create_pull_request(repo, new_branch_name, backport_base_branch, backport_pr_title, pr.body, pr.number, commit_sha, pr.user.login, is_draft=is_draft)
                    except Exception as e:
                        logging.error(f"Failed to process PR #{pr.number}: {e}")


=======
                        repo_local.git.add(A=True)
                        repo_local.git.commit('--no-edit')
                        repo_local.git.push('origin', new_branch_name, force=True)
                        create_pull_request(repo, new_branch_name, backport_base_branch, backport_pr_title, pr.body, pr.number, commit_sha, pr.user.login, is_draft=True)
                    except Exception as e:
                        logging.error(f"Failed to process PR #{pr.number}: {e}")

>>>>>>> ae51704 (Merge 'test2: Update README' from Yaron Kaikov)
if __name__ == "__main__":
    main()
