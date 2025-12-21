# 🚀 PersonalAI Production Deployment Guide

Complete gids voor het deployen van PersonalAI in productie.

## 📋 Inhoudsopgave

1. [Deployment Opties](#deployment-opties)
2. [Lokale Deployment](#lokale-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Systemd Service](#systemd-service)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Deployment Opties

### Optie 1: Quick Deploy (Aanbevolen voor beginners)
```bash
chmod +x deploy.sh
./deploy.sh
```
✅ Automatische setup
✅ Detecteert GPU
✅ Installeert dependencies
✅ Optioneel systemd service

### Optie 2: Docker (Aanbevolen voor productie)
```bash
docker-compose up -d
```
✅ Geïsoleerde omgeving
✅ Makkelijk schalen
✅ Portable

### Optie 3: Manueel
Zie [Lokale Deployment](#lokale-deployment)

---

## 💻 Lokale Deployment

### Systeemvereisten

**Minimaal:**
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Python 3.10+
- 16GB RAM
- 50GB disk space
- (Optioneel) NVIDIA GPU met CUDA 12.x

**Aanbevolen:**
- Ubuntu 22.04 LTS
- Python 3.10
- 32GB RAM
- 100GB SSD
- NVIDIA GPU (RTX 3090 / A100 / etc.)

### Stap-voor-Stap Installatie

#### 1. Systeem Voorbereiden
```bash
# Update systeem
sudo apt update && sudo apt upgrade -y

# Installeer dependencies
sudo apt install -y python3.10 python3.10-venv python3-pip git wget curl

# NVIDIA drivers (indien GPU)
# Zie: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
```

#### 2. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/FlagOpen/RoboBrain2.0.git
cd RoboBrain2.0/PersonalAI
```

#### 3. Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate
```

#### 4. Installeer Dependencies
```bash
# RoboBrain dependencies
cd ..
pip install -r requirements.txt

# PersonalAI dependencies
cd PersonalAI
pip install -r requirements.txt
```

#### 5. Configuratie
```bash
# Kopieer environment template
cp .env.example .env

# Bewerk configuratie
nano .env
```

Voeg toe:
```bash
TELEGRAM_BOT_TOKEN=your_actual_token_here
TELEGRAM_ALLOWED_USERS=  # Laat leeg voor iedereen
```

#### 6. Test Installatie
```bash
python main.py test
```

Als alles groen is ✅, ga door!

#### 7. Start Applicatie
```bash
# Telegram bot
python main.py telegram

# OF web interface
python main.py web
```

---

## 🐳 Docker Deployment

### Vereisten
- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Container Toolkit (voor GPU)

### NVIDIA Container Toolkit Setup
```bash
# Installeer NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Build & Run

#### Telegram Bot
```bash
# Build image
docker-compose build personalai-telegram

# Start service
docker-compose up -d personalai-telegram

# Bekijk logs
docker-compose logs -f personalai-telegram
```

#### Web Interface
```bash
# Start web service
docker-compose up -d personalai-web

# Access op http://localhost:7860
```

#### Beide Interfaces
```bash
docker-compose up -d
```

### Docker Commands

```bash
# Status check
docker-compose ps

# Logs bekijken
docker-compose logs -f

# Stop services
docker-compose down

# Restart
docker-compose restart

# Update (nieuwe versie)
git pull
docker-compose build
docker-compose up -d
```

### Data Persistence

Data wordt opgeslagen in volumes:
```bash
# Backup data
docker run --rm -v personalai_huggingface-cache:/data -v $(pwd)/backup:/backup \
    ubuntu tar czf /backup/huggingface-backup.tar.gz /data

# Restore data
docker run --rm -v personalai_huggingface-cache:/data -v $(pwd)/backup:/backup \
    ubuntu tar xzf /backup/huggingface-backup.tar.gz -C /
```

---

## ☁️ Cloud Deployment

### AWS EC2

#### Instance Type
- **Aanbevolen**: g5.xlarge (A10G GPU)
- **Budget**: t3.xlarge (CPU only, trager)
- **High-end**: g5.2xlarge / p4d.24xlarge

#### Setup
```bash
# SSH naar instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update systeem
sudo apt update && sudo apt upgrade -y

# Installeer NVIDIA drivers (g5 instance)
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall

# Clone en deploy
cd /opt
sudo git clone https://github.com/FlagOpen/RoboBrain2.0.git
cd RoboBrain2.0/PersonalAI
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

#### Security Groups
- **Telegram**: Geen inbound poorten nodig (uitgaande verbindingen)
- **Web**: Open port 7860 (of gebruik NGINX reverse proxy)

### Google Cloud Platform

```bash
# GCE instance met GPU
gcloud compute instances create personalai \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --accelerator=type=nvidia-tesla-t4,count=1 \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB \
    --maintenance-policy=TERMINATE

# SSH en deploy
gcloud compute ssh personalai
# ... volg lokale deployment stappen
```

### DigitalOcean

```bash
# Maak droplet met GPU
# Kies: GPU Droplet, Ubuntu 22.04

# SSH en deploy
ssh root@your-droplet-ip
# ... volg deployment
```

---

## ⚙️ Systemd Service

Voor auto-start bij system boot en automatische restarts.

### Installatie

#### 1. Kopieer Service Files
```bash
sudo cp systemd/personalai-telegram.service /etc/systemd/system/
sudo cp systemd/personalai-web.service /etc/systemd/system/
```

#### 2. Pas Paths Aan (indien nodig)
```bash
sudo nano /etc/systemd/system/personalai-telegram.service
```

Verander:
- `User=` naar jouw gebruiker
- `WorkingDirectory=` naar jouw installatie path
- `ExecStart=` naar jouw python path

#### 3. Enable & Start
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable personalai-telegram.service

# Start service
sudo systemctl start personalai-telegram.service

# Check status
sudo systemctl status personalai-telegram.service
```

### Service Management

```bash
# Start
sudo systemctl start personalai-telegram

# Stop
sudo systemctl stop personalai-telegram

# Restart
sudo systemctl restart personalai-telegram

# Status
sudo systemctl status personalai-telegram

# Logs
sudo journalctl -u personalai-telegram -f

# Disable auto-start
sudo systemctl disable personalai-telegram
```

---

## 📊 Monitoring & Logging

### Logs Bekijken

#### Direct
```bash
# Telegram bot (als systemd service)
sudo journalctl -u personalai-telegram -f

# Web interface
sudo journalctl -u personalai-web -f
```

#### Docker
```bash
docker-compose logs -f personalai-telegram
```

### Log Rotatie

Configureer in `/etc/logrotate.d/personalai`:
```
/var/log/personalai/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 personalai personalai
    sharedscripts
    postrotate
        systemctl reload personalai-telegram > /dev/null 2>&1 || true
    endscript
}
```

### Monitoring Tools

#### Prometheus + Grafana
```bash
# Voeg metrics endpoint toe aan config.py
# Gebruik prometheus-client library
```

#### Simple monitoring script
```bash
#!/bin/bash
# check-personalai.sh

if systemctl is-active --quiet personalai-telegram; then
    echo "✅ PersonalAI Telegram: Running"
else
    echo "❌ PersonalAI Telegram: Down"
    # Stuur notificatie / restart
    sudo systemctl restart personalai-telegram
fi
```

Voeg toe aan crontab:
```bash
*/5 * * * * /opt/personalai/check-personalai.sh
```

---

## 🔒 Security Best Practices

### 1. Dedicated User
```bash
# Maak dedicated user
sudo useradd -r -s /bin/bash -m -d /opt/personalai personalai

# Zet ownership
sudo chown -R personalai:personalai /opt/personalai
```

### 2. Firewall (UFW)
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow web interface (alleen indien nodig)
sudo ufw allow 7860/tcp

# Check status
sudo ufw status
```

### 3. NGINX Reverse Proxy (voor web)
```nginx
server {
    listen 80;
    server_name personalai.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Met SSL (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d personalai.yourdomain.com
```

### 4. Environment Variables
```bash
# Bescherm .env file
chmod 600 .env
chown personalai:personalai .env
```

### 5. Regular Updates
```bash
# Update systeem
sudo apt update && sudo apt upgrade

# Update PersonalAI
cd /opt/RoboBrain2.0
git pull
cd PersonalAI
source venv/bin/activate
pip install --upgrade -r requirements.txt
sudo systemctl restart personalai-telegram
```

---

## 🔧 Troubleshooting

### Bot Start Niet

**Check logs:**
```bash
sudo journalctl -u personalai-telegram -n 50
```

**Common issues:**
- ❌ Telegram token niet ingesteld → Check `.env`
- ❌ Dependencies niet geïnstalleerd → `pip install -r requirements.txt`
- ❌ Model niet gedownload → Wacht tot eerste download compleet is
- ❌ Geen GPU gevonden → Check NVIDIA drivers

### CUDA Out of Memory

**Oplossingen:**
1. Gebruik kleiner model: `ROBOBRAIN_MODEL = "BAAI/RoboBrain2.0-3B"`
2. Beperk batch size in config
3. Gebruik meer GPU memory of CPU fallback

### Web Interface Niet Bereikbaar

**Check:**
```bash
# Is service running?
sudo systemctl status personalai-web

# Port open?
sudo netstat -tulpn | grep 7860

# Firewall?
sudo ufw status
```

### Model Download Traag

**Tip:**
```bash
# Pre-download model
python -c "from transformers import AutoProcessor; AutoProcessor.from_pretrained('BAAI/RoboBrain2.0-7B')"
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R personalai:personalai /opt/personalai

# Fix permissions
chmod -R 755 /opt/personalai
chmod 600 /opt/personalai/PersonalAI/.env
```

---

## 📈 Performance Tuning

### GPU Optimalisatie
```python
# In config.py
ROBOBRAIN_DEVICE = "cuda:0"  # Specifieke GPU
```

### Memory Management
```python
# Beperk conversation history
MAX_CONVERSATION_HISTORY = 20  # Kleiner getal
```

### Concurrent Users (web)
```python
# In web_app.py bij demo.launch()
demo.launch(
    max_threads=10,  # Max concurrent requests
    server_port=7860
)
```

---

## 🎯 Production Checklist

Voordat je live gaat:

- [ ] ✅ .env geconfigureerd met echte credentials
- [ ] ✅ Systemd service geïnstalleerd
- [ ] ✅ Firewall geconfigureerd
- [ ] ✅ NGINX reverse proxy (indien web)
- [ ] ✅ SSL certificaat (indien publiek)
- [ ] ✅ Monitoring setup
- [ ] ✅ Log rotatie geconfigureerd
- [ ] ✅ Backup strategie
- [ ] ✅ Model gedownload en getest
- [ ] ✅ Performance getest met echte queries
- [ ] ✅ Error handling getest
- [ ] ✅ Security audit gedaan
- [ ] ✅ Documentatie up-to-date

---

## 📞 Support

Bij problemen:
1. Check deze guide
2. Run `python main.py test`
3. Check logs: `sudo journalctl -u personalai-telegram -f`
4. Zie README.md voor basis troubleshooting

---

**Happy Deploying! 🚀**

PersonalAI Production Deployment v1.0
