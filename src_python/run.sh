#!/bin/bash
# HCI Gesture Control Run Script
# Bu script extension tarafindan çağrilir ve environment variables ile ayarlari alir

source /home/kaplan/anaconda3/etc/profile.d/conda.sh
conda activate base
cd "$(dirname "$0")"

# Extension'dan gelen environment variables'lari logla
echo "HCI Gesture Control başlatiliyor..."
echo "Tarih: $(date)"
echo "Çalişma dizini: $(pwd)"

# Environment variables'lari kontrol et ve varsayilanlari ayarla
export HCI_TUTORIAL_MODE="${HCI_TUTORIAL_MODE:-false}"
export HCI_SAFE_MODE="${HCI_SAFE_MODE:-true}"
export HCI_AUTO_CALIBRATE="${HCI_AUTO_CALIBRATE:-true}"
export HCI_SMOOTHING_FACTOR="${HCI_SMOOTHING_FACTOR:-0.3}"
export HCI_PINCH_THRESHOLD="${HCI_PINCH_THRESHOLD:-0.05}"
export HCI_CONFIDENCE_MINIMUM="${HCI_CONFIDENCE_MINIMUM:-0.7}"
export HCI_CLICK_COOLDOWN="${HCI_CLICK_COOLDOWN:-0.3}"
export HCI_CAMERA_INDEX="${HCI_CAMERA_INDEX:-0}"
export HCI_CAMERA_FPS="${HCI_CAMERA_FPS:-30}"
export HCI_SHOW_NOTIFICATIONS="${HCI_SHOW_NOTIFICATIONS:-true}"
export HCI_LOG_LEVEL="${HCI_LOG_LEVEL:-INFO}"
export HCI_DEBUG_MODE="${HCI_DEBUG_MODE:-false}"

echo "   Ayarlar:"
echo "   Tutorial Mode: $HCI_TUTORIAL_MODE"
echo "   Safe Mode: $HCI_SAFE_MODE"
echo "   Auto Calibrate: $HCI_AUTO_CALIBRATE"
echo "   Smoothing: $HCI_SMOOTHING_FACTOR"
echo "   Camera: $HCI_CAMERA_INDEX @ ${HCI_CAMERA_FPS}fps"
echo "   Confidence: $HCI_CONFIDENCE_MINIMUM"
echo "   Log Level: $HCI_LOG_LEVEL"

# Gerekli dizinleri oluştur
mkdir -p logs

# Python script'i başlat
echo "Python script başlatiliyor..."
python3 -u "src/main.py" 2>&1 | tee "logs/hci_service.log"

# Exit kodunu yakala
EXIT_CODE=$?
echo "HCI Gesture Control durdu (exit code: $EXIT_CODE)"

exit $EXIT_CODE