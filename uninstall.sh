#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

LANG_ENV="${LC_ALL:-${LANG:-en_US}}"
if [[ "${LANG_ENV,,}" == it* ]]; then
    IS_IT=true
else
    IS_IT=false
fi

if [ "$IS_IT" = true ]; then
    MSG_TITLE="=== cmdsec Uninstaller ==="
    MSG_REMOVED="[OK] Rimosso %s"
    MSG_SUCCESS="[SUCCESS] cmdsec è stato completamente disinstallato dal sistema."
else
    MSG_TITLE="=== cmdsec Uninstaller ==="
    MSG_REMOVED="[OK] Removed %s"
    MSG_SUCCESS="[SUCCESS] cmdsec has been completely uninstalled from your system."
fi

echo -e "${CYAN}${MSG_TITLE}${NC}\n"

BIN_FILE="$HOME/.local/bin/cmdsec"
INSTALL_DIR="$HOME/.local/share/cmdsec"

if [ -f "$BIN_FILE" ]; then
    rm -f "$BIN_FILE"
    echo -e "${GREEN}$(printf "$MSG_REMOVED" "$BIN_FILE")${NC}"
fi

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}$(printf "$MSG_REMOVED" "$INSTALL_DIR")${NC}"
fi

echo -e "\n${GREEN}${MSG_SUCCESS}${NC}"
