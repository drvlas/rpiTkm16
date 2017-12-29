#!/usr/bin/python3

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal


class QLineEditFocus(QLineEdit):
    focusIn = pyqtSignal()
    focusOut = pyqtSignal()

    def __init__(self, parent=None):
        super(QLineEditFocus, self).__init__(parent)
         
    # def focusInEvent(self, event):
    #     print('This widget is in focus')
    #     self.focusIn.emit()
    #     QLineEdit.focusInEvent(self, event)
    #
    # def focusOutEvent(self, event):
    #     print('This widget lost focus')
    #     self.focusOut.emit()
    #     QLineEdit.focusOutEvent(self, event)

    # # Returns True if left key pressed ?????
    # def mousePressEvent(self, event):
    #     print('This widget got mouse pressed')
    #     super(QLineEditFocus, self).mousePressEvent(event)
    #     if event.button() == QLineEdit.LeftButton:
    #         #self.emit(SIGNAL("mousePressed()"))

    # def returnPressedEvent() - is a standard QLineEdit method, emits a
    # 'returnPressed' signal. So I don't need to redefine it here
