#!/bin/bash
echo "Compile mainWindow.ui file to Python mainWindow.py"
pyuic5 mainWindow.ui -o mainWindow.py
echo "The end!"
echo ""

