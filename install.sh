#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

LANG_ENV="${LC_ALL:-${LANG:-en_US}}"
if [[ "${LANG_ENV,,}" == it* ]]; then
    IS_IT=true
else
    IS_IT=false
fi

if [ "$IS_IT" = true ]; then
    MSG_TITLE="=== cmdsec Installer ==="
    MSG_NO_PYTHON="[ERROR] Python 3 non è installato. Installa Python 3 e riprova."
    MSG_NO_KEY_ENV="GEMINI_API_KEY non trovata nell'ambiente."
    MSG_PROMPT_KEY="Inserisci la tua Google Gemini API Key: "
    MSG_NO_KEY_INPUT="[ERROR] Chiave API non fornita. L'installazione non può proseguire."
    MSG_CREATING_VENV="Creazione ambiente virtuale Python (venv)..."
    MSG_VENV_ERROR="[ERROR] Impossibile creare l'ambiente virtuale python3 -m venv."
    MSG_VENV_DEBIAN="Su distribuzioni basate su Debian/Ubuntu, esegui:"
    MSG_VENV_ARCH="Su distribuzioni basate su Arch/EndeavourOS, assicurati di avere python installato."
    MSG_INSTALLING_DEPS="Installazione dipendenze isolata in venv..."
    MSG_SUCCESS="[SUCCESS] cmdsec installato con successo in"
    MSG_PATH_NOTE="[NOTE] '%s' non sembra essere nel tuo PATH."
    MSG_PATH_ADD="Aggiungi la seguente riga al tuo file di configurazione (~/.bashrc o ~/.zshrc):"
    MSG_RUN_HINT="Puoi avviare il tool digitando:"
else
    MSG_TITLE="=== cmdsec Installer ==="
    MSG_NO_PYTHON="[ERROR] Python 3 is not installed. Please install Python 3 and try again."
    MSG_NO_KEY_ENV="GEMINI_API_KEY not found in environment."
    MSG_PROMPT_KEY="Enter your Google Gemini API Key: "
    MSG_NO_KEY_INPUT="[ERROR] API key not provided. Installation cannot continue."
    MSG_CREATING_VENV="Creating isolated Python virtual environment (venv)..."
    MSG_VENV_ERROR="[ERROR] Could not create python3 -m venv virtual environment."
    MSG_VENV_DEBIAN="On Debian/Ubuntu based distributions, run:"
    MSG_VENV_ARCH="On Arch/EndeavourOS based distributions, make sure python is installed."
    MSG_INSTALLING_DEPS="Installing dependencies inside venv..."
    MSG_SUCCESS="[SUCCESS] cmdsec installed successfully at"
    MSG_PATH_NOTE="[NOTE] '%s' does not seem to be in your PATH."
    MSG_PATH_ADD="Add the following line to your shell config file (~/.bashrc or ~/.zshrc):"
    MSG_RUN_HINT="You can launch the tool by typing:"
fi

echo -e "${CYAN}${MSG_TITLE}${NC}\n"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}${MSG_NO_PYTHON}${NC}"
    exit 1
fi

API_KEY="${GEMINI_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}${MSG_NO_KEY_ENV}${NC}"
    echo -n "$MSG_PROMPT_KEY"
    read -r API_KEY
    if [ -z "$API_KEY" ]; then
        echo -e "${RED}${MSG_NO_KEY_INPUT}${NC}"
        exit 1
    fi
fi

INSTALL_DIR="$HOME/.local/share/cmdsec"
BIN_DIR="$HOME/.local/bin"
VENV_DIR="$INSTALL_DIR/venv"

mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo -e "\n${CYAN}${MSG_CREATING_VENV}${NC}"
if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
    echo -e "${RED}${MSG_VENV_ERROR}${NC}"
    echo -e "${YELLOW}${MSG_VENV_DEBIAN}${NC}"
    echo -e "  sudo apt update && sudo apt install python3-venv python3-full"
    echo -e "${YELLOW}${MSG_VENV_ARCH}${NC}"
    exit 1
fi

echo -e "${CYAN}${MSG_INSTALLING_DEPS}${NC}"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip 2>/dev/null || true
"$VENV_DIR/bin/pip" install --quiet google-genai pydantic colorama distro

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    cp "$SCRIPT_DIR/main.py" "$INSTALL_DIR/main.py" 2>/dev/null || true
    if [ -f "$SCRIPT_DIR/uninstall.sh" ]; then
        cp "$SCRIPT_DIR/uninstall.sh" "$INSTALL_DIR/uninstall.sh" 2>/dev/null || true
    fi
fi

LAUNCHER="$BIN_DIR/cmdsec"

cat << EOF > "$LAUNCHER"
#!/usr/bin/env bash
# cmdsec executable launcher
export GEMINI_API_KEY="$API_KEY"
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/main.py" "\$@"
EOF

chmod +x "$LAUNCHER"

echo -e "\n${GREEN}${MSG_SUCCESS} $LAUNCHER!${NC}"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "\n${YELLOW}$(printf "$MSG_PATH_NOTE" "$BIN_DIR")${NC}"
    echo -e "$MSG_PATH_ADD"
    echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
fi

echo -e "\n$MSG_RUN_HINT ${GREEN}cmdsec${NC}"
