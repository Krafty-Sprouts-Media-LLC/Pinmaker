# Password-Based Deployment Guide

## 🚀 Deploy from GitHub to VPS (Password Authentication)

This guide shows how to deploy the Pinmaker project using password authentication instead of SSH keys.

## Prerequisites

- VPS with Ubuntu 20.04+ or similar Linux distribution
- Root access to the VPS
- GitHub repository: `https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker`

## Step 1: Initial VPS Setup

### Connect to your VPS
```bash
ssh root@YOUR_VPS_IP
# Enter your root password when prompted
```

### Create dedicated user
```bash
# Create pinmaker user
adduser pinmaker
# Set a strong password when prompted

# Add to sudo group
usermod -aG sudo pinmaker

# Switch to pinmaker user
su - pinmaker
```

## Step 2: Install Git and Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Git
sudo apt install git -y

# Install Python and other dependencies
sudo apt install python3 python3-pip python3-venv nginx -y
```

## Step 3: Clone Repository (Password Method)

### Option A: HTTPS Clone (Recommended)
```bash
# Clone using HTTPS (will prompt for GitHub credentials)
cd /opt
sudo git clone https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git
sudo chown -R pinmaker:pinmaker Pinmaker/
cd Pinmaker
```

### Option B: Download and Extract
```bash
# Alternative: Download as ZIP
cd /opt
sudo wget https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker/archive/refs/heads/main.zip
sudo unzip main.zip
sudo mv Pinmaker-main Pinmaker
sudo chown -R pinmaker:pinmaker Pinmaker/
cd Pinmaker
```

## Step 4: Run Setup Script

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (will install all dependencies)
./setup.sh
```

## Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Key settings to update in `.env`:**
```bash
# Basic settings
ENVIRONMENT=production
DEBUG=false
DOMAIN=your-domain.com
APP_URL=https://your-domain.com

# Security
SECRET_KEY=your-super-secret-key-here
ADMIN_API_KEY=your-admin-api-key

# API Keys (get from respective services)
UNSPLASH_ACCESS_KEY=your-unsplash-key
PEXELS_API_KEY=your-pexels-key
GOOGLE_FONTS_API_KEY=your-google-fonts-key
```

## Step 6: Start Services

```bash
# Start the application
sudo systemctl enable pinmaker
sudo systemctl start pinmaker

# Configure and start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Check status
sudo systemctl status pinmaker
sudo systemctl status nginx
```

## Step 7: Update Deployment (Future Updates)

### Manual Update Method
```bash
# Navigate to project directory
cd /opt/Pinmaker

# Pull latest changes
git pull origin main
# Enter GitHub credentials when prompted

# Update dependencies
pip install -r requirements.txt

# Restart services
sudo systemctl restart pinmaker
sudo systemctl restart nginx
```

### Using Deploy Script
```bash
# Use the automated deploy script
./deploy.sh deploy
```

## Step 8: SSL Certificate (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

## Troubleshooting

### Check Application Logs
```bash
# Application logs
sudo journalctl -u pinmaker -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Common Issues

1. **Permission Denied**
   ```bash
   sudo chown -R pinmaker:pinmaker /opt/Pinmaker
   sudo chmod +x /opt/Pinmaker/setup.sh
   ```

2. **Port Already in Use**
   ```bash
   sudo netstat -tulpn | grep :8000
   sudo systemctl stop pinmaker
   sudo systemctl start pinmaker
   ```

3. **Git Authentication Issues**
   - Use personal access token instead of password
   - Generate at: GitHub → Settings → Developer settings → Personal access tokens

## Security Notes

⚠️ **Important Security Considerations:**

1. **Use Strong Passwords**: Ensure all user accounts have strong passwords
2. **Firewall**: Configure UFW firewall
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   ```
3. **Regular Updates**: Keep system and dependencies updated
4. **Backup**: Use the included backup script
   ```bash
   ./backup.sh daily
   ```

## Alternative: GitHub Personal Access Token

For better security without SSH keys:

1. **Generate Token**: GitHub → Settings → Developer settings → Personal access tokens → Generate new token
2. **Clone with Token**:
   ```bash
   git clone https://YOUR_TOKEN@github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git
   ```
3. **Store Token Securely**: Save in password manager

## Quick Commands Summary

```bash
# Initial setup
ssh root@YOUR_VPS_IP
adduser pinmaker && usermod -aG sudo pinmaker
su - pinmaker
sudo apt update && sudo apt install git python3 python3-pip nginx -y
cd /opt && sudo git clone https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git
sudo chown -R pinmaker:pinmaker Pinmaker/
cd Pinmaker && ./setup.sh

# Future updates
cd /opt/Pinmaker && git pull origin main && ./deploy.sh deploy
```

## Support

If you encounter issues:
1. Check the logs using commands in troubleshooting section
2. Verify all services are running: `sudo systemctl status pinmaker nginx`
3. Check the main DEPLOYMENT.md for additional configuration options

---

**Note**: This method uses password authentication instead of SSH keys. While functional, SSH keys are more secure for production environments.