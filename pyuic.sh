#!/bin/bash
echo "Compile mainWindow.ui file to Python mainWindow.py"
pyuic5 -x mainWindow.ui -o mainWindow.py
pyuic5 -x numPad.ui -o numPad.py
echo "The end!"
echo ""
sleep 2s
