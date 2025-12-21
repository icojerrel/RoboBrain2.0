#!/bin/bash
# PersonalAI Quick Deploy Script
# Snel deployen van PersonalAI in productie

set -e

echo "╔═══════════════════════════════════════╗"
echo "║   PersonalAI Production Deployment    ║"
echo "║                                       ║"
echo "║   Quick deploy voor Linux servers     ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Kleuren voor output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functies
print_status() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Consider using a non-root user."
fi

# Detecteer OS
print_status "Detecteren operating system..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    print_success "OS: $OS"
else
    print_error "Kan OS niet detecteren"
    exit 1
fi

# Check Python versie
print_status "Controleren Python versie..."
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD=python3.10
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$PYTHON_VERSION >= 3.10" | bc)" -eq 0 ]; then
        print_error "Python 3.10+ vereist. Gevonden: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 niet gevonden!"
    exit 1
fi
print_success "Python: $($PYTHON_CMD --version)"

# Check CUDA/GPU (optioneel)
print_status "Controleren GPU..."
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
    print_success "GPU gevonden: $GPU_INFO"
    HAS_GPU=true
else
    print_warning "Geen NVIDIA GPU gevonden. CPU-only mode."
    HAS_GPU=false
fi

# Installatie directory
INSTALL_DIR=$(pwd)
print_status "Installatie directory: $INSTALL_DIR"

# Stap 1: Virtual environment
print_status "Aanmaken virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment aangemaakt"
else
    print_warning "Virtual environment bestaat al"
fi

# Activeer venv
source venv/bin/activate
print_success "Virtual environment geactiveerd"

# Stap 2: Installeer dependencies
print_status "Installeren dependencies..."
cd ..
pip install --upgrade pip > /dev/null 2>&1
print_status "Installeren RoboBrain dependencies..."
pip install -r requirements.txt
print_status "Installeren PersonalAI dependencies..."
cd PersonalAI
pip install -r requirements.txt
print_success "Dependencies geïnstalleerd"

# Stap 3: Configuratie
print_status "Setup configuratie..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning ".env bestand aangemaakt - CONFIGUREER DIT BESTAND!"
    print_warning "  1. Voeg je Telegram bot token toe"
    print_warning "  2. Pas andere instellingen aan indien nodig"
    read -p "Druk op ENTER om .env te bewerken (of Ctrl+C om over te slaan)..."
    ${EDITOR:-nano} .env
else
    print_success ".env bestaat al"
fi

# Stap 4: Test installatie
print_status "Testen installatie..."
if $PYTHON_CMD main.py test; then
    print_success "Alle tests geslaagd!"
else
    print_error "Tests gefaald. Check de output hierboven."
    exit 1
fi

# Stap 5: Download model (optioneel)
read -p "Wil je het RoboBrain model nu downloaden? (~20GB) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Model wordt gedownload bij eerste gebruik..."
    print_warning "Dit kan 10-30 minuten duren afhankelijk van je internet"
fi

# Stap 6: Systemd service (optioneel)
if command -v systemctl &> /dev/null; then
    read -p "Wil je een systemd service installeren voor auto-start? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installeren systemd service..."

        # Maak service file
        SERVICE_FILE="/etc/systemd/system/personalai.service"
        sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=PersonalAI Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python main.py telegram
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable personalai.service
        print_success "Systemd service geïnstalleerd"
        print_status "Start met: sudo systemctl start personalai"
        print_status "Status check: sudo systemctl status personalai"
        print_status "Logs bekijken: sudo journalctl -u personalai -f"
    fi
fi

# Stap 7: Firewall (indien web interface)
read -p "Wil je de web interface gebruiken? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v ufw &> /dev/null; then
        read -p "Firewall port 7860 openen voor web interface? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo ufw allow 7860/tcp
            print_success "Port 7860 geopend in firewall"
        fi
    fi
fi

# Deployment summary
echo ""
echo "╔═══════════════════════════════════════╗"
echo "║     Deployment Succesvol! 🎉          ║"
echo "╚═══════════════════════════════════════╝"
echo ""
print_success "PersonalAI is klaar voor productie!"
echo ""
echo "📋 Volgende stappen:"
echo ""
echo "1️⃣  Configureer .env met je Telegram token:"
echo "   nano .env"
echo ""
echo "2️⃣  Start Telegram bot:"
echo "   python main.py telegram"
echo ""
echo "   OF start web interface:"
echo "   python main.py web"
echo ""
echo "3️⃣  Test met je Telegram bot of browse naar:"
echo "   http://localhost:7860"
echo ""
if [ "$HAS_GPU" = true ]; then
    echo "✅ GPU gedetecteerd - optimale performance!"
else
    echo "⚠️  Geen GPU - overweeg cloud deployment met GPU"
fi
echo ""
echo "📚 Meer info: cat README.md"
echo "🔧 Status check: python main.py status"
echo ""
echo "Veel plezier met PersonalAI! 🚀"
