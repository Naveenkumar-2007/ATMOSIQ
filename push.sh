#!/usr/bin/env bash
# Usage: ./push.sh https://github.com/<user>/<repo>.git
set -e
REPO="${1:?usage: ./push.sh <git-remote-url>}"
git init
git add .
git commit -m "AtmosIQ: initial import"
git branch -M main
git remote add origin "$REPO"
git push -u origin main
