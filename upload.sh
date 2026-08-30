#!/usr/bin/env bash
set -e

SERVER_URL="${SERVER_URL:-https://cdn-ascp.vercel.app}"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# Username
DETECTED_USER=""
if command -v git &>/dev/null; then
    DETECTED_USER=$(git config --get user.name || git config --get github.user || true)
    if [ -z "$DETECTED_USER" ]; then
        GIT_EMAIL=$(git config --get user.email || true)
        DETECTED_USER="${GIT_EMAIL%%@*}"
    fi
fi

if [ -z "$DETECTED_USER" ]; then
    DETECTED_USER="$USER"
fi

DETECTED_USER=$(echo "$DETECTED_USER" | tr -d ' ' | tr '[:upper:]' '[:lower:]')

if [ -n "$DETECTED_USER" ]; then
    USERNAME="$DETECTED_USER"
    echo -e "Maintainer Username: ${BOLD}${USERNAME}${NC}"
else
    read -rp "GitHub Maintainer Username: " USERNAME
fi

if [ -z "$USERNAME" ]; then
    echo -e "${RED}Error: Username cannot be empty.${NC}"
    exit 1
fi

# Codename
TARGET_FILE="$1"
DETECTED_CODENAME=""

if [ -n "$TARGET_FILE" ]; then
    FILENAME=$(basename "$TARGET_FILE")
    if [[ "$TARGET_FILE" =~ out/target/product/([^/]+)/ ]]; then
        DETECTED_CODENAME="${BASH_REMATCH[1]}"
    elif [[ "$FILENAME" =~ ASCP-[^-]+-([^-]+)- ]]; then
        DETECTED_CODENAME="${BASH_REMATCH[1]}"
    fi
else
    if [ -d "out/target/product" ]; then
        FOUND_DIRS=($(find out/target/product -mindepth 1 -maxdepth 1 -type d 2>/dev/null || true))
        if [ ${#FOUND_DIRS[@]} -eq 1 ]; then
            DETECTED_CODENAME=$(basename "${FOUND_DIRS[0]}")
        elif [ ${#FOUND_DIRS[@]} -gt 1 ]; then
            for dir in "${FOUND_DIRS[@]}"; do
                if find "$dir" -maxdepth 2 -type f -name "*.zip" 2>/dev/null | grep -v "otacerts.zip" | grep -q .; then
                    DETECTED_CODENAME=$(basename "$dir")
                    break
                fi
            done
        fi
    fi
fi

if [ -n "$DETECTED_CODENAME" ]; then
    CODENAME="$DETECTED_CODENAME"
    echo -e "Device Codename: ${BOLD}${CODENAME}${NC}"
else
    read -rp "Enter Device Codename (e.g., alioth): " CODENAME
fi

CODENAME=$(echo "$CODENAME" | tr -d ' ' | tr '[:upper:]' '[:lower:]')
if [ -z "$CODENAME" ]; then
    echo -e "${RED}Error: Device codename cannot be empty.${NC}"
    exit 1
fi

# Scan for Build Files
if [ -z "$TARGET_FILE" ]; then
    SEARCH_DIR="out/target/product/${CODENAME}"
    if [ -d "$SEARCH_DIR" ]; then
        echo -e "${YELLOW}Scanning for .zip build files in ${SEARCH_DIR}...${NC}"
        ZIP_FILES=($(find "$SEARCH_DIR" -maxdepth 2 -type f -name "*.zip" 2>/dev/null | grep -v "otacerts.zip" || true))
    else
        echo -e "${YELLOW}Scanning for .zip build files...${NC}"
        ZIP_FILES=($(find . -maxdepth 3 -type f -name "*.zip" 2>/dev/null | grep -v "/\.git/" | grep -v "otacerts.zip" || true))
    fi

    if [ ${#ZIP_FILES[@]} -eq 0 ]; then
        echo -e "${RED}Error: No .zip files found for device '${CODENAME}'${NC}"
        read -rp "Please enter file path manually: " TARGET_FILE
    elif [ ${#ZIP_FILES[@]} -eq 1 ]; then
        TARGET_FILE="${ZIP_FILES[0]}"
        echo -e "Found build file: ${GREEN}${TARGET_FILE}${NC}"
    else
        echo -e "${BOLD}Multiple .zip files detected for ${CODENAME}:${NC}"
        for i in "${!ZIP_FILES[@]}"; do
            echo -e "  [${GREEN}$((i+1))${NC}] ${ZIP_FILES[$i]}"
        done
        read -rp "Select file number [1-${#ZIP_FILES[@]}]: " CHOICE
        INDEX=$((CHOICE - 1))
        TARGET_FILE="${ZIP_FILES[$INDEX]}"
    fi
fi

if [ ! -f "$TARGET_FILE" ]; then
    echo -e "${RED}Error: File not found: $TARGET_FILE${NC}"
    exit 1
fi

FILENAME=$(basename "$TARGET_FILE")
FILESIZE=$(du -h "$TARGET_FILE" | cut -f1)
echo -e "Selected File: ${BOLD}${FILENAME}${NC} (${FILESIZE})"

# Password
read -s -rp "Enter Password for @${USERNAME}: " PASSWORD
echo ""

if [ -z "$PASSWORD" ]; then
    echo -e "${RED}Error: Password cannot be empty.${NC}"
    exit 1
fi

# Uploading
SERVER_BASE="${SERVER_URL%/}"
UPLOAD_ENDPOINT="${SERVER_BASE}/upload/${CODENAME}"

echo -e "\n${BOLD}${CYAN}Uploading ${FILENAME} to ${UPLOAD_ENDPOINT}...${NC}"

HTTP_RESPONSE=$(curl -# \
    -u "${USERNAME}:${PASSWORD}" \
    -F "file=@${TARGET_FILE}" \
    "${UPLOAD_ENDPOINT}")

echo -e "\n${GREEN}${BOLD}Server Response:${NC}"
echo "$HTTP_RESPONSE"
