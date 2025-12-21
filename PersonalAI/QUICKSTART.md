# ⚡ PersonalAI Quick Start

**Klaar voor productie in 5 minuten!**

## 🚀 Super Snelle Start

### Optie 1: Eén-Commando Deploy (Linux)

```bash
chmod +x deploy.sh && ./deploy.sh
```

✅ Klaar! Volg de instructies op het scherm.

---

### Optie 2: Docker (Aanbevolen)

**Vereisten:**
- Docker & Docker Compose
- NVIDIA GPU (optioneel maar aanbevolen)

```bash
# 1. Configureer
cp .env.example .env
nano .env  # Voeg je Telegram token toe

# 2. Start!
docker-compose up -d

# 3. Check logs
docker-compose logs -f
```

✅ Telegram bot draait nu!

**Web interface:**
```bash
docker-compose up -d personalai-web
```
Open: http://localhost:7860

---

### Optie 3: Handmatig (Linux/Mac)

```bash
# 1. Python venv
python3.10 -m venv venv
source venv/bin/activate

# 2. Dependencies
cd ..
pip install -r requirements.txt
cd PersonalAI
pip install -r requirements.txt

# 3. Configuratie
cp .env.example .env
nano .env  # Telegram token

# 4. Test
python main.py test

# 5. Start!
python main.py telegram
```

---

## 📱 Telegram Bot Setup

1. Open Telegram
2. Zoek: **@BotFather**
3. Stuur: `/newbot`
4. Volg instructies
5. Kopieer token
6. Plak in `.env`:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

---

## ✅ Eerste Test

**Telegram:**
1. Zoek je bot op Telegram
2. Stuur: `/start`
3. Upload een foto
4. Caption: "Wat zie je?"

**Web:**
1. Open: http://localhost:7860
2. Upload foto
3. Klik "Analyseer"

---

## 🎯 Veel Gebruikte Commands

```bash
# Status check
python main.py status

# Test systeem
python main.py test

# Start Telegram bot
python main.py telegram

# Start web interface
python main.py web

# Docker status
docker-compose ps

# Docker logs
docker-compose logs -f
```

---

## 🔧 Als Het Niet Werkt

### "No module named 'telegram'"
```bash
pip install python-telegram-bot
```

### "CUDA out of memory"
Edit `config.py`:
```python
ROBOBRAIN_MODEL = "BAAI/RoboBrain2.0-3B"  # Kleiner model
```

### "Bot token not found"
Check `.env` bestand:
```bash
cat .env
```

### Docker GPU niet gevonden
```bash
# Installeer NVIDIA Container Toolkit
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

---

## 📚 Meer Info

- **Volledige Setup**: Zie [README.md](README.md)
- **Production Deploy**: Zie [DEPLOYMENT.md](DEPLOYMENT.md)
- **Troubleshooting**: Run `python main.py test`

---

## 🎉 Dat Was Het!

PersonalAI draait nu! Stuur je eerste foto naar de bot en ervaar de kracht van AI vision!

**Veel plezier! 🚀**
