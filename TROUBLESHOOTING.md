# Troubleshooting Guide - Error 405 & CORS Issues

## 🔧 Fix yang Sudah Dilakukan:

### 1. ✅ Menambahkan Flask-CORS
File `main.py` sudah diupdate dengan:
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 2. ✅ Menambahkan Debug Endpoint
Endpoint baru: `GET/POST /api/debug`
- Untuk cek apakah request sampai ke server
- Melihat headers, method, dan body yang diterima

---

## 🚀 Cara Deploy Update ke Server:

### Step 1: Upload File Baru
```bash
# Di server
cd /var/www/BackendKriptoPy

# Pull dari git (atau upload manual)
git pull

# Atau copy file main.py yang baru
```

### Step 2: Restart Service
```bash
# Restart service
sudo systemctl restart backend
# atau
sudo systemctl restart backend-kripto

# Check status
sudo systemctl status backend
```

### Step 3: Check Logs
```bash
# Lihat log real-time
sudo journalctl -u backend -f

# Atau check gunicorn logs
sudo tail -f /var/log/backend-kripto/error.log
```

---

## 🧪 Testing di Server:

### Test 1: Cek Server Hidup
```bash
curl http://your-server-ip:5000/
```

**Expected Response:**
```json
{
  "message": "Kripto App API...",
  "status": "running",
  "cors": "enabled"
}
```

### Test 2: Debug Endpoint (GET)
```bash
curl http://your-server-ip:5000/api/debug
```

### Test 3: Debug Endpoint (POST)
```bash
curl -X POST http://your-server-ip:5000/api/debug \
  -H "Content-Type: application/json" \
  -d '{"test":"data"}'
```

**Expected:** Harus return info tentang request

### Test 4: Register User
```bash
curl -X POST http://your-server-ip:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","username":"testuser"}'
```

### Test 5: Login User
```bash
curl -X POST http://your-server-ip:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

---

## 🐛 Diagnosa Error 405:

### Kemungkinan 1: CORS Preflight
**Problem:** Browser mengirim OPTIONS request dulu sebelum POST

**Solusi:** Sudah fixed dengan CORS configuration

**Test:**
```bash
# Test OPTIONS request
curl -X OPTIONS http://your-server-ip:5000/api/register -v
```

### Kemungkinan 2: Nginx Config
**Problem:** Nginx tidak forward method dengan benar

**Check:**
```bash
sudo nano /etc/nginx/sites-available/backend-kripto
```

**Pastikan ada:**
```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
    # Important for method forwarding
    proxy_method $request_method;
}
```

**Restart Nginx:**
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Kemungkinan 3: Firewall
**Problem:** Port 5000 tidak terbuka

**Fix:**
```bash
# Allow port 5000
sudo ufw allow 5000/tcp

# Check status
sudo ufw status
```

### Kemungkinan 4: Gunicorn Workers
**Problem:** Worker crash atau timeout

**Check logs:**
```bash
sudo tail -f /var/log/backend-kripto/error.log
```

**Increase workers/timeout di service file:**
```bash
sudo nano /etc/systemd/system/backend-kripto.service
```

Change:
```
--workers 4  → --workers 2
--timeout 120 → --timeout 300
```

**Restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart backend-kripto
```

---

## 📊 Common Error Messages & Fixes:

### Error 405: Method Not Allowed
**Cause:**
1. ❌ Pakai GET untuk endpoint POST
2. ❌ CORS preflight gagal
3. ❌ Nginx config salah
4. ❌ Endpoint tidak support method yang diminta

**Fix:**
1. ✅ Pastikan pakai method yang benar (POST untuk /api/register)
2. ✅ CORS sudah enabled di code
3. ✅ Nginx config benar
4. ✅ Test dengan curl dulu tanpa browser

### Error 500: Internal Server Error
**Cause:**
- Database connection error
- Python error di code

**Fix:**
```bash
# Check logs
sudo journalctl -u backend -n 50

# Check database
mysql -u kripto_user -p -e "SHOW DATABASES;"

# Test manual
cd /var/www/BackendKriptoPy
source venv/bin/activate
python main.py
```

### Error 502: Bad Gateway
**Cause:**
- Backend service tidak running
- Nginx tidak bisa connect ke backend

**Fix:**
```bash
# Check if backend running
sudo systemctl status backend

# Check if port 5000 listening
sudo netstat -tlnp | grep 5000

# Restart both
sudo systemctl restart backend
sudo systemctl restart nginx
```

### Error 504: Gateway Timeout
**Cause:**
- Request terlalu lama
- Database query lambat

**Fix:**
- Increase timeout di gunicorn
- Optimize database queries
- Check database performance

---

## 🔍 Step-by-Step Debugging:

### 1. Test dari Server Langsung
```bash
# SSH ke server
ssh user@your-server

# Test localhost
curl http://localhost:5000/
curl -X POST http://localhost:5000/api/debug \
  -H "Content-Type: application/json" \
  -d '{"test":"local"}'
```

**If this works:** Problem ada di Nginx/firewall  
**If this fails:** Problem ada di Flask app

### 2. Test dari External
```bash
# Dari komputer lokal
curl http://your-server-ip:5000/
```

**If this works:** Backend OK  
**If this fails:** Firewall issue

### 3. Test dengan Browser
```javascript
// Di browser console
fetch('http://your-server-ip:5000/api/debug', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({test: 'browser'})
})
.then(r => r.json())
.then(d => console.log(d))
```

### 4. Check Request Headers
```bash
# Dengan verbose
curl -v -X POST http://your-server-ip:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Look for:
- `< HTTP/1.1 200 OK` (success)
- `< HTTP/1.1 405 Method Not Allowed` (error)
- `Access-Control-Allow-Origin` header (CORS)

---

## 📝 Quick Checklist:

- [ ] Flask-CORS installed: `pip list | grep Flask-CORS`
- [ ] CORS enabled in main.py
- [ ] Service restarted: `sudo systemctl restart backend`
- [ ] Port 5000 listening: `netstat -tlnp | grep 5000`
- [ ] Firewall allows 5000: `sudo ufw status`
- [ ] Nginx config correct (if using nginx)
- [ ] Database connection OK: `curl http://localhost:5000/api/test-db`
- [ ] No errors in logs: `sudo journalctl -u backend -n 20`

---

## 🆘 Last Resort:

### Full Clean Restart:
```bash
# Stop everything
sudo systemctl stop backend
sudo systemctl stop nginx

# Clear logs
sudo journalctl --vacuum-time=1s

# Start fresh
sudo systemctl start backend
sudo systemctl start nginx

# Monitor logs
sudo journalctl -u backend -f
```

### Test with Python Directly:
```bash
cd /var/www/BackendKriptoPy
source venv/bin/activate

# Kill any existing process
pkill -f gunicorn
pkill -f "python main.py"

# Run directly
python main.py

# In another terminal, test
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

---

## 📞 Need More Help?

Share these logs:
1. `sudo journalctl -u backend -n 50`
2. `sudo tail -20 /var/log/backend-kripto/error.log`
3. Output dari: `curl -v http://your-server:5000/api/debug`
4. Your exact request (curl command or fetch code)
