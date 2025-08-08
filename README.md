# Pinterest Template Generator

A production-ready AI-powered Pinterest template generator that analyzes uploaded images and creates high-quality, customizable Pinterest templates with >90% visual accuracy.

## 🚀 Features

- **AI-Powered Analysis**: Custom CV pipeline using color segmentation, EasyOCR, and contour detection
- **Template Generation**: Automatic SVG template creation with intelligent layout detection
- **Custom Fonts**: Upload and manage TTF, OTF, WOFF font files
- **Real-time Preview**: Generate previews with customizable text and images
- **Stock Photo Integration**: Support for Unsplash, Pexels, and Pixabay APIs
- **Modern UI**: React TypeScript frontend with Tailwind CSS
- **Production Ready**: FastAPI backend with comprehensive monitoring and deployment

## 🏗️ Architecture

- **Backend**: FastAPI (Python) serving both API and static files
- **Frontend**: React TypeScript with Vite build system
- **AI Libraries**: PyTorch, Ultralytics, EasyOCR, OpenCV, scikit-learn
- **Deployment**: Single Python process with Nginx reverse proxy
- **Storage**: Temporary file-based storage (no database required)

## 📋 Requirements

### System Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.12+
- Node.js 18+
- 4GB+ RAM (8GB+ recommended for AI models)
- 20GB+ disk space
- Domain with DNS pointing to your VPS

### VPS Specifications
- **Minimum**: 2 vCPU, 4GB RAM, 40GB SSD
- **Recommended**: 4 vCPU, 8GB RAM, 80GB SSD
- **Optimal**: 8 vCPU, 16GB RAM, 160GB SSD

## 🚀 Quick Start (VPS Deployment)

### 1. Initial Server Setup

```bash
# Connect to your VPS
ssh root@your-server-ip

# Create sudo user
adduser pinmaker
usermod -aG sudo pinmaker

# Switch to the new user
su - pinmaker
```

### 2. Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/pinmaker.git
cd pinmaker

# Make setup script executable
chmod +x setup.sh
```

### 3. Run Automated Setup

```bash
# Run the complete setup script
./setup.sh
```

The setup script will:
- Install all system dependencies
- Set up Python 3.12 and virtual environment
- Install AI libraries and dependencies
- Build the React frontend
- Configure Nginx with SSL
- Set up systemd service
- Configure firewall and security
- Create monitoring and backup scripts

### 4. Configure Environment

Edit the environment file:

```bash
nano /opt/Pinmaker/.env
```

Add your API keys:

```env
# Stock photo API keys
UNSPLASH_ACCESS_KEY=your_unsplash_key
PEXELS_API_KEY=your_pexels_key
PIXABAY_API_KEY=your_pixabay_key
```

### 5. Restart and Test

```bash
# Restart the application
sudo systemctl restart pinmaker

# Check status
sudo systemctl status pinmaker

# Test the application
curl https://pinmaker.kraftysprouts.com/health
```

## 🔧 Development Workflow

### Making Changes

1. **Edit files directly on VPS**:
   ```bash
   cd /opt/Pinmaker
   nano main.py  # or any other file
   ```

2. **Commit and push changes**:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

3. **Deploy updates**:
   ```bash
   ./deploy.sh
   ```

### Frontend Development

```bash
cd /opt/Pinmaker/frontend

# Install dependencies
npm install

# Development server (for testing)
npm run dev

# Build for production
npm run build

# Copy to static directory
cp -r dist/* ../static/
```

### Backend Development

```bash
cd /home/pinmaker/app

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install package_name
pip freeze > requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
pinmaker/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── setup.sh               # VPS deployment script
├── README.md              # This file
├── .env                   # Environment configuration
├── gunicorn.conf.py       # Gunicorn configuration
├── deploy.sh              # Deployment script
├── backup.sh              # Backup script
├── monitor.sh             # Monitoring script
├── frontend/              # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   ├── vite.config.ts     # Vite configuration
│   ├── tailwind.config.js # Tailwind CSS config
│   └── tsconfig.json      # TypeScript config
├── static/                # Built frontend files
├── uploads/               # Uploaded images
├── templates/             # Generated templates
├── previews/              # Generated previews
├── fonts/                 # Custom fonts
├── logs/                  # Application logs
└── backups/               # Backup files
```

## 🔌 API Endpoints

### Health Check
```
GET /health
```

### Image Analysis
```
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- image: File (required)
```

### Template Generation
```
POST /api/generate-template
Content-Type: application/json

{
  "analysis_id": "string",
  "style": "modern|vintage|minimal|bold",
  "color_scheme": "original|monochrome|vibrant|pastel",
  "template_type": "pinterest|instagram|facebook"
}
```

### Preview Generation
```
POST /api/generate-preview
Content-Type: application/json

{
  "template_id": "string",
  "sample_text": "string",
  "stock_keywords": "string",
  "style": "string",
  "color_scheme": "string",
  "export_format": "png|jpg|svg",
  "quality": 90
}
```

### Font Management
```
POST /api/fonts/upload     # Upload font file
GET /api/fonts/list        # List available fonts
DELETE /api/fonts/{name}   # Delete font
GET /api/fonts/{name}/info # Get font information
```

## 🎨 Frontend Components

### Main Components
- **ImageUpload**: Drag-and-drop image upload with preview
- **TemplateEditor**: Interactive SVG template editor
- **PreviewPanel**: Template preview generation and export
- **FontManager**: Custom font upload and management
- **ColorPicker**: Color selection with presets
- **FontSelector**: Font selection with preview
- **ElementEditor**: Individual element editing

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Components**: Reusable UI components
- **Responsive Design**: Mobile-first approach
- **Dark Mode**: Optional dark theme support

## 🤖 AI Pipeline

### Image Analysis
1. **Color Segmentation**: Extract dominant colors and regions
2. **Text Detection**: Use EasyOCR for text recognition
3. **Contour Detection**: Identify shapes and layout elements
4. **Layout Analysis**: Determine optimal template structure

### Template Generation
1. **SVG Creation**: Generate scalable vector graphics
2. **Element Positioning**: Intelligent layout placement
3. **Typography**: Font selection and text styling
4. **Color Harmony**: Automatic color scheme generation

### Model Management
- **YOLOv8**: Object detection and segmentation
- **EasyOCR**: Optical character recognition
- **Custom Models**: Layout-specific trained models
- **Model Caching**: Efficient model loading and caching

## 🔒 Security Features

- **SSL/TLS**: Automatic HTTPS with Let's Encrypt
- **Firewall**: UFW configuration with minimal open ports
- **Fail2ban**: Intrusion prevention system
- **File Validation**: Strict file type and size checking
- **Rate Limiting**: API request throttling
- **CORS**: Cross-origin resource sharing protection
- **Security Headers**: Comprehensive HTTP security headers

## 📊 Monitoring & Logging

### Log Files
- **Application**: `/opt/Pinmaker/logs/app.log`
- **Access**: `/opt/Pinmaker/logs/access.log`
- **Error**: `/opt/Pinmaker/logs/error.log`
- **Monitor**: `/opt/Pinmaker/logs/monitor.log`

### Monitoring Commands
```bash
# View application logs
sudo journalctl -u pinmaker -f

# Check service status
sudo systemctl status pinmaker

# Monitor system resources
htop

# Check disk usage
df -h

# View recent errors
tail -f /opt/Pinmaker/logs/error.log
```

### Automated Monitoring
- **Health Checks**: Every 5 minutes
- **Resource Monitoring**: CPU, memory, disk usage
- **Service Recovery**: Automatic restart on failure
- **Log Rotation**: Daily log rotation with compression

## 🔄 Backup & Recovery

### Automated Backups
- **Daily Backups**: Automatic backup at 2 AM
- **Retention**: Keep last 7 backups
- **Includes**: Application code, uploads, templates, fonts
- **Excludes**: Virtual environment, node_modules, cache

### Manual Backup
```bash
# Create backup
/opt/Pinmaker/backup.sh

# List backups
ls -la /opt/Pinmaker/backups/

# Restore from backup
tar -xzf /opt/Pinmaker/backups/pinmaker_backup_YYYYMMDD_HHMMSS.tar.gz
```

## 🚀 Performance Optimization

### Backend Optimization
- **Gunicorn**: Multi-worker WSGI server
- **Async Processing**: FastAPI async/await support
- **Model Caching**: Efficient AI model loading
- **File Compression**: Gzip compression for responses
- **Connection Pooling**: Optimized HTTP client connections

### Frontend Optimization
- **Code Splitting**: Dynamic imports for components
- **Asset Optimization**: Minified CSS/JS bundles
- **Image Optimization**: WebP format support
- **Caching**: Browser and CDN caching strategies
- **Lazy Loading**: Component and image lazy loading

### Infrastructure Optimization
- **Nginx**: High-performance reverse proxy
- **SSL Optimization**: Modern TLS configuration
- **Static File Serving**: Direct Nginx file serving
- **Compression**: Gzip and Brotli compression
- **Caching**: Browser and proxy caching headers

## 🐛 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status pinmaker

# View detailed logs
sudo journalctl -u pinmaker --no-pager -l

# Check configuration
nginx -t
```

#### High Memory Usage
```bash
# Check memory usage
free -h

# Monitor processes
top

# Restart application
sudo systemctl restart pinmaker
```

#### SSL Certificate Issues
```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate status
sudo certbot certificates
```

#### File Upload Issues
```bash
# Check disk space
df -h

# Check permissions
ls -la /opt/Pinmaker/uploads/

# Fix permissions
sudo chown -R pinmaker:pinmaker /opt/Pinmaker/
```

### Performance Issues

#### Slow Response Times
1. Check system resources: `htop`
2. Monitor logs: `tail -f /opt/Pinmaker/logs/app.log`
3. Restart services: `sudo systemctl restart pinmaker nginx`
4. Clear cache: `rm -rf /opt/Pinmaker/__pycache__`

#### High CPU Usage
1. Check running processes: `ps aux | grep python`
2. Monitor AI model usage
3. Adjust worker count in `gunicorn.conf.py`
4. Consider upgrading server resources

## 📈 Scaling Considerations

### Horizontal Scaling
- **Load Balancer**: Nginx upstream configuration
- **Multiple Instances**: Deploy on multiple servers
- **Shared Storage**: NFS or cloud storage for files
- **Database**: Add PostgreSQL for persistent data

### Vertical Scaling
- **CPU**: More cores for AI processing
- **Memory**: Additional RAM for model caching
- **Storage**: SSD for faster file operations
- **GPU**: CUDA support for AI acceleration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature-name`
7. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: This README and inline code comments
- **Issues**: GitHub Issues for bug reports and feature requests
- **Logs**: Check application logs for detailed error information
- **Monitoring**: Use built-in monitoring scripts for system health

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core AI pipeline implementation
- ✅ React TypeScript frontend
- ✅ FastAPI backend
- ✅ VPS deployment automation
- ✅ SSL and security configuration

### Phase 2 (Future)
- 🔄 Advanced AI models for better accuracy
- 🔄 Real-time collaboration features
- 🔄 Template marketplace
- 🔄 Advanced analytics and reporting
- 🔄 Mobile app development

### Phase 3 (Long-term)
- 🔄 Multi-tenant architecture
- 🔄 Enterprise features
- 🔄 API monetization
- 🔄 White-label solutions
- 🔄 International expansion

---

**Pinterest Template Generator** - Transforming images into stunning Pinterest templates with AI precision. 🎨✨#   D e p l o y m e n t   t r i g g e r   f o r   n g i n x   c o n f i g   u p d a t e  
 