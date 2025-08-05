# GitHub Actions Deployment Guide

## 🚀 Automated Deployment with GitHub Actions

This guide shows how to set up automated deployment to your VPS using GitHub Actions with password authentication.

## 📋 Prerequisites

- VPS with initial setup completed (see `DEPLOYMENT_PASSWORD.md`)
- GitHub repository with admin access
- VPS credentials (host, username, password)

## 🔧 Setup Instructions

### Step 1: Configure GitHub Secrets

1. **Go to your GitHub repository**
2. **Navigate to**: `Settings` → `Secrets and variables` → `Actions`
3. **Click**: `New repository secret`
4. **Add the following secrets**:

| Secret Name | Description | Example |
|-------------|-------------|----------|
| `VPS_HOST` | Your VPS IP address or domain | `192.168.1.100` or `myserver.com` |
| `VPS_USERNAME` | VPS username (usually `pinmaker`) | `pinmaker` |
| `VPS_PASSWORD` | VPS user password | `your-secure-password` |
| `VPS_PORT` | SSH port (optional, defaults to 22) | `22` |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications (optional) | `https://hooks.slack.com/...` |

### Step 2: Initial VPS Setup

**Run this ONCE on your VPS before using GitHub Actions:**

```bash
# Connect to VPS
ssh pinmaker@YOUR_VPS_IP

# Clone repository (first time only)
cd /opt
sudo git clone https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git
sudo chown -R pinmaker:pinmaker Pinmaker/
cd Pinmaker

# Run initial setup
./setup.sh

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings
```

### Step 3: Workflow Overview

The GitHub Actions workflow (`.github/workflows/deploy.yml`) includes:

#### 🧪 **Test Job**
- ✅ Python linting with flake8
- ✅ Code formatting check with black
- ✅ Python tests with pytest
- ✅ Frontend build and tests
- ✅ Dependency caching for faster builds

#### 🚀 **Deploy Job** (only on main/master branch)
- ✅ Automated backup creation
- ✅ Git pull latest changes
- ✅ Python dependency updates
- ✅ Frontend build
- ✅ Service restart (pinmaker + nginx)
- ✅ Health checks
- ✅ Slack notifications (optional)

#### 🔄 **Rollback Job** (on deployment failure)
- ✅ Automatic rollback to previous version
- ✅ Service restoration

## 🎯 How to Use

### Automatic Deployment

1. **Push to main branch**:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

2. **GitHub Actions will automatically**:
   - Run tests
   - Deploy to Pinmaker (if tests pass)
   - Send notifications
   - Rollback if deployment fails

### Manual Deployment

1. **Go to**: `Actions` tab in your GitHub repository
2. **Select**: `Deploy to Pinmaker` workflow
3. **Click**: `Run workflow`
4. **Choose**: branch to deploy
5. **Click**: `Run workflow` button

## 📊 Monitoring Deployments

### GitHub Actions Dashboard

- **View logs**: `Actions` tab → Select workflow run
- **Check status**: Green ✅ = Success, Red ❌ = Failed
- **Download logs**: Click on job → Download logs

### VPS Monitoring

```bash
# Check service status
sudo systemctl status pinmaker nginx

# View application logs
sudo journalctl -u pinmaker -f

# Check deployment logs
tail -f /opt/Pinmaker/logs/deploy.log
```

## 🔧 Customization

### Modify Workflow Triggers

Edit `.github/workflows/deploy.yml`:

```yaml
# Deploy only on specific branches
on:
  push:
    branches: [ main, production ]

# Deploy on tags
on:
  push:
    tags: [ 'v*' ]

# Deploy on schedule (daily at 2 AM)
on:
  schedule:
    - cron: '0 2 * * *'
```

### Add Environment-Specific Deployments

```yaml
# Add staging environment
staging:
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/develop'
  steps:
    - name: Deploy to Staging
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.STAGING_HOST }}
        username: ${{ secrets.STAGING_USERNAME }}
        password: ${{ secrets.STAGING_PASSWORD }}
        # ... rest of deployment steps
```

### Add Slack Notifications

1. **Create Slack App**: https://api.slack.com/apps
2. **Add Incoming Webhook**: Copy webhook URL
3. **Add to GitHub Secrets**: `SLACK_WEBHOOK_URL`

## 🛠️ Troubleshooting

### Common Issues

#### 1. **SSH Connection Failed**
```
Error: ssh: connect to host X.X.X.X port 22: Connection refused
```
**Solution**: Check VPS_HOST, VPS_PORT, and firewall settings

#### 2. **Permission Denied**
```
Error: sudo: no tty present and no askpass program specified
```
**Solution**: Add pinmaker user to sudoers without password:
```bash
# On VPS as root
echo "pinmaker ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/pinmaker
```

#### 3. **Git Pull Failed**
```
Error: fatal: could not read Username for 'https://github.com'
```
**Solution**: Use personal access token or ensure repository is public

#### 4. **Service Restart Failed**
```
Error: Failed to restart pinmaker.service
```
**Solution**: Check service configuration and logs:
```bash
sudo systemctl status pinmaker
sudo journalctl -u pinmaker
```

### Debug Mode

Add debug steps to workflow:

```yaml
- name: Debug Environment
  run: |
    echo "Current directory: $(pwd)"
    echo "User: $(whoami)"
    echo "Python version: $(python3 --version)"
    echo "Git status: $(git status --short)"
    echo "Services status:"
    sudo systemctl status pinmaker nginx --no-pager
```

## 🔒 Security Best Practices

### 1. **Use Environment Secrets**
- Never commit passwords or API keys
- Use GitHub repository secrets
- Rotate passwords regularly

### 2. **Limit Permissions**
```bash
# Create dedicated deployment user
sudo adduser github-deploy
sudo usermod -aG pinmaker github-deploy

# Use in GitHub secrets
VPS_USERNAME=github-deploy
```

### 3. **Network Security**
```bash
# Restrict SSH access
sudo ufw allow from YOUR_GITHUB_ACTIONS_IP to any port 22

# Use non-standard SSH port
sudo nano /etc/ssh/sshd_config
# Change: Port 2222
sudo systemctl restart ssh
```

### 4. **Backup Strategy**
```yaml
# Add backup verification
- name: Verify Backup
  run: |
    if [ ! -f "/opt/backups/$(date +%Y%m%d)_backup.tar.gz" ]; then
      echo "❌ Backup verification failed"
      exit 1
    fi
```

## 📈 Advanced Features

### Blue-Green Deployment

```yaml
- name: Blue-Green Deployment
  run: |
    # Deploy to blue environment
    ./deploy.sh deploy --environment=blue
    
    # Health check
    if curl -f http://localhost:8001/health; then
      # Switch traffic to blue
      sudo ln -sfn /opt/Pinmaker-blue /opt/Pinmaker-current
      sudo systemctl reload nginx
    else
      echo "Health check failed, keeping green environment"
      exit 1
    fi
```

### Database Migrations

```yaml
- name: Run Migrations
  run: |
    cd /opt/Pinmaker
    source venv/bin/activate
    python manage.py migrate --check
    python manage.py migrate
```

### Performance Testing

```yaml
- name: Performance Test
  run: |
    # Install Apache Bench
    sudo apt-get update && sudo apt-get install -y apache2-utils
    
    # Run load test
    ab -n 100 -c 10 http://localhost:8000/
```

## 📞 Support

If you encounter issues:

1. **Check workflow logs** in GitHub Actions tab
2. **Review VPS logs** using commands in troubleshooting section
3. **Test manual deployment** using `DEPLOYMENT_PASSWORD.md`
4. **Verify secrets** are correctly set in GitHub repository settings

---

**🎉 Congratulations!** You now have automated deployment with GitHub Actions. Every push to main will automatically deploy your changes to the VPS with full testing, health checks, and rollback capabilities.