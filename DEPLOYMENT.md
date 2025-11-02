# Deployment Guide - Backend Kriptografi

Panduan untuk deploy aplikasi Flask ke server Linux menggunakan systemd service.

## 📋 Prerequisites

- Server Linux (Ubuntu/Debian)
- Python 3.8+
- MySQL/MariaDB Server
- Akses root atau sudo

## 🚀 Deployment Steps

### 1. Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv mysql-server nginx -y

# Install MySQL client
sudo apt install default-libmysqlclient-dev build-essential -y
```

### 2. Clone Project

```bash
# Buat directory
sudo mkdir -p /var/www/BackendKriptoPy
cd /var/www/BackendKriptoPy

# Clone dari git (sesuaikan dengan repo Anda)
sudo git clone https://github.com/ArdhikaRizki/BackendKriptoPy.git .

# Atau upload manual via FTP/SCP
```

### 3. Setup Python Virtual Environment

```bash
# Buat virtual environment
sudo python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Jika menggunakan gunicorn (recommended untuk production)
pip install gunicorn

deactivate
```

### 4. Setup Database

```bash
# Login ke MySQL
sudo mysql -u root -p

# Buat database dan user
CREATE DATABASE kriptografi_db;
CREATE USER 'kripto_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON kriptografi_db.* TO 'kripto_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Import schema database jika ada
# mysql -u kripto_user -p kriptografi_db < schema.sql
```

### 5. Configure Environment

```bash
# Edit .env file
sudo nano /var/www/BackendKriptoPy/.env
```

**Isi .env:**
```env
# Database Configuration
DB_HOST=localhost
DB_USER=kripto_user
DB_PASSWORD=your_strong_password
DB_DATABASE=kriptografi_db
DB_PORT=3306

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
SECRET_KEY=your-very-secret-random-key-change-this-in-production

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_FOLDER=uploads/message_attachments
```

### 6. Set Permissions

```bash
# Set ownership
sudo chown -R www-data:www-data /var/www/BackendKriptoPy

# Set permissions
sudo chmod -R 755 /var/www/BackendKriptoPy

# Buat folder uploads jika belum ada
sudo mkdir -p /var/www/BackendKriptoPy/uploads/message_attachments
sudo chown -R www-data:www-data /var/www/BackendKriptoPy/uploads
sudo chmod -R 775 /var/www/BackendKriptoPy/uploads

# Buat folder log untuk gunicorn
sudo mkdir -p /var/log/backend-kripto
sudo chown -R www-data:www-data /var/log/backend-kripto
```

### 7. Setup Systemd Service

#### Option A: Development Mode (Flask built-in server)

```bash
# Copy service file
sudo cp backend.service /etc/systemd/system/

# Edit jika perlu sesuaikan path
sudo nano /etc/systemd/system/backend.service
```

#### Option B: Production Mode (Gunicorn - RECOMMENDED)

```bash
# Copy service file
sudo cp backend-gunicorn.service /etc/systemd/system/backend-kripto.service

# Edit jika perlu sesuaikan path
sudo nano /etc/systemd/system/backend-kripto.service
```

### 8. Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable backend-kripto

# Start service
sudo systemctl start backend-kripto

# Check status
sudo systemctl status backend-kripto
```

### 9. Manage Service

```bash
# Stop service
sudo systemctl stop backend-kripto

# Restart service
sudo systemctl restart backend-kripto

# View logs
sudo journalctl -u backend-kripto -f

# View gunicorn logs (if using gunicorn)
sudo tail -f /var/log/backend-kripto/error.log
sudo tail -f /var/log/backend-kripto/access.log
```

## 🌐 Setup Nginx Reverse Proxy (Optional tapi Recommended)

```bash
# Buat nginx config
sudo nano /etc/nginx/sites-available/backend-kripto
```

**Isi config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Ganti dengan domain Anda

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (jika belum ada di Flask)
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
    }

    # Serve static files directly (if any)
    location /static {
        alias /var/www/BackendKriptoPy/static;
        expires 30d;
    }

    location /uploads {
        alias /var/www/BackendKriptoPy/uploads;
        expires 7d;
    }
}
```

**Enable site:**
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/backend-kripto /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## 🔒 Setup SSL with Let's Encrypt (Optional)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (biasanya sudah otomatis)
sudo certbot renew --dry-run
```

## 🔧 Troubleshooting

### Service tidak start:
```bash
# Cek error detail
sudo journalctl -u backend-kripto -n 50 --no-pager

# Cek permission
ls -la /var/www/BackendKriptoPy

# Test manual
cd /var/www/BackendKriptoPy
source venv/bin/activate
python main.py
```

### Database connection error:
```bash
# Cek MySQL running
sudo systemctl status mysql

# Test connection
mysql -u kripto_user -p -h localhost kriptografi_db

# Cek .env file
cat /var/www/BackendKriptoPy/.env
```

### Permission denied:
```bash
# Reset permissions
sudo chown -R www-data:www-data /var/www/BackendKriptoPy
sudo chmod -R 755 /var/www/BackendKriptoPy
sudo chmod -R 775 /var/www/BackendKriptoPy/uploads
```

## 📊 Monitoring

```bash
# CPU & Memory usage
htop

# Disk space
df -h

# Real-time logs
sudo journalctl -u backend-kripto -f

# Check if port 5000 listening
sudo netstat -tlnp | grep 5000
```

## 🔄 Update Application

```bash
# Stop service
sudo systemctl stop backend-kripto

# Pull latest code
cd /var/www/BackendKriptoPy
sudo -u www-data git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Restart service
sudo systemctl start backend-kripto
sudo systemctl status backend-kripto
```

## 📝 Notes

- **Development**: Gunakan `backend.service` (Flask development server)
- **Production**: Gunakan `backend-gunicorn.service` dengan gunicorn
- Jangan lupa set `FLASK_DEBUG=False` di production
- Backup database secara regular
- Monitor logs untuk error
- Gunakan strong password untuk DB dan SECRET_KEY

## 🆘 Support

Jika ada masalah:
1. Check logs: `sudo journalctl -u backend-kripto -n 100`
2. Check service status: `sudo systemctl status backend-kripto`
3. Test manual: Run `python main.py` di virtual environment
4. Check firewall: `sudo ufw status`
5. Check port: `sudo netstat -tlnp | grep 5000`
