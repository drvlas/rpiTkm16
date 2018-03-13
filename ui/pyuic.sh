#!/bin/bash
echo "Compile ui to .py"
pyuic5 -x qt_window.ui -o qt_window.py
pyuic5 -x qt_numpad.ui -o qt_numpad.py
echo "The end!"
sleep 1s
