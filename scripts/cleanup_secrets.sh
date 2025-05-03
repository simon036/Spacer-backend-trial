#!/bin/bash

# Remove sensitive files from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push the changes
git push origin --force --all
git push origin --force --tags

# Clean up
git for-each-ref --format='delete %(refname)' refs/original/ | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive 