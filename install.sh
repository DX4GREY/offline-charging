#!/bin/bash
# ==============================================================================
# Installer for Offline Charging Mode (Mobile Linux / SDM845 / Poco F1)
# ==============================================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}   Offline Charging Mode Installer for Mobile Linux   ${NC}"
echo -e "${BLUE}======================================================${NC}"

# 1. Check Root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo ./install.sh)${NC}"
    exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 2. Check Dependencies
echo -e "\n${YELLOW}[1/5] Checking dependencies...${NC}"
MISSING_PKGS=()

if ! command -v python3 &>/dev/null; then
    MISSING_PKGS+=("python3")
fi

if ! python3 -c "import cairo" &>/dev/null; then
    MISSING_PKGS+=("python3-cairo")
fi

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing dependencies: ${MISSING_PKGS[*]}...${NC}"
    apt-get update -qq && apt-get install -y -qq "${MISSING_PKGS[@]}"
else
    echo -e "${GREEN}All dependencies satisfied (python3, python3-cairo).${NC}"
fi

# 3. Install Daemon Binary
echo -e "\n${YELLOW}[2/5] Installing daemon binary...${NC}"
install -m 755 "${REPO_DIR}/bin/offline-charger" /usr/local/bin/offline-charger
echo -e "${GREEN}Installed to /usr/local/bin/offline-charger${NC}"

# 4. Install Systemd Units
echo -e "\n${YELLOW}[3/5] Installing systemd target and service...${NC}"
install -m 644 "${REPO_DIR}/systemd/offline-charger.service" /etc/systemd/system/offline-charger.service
install -m 644 "${REPO_DIR}/systemd/charger.target" /etc/systemd/system/charger.target
echo -e "${GREEN}Installed units to /etc/systemd/system/${NC}"

# 5. Install Systemd Generator
echo -e "\n${YELLOW}[4/5] Installing systemd boot interceptor generator...${NC}"
mkdir -p /etc/systemd/system-generators
install -m 755 "${REPO_DIR}/systemd/charger-mode-generator" /etc/systemd/system-generators/charger-mode-generator
echo -e "${GREEN}Installed generator to /etc/systemd/system-generators/${NC}"

# 6. Reload Systemd and Enable Service
echo -e "\n${YELLOW}[5/5] Reloading systemd and enabling service...${NC}"
systemctl daemon-reload
systemctl enable offline-charger.service

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}   Offline Charging Mode Successfully Installed!     ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "How it works:"
echo -e " 1. Turn off your device completely."
echo -e " 2. Connect the charger cable."
echo -e " 3. The device will boot into minimal Offline Charging Mode."
echo -e " 4. Hold Power key for 3 seconds to boot into full OS anytime."
echo -e " 5. Disconnect cable to power off automatically."
echo
