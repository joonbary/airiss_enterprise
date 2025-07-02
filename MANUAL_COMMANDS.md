# AIRISS v4.1 Manual Deployment Commands

## Step 1: Git Setup and Commit
```cmd
git add .
git commit -m "AIRISS v4.1 - Production Ready for GitHub and AWS"
```

## Step 2: GitHub Connection  
Replace YOUR_USERNAME with your actual GitHub username:
```cmd
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/airiss_enterprise.git
git branch -M main
```

## Step 3: Upload to GitHub
```cmd
git push -u origin main
```

## Step 4: AWS Amplify Build Settings
Copy and paste this into AWS Amplify build settings:

```yaml
version: 1
backend:
  phases:
    preBuild:
      commands:
        - python -m pip install --upgrade pip
        - pip install -r requirements.txt
    build:
      commands:
        - python init_database.py
frontend:
  artifacts:
    baseDirectory: /
    files:
      - '**/*'
```

## Quick Links:
- GitHub: https://github.com/new
- AWS Amplify: https://console.aws.amazon.com/amplify/
- Your Repository: https://github.com/YOUR_USERNAME/airiss_enterprise

## Troubleshooting:
- If git push fails: Check GitHub credentials
- If AWS build fails: Verify Python dependencies
- If website doesn't load: Check AWS logs in console
