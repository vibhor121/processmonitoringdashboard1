#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Process Monitor - Render Deployment Script${NC}"
echo -e "${BLUE}=============================================${NC}"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git repository not initialized. Initializing now...${NC}"
    git init
fi

# Check git status
echo -e "\n${BLUE}📊 Checking git status...${NC}"
git status --porcelain

# Add all files
echo -e "\n${BLUE}📦 Adding all files to git...${NC}"
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo -e "${YELLOW}ℹ️  No changes to commit.${NC}"
else
    echo -e "\n${BLUE}💾 Committing changes...${NC}"
    read -p "Enter commit message (or press Enter for default): " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Deploy to Render - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    git commit -m "$commit_msg"
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo -e "\n${YELLOW}⚠️  No remote origin found.${NC}"
    read -p "Enter your GitHub repository URL: " repo_url
    git remote add origin "$repo_url"
fi

# Push to GitHub
echo -e "\n${BLUE}🚀 Pushing to GitHub...${NC}"
git push origin main

echo -e "\n${GREEN}✅ Code pushed to GitHub successfully!${NC}"

echo -e "\n${BLUE}📋 Next Steps for Render Deployment:${NC}"
echo -e "1. Go to ${YELLOW}https://dashboard.render.com${NC}"
echo -e "2. Click 'New +' → 'Web Service'"
echo -e "3. Connect your GitHub account"
echo -e "4. Select this repository"
echo -e "5. Configure the service:"
echo -e "   - Name: process-monitor"
echo -e "   - Environment: Python 3"
echo -e "   - Build Command: (leave empty - uses build.sh)"
echo -e "   - Start Command: (leave empty - uses Procfile)"
echo -e "6. Create PostgreSQL database:"
echo -e "   - Click 'New +' → 'PostgreSQL'"
echo -e "   - Name: process-monitor-db"
echo -e "   - Plan: Free"
echo -e "7. Deploy and monitor the build logs"

echo -e "\n${GREEN}🎉 Your Process Monitor app is ready for deployment!${NC}"
echo -e "${BLUE}Check the DEPLOYMENT.md file for detailed instructions.${NC}" 