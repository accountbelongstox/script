#!/bin/bash
timestamp=$(date +"%Y-%m-%d %H:%M:%S")
git add .
git commit -m "$timestamp"
git push --set-upstream origin main
git push