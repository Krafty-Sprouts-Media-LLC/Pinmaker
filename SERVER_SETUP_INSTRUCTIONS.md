# Server Setup Instructions for Pinmaker

## Server Details
- **IP Address:** 91.99.219.136
- **Username:** pinmaker
- **Password:** @@pinmaker@@

## Step-by-Step Setup Process

### 1. Connect to Your Server
```bash
ssh pinmaker@91.99.219.136
# Enter password: @@pinmaker@@
```

### 2. Upload the Fix Script
First, upload the `fix_setup.sh` script to your server. You can do this in several ways:

**Option A: Using SCP (from your local machine)**
```bash
scp fix_setup.sh pinmaker@91.99.219.136:~/
```

**Option B: Create the script directly on the server**
```bash
# After SSH connection, create the script
nano fix_setup.sh
# Copy and paste the content from fix_setup.sh
# Save with Ctrl+X, then Y, then Enter
```

### 3. Make the Script Executable and Run It
```bash
chmod +x fix_setup.sh
./fix_setup.sh
```

### 4. Access the Virtual Environment
After the fix script completes successfully:

```bash
# Navigate to the application directory
cd /opt/Pinmaker

# Activate the virtual environment
source venv/bin/activate

# You should see (venv) in your prompt, indicating the virtual environment is active
# Example: (venv) pinmaker@pinmaker:/opt/Pinmaker$
```

### 5. Run the Deployment Script
```bash
# Make sure you're in /opt/Pinmaker with virtual environment activated
# Make the deploy script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

### 6. Verify the Setup
After deployment completes:

```bash
# Check if the service is running
sudo systemctl status pinmaker

# Check if the application responds
curl http://localhost:8000/health

# Check if the website is accessible
curl -I https://pinmaker.kraftysprouts.com
```

## Troubleshooting

### If Virtual Environment Activation Fails
```bash
# Check if virtual environment exists
ls -la /opt/Pinmaker/venv

# If it doesn't exist, recreate it
cd /opt/Pinmaker
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### If Deploy Script Fails
```bash
# Check the deployment logs
tail -f /opt/Pinmaker/logs/deploy.log

# Check application logs
sudo journalctl -u pinmaker -f

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

### If Services Don't Start
```bash
# Restart services manually
sudo systemctl daemon-reload
sudo systemctl restart pinmaker
sudo systemctl restart nginx

# Check service status
sudo systemctl status pinmaker
sudo systemctl status nginx
```

## Important Notes

1. **Always activate the virtual environment** before running Python commands:
   ```bash
   cd /opt/Pinmaker
   source venv/bin/activate
   ```

2. **The deploy script must be run as the pinmaker user** (not root)

3. **If you need to make changes to the code:**
   ```bash
   cd /opt/Pinmaker
   source venv/bin/activate
   # Make your changes
   ./deploy.sh  # This will pull latest changes and redeploy
   ```

4. **To check if everything is working:**
   - Application health: `curl http://localhost:8000/health`
   - Website: Visit `https://pinmaker.kraftysprouts.com` in your browser

## Quick Reference Commands

```bash
# Connect to server
ssh pinmaker@91.99.219.136

# Go to app directory and activate virtual environment
cd /opt/Pinmaker && source venv/bin/activate

# Deploy latest changes
./deploy.sh

# Check service status
sudo systemctl status pinmaker nginx

# View logs
sudo journalctl -u pinmaker -f
tail -f /opt/Pinmaker/logs/deploy.log
```

## Security Reminder

- Change the default password after first login
- Consider setting up SSH key authentication
- The password `@@pinmaker@@` should be changed for security

---

**Next Steps:** Follow steps 1-6 above to complete your server setup!