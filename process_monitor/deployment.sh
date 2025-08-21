#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear

echo -e "${BLUE}===============================${NC}"
echo -e "${YELLOW}🤖 Interactive Deployment Bot${NC}"
echo -e "${BLUE}===============================${NC}"

# Step 1: GitHub Setup
echo -e "\n${YELLOW}Step 1: GitHub Setup 📦${NC}"
read -p "Have you created a GitHub account? (y/n): " has_github

if [[ $has_github =~ ^[Nn]$ ]]; then
    echo -e "\n${BLUE}Please:${NC}"
    echo "1. Go to https://github.com"
    echo "2. Sign up for a free account"
    echo "3. Come back here when done"
    read -p "Press Enter when ready..."
fi

# Step 2: Configure Project
echo -e "\n${YELLOW}Step 2: Project Configuration 🔧${NC}"

# Add necessary files for deployment
echo "Creating deployment files..."

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << EOL
Django>=5.2.0
djangorestframework>=3.16.0
psutil>=7.0.0
requests>=2.32.0
gunicorn>=21.2.0
whitenoise>=6.5.0
dj-database-url>=2.1.0
EOL
fi

# Create render.yaml
cat > render.yaml << EOL
services:
  - type: web
    name: process-monitor
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd backend && gunicorn backend.wsgi:application --bind 0.0.0.0:\$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DJANGO_SECRET_KEY
        generateValue: true
      - key: DJANGO_DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: ".onrender.com"

databases:
  - name: process-monitor-db
    plan: free
EOL

echo -e "${GREEN}✅ Configuration files created!${NC}"

# Step 3: Push to GitHub
echo -e "\n${YELLOW}Step 3: Push to GitHub 🚀${NC}"
read -p "Enter your GitHub username: " github_username

git init
git add .
git commit -m "Prepared for deployment 🚀"
git branch -M main
git remote add origin https://github.com/$github_username/process-monitor.git
git push -u origin main

echo -e "\n${YELLOW}Step 4: Deploy to Render 🎯${NC}"
echo -e "${BLUE}Please follow these steps:${NC}"
echo "1. Go to https://render.com"
echo "2. Sign up with GitHub"
echo "3. Click 'New +' button"
echo "4. Select 'Web Service'"
echo "5. Find and select 'process-monitor' repository"
echo "6. Click 'Connect'"
echo "7. Click 'Create Web Service'"

read -p "Press Enter when you've completed these steps..."

echo -e "\n${GREEN}🎉 Your app is now deploying!${NC}"
echo -e "\n${BLUE}To check your deployment:${NC}"
echo "1. Go to https://dashboard.render.com"
echo "2. Click on 'process-monitor'"
echo "3. Watch the deploy logs"

echo -e "\n${YELLOW}Need help? Let me know!${NC}"