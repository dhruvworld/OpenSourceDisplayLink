#!/bin/bash
# Dev launcher for OpenSourceDisplayLink (macOS version)

osascript -e 'tell application "Terminal" to do script "cd $(pwd) && source venv/bin/activate && python3 server/main.py"'
sleep 1
osascript -e 'tell application "Terminal" to do script "cd $(pwd) && source venv/bin/activate && python3 client/python/gui.py"'
