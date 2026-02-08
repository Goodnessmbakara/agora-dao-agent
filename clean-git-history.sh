#!/bin/bash
# Script to remove venv from git history
# WARNING: This rewrites history and requires force push!

echo "🧹 Cleaning venv from git history..."
echo "⚠️  This will require 'git push --force'"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

cd /home/ubuntu/.openclaw/workspace/agora

# Backup
echo "📦 Creating backup branch..."
git branch backup-before-cleanup

# Method 1: Using filter-branch (built-in)
echo "🔧 Removing venv from history..."
git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch venv' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up refs
echo "🧹 Cleaning up..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ History cleaned!"
echo ""
echo "📊 New repo size:"
du -sh .git

echo ""
echo "⚠️  TO APPLY TO GITHUB:"
echo "   git push --force origin main"
echo ""
echo "💡 If you change your mind:"
echo "   git checkout backup-before-cleanup"
