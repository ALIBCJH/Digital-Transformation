#!/bin/bash
# Auto-create Pull Request using GitHub CLI
# Usage: ./create-pr.sh "PR title" "PR description"

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) not found${NC}"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Not in a git repository${NC}"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo -e "${RED}❌ Cannot create PR from main/master branch${NC}"
    exit 1
fi

echo -e "${GREEN}📋 Creating Pull Request from: ${CURRENT_BRANCH}${NC}"
echo ""

# Get PR title from argument or ask
if [ -z "$1" ]; then
    read -p "Enter PR title: " PR_TITLE
else
    PR_TITLE="$1"
fi

# Get PR description from argument or ask
if [ -z "$2" ]; then
    read -p "Enter PR description (optional): " PR_DESCRIPTION
else
    PR_DESCRIPTION="$2"
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes${NC}"
    read -p "Commit and push now? (y/N): " should_commit
    
    if [ "$should_commit" = "y" ] || [ "$should_commit" = "Y" ]; then
        echo "Staging all changes..."
        git add -A
        
        read -p "Enter commit message: " COMMIT_MSG
        git commit -m "$COMMIT_MSG"
        
        echo "Pushing to remote..."
        git push origin "$CURRENT_BRANCH"
    else
        echo -e "${RED}❌ Please commit and push your changes first${NC}"
        exit 1
    fi
fi

# Ensure branch is pushed
if ! git ls-remote --exit-code --heads origin "$CURRENT_BRANCH" > /dev/null 2>&1; then
    echo "Branch not on remote. Pushing..."
    git push origin "$CURRENT_BRANCH"
fi

# Create PR
echo ""
echo -e "${GREEN}🚀 Creating Pull Request...${NC}"

if [ -z "$PR_DESCRIPTION" ]; then
    gh pr create \
        --title "$PR_TITLE" \
        --base main \
        --head "$CURRENT_BRANCH" \
        --web
else
    gh pr create \
        --title "$PR_TITLE" \
        --body "$PR_DESCRIPTION" \
        --base main \
        --head "$CURRENT_BRANCH" \
        --web
fi

echo ""
echo -e "${GREEN}✅ Pull Request created successfully!${NC}"
echo ""
echo "The PR will trigger the CI/CD pipeline which will:"
echo "  1. ✅ Run Terraform Plan (no changes applied)"
echo "  2. ✅ Run tests and linting"
echo "  3. ✅ Build Docker images"
echo "  4. ❌ Skip deployment (only happens on main)"
echo ""
echo "After review and approval, merge the PR to deploy to production."
