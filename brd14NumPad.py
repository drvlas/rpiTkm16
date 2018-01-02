#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" NumPad Module
    Opens QDialog Widget and accepts a numeric value
    Uses its own numeric pad
    01.01.2017
"""
import logging
import sys
from sys import platform

# from PyQt5 import uic
from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QMenu
from PyQt5 import QtWidgets

# My modules
from numPad import Ui_Dialog

logging.basicConfig(level=logging.INFO)


class NumDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(Main, self).__init__()
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        xScreen = sizeObject.width()
        yScreen = sizeObject.height()
        xApp = 480
        yApp = 290
        if xScreen < xApp: xApp = xScreen
        if yScreen < yApp: yApp = yScreen
        #print(" Screen   size : "  + str(xScreen) + "x"  + str(yScreen))
        #print(" Accepted size : "  + str(xApp) + "x"  + str(yApp))
        self.setupUi(self) 
        QDialog.setFixedSize(self, xApp, yApp)
        self.inputValue = 0
        self.acceptData()
        

    def acceptData(self):
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
        form5 = pointFormat5[point][0]
        deci5 = pointFormat5[point][1]
        form9 = pointFormat9[point][0]
        deci9 = pointFormat9[point][1]
        # Fill widgets
        phase = rg[adcRg['PHASE'][0]]
        txt = "{:02d}: {:s}".format(phase, phaseText[phase])
        self.PhaseLabel.setText(txt)
        weight = rg[adcRg['WEI16'][0]]
        txt = form5.format(weight * deci5)
        self.WeightLabel.setText(txt + "kg")
        self.LevRadioButton0.setChecked(statusRg & adcBit['LEV0MSK'])
        self.LevRadioButton1.setChecked(statusRg & adcBit['LEV1MSK'])
        self.LevRadioButton2.setChecked(statusRg & adcBit['LEV2MSK'])
        self.OverRadioButton.setChecked(statusRg & adcBit['OVERMSK'])
        self.StabRadioButton.setChecked(statusRg & adcBit['STABMSK'])
        tare = rg[adcRg['TARE'][0]]
        txt = form5.format(tare * deci5)
        if tare == 0:
            self.TareRadioButton.setChecked(False)
        else:
            self.TareRadioButton.setChecked(True)
        # Switch by page number
        currInd = self.stackedWidget.currentIndex()
        if currInd == MAIN_PAGE:
            weight = rg[adcRg['DOZA1'][0]]
            txt = form5.format(weight * deci5)
            self.DoseLabel.setText(txt + "kg")
            weight = rg[adcRg['DOZA1'][0]]
            txt = form9.format(weight * deci9)
            self.TotalLabel.setText(form9.format(deci9*rg[adcRg['TOTW'][0]]) + 'kg')
        elif currInd == PARS_PAGE:
            parn = rg[adcRg['PARN'][0]]
            parv= 0
            key = ''
            for key in adcRg:
                if adcRg[key][0] == parn:
                    parv = rg[parn]
                    break
            self.ParameterLabel.setText("{:02d}: ".format(parn) + key + " = {:d} ".format(parv))
        elif currInd == CLBR_PAGE:
            self.ClbLabel0.setText("{:011.3f}".format(0.001*rg[adcRg['CLB0'][0]]))
            self.ClbLabel1.setText("{:011.3f}".format(0.001*rg[adcRg['CLB1'][0]]))
            self.ClbLabel2.setText("{:011.3f}".format(0.001*rg[adcRg['CLB2'][0]]))
            self.ClbLabel3.setText("{:011.3f}".format(0.001*rg[adcRg['CLB3'][0]]))
            self.AdcCodeLabel.setText("{:011.3f}".format(0.001*rg[adcRg['ADC'][0]]))
            self.ZeroLabel.setText(pointFormat5[point][0].format(pointFormat5[point][1]*rg[adcRg['ZERO'][0]]/256) + "kg")
        elif currInd == MANU_PAGE:
            dio = rg[adcRg['CLB0'][0]]
            self.InpRadioButton0.setChecked(dio & 1)
            self.InpRadioButton1.setChecked(dio & 2)
            self.InpRadioButton2.setChecked(dio & 4)
            self.InpRadioButton3.setChecked(dio & 8)
            self.InpRadioButton4.setChecked(dio & 16)
            self.InpRadioButton5.setChecked(dio & 32)
            self.InpRadioButton6.setChecked(dio & 64)
            self.InpRadioButton7.setChecked(dio & 128)
            self.OutRadioButton6.setChecked(dio & 64)
            self.OutRadioButton7.setChecked(dio & 128)
            self.OutRadioButton8.setChecked(dio & 256)
            self.OutRadioButton9.setChecked(dio & 512)
            self.OutRadioButtonA.setChecked(dio & 1024)
            self.OutRadioButtonB.setChecked(dio & 2048)
            self.OutRadioButtonC.setChecked(dio & 4096)
            self.OutRadioButtonD.setChecked(dio & 8192)
        elif currInd == LOGO_PAGE:
            self.DvaTxtLabel.setText("DVA TKM16 Batch Weigher Controler")
            self.VersionLabel.setText("Program version: " + "{:d}".format(rg[adcRg['V_SN'][0]]))
            self.MasterRadioButton.setChecked(statusRg & adcBit['DOSTUPMSK'])
            #self.CheckSumLabel.setText("Check Sum " + "0x{: 08X}".format(rg[adcRg['CASH'][0]]))
            self.CheckSumLabel.setText("Check Sum: " + "{:d}".format(rg[adcRg['CASH'][0]]))
            self.TokomTxtLabel.setText("TOKOM, Kyiv-2018")
            self.MailTxtLabel.setText("tokom2009@gmail.com")
        else:
            print("Page index out of range: " + "{:%d}".format(currInd))
        
    # def resume(self): self.ui_stopped = False

    # 31 slots for Registers' setting
    def on_MainPushButtonL_clicked(self): self.stackedWidget.setCurrentIndex(MAIN_PAGE)
    def on_MainPushButtonR_clicked(self): self.stackedWidget.setCurrentIndex(MAIN_PAGE)
    def on_ParsPushButtonL_clicked(self): self.stackedWidget.setCurrentIndex(PARS_PAGE)
    def on_ParsPushButtonR_clicked(self): self.stackedWidget.setCurrentIndex(PARS_PAGE)
    def on_ClbrPushButtonL_clicked(self): self.stackedWidget.setCurrentIndex(CLBR_PAGE)
    def on_ClbrPushButtonR_clicked(self): self.stackedWidget.setCurrentIndex(CLBR_PAGE)
    def on_ManuPushButtonL_clicked(self): self.stackedWidget.setCurrentIndex(MANU_PAGE)
    def on_ManuPushButtonR_clicked(self): self.stackedWidget.setCurrentIndex(MANU_PAGE)
    def on_LogoPushButtonL_clicked(self): self.stackedWidget.setCurrentIndex(LOGO_PAGE)
    def on_LogoPushButtonR_clicked(self): self.stackedWidget.setCurrentIndex(LOGO_PAGE)
    
    def on_DoseNomPushButton_clicked(self): self.showNumPad('DOZA1')
    
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
    
    def showNumPad(self, register_name):
        dialog = Ui_Dialog(self)
        dialog.show()
        txt, accept = self.getNumber(self)
        if accept:
            self.write_rg(register_name, str(txt))
        dialog.close()
    
    def getNumber(self, reg)




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
        self.status2freeze = FaphaseTextlse

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
