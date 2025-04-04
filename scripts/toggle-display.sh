#!/bin/bash

CONFIG_FILE="shared/config.py"

if grep -q "USE_EXTENDED_DISPLAY = True" "$CONFIG_FILE"; then
    sed -i '' 's/USE_EXTENDED_DISPLAY = True/USE_EXTENDED_DISPLAY = False/' "$CONFIG_FILE"
    echo "Switched to MAIN display"
else
    sed -i '' 's/USE_EXTENDED_DISPLAY = False/USE_EXTENDED_DISPLAY = True/' "$CONFIG_FILE"
    echo "Switched to EXTENDED display"
fi
