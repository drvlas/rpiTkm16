#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Програма для роботи з тензоАЦП-ПЛК TKM.99.01.14 (brd14)
    Проект CLion/brd14c2, замість ИП320 ставлю ПК
    12.12.2017
"""
import logging
import sys
from sys import platform

# from PyQt5 import uic
from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMenu

# My modules
from mainWindow import Ui_MainWindow
"""
    УВАГА! Зараз запуску з аргументами нема. Тому треба ручками задати тип плати і debug mode
"""
from brd14Io import *
from brd14Descriptor import nregs  # ctrl_cmd, adc_bits, adc_rg,  adc_io does not import descriptor

# check me:
print('Read from Map nregs:', nregs)

if platform.startswith('linux'):
    linux = True
else:
    linux = False   # поки що...

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
        self.port = 'COM1'                  # Default Windows port name
        self.slave = 1
        self.baud = 38400
        if linux:
            self.port = '/dev/ttyUSB0'      # Default Linux port name
        if len(sys.argv) > 1:               # Можна змінити ім’я послідовного порту аргументом
            self.port = sys.argv[1]
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
    
    # Main refresh method. Може "сачкувати" у двох випадках:
    #   1) requests_stopped - не робимо ні запитів на АЦП, ні оновлення екрану. Це для того,
    # щоб оперативно працювати з діалоговими вікнами - особливо, коли у модбаса є проблеми
    #   2) ui_stopped - запити до АЦП продовжуємо, щоб АЦП не втрачав зв’язок і не ресетувався,
    # але оновлення екрану зупиняємо, щоб юзер міг ввести нове значення регістру
    # У решті випадків намагається вичитувати усі регістри АЦП і малювати морду.
    # Але, якщо порт не відкритий - намагається його відкрити. І це єдине місце,
    # де відкривається порт.
    #

    def update_data(self):
        if self.requests_stopped:
            self.refresh.singleShot(400, self.update_data)
            return                  # To allow dialogs run undisturbed
        if not self.port_opened:
            self.status_refresh('INFO: Port is not opened. Refreshing stopped')
            try:
                logging.info('update data(): opening port {:s}, baud {:d}'.format(self.port,
                                                                                  self.baud))
                self.io = ModbusChannel(self.port, self.baud)
                self.port_opened = True
            except:
                self.status_refresh('ERROR: Port opening fault')
                self.refresh.singleShot(1000, self.update_data)
                return
        # This text will begin the status line
        tx0 = 'Port: {:s}, SlaveID: {:d}, baudrate: {:d}    count: {:d}.  '.format(self.port, self.slave,
                                                                     self.baud, self.modbusCount)
        txt, self.inpBin = self.io.get_db(self.slave, 0, nregs)
        self.modbusCount += 1
        if 'error' in txt.lower():          # Modbus command execution error (no link?)
            self.status_refresh('{:s}INFO: modbus error: {:s}'.format(tx0, txt))
            self.port_opened = False
            self.refresh.singleShot(2000, self.update_data)  # 2000
            return
        elif 'code' in txt.lower():         # %s- Code=%d
            self.status_refresh('{:s}INFO: modbus error: {:s}'.format(tx0, txt))
            self.port_opened = False
            self.refresh.singleShot(2000, self.update_data)  # 2000
            return
        # From here there is no any error. So default update rate may be set
        # if self.ui_stopped:
        #     self.refresh.singleShot(1000, self.update_data)
        #     self.status_refresh('Refreshing stopped')
        #     return
        if txt is not '':
            self.freeze_status('Error: {:s}'.format(txt))
            self.refresh.singleShot(1000, self.update_data)
            return
        self.status_refresh(tx0)
        self.refresh.singleShot(100, self.update_data)
        self.morda(self.inpBin)     # Абсолютно штучно виділив усе малювання морди, щоби логіка
                                    # самого update_data була більш прозорою

    def morda(self, rg):                # Це, по суті, просто шматок (закінчення) update_data()
        statusRg = rg[adcRg['STAT'][0]]
        ctrlRg = rg[adcRg['CTRL'][0]]
        form = pointFormat7[point][0]
        decimal = pointFormat7[point][1]
        weight = rg[adcRg['WEI16'][0]]
        txt = form.format(weight * decimal)
        self.labelWeight.setText(txt + " kg")
        weight = rg[adcRg['DOZA1'][0]]
        txt = form.format(weight * decimal)
        self.labelWei1Txt.setText("Doza1: " + txt)
        weight = rg[adcRg['DOZA2'][0]]
        txt = form.format(weight * decimal)
        self.labelWei2Txt.setText("Doza2: " + txt)
        weight = rg[adcRg['WEI1'][0]]
        txt = form.format(weight * decimal)
        self.labelWei1.setText(txt + " kg")
        weight = rg[adcRg['WEI2'][0]]
        txt = form.format(weight * decimal)
        self.labelWei2.setText(txt + " kg")

        tare = rg[adcRg['TARE'][0]]
        txt = form.format(tare * decimal)
        self.lineEditTare.setText(txt)
        if tare == 0:
            self.radioButtonTare.setChecked(False)
        else:
            self.radioButtonTare.setChecked(True)
        zero = rg[adcRg['ZERO'][0]]
        txt = form.format(zero * decimal)
        self.lineEditZero.setText(txt)
        if zero == 0:
            self.radioButtonZero.setChecked(False)
        else:
            self.radioButtonZero.setChecked(True)
        self.radioButtonMaster.setChecked(statusRg & adcBit['DOSTUPMSK'])
        self.radioButtonLev0.setChecked(statusRg & adcBit['LEV0MSK'])
        self.radioButtonLev1.setChecked(statusRg & adcBit['LEV1MSK'])
        self.radioButtonLev2.setChecked(statusRg & adcBit['LEV2MSK'])
        self.radioButtonOver.setChecked(statusRg & adcBit['OVERMSK'])
        #self.radioButtonOver.setChecked(True)
        self.radioButtonStab.setChecked(statusRg & adcBit['STABMSK'])
        self.radioButtonFast.setChecked(ctrlRg & adcBit['FASTMSK'])

        self.labelVersVal.setText("{:5d}".format(rg[adcRg['V_SN'][0]]))
        self.lineEditLev0.setText("{:5d} ".format(rg[adcRg['LEV0'][0]]))
        self.lineEditLev1.setText("{:5d} ".format(rg[adcRg['LEV1'][0]]))
        self.lineEditLev2.setText("{:5d} ".format(rg[adcRg['LEV2'][0]]))
        self.lineEditScale.setText("{:5d} ".format(rg[adcRg['SCALE'][0]]))
        self.lineEditStab.setText("{:5d} ".format(rg[adcRg['STAB'][0]]))
        self.labelCashVal.setText("0x{:08X}".format(0xFFFFFFFF & rg[adcRg['CASH'][0]]))
        self.labelTotWVal.setText("{:9d}".format(rg[adcRg['TOTW'][0]]))
        self.labelTotNVal.setText("{:9d}".format(rg[adcRg['TOTN'][0]]))
        self.labelStatusVal.setText("0x{:04x}".format(statusRg))
        self.labelErrorsVal.setText("0x{:04x}".format(rg[adcRg['ERROR'][0]]))
        self.labelPhaseVal.setText("Phase: " + phaseText[rg[adcRg['PHASE'][0]]])
        self.lineEditCtrl.setText("0x{:04X}".format(ctrlRg))
        self.labelDirVal.setText("0x{:04X}".format(rg[adcRg['DIRR'][0]]))
        self.labelDioVal.setText("0x{:04X} / {:05d}".format(rg[adcRg['DIO'][0]], rg[adcRg['DIO'][0]]))
        self.labelFltrVal.setText("{:02d}".format(rg[adcRg['FLTR'][0]]))
        self.labelCycleVal.setText("{:02d}".format(rg[adcRg['CYCLE'][0]]))

        self.lineEditClb0.setText("{:9d}".format(rg[adcRg['CLB0'][0]]))
        self.lineEditClb1.setText("{:9d}".format(rg[adcRg['CLB1'][0]]))
        self.lineEditClb2.setText("{:9d}".format(rg[adcRg['CLB2'][0]]))
        self.lineEditClb3.setText("{:9d}".format(rg[adcRg['CLB3'][0]]))
        self.labelAdcVal.setText("{:9d}".format(rg[adcRg['ADC'][0]]))
        self.lineEditRep0.setText("{:5d}".format(rg[adcRg['REP0'][0]]))
        self.lineEditRep1.setText("{:5d}".format(rg[adcRg['REP1'][0]]))
        self.lineEditRep2.setText("{:5d}".format(rg[adcRg['REP2'][0]]))
        self.lineEditRep3.setText("{:5d}".format(rg[adcRg['REP3'][0]]))
        self.lineEditPcn.setText("{:5d}".format(rg[adcRg['PCSN'][0]]))
        self.lineEditRnd.setText("{:5d}".format(rg[adcRg['ROUND'][0]]))
        self.lineEditRs485.setText("{:5d}".format(rg[adcRg['RS485'][0]]))

        self.lineEditTunld.setText("{:5d}".format(rg[adcRg['TUNLD'][0]]))
        self.lineEditTfeed.setText("{:5d}".format(rg[adcRg['TFEED'][0]]))
        self.lineEditTmeas.setText("{:5d}".format(rg[adcRg['TMEAS'][0]]))
        self.lineEditTbtm.setText("{:5d}".format(rg[adcRg['TBTM'][0]]))
        self.lineEditTdiag.setText("{:5d}".format(rg[adcRg['TDIAG'][0]]))
        self.lineEditTshrt.setText("{:5d}".format(rg[adcRg['TSHRT'][0]]))
        self.lineEditTlong.setText("{:5d}".format(rg[adcRg['TLONG'][0]]))
        self.lineEditTsleep.setText("{:5d}".format(rg[adcRg['TSLP'][0]]))
        self.lineEditTrdy.setText("{:5d}".format(rg[adcRg['TRDY'][0]]))
        self.lineEditTcycle.setText("{:5d}".format(rg[adcRg['TCYCL'][0]]))

        self.lineEditDebounce.setText("{:5d}".format(rg[adcRg['TKEYS'][0]]))
        self.lineEditAuto.setText("{:5d}".format(rg[adcRg['AUTOS'][0]]))
        self.lineEditNskip.setText("{:5d}".format(rg[adcRg['NSKIP'][0]]))
        self.lineEditTareZ.setText("{:5d}".format(rg[adcRg['TARZN'][0]]))

        self.lineEditDoza1.setText("{:5d}".format(rg[adcRg['DOZA1'][0]]))
        self.lineEditDoza2.setText("{:5d}".format(rg[adcRg['DOZA2'][0]]))
        self.lineEditUpr11.setText("{:5d}".format(rg[adcRg['UPR11'][0]]))
        self.lineEditUpr12.setText("{:5d}".format(rg[adcRg['UPR12'][0]]))
        self.lineEditUpr21.setText("{:5d}".format(rg[adcRg['UPR21'][0]]))
        self.lineEditUpr22.setText("{:5d}".format(rg[adcRg['UPR22'][0]]))
        self.lineEditFfa1.setText("{:5d}".format(rg[adcRg['FFA1'][0]]))
        self.lineEditFfa2.setText("{:5d}".format(rg[adcRg['FFA2'][0]]))
        self.lineEditOpen1.setText("{:5d}".format(rg[adcRg['TOPN1'][0]]))
        self.lineEditOpen2.setText("{:5d}".format(rg[adcRg['TOPN2'][0]]))
        self.lineEditTsmin1.setText("{:5d}".format(rg[adcRg['TMIN1'][0]]))
        self.lineEditTsmin2.setText("{:5d}".format(rg[adcRg['TMIN2'][0]]))
        self.lineEditDozz1.setText("{:5d}".format(rg[adcRg['DOZZ1'][0]]))
        self.lineEditDozz2.setText("{:5d}".format(rg[adcRg['DOZZ2'][0]]))

    # def resume(self): self.ui_stopped = False

    # 31 slots for Registers' setting
    def on_pushButtonScale_clicked(self): self.set_new_value('SCALE')
    def on_pushButtonLev2_clicked(self): self.set_new_value('LEV2')
    def on_pushButtonLev1_clicked(self): self.set_new_value('LEV1')
    def on_pushButtonLev0_clicked(self): self.set_new_value('LEV0')
    def on_pushButtonStab_clicked(self): self.set_new_value('STAB')
    def on_pushButtonTotW_clicked(self): self.set_new_value('TOTW')
    def on_pushButtonTotN_clicked(self): self.set_new_value('TOTN')
    def on_pushButtonCtrl_clicked(self): self.set_new_value('CTRL')
    def on_pushButtonRs485_clicked(self): self.set_new_value('RS485')
    def on_pushButtonTare_clicked(self): self.set_new_value('TARE')
    def on_pushButtonZero_clicked(self): self.set_new_value('ZERO')
    def on_pushButtonADC0_clicked(self): self.set_new_value('CLB0')
    def on_pushButtonADC1_clicked(self): self.set_new_value('CLB1')
    def on_pushButtonADC2_clicked(self): self.set_new_value('CLB2')
    def on_pushButtonADC3_clicked(self): self.set_new_value('CLB3')
    def on_pushButtonRep0_clicked(self): self.set_new_value('REP0')
    def on_pushButtonRep1_clicked(self): self.set_new_value('REP1')
    def on_pushButtonRep2_clicked(self): self.set_new_value('REP2')
    def on_pushButtonRep3_clicked(self): self.set_new_value('REP3')
    def on_pushButtonPcn_clicked(self): self.set_new_value('PCSN')
    def on_pushButtonRound_clicked(self): self.set_new_value('UNIT')

    def on_pushButtonTunld_clicked(self): self.set_new_value('TUNLD')
    def on_pushButtonTfeed_clicked(self): self.set_new_value('TFEED')
    def on_pushButtonTmeas_clicked(self): self.set_new_value('TMEAS')
    def on_pushButtonTbtm_clicked(self): self.set_new_value('TBTM')
    def on_pushButtonTdiag_clicked(self): self.set_new_value('TDIAG')
    def on_pushButtonTshort_clicked(self): self.set_new_value('TSHRT')
    def on_pushButtonTlong_clicked(self): self.set_new_value('TLONG')
    def on_pushButtonTsleep_clicked(self): self.set_new_value('TSLP')
    def on_pushButtonTrdy_clicked(self): self.set_new_value('TRDY')
    def on_pushButtonTcycle_clicked(self): self.set_new_value('TCYCL')
    def on_pushButtonDebounce_clicked(self): self.set_new_value('TKEYS')
    def on_pushButtonAuto_clicked(self): self.set_new_value('AUTOS')
    def on_pushButtonSkip_clicked(self): self.set_new_value('NSKIP')
    def on_pushButtonTareZ_clicked(self): self.set_new_value('TARZN')
    def on_pushButtonDoza1_clicked(self): self.set_new_value('DOZA1')
    def on_pushButtonUpr11_clicked(self): self.set_new_value('UPR11')
    def on_pushButtonUpr21_clicked(self): self.set_new_value('UPR21')
    def on_pushButtonFfa1_clicked(self): self.set_new_value('FFA1')
    def on_pushButtonOpen1_clicked(self): self.set_new_value('TOPN1')
    def on_pushButtonDozz1_clicked(self): self.set_new_value('DOZZ1')
    def on_pushButtonTsmin1_clicked(self): self.set_new_value('TMIN1')
    def on_pushButtonDoza2_clicked(self): self.set_new_value('DOZA2')
    def on_pushButtonUpr12_clicked(self): self.set_new_value('UPR12')
    def on_pushButtonUpr22_clicked(self): self.set_new_value('UPR22')
    def on_pushButtonFfa2_clicked(self): self.set_new_value('FFA2')
    def on_pushButtonOpen2_clicked(self): self.set_new_value('TOPN2')
    def on_pushButtonDozz2_clicked(self): self.set_new_value('DOZZ2')
    def on_pushButtonTsmin2_clicked(self): self.set_new_value('TMIN2')

    def on_pushButtonRun_clicked(self): self.send_key('K_RUN', 1)
    def on_pushButtonStop_clicked(self): self.send_key('K_STOP', 1)
    def on_pushButtonUnload_clicked(self): self.send_key('K_UNLD', 1)

    # 10 slots for bits' setting
    def on_radioButtonTare_clicked(self): self.tare_toggle()
    def on_radioButtonZero_clicked(self): self.zero_toggle()
    def on_radioButtonFast_clicked(self): self.fast_toggle()
    def on_radioButtonMaster_clicked(self): self.write_ctrl_bit('DOSTUPP', 1)
    def on_pushButtonClb0_customContextMenuRequested(self): self.adc_clbr('CLB0BIT')
    def on_pushButtonClb1_customContextMenuRequested(self): self.adc_clbr('CLB1BIT')
    def on_pushButtonClb2_customContextMenuRequested(self): self.adc_clbr('CLB2BIT')
    def on_pushButtonClb3_customContextMenuRequested(self): self.adc_clbr('CLB3BIT')

    def set_new_value(self, register_name):
        dialog = QInputDialog(self)
        dialog.show()
        txt, accept = dialog.getText(self, 'Register Value', 'Enter integer')
        if accept:
            self.write_rg(register_name, str(txt))
        dialog.close()      # Не закривається, сука! Лише через пару спроб...

    def tare_toggle(self):
        tr = self.inpBin[adcRg['TARE'][0]]
        if tr == 0:
            self.write_ctrl_bit('TAREBIT', 1)   # Take tare via CTRL command
        else:
            self.write_rg('TARE', '0')         # reset tare to Null

    def zero_toggle(self):
        tr = self.inpBin[adcRg['ZERO'][0]]
        if tr == 0:
            self.write_ctrl_bit('ZEROBIT', 1)   # Take zero via CTRL command
        else:
            self.write_rg('ZERO', '0')         # reset zero to Null

    def fast_toggle(self):
        if self.inpBin[adcRg['CTRL'][0]] & adcBit['FASTMSK'] == 0:
            print('1')
            self.write_ctrl_bit('FASTBIT', 1)   # set FAST bit
        else:
            print('0')
            self.write_ctrl_bit('FASTBIT', 0)   # reset FAST bit

    def adc_clbr(self, bit_name):
        menu = QMenu(self)
        setAction = menu.addAction("Click to calibrate ADC or ESC to dismiss")
        pnt = QPoint(50, 250)    # facepalm....
        action = menu.exec_(self.mapToGlobal(pnt))
        if action == setAction:
            self.write_ctrl_bit(bit_name, 1)

    def write_rg(self, c, t):   # c - conf text (adc descriptor), t - entered editLine text
        logging.info("In write_rg: c={:s} t={:s}".format(c, t))
        try:
            b = adcRg[c][0]                       # Register number (b - begin)
        except LookupError:
            txt = 'PROG ERROR: set_ctrl_bit(): No par \'{:s}\' in ADC descriptor'.format(c)
            logging.error(txt)
            return
        try:
            v = float(t)    # Input fields looks as FLOATs (sometimes)
        except ValueError:
            txt = 'USER ERROR: write_rg(): {:s} is not a number'.format(t)
            self.freeze_status(txt)
            return
        v = int(v)          # But the ADC registers are always INTEGERs
        dostup_set = 0 != self.inpBin[adcRg['STAT'][0]] & adcBit['DOSTUPMSK']
        master_protected = 'MB' == adcRg[c][2][3:]
        if master_protected and (not dostup_set):
            txt = 'USER ERROR: write_rg(): Rg{:d} is Masterbit protected'.format(b)
            logging.error(txt)
            self.freeze_status(txt)
            return
        if adcRg[c][2] == 'ReadO':
            txt = 'USER ERROR: write_rg(): Rg{:d} is READ ONLY'.format(b)
            logging.error(txt)
            self.freeze_status(txt)
            return
        elif (adcRg[c][2][:3] == 'Cle') and (v != 0):
            txt = 'USER ERROR: write_rg(): Rg{:d} is CLEAR ONLY'.format(b)
            logging.error(txt)
            self.freeze_status(txt)
            return
        elif (adcRg[c][2][:3] == 'Wri') or (adcRg[c][2][:3] == 'Cle'):
            if adcRg[c][1] is 0:          # simple register
                t, b = self.io.write_rg(self.slave, b, v)
                if t is not '':
                    txt = 'HARDWARE ERROR: io.write_rg() returns error: {:s}'.format(t)
                    logging.error(txt)
                    self.freeze_status(txt)
                    return
            else:                       # double register
                t, b = self.io.write_db(self.slave, b, v)
                if t is not '':
                    txt = 'HARDWARE ERROR: io.write_db() returns error: {:s}'.format(t)
                    logging.error(txt)
                    self.freeze_status(txt)
                    return
            return
        else:               # No more siutable cases
            txt = 'PROG ERROR: write_rg(): Rg{:d} is of unknown type'.format(b)
            self.freeze_status(txt)
            return

    def write_ctrl_bit(self, c, v):   # c - conf text (look adc descriptor), TAREBIT etc.
        r = adcRg['CTRL'][0]                  # Register number is const in this method
        try:
            bit = adcBit[c][0]                 # bit number 0...15
        except LookupError:
            txt = 'USER ERROR: set_ctrl_bit(): No bit \'{:s}\' in CTRL register'.format(c)
            logging.info(txt)
            return
        dostup_set = 0 != self.inpBin[adcRg['STAT'][0]] & adcBit['DOSTUPMSK']
        master_protected = 1 == adcBit[c][1]
        if master_protected and (not dostup_set):
            txt = 'USER ERROR: set_ctrl_bit(): Bit \'{:s}\' is Masterbit protected'.format(c)
            logging.error(txt)
            self.freeze_status(txt)
            return
        # # FAST bit may be set or may be reset
        # v = 1
        # if c == 'FASTBIT':
        #     if self.inpBin[adc_rg['CTRL'][0]] & (1 << adc_bits['FASTBIT'][0]):
        #         v = 0
        print('try to write bit: ', 32 * r + bit, v)
        t, b = self.io.write_coil(self.slave, 32 * r + bit, v)
        if t is not '':
            txt = 'HARDWARE ERROR: io.write_coil() returns error: {:s}'.format(t)
            logging.error(txt)
            self.freeze_status(txt)
        return

    def send_key(self, c, v):   # c - conf text (look adc descriptor), TAREBIT etc.
        r = adcRg['KEYS'][0]                  # Register number is const in this method
        try:
            bit = keyBit[c]                 # bit number 0...15
        except LookupError:
            txt = 'USER ERROR: sendKey(): No bit \'{:s}\' in KEYS register'.format(c)
            logging.info(txt)
            return
        print('try to write bit: ', 32 * r + bit, v)
        t, b = self.io.write_coil(self.slave, 32 * r + bit, v)
        if t is not '':
            txt = 'HARDWARE ERROR: io.write_coil() returns error: {:s}'.format(t)
            logging.error(txt)
            self.freeze_status(txt)
        return

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
            msg += '     Port: {:s}, SlaveID: {:d}, baudrate: {:d}'.format(self.port,
                                                                           self.slave, self.baud)
            self.statusbar.showMessage(msg)
        else:
            self.statusbar.showMessage(msg)
            self.statusbar.color = 'red'


def int32(x):
    if x > 0xFFFFFFFF:              # more than 32-bits
        raise OverflowError
    if x > 0x7FFFFFFF:              # maximal positive int32_t number
        x = int(0x100000000 - x)    # 0x100000000 = 4,294,967,296 = 2 * 2,147,483,648
        if x < 2147483648:
            return -x
        else:
            return -2147483648      # = 0x80000000 - minimal (negative) int32_t number
    return x

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    # QMetaObject.connectSlotsByName(window)
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())