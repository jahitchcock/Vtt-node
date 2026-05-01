#!/usr/bin/env bash
# =============================================================================
# VTT-Node | bootstrap.sh
# First-time setup wizard. Run once to configure and launch VTT-Node.
# =============================================================================

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

header() { echo -e "\n${BOLD}${BLUE}$1${NC}"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn()    { echo -e "${YELLOW}⚠${NC}  $1"; }
error()   { echo -e "${RED}✗${NC}  $1"; }
ask()     { echo -e "${CYAN}?${NC}  $1"; }

# =============================================================================
# BANNER
# =============================================================================
clear
echo -e "${BOLD}"
cat << 'EOF'
 _   _____________   _   _           _
| | | |_   _|_   _| | \ | |         | |
| | | | | |   | |   |  \| | ___   __| | ___
| | | | | |   | |   | . ` |/ _ \ / _` |/ _ \
\ \_/ / | |  _| |_  | |\  | (_) | (_| |  __/
 \___/  \_/  \___/  \_| \_/\___/ \__,_|\___|

  Private Cloud VTT — Zero Config Self-Hosting
  ─────────────────────────────────────────────
EOF
echo -e "${NC}"

# =============================================================================
# PREFLIGHT CHECKS
# =============================================================================
header "[ 1/5 ] Checking dependencies..."

check_cmd() {
    if command -v "$1" &>/dev/null; then
        success "$1 found ($(command -v "$1"))"
    else
        error "$1 not found. Please install it first."
        echo "    → $2"
        exit 1
    fi
}

check_cmd docker      "https://docs.docker.com/get-docker/"
check_cmd "docker compose" "Included with Docker Desktop; 'docker-compose-plugin' on Linux"
check_cmd curl        "sudo apt install curl / brew install curl"

DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
success "Docker ${DOCKER_VERSION}"

# Check Docker is running
if ! docker info &>/dev/null; then
    error "Docker daemon is not running. Start Docker and try again."
    exit 1
fi
success "Docker daemon is running"

# =============================================================================
# ENGINE SELECTION
# =============================================================================
header "[ 2/5 ] Choose your VTT engine"
echo ""
echo "  ${BOLD}[1] Foundry VTT${NC} (recommended)"
echo "      → The best self-hosted VTT. Requires a \$50 license from foundryvtt.com"
echo "      → Massive module ecosystem, best-in-class lighting & automation"
echo ""
echo "  ${BOLD}[2] MapTool${NC} (free & open source)"
echo "      → 100% free, AGPLv3, no license needed"
echo "      → Great for groups who don't own Foundry"
echo "      → Accessed via browser (noVNC) or the MapTool desktop client"
echo ""

while true; do
    ask "Select engine [1/2]:"
    read -r ENGINE_CHOICE
    case $ENGINE_CHOICE in
        1) VTT_ENGINE=foundry;  ENGINE_FILE="engines/foundry.yml";  break ;;
        2) VTT_ENGINE=maptool;  ENGINE_FILE="engines/maptool.yml";  break ;;
        *) warn "Please enter 1 or 2" ;;
    esac
done
success "Engine: ${BOLD}${VTT_ENGINE}${NC}"

# =============================================================================
# .ENV SETUP
# =============================================================================
header "[ 3/5 ] Configuring environment"

if [ ! -f ".env" ]; then
    cp .env.example .env
    success "Created .env from template"
else
    warn ".env already exists — skipping copy (edit manually if needed)"
fi

# Set engine in .env
sed -i.bak "s/^VTT_ENGINE=.*/VTT_ENGINE=${VTT_ENGINE}/" .env && rm -f .env.bak
success "VTT_ENGINE set to ${VTT_ENGINE}"

# --- Shared prompts ---
echo ""
ask "Enter your timezone (e.g. America/New_York) [UTC]:"
read -r TZ_INPUT
TZ_INPUT="${TZ_INPUT:-UTC}"
sed -i.bak "s|^TZ=.*|TZ=${TZ_INPUT}|" .env && rm -f .env.bak

echo ""
echo "  Generating API secret key..."
API_SECRET=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-f0-9' | head -c 64)
sed -i.bak "s/^VTT_UI_SECRET=.*/VTT_UI_SECRET=${API_SECRET}/" .env && rm -f .env.bak
success "API secret key generated"

# --- Engine-specific prompts ---
if [ "$VTT_ENGINE" = "foundry" ]; then
    echo ""
    warn "Foundry VTT requires a purchased license (https://foundryvtt.com)"
    echo ""

    ask "Foundry username (foundryvtt.com account):"
    read -r FU; sed -i.bak "s/^FOUNDRY_USERNAME=.*/FOUNDRY_USERNAME=${FU}/" .env && rm -f .env.bak

    ask "Foundry password:"
    read -rs FP; echo
    sed -i.bak "s/^FOUNDRY_PASSWORD=.*/FOUNDRY_PASSWORD=${FP}/" .env && rm -f .env.bak

    ask "Foundry license key (XXXX-XXXX-XXXX-XXXX-XXXX-XXXX):"
    read -r FK; sed -i.bak "s/^FOUNDRY_LICENSE_KEY=.*/FOUNDRY_LICENSE_KEY=${FK}/" .env && rm -f .env.bak

    ask "Admin password for Foundry setup screen:"
    read -rs FAK; echo
    # Hash it using Node.js if available, otherwise warn to set manually
    if command -v node &>/dev/null; then
        HASHED=$(node -e "const crypto=require('crypto');console.log(crypto.createHash('sha512').update('${FAK}').digest('hex'));")
        sed -i.bak "s/^FOUNDRY_ADMIN_KEY=.*/FOUNDRY_ADMIN_KEY=${HASHED}/" .env && rm -f .env.bak
        success "Admin password hashed and saved"
    else
        warn "Node.js not found — set FOUNDRY_ADMIN_KEY manually in .env (must be SHA-512 hash)"
    fi

elif [ "$VTT_ENGINE" = "maptool" ]; then
    echo ""
    ask "Campaign server name [VTT-Node Campaign]:"
    read -r MT_NAME; MT_NAME="${MT_NAME:-VTT-Node Campaign}"
    sed -i.bak "s/^MT_SERVER_NAME=.*/MT_SERVER_NAME=${MT_NAME}/" .env && rm -f .env.bak

    ask "Player join password (leave blank for open server):"
    read -rs MT_PASS; echo
    sed -i.bak "s/^MT_SERVER_PASSWORD=.*/MT_SERVER_PASSWORD=${MT_PASS}/" .env && rm -f .env.bak

    ask "GM password [REQUIRED]:"
    read -rs MT_GM; echo
    sed -i.bak "s/^MT_GM_PASSWORD=.*/MT_GM_PASSWORD=${MT_GM}/" .env && rm -f .env.bak
fi

# --- Cloudflare tunnel ---
echo ""
ask "Cloudflare Tunnel token (leave blank to skip — use port 80 locally):"
read -r CF_TOKEN
if [ -n "$CF_TOKEN" ]; then
    sed -i.bak "s/^CLOUDFLARE_TUNNEL_TOKEN=.*/CLOUDFLARE_TUNNEL_TOKEN=${CF_TOKEN}/" .env && rm -f .env.bak
    success "Cloudflare tunnel configured"
else
    warn "No tunnel token — VTT will be accessible on http://localhost only"
    warn "Add CLOUDFLARE_TUNNEL_TOKEN to .env when ready for public access"
fi

# =============================================================================
# BUILD & PULL
# =============================================================================
header "[ 4/5 ] Pulling images..."

if [ "$VTT_ENGINE" = "maptool" ]; then
    echo "  Building MapTool container (first run takes a few minutes)..."
    docker compose -f docker-compose.yml -f "$ENGINE_FILE" build vtt-engine
fi

docker compose -f docker-compose.yml -f "$ENGINE_FILE" pull --ignore-buildable
success "Images ready"

# =============================================================================
# LAUNCH
# =============================================================================
header "[ 5/5 ] Starting VTT-Node..."

docker compose -f docker-compose.yml -f "$ENGINE_FILE" up -d

echo ""
echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  VTT-Node is running!${NC}"
echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  VTT URL (local)  →  ${BOLD}http://localhost${NC}"
if [ -n "${CF_TOKEN:-}" ]; then
echo -e "  VTT URL (public) →  ${BOLD}Check your Cloudflare dashboard${NC}"
fi
echo -e "  Dashboard        →  ${BOLD}http://localhost/vtt-node/${NC}"
if [ "$VTT_ENGINE" = "maptool" ]; then
echo -e "  VNC (GM access)  →  ${BOLD}localhost:5900${NC}"
fi
echo ""
echo -e "  Useful commands:"
echo -e "  ${CYAN}docker compose -f docker-compose.yml -f ${ENGINE_FILE} logs -f${NC}"
echo -e "  ${CYAN}docker compose -f docker-compose.yml -f ${ENGINE_FILE} down${NC}"
echo ""
echo -e "  Full docs → ${BOLD}https://vtt-node.io/docs${NC}"
echo ""
