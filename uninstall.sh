#!/bin/bash
# ==============================================================================
# Uninstaller for Offline Charging Mode
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Uninstalling Offline Charging Mode...${NC}"

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo ./uninstall.sh)${NC}"
    exit 1
fi

# Stop and disable service
if systemctl is-active --quiet offline-charger.service; then
    systemctl stop offline-charger.service || true
fi
systemctl disable offline-charger.service 2>/dev/null || true

# Remove installed files
rm -f /usr/local/bin/offline-charger
rm -f /etc/systemd/system/offline-charger.service
rm -f /etc/systemd/system/charger.target
rm -f /etc/systemd/system-generators/charger-mode-generator
rm -rf /etc/systemd/system/charger.target.wants

# Reload systemd
systemctl daemon-reload

echo -e "${GREEN}Offline Charging Mode has been completely removed.${NC}"
