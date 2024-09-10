#!/bin/bash

# Script for pulling a github pull request
# along with generating a merge commit message.
# Example usage for pull request #6007 and /next branch:
# git fetch
# git checkout origin/next
# ./scripts/pull_github_pr.sh 6007

set -e

gh_hosts=~/.config/gh/hosts.yml

if [[ ( -z "$GITHUB_LOGIN" || -z "$GITHUB_TOKEN" ) && -f "$gh_hosts" ]]; then
	GITHUB_LOGIN=$(awk '/user:/ { print $2 }' "$gh_hosts")
	GITHUB_TOKEN=$(awk '/oauth_token:/ { print $2 }' "$gh_hosts")
fi

if [[ $# != 1 ]]; then
	echo Please provide a github pull request number
	exit 1
fi

for required in jq curl; do
	if ! type $required >& /dev/null; then
		echo Please install $required first
		exit 1
	fi
done

curl() {
    local opts=()
    if [[ -n "$GITHUB_LOGIN" && -n "$GITHUB_TOKEN" ]]; then
        opts+=(--user "${GITHUB_LOGIN}:${GITHUB_TOKEN}")
    fi
    command curl "${opts[@]}" "$@"
}

PR_NUM=$1
pr_json="pr_${PR_NUM}.json"

echo "Fetching info on PR #$PR_NUM... "

gh pr view "$PR_NUM" --json title,body,author,commits,headRefName > "${pr_json}"

title=$(jq -r '.title' < "${pr_json}")
body=$(jq -r '.body' < "${pr_json}")
author=$(jq -r '[.author.name] | join(",")' < "${pr_json}")
nr_commits=$(jq -r '.commits | length' < "${pr_json}")
headRefName=$(jq -r '.headRefName' < "${pr_json}")

if [[ $nr_commits == 1 ]]; then
  gh pr "$PR_NUM" merge -r
else
  gh pr "$PR_NUM" merge -m -t "Merge $title from $author $body"
fi

rm -rf "${pr_json}"
