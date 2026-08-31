#!/usr/bin/env bash
set -e

MSG="${*:-update $(date +'%Y-%m-%d %H:%M')}"

git add -A
git commit -m "$MSG" || echo "Nothing new to commit."
git push -u origin main
