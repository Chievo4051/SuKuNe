# Docker Deployment Guide SeKuNe

Panduan lengkap untuk menjalankan aplikasi SeKuNe menggunakan Docker. Docker memastikan aplikasi berjalan konsisten di berbagai lingkungan dan sistem operasi.

## 🐳 Mengapa Docker?

### Keuntungan Docker untuk SeKuNe:
- **Portabilitas**: Berjalan identik di Ubuntu, Alpine, Arch Linux, Windows, macOS
- **Konsistensi**: Environment yang sama dari development hingga production
- **Isolasi**: Aplikasi terisolasi dari sistem host
- **Skalabilitas**: Mudah di-scale horizontal dengan orchestration
- **Dependency Management**: Semua dependencies terbundle dalam container

## 📋 Persyaratan Sistem

### Minimum Requirements:
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **RAM**: 2GB available
- **Storage**: 5GB free space
- **CPU**: 2 cores (recommended)

### Supported Operating Systems:
- **Linux**: Ubuntu 18.04+, Debian 10+, CentOS 7+, Alpine Linux, Arch Linux
- **Windows**: Windows 10/11 dengan WSL2
- **macOS**: macOS 10.14+

## 🚀 Quick Start

### 1. Install Docker & Docker Compose

#### Ubuntu/Debian:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout dan login kembali untuk apply group changes
```

#### Alpine Linux:
```bash
# Install Docker
sudo apk add docker docker-compose
sudo rc-update add docker boot
sudo service docker start
sudo addgroup $USER docker

# Logout dan login kembali
```

#### Arch Linux:
```bash
# Install Docker
sudo pacman -S docker docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Logout dan login kembali
```

#### Windows (WSL2):
1. Install Docker Desktop for Windows
2. Enable WSL2 integration
3. Restart komputer

#### macOS:
1. Install Docker Desktop for Mac
2. Start Docker Desktop application

### 2. Clone Repository
```bash
git clone https://github.com/Chievo4051/SuKuNe.git
cd SuKuNe
```

### 3. Jalankan Aplikasi

#### Menggunakan Make (Recommended):
```bash
# Install aplikasi pertama kali
make install

# Atau manual step-by-step:
make build    # Build images
make up       # Start services
```

#### Menggunakan Docker Compose langsung:
```bash
# Build dan start services
docker-compose up -d --build

# Lihat logs
docker-compose logs -f
```

### 4. Akses Aplikasi
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **Admin Login**: admin@sekune.com / admin123

## 🏗 Arsitektur Docker

### Services Overview:
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Nginx)       │◄──►│    (Flask)      │◄──►│  (PostgreSQL)   │
│   Port: 80      │    │   Port: 5000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Caching)     │
                    │   Port: 6379    │
                    └─────────────────┘
```

### Container Details:

#### Frontend Container:
- **Base Image**: nginx:alpine
- **Build**: Multi-stage (Node.js builder + Nginx runtime)
- **Port**: 80
- **Features**: Gzip compression, security headers, API proxy

#### Backend Container:
- **Base Image**: python:3.11-alpine
- **Port**: 5000
- **Features**: Flask app, JWT auth, SQLite/PostgreSQL support
- **Health Check**: API endpoint monitoring

#### Database Container:
- **Image**: postgres:15-alpine
- **Port**: 5432 (internal)
- **Persistence**: Volume-backed storage

#### Redis Container:
- **Image**: redis:7-alpine
- **Port**: 6379 (internal)
- **Usage**: Session storage, caching

## 🔧 Configuration

### Environment Variables

#### Backend (.env):
```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
JWT_ACCESS_TOKEN_EXPIRES=3600

# Database Configuration
DATABASE_URL=postgresql://sekune_user:password@database:5432/sekune_db
# Atau untuk SQLite:
# DATABASE_URL=sqlite:///sekune.db

# CORS Configuration
CORS_ORIGINS=http://localhost,http://localhost:80

# Redis Configuration (optional)
REDIS_URL=redis://:password@redis:6379/0
```

#### Database:
```env
POSTGRES_DB=sekune_db
POSTGRES_USER=sekune_user
POSTGRES_PASSWORD=change-this-password
```

### Custom Configuration

#### Override docker-compose.yml:
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  backend:
    environment:
      - JWT_SECRET_KEY=your-custom-secret
    ports:
      - "5001:5000"  # Custom port
  
  frontend:
    ports:
      - "8080:80"    # Custom port
```

## 🛠 Development Mode

### Development dengan Hot Reload:
```bash
# Start development environment
make dev-up

# Atau manual:
docker-compose -f docker-compose.dev.yml up -d
```

### Development Features:
- **Hot Reload**: Code changes auto-reload
- **Debug Mode**: Flask debug enabled
- **Volume Mounts**: Source code mounted for live editing
- **Development Tools**: Debugger, linter, formatter included

### Development Commands:
```bash
# Build development images
make dev-build

# Start development services
make dev-up

# View development logs
make dev-logs

# Access backend shell
make dev-shell-backend

# Access frontend shell
make dev-shell-frontend

# Run tests
make test-backend
make test-frontend
```

## 📊 Monitoring & Maintenance

### Health Checks:
```bash
# Check service health
make health

# Monitor resource usage
make monitor

# View detailed status
make status
```

### Logs Management:
```bash
# View all logs
make logs

# Backend logs only
make logs-backend

# Frontend logs only
make logs-frontend

# Follow logs in real-time
docker-compose logs -f --tail=100
```

### Database Management:
```bash
# Backup database
make backup-db

# Access database shell
make shell-db

# View database logs
docker-compose logs database
```

## 🔒 Security Best Practices

### Container Security:
- **Non-root user**: All containers run as non-root
- **Minimal base images**: Alpine Linux for smaller attack surface
- **Security headers**: Nginx configured with security headers
- **Network isolation**: Services communicate via internal network

### Production Security Checklist:
- [ ] Change default passwords in docker-compose.yml
- [ ] Use strong JWT secret key
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor container vulnerabilities

### Security Scanning:
```bash
# Scan images for vulnerabilities (requires Trivy)
make security-scan

# Install Trivy scanner
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

## 🚀 Production Deployment

### Production Checklist:
- [ ] Update environment variables
- [ ] Configure SSL/TLS certificates
- [ ] Set up reverse proxy (if needed)
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation

### SSL/HTTPS Setup:
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
```

### Reverse Proxy Configuration:
```nginx
# nginx.conf for production
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📈 Scaling & Performance

### Horizontal Scaling:
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
    
  frontend:
    deploy:
      replicas: 2
```

### Load Balancing:
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Use nginx for load balancing
upstream backend_servers {
    server backend_1:5000;
    server backend_2:5000;
    server backend_3:5000;
}
```

### Performance Optimization:
- **Resource Limits**: Set CPU and memory limits
- **Caching**: Use Redis for session and data caching
- **Database Optimization**: Connection pooling, indexing
- **Static Assets**: CDN for static files

## 🔧 Troubleshooting

### Common Issues:

#### Port Already in Use:
```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :5000

# Kill the process or change port in docker-compose.yml
```

#### Container Won't Start:
```bash
# Check container logs
docker-compose logs <service_name>

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart <service_name>
```

#### Database Connection Error:
```bash
# Check database container
docker-compose logs database

# Verify database is ready
docker-compose exec database pg_isready -U sekune_user

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Out of Disk Space:
```bash
# Clean up Docker resources
make clean

# Remove unused images and containers
docker system prune -a

# Check disk usage
docker system df
```

### Performance Issues:
```bash
# Monitor resource usage
docker stats

# Check container resource limits
docker inspect <container_name> | grep -A 10 Resources

# Optimize images
docker-compose build --no-cache
```

## 🔄 Updates & Maintenance

### Update Application:
```bash
# Automated update
make update

# Manual update
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Strategy:
```bash
# Backup database
make backup-db

# Backup volumes
docker run --rm -v sekune_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Backup uploaded files
docker run --rm -v sekune_backend_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads_backup.tar.gz /data
```

### Restore from Backup:
```bash
# Restore database
docker run --rm -v sekune_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /

# Restore uploaded files
docker run --rm -v sekune_backend_uploads:/data -v $(pwd):/backup alpine tar xzf /backup/uploads_backup.tar.gz -C /
```

## 📚 Advanced Usage

### Custom Networks:
```yaml
networks:
  frontend_network:
    driver: bridge
  backend_network:
    driver: bridge
    internal: true
```

### Health Checks:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Resource Limits:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

## 🆘 Support & Community

### Getting Help:
- **GitHub Issues**: Report bugs dan feature requests
- **Documentation**: Lengkap di repository
- **Community**: Discord/Slack channel (jika tersedia)

### Contributing:
- Fork repository
- Create feature branch
- Submit pull request
- Follow coding standards

---

**Docker deployment SeKuNe** memberikan solusi yang robust, scalable, dan portable untuk menjalankan aplikasi di berbagai environment. Dengan konfigurasi yang tepat, aplikasi dapat berjalan optimal dari development hingga production scale.

