#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Програма для запуску на Малинці
    26.12.2017
"""
import logging
import sys

# from PyQt5 import uic
from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMenu

# My modules
from mainWindow import Ui_MainWindow
"""
    УВАГА! Зараз запуску з аргументами нема. Тому треба ручками задати тип плати і debug mode
"""

logging.basicConfig(level=logging.INFO)

bauds = ['2400', '4800', '9600', '14400', '19200', '28800', '38400', '57600', '76800', '115200']
ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', 'COM1', 'COM2']
pointFormat7 = {
            0: ('{: 07.0f}', 1),
            1: ('{: 07.1f}', 0.1),
            2: ('{: 07.2f}', 0.01),
            3: ('{: 07.3f}', 0.001),
        }
point = 1

class Main(QMainWindow, Ui_MainWindow):  # uic.loadUiType("adc_main_form.ui")[0]):
    def __init__(self):
        super(Main, self).__init__()
        # Set up the user interface from Designer.
        self.setupUi(self)      # інакше не розуміє атрібуту statusBar...
        # QMetaObject.connectSlotsByName(self)
        # self.ui_stopped = False
        self.port_opened = False
        self.port = '/dev/ttyUSB0'      # Default Linux port name
        self.slave = 1
        self.baud = 38400
        self.refresh = QTimer()             # refresh.singleShot() is used for update data rate
        self.status_freeze_timer = QTimer()
        self.status2freeze = False
        self.inpBin = ()
        self.requests_stopped = False   # During port setting dialog request are stopped
        # self.ui_stopped = False
        self.io = None
        self.modbusCount = 0
        self.update_data()              # почнеться з adc_io.ModbusChannel()

    def on_action_Port_triggered(self):               # toolbar: 'Port' key
        self.requests_stopped = True
        p, ok = QInputDialog.getItem(self, 'Input Dialog', 'Enter or choose port name:', ports)
        if ok:
            self.port = str(p)      # because p is QtCore.QString(u'/dev/ttyUSB0')
        self.port_opened = False    # ModbusChannel may be reopened
        self.requests_stopped = False
        self.update_data()

    def on_action_Slave_ID_triggered(self):               # toolbar: 'Slave' key
        self.requests_stopped = True
        s, ok = QInputDialog.getInt(self, 'Input Dialog', 'Enter Slave ID (1..247):', 1, 1, 247)
        if ok:
            self.slave = s
        self.port_opened = False    # ModbusChannel may be reopened even if no new sl.ID entered
        self.requests_stopped = False
        self.update_data()

    def on_action_Baudrate_triggered(self):               # toolbar: 'Baud' key
        self.requests_stopped = True
        b, ok = QInputDialog.getItem(self, 'Input Dialog', 'Enter baud rate:', bauds)
        if ok:
            self.baud = int(b)
        self.port_opened = False    # ModbusChannel may be reopened even if no new baud entered
        self.requests_stopped = False
        self.update_data()          # ..e.g. we just want to reopen port manually

    def on_action_Quit_triggered(self):
        # ModbusChannel.close(self.io)
        self.close()

    # def on_action_Modify_triggered(self):
    #     self.ui_stopped = True

    def resumeRefresh(self): pass

    def stopRefresh(self): pass
    
    def update_data(self):
        if self.requests_stopped:
            self.refresh.singleShot(400, self.update_data)
            return                  # To allow dialogs run undisturbed
        # This text will begin the status line
        tx0 = 'Port: {:s}, SlaveID: {:d}, Baud: {:d}  {:d}'.format(self.port, self.slave,
                                                                     self.baud, self.modbusCount)
        self.status_refresh(tx0)
        self.refresh.singleShot(300, self.update_data)
        self.morda("Hello, World!")     # Абсолютно штучно виділив усе малювання морди, щоби логіка
                                    # самого update_data була більш прозорою

    def morda(self, txt):                # Це, по суті, просто шматок (закінчення) update_data()
        #self.label.setText(txt)
        self.modbusCount += 1

    def freeze_status(self, msg):
        self.status2freeze = True
        self.status_freeze_timer.singleShot(4000, self.defreeze_status)
        #self.statusBar.showMessage(msg)

    def defreeze_status(self):
        self.status2freeze = False

    def status_refresh(self, msg):
        if self.status2freeze:
            return
        if msg.lower() == 'ok':
            msg += 'Port: {:s}, SlaveID: {:d}, baud: {:d}'.format(self.port, self.slave, self.baud)
            self.statusbar.showMessage(msg)
        else:
            self.statusbar.showMessage(msg)
            self.statusbar.color = 'red'

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    # QMetaObject.connectSlotsByName(window)
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
