# CLEAR SERVER SETUP INSTRUCTIONS

## Fresh Server Setup - Step by Step

### Prerequisites
- Server IP: Your server IP
- Username: root
- Password: Your server password

### Step 1: Connect to Server
```bash
ssh root@YOUR_SERVER_IP
# Enter password when prompted
```

### Step 2: Create User and Directory Structure
```bash
# Create pinmaker user
useradd -m -s /bin/bash pinmaker
passwd pinmaker
# Set a password for pinmaker user

# Add pinmaker to sudo group
usermod -aG sudo pinmaker

# Create the application directory
mkdir -p /opt/Pinmaker
chown -R pinmaker:pinmaker /opt/Pinmaker
```

### Step 3: Switch to Pinmaker User
```bash
su - pinmaker
cd /opt/Pinmaker
```

### Step 4: Clone Repository
```bash
# Clone the repository into current directory
git clone https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git .

# Verify files are present
ls -la
# You should see: main.py, requirements.txt, setup.sh, deploy.sh, etc.
```

### Step 5: Run Setup Script
```bash
# Make setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Step 6: Activate Virtual Environment
```bash
# Activate the virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in prompt)
which python
# Should show: /opt/Pinmaker/venv/bin/python
```

### Step 7: Run Deploy Script
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

### Step 8: Verify Installation
```bash
# Check if services are running
sudo systemctl status pinmaker
sudo systemctl status nginx

# Test the application
curl http://localhost:8000/health

# Check if website is accessible
curl -I https://pinmaker.kraftysprouts.com
```

## Troubleshooting

### If setup.sh fails:
1. Check you're in the right directory: `pwd` should show `/opt/Pinmaker`
2. Check files exist: `ls -la` should show main.py, requirements.txt, etc.
3. Check you're the pinmaker user: `whoami` should show `pinmaker`

### If deploy.sh fails:
1. Make sure virtual environment is activated: `which python` should show venv path
2. Check logs: `tail -f logs/pinmaker.log`
3. Check service status: `sudo systemctl status pinmaker`

### If website not accessible:
1. Check nginx status: `sudo systemctl status nginx`
2. Check nginx config: `sudo nginx -t`
3. Check SSL certificates: `sudo certbot certificates`

## Important Notes

1. **Always run as pinmaker user** after initial setup
2. **Always activate virtual environment** before running deploy.sh
3. **The /opt/Pinmaker directory must contain the actual files**, not just folders
4. **If you need to start over**, delete everything and follow from Step 2

## Commands Summary

```bash
# Connect
ssh root@YOUR_SERVER_IP

# Setup user and directory
useradd -m -s /bin/bash pinmaker
passwd pinmaker
usermod -aG sudo pinmaker
mkdir -p /opt/Pinmaker
chown -R pinmaker:pinmaker /opt/Pinmaker

# Switch user and clone
su - pinmaker
cd /opt/Pinmaker
git clone https://github.com/Krafty-Sprouts-Media-LLC/Pinmaker.git .

# Setup and deploy
chmod +x setup.sh deploy.sh
./setup.sh
source venv/bin/activate
./deploy.sh
```

This is the correct sequence. No complex scripts, no fixes - just the proper order of operations.