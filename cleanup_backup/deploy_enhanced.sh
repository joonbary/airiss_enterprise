#!/bin/bash
# AIRISS Enhanced Deployment Script
# Safe deployment with rollback capability

echo "=========================================="
echo "AIRISS Phase 1.5 Enhanced Deployment"
echo "=========================================="

# Backup current application.py
echo "Step 1: Creating backup..."
cp application.py application_backup_$(date +%Y%m%d_%H%M%S).py

# Deploy enhanced version
echo "Step 2: Deploying enhanced version..."
cp application_enhanced.py application.py

# Test deployment
echo "Step 3: Testing deployment..."
eb deploy

# Check deployment status
echo "Step 4: Checking deployment status..."
sleep 30
eb status

echo "Step 5: Testing health endpoint..."
curl -f https://airiss-v4.ap-northeast-2.elasticbeanstalk.com/health

if [ $? -eq 0 ]; then
    echo "SUCCESS: Enhanced deployment completed!"
    echo "Executive Dashboard: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com/executive"
else
    echo "WARNING: Health check failed, rolling back..."
    cp application_backup_*.py application.py
    eb deploy
    echo "Rollback completed"
fi

echo "=========================================="
echo "Deployment process finished"
echo "=========================================="
