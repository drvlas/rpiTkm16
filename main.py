#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Програма для роботи з тензоАЦП-ПЛК TKM.99.01.14 (brd14)
    12.12.2017 - my desktop
    29.12.2017 - GIT, pass to Raspberry Pi3 and develop on it
    02.01.2018 - Was working with PAGES, but I began to add NUMPAD and the project is broken
                Pushed to Git to continue on the Desktop
    05.01.2017 - pulled from Git and begin to "nodule-refactor"
"""
import sys

from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMenu
from PyQt5 import QtWidgets

from ui.numpad import Numpad, VALID, VAL, PNT, SGN
from modbus import *
from descriptor import nregs  # ctrl_cmd, adc_bits, adc_rg,  adc_io does not import descriptor
from data import bauds, ports, point_table, RIGHT_SHIFT, LEFT_SHIFT, pointFormat5, pointFormat9, fixed_point
from data import MAIN_PAGE, PARS_PAGE, CLBR_PAGE, MANU_PAGE, LOGO_PAGE
from qt_window import Ui_Window

logging.basicConfig(level=logging.INFO)


class Main(QMainWindow, Ui_Window):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        # Set up the user interface from Designer.
        xy_screen = QtWidgets.QDesktopWidget().screenGeometry(-1)
        x_screen = xy_screen.width()
        y_screen = xy_screen.height()
        x_app = 480
        y_app = 290
        if x_screen < x_app: x_app = x_screen
        if y_screen < y_app: y_app = y_screen
        print(" Screen   size : " + str(x_screen) + "x" + str(y_screen))
        print(" Accepted size : " + str(x_app) + "x" + str(y_app))
        self.setupUi(self)
        QMainWindow.setFixedSize(self, x_app, y_app)
        self.sw_pages.setCurrentIndex(0)
        #self.statusbar.showMessage(greeting)
        # Serial port
        self.port_opened = False
        self.baud = bauds[6]
        self.port = ports[0]                # Default Linux port name
        self.slave = 1                      # Default Slave ID
        if len(sys.argv) > 1:
            self.port = sys.argv[1]
            if len(sys.argv) > 2:
                self.slave = sys.argv[2]
        # Main loop settings
        self.refresh = QTimer()             # refresh.singleShot() is used for update data rate
        self.status_freeze_timer = QTimer()
        self.status2freeze = False
        self.requests_stopped = False       # During port setting dialog request are stopped
        self.modbus_count = 0
        print('Read from Map nregs:', nregs)
        self.inpBin = ()                    # To accept data from ADC
        self.io = None                      # Modbus channel will be opened later
        # Main Loop
        self.sw_pages.setCurrentIndex(0)
        self.update_data()  # почнеться з adc_io.ModbusChannel()
        self.show()

    def update_data(self):
        if self.requests_stopped:
            self.refresh.singleShot(400, self.update_data)
            return  # To allow dialogs run undisturbed
        if not self.port_opened:
            #self.status_refresh('INFO: Port is not opened. Refreshing stopped')
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
        tx0 = 'Port:{:s}, SlaveID:{:d}, baud:{:d} count: {:d} {:d}'.format(self.port, self.slave,
                                                                      self.baud, self.modbus_count, self.sw_pages.currentIndex())
        txt, self.inpBin = self.io.get_db(self.slave, 0, nregs)
        self.modbus_count += 1
        if 'error' in txt.lower():  # Modbus command execution error (no link?)
            self.status_refresh('{:s}INFO: modbus error: {:s}'.format(tx0, txt))
            self.port_opened = False
            self.refresh.singleShot(2000, self.update_data)  # 2000
            return
        elif 'code' in txt.lower():  # %s- Code=%d
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
        self.morda(self.inpBin)

    def morda(self, rg):                # Це, по суті, просто шматок (закінчення) update_data()
        statusRg = rg[adcRg['STAT'][0]]
        ctrlRg = rg[adcRg['CTRL'][0]]
        form5 = pointFormat5[fixed_point][0]
        deci5 = pointFormat5[fixed_point][1]
        form9 = pointFormat9[fixed_point][0]
        deci9 = pointFormat9[fixed_point][1]
        # Fill widgets
        phase = rg[adcRg['PHASE'][0]]
        txt = "{:02d}: {:s}".format(phase, phaseText[phase])
        self.lab_phase.setText(txt)
        weight = rg[adcRg['WEI16'][0]]
        txt = form5.format(weight * deci5)
        self.lab_weight.setText(txt + "kg")
        self.rb_lev0.setChecked(statusRg & adcBit['LEV0MSK'])
        self.rb_lev1.setChecked(statusRg & adcBit['LEV1MSK'])
        self.rb_lev2.setChecked(statusRg & adcBit['LEV2MSK'])
        self.rb_over.setChecked(statusRg & adcBit['OVERMSK'])
        self.rb_stab.setChecked(statusRg & adcBit['STABMSK'])
        tare = rg[adcRg['TARE'][0]]
        txt = form5.format(tare * deci5)
        if tare == 0:
            self.rb_tare.setChecked(False)
        else:
            self.rb_tare.setChecked(True)
        # Switch by page number
        curr_ind = self.sw_pages.currentIndex()
        if curr_ind == MAIN_PAGE:
            weight = rg[adcRg['DOZA1'][0]]
            txt = form5.format(weight * deci5)
            self.lab_dose.setText(txt + "kg")
            weight = rg[adcRg['DOZA1'][0]]
            txt = form9.format(weight * deci9)
            self.lab_total.setText(form9.format(deci9*rg[adcRg['TOTW'][0]]) + 'kg')
        elif curr_ind == PARS_PAGE:
            parn = rg[adcRg['PARN'][0]]
            parv= 0
            key = ''
            for key in adcRg:
                if adcRg[key][0] == parn:
                    parv = rg[parn]
                    break
            self.lab_parameter.setText("{:02d}: ".format(parn) + key + " = {:d} ".format(parv))
        elif curr_ind == CLBR_PAGE:
            self.lab_clb0.setText("{:011.3f}".format(0.001*rg[adcRg['CLB0'][0]]))
            self.lab_clb1.setText("{:011.3f}".format(0.001*rg[adcRg['CLB1'][0]]))
            self.lab_clb2.setText("{:011.3f}".format(0.001*rg[adcRg['CLB2'][0]]))
            self.lab_clb3.setText("{:011.3f}".format(0.001*rg[adcRg['CLB3'][0]]))
            self.lab_adc_code.setText("{:011.3f}".format(0.001*rg[adcRg['ADC'][0]]))
            self.lab_zero.setText(pointFormat5[fixed_point][0].format(pointFormat5[fixed_point][1]*rg[adcRg['ZERO'][0]]/256) + "kg")
        elif curr_ind == MANU_PAGE:
            dio = rg[adcRg['CLB0'][0]]
            self.rb_inp0.setChecked(dio & 1)
            self.rb_inp1.setChecked(dio & 2)
            self.rb_inp2.setChecked(dio & 4)
            self.rb_inp3.setChecked(dio & 8)
            self.rb_inp4.setChecked(dio & 16)
            self.rb_inp5.setChecked(dio & 32)
            self.rb_inp6.setChecked(dio & 64)
            self.rb_inp7.setChecked(dio & 128)
            self.rb_out6.setChecked(dio & 64)
            self.rb_out7.setChecked(dio & 128)
            self.rb_out8.setChecked(dio & 256)
            self.rb_out9.setChecked(dio & 512)
            self.rb_outa.setChecked(dio & 1024)
            self.rb_outb.setChecked(dio & 2048)
            self.rb_outc.setChecked(dio & 4096)
            self.rb_outd.setChecked(dio & 8192)
        elif curr_ind == LOGO_PAGE:
            self.lab_dva_tkm.setText("DVA TKM16 Batch Weigher Controler")
            self.lab_version.setText("Program version: " + "{:d}".format(rg[adcRg['V_SN'][0]]))
            self.rb_master.setChecked(statusRg & adcBit['DOSTUPMSK'])
            #self.CheckSumLabel.setText("Check Sum " + "0x{: 08X}".format(rg[adcRg['CASH'][0]]))
            self.lab_cheksum.setText("Check Sum: " + "{:d}".format(rg[adcRg['CASH'][0]]))
            self.lab_tokom.setText("TOKOM, Kyiv-2018")
            self.lab_mail.setText("tokom2009@gmail.com")
        else:
            print("Page index out of range: " + "{:%d}".format(curr_ind))

    # @pyqtSlot()
    def show_numpad(self, key):
        # TODO: request Min and Max from ADC, add Point to tables (data.py?)
        indx = adcRg[key][0]
        print(indx)
        val = self.inpBin[indx]
        #val = self.inpBin[adcRg[key][0]]
        mi = -999999999
        ma = 999999999
        rg_pnt = 2
        si = 1
        np = Numpad(mi=mi, ma=ma, va=val, po=rg_pnt, si=si)
        np.exec_()
        print("Numpad answer: ", np.answer)  # DEBUG
        np.close()
        if (len(np.answer) != 0) and (np.answer[VALID] == 1):
            val = np.answer[VAL]
            point = np.answer[PNT]
            sign = np.answer[SGN]
            if point < 0:
                point = 0  # Value -1 means zero (as no point was pressed)
            if point > rg_pnt:
                mult = point_table[point - rg_pnt][RIGHT_SHIFT]
                val *= mult
            elif point < rg_pnt:
                mult = point_table[rg_pnt - point][LEFT_SHIFT]
                val *= int(mult)
            a_half = 0.5
            if sign == -1:
                val = -val
                a_half = -0.5
            if val < mi:
                val = mi
            elif val > ma:
                val = ma
            else:
                val = int(val + a_half)
        self.write_rg(key, int(val))  # But the ADC registers are always INTEGERs

    def write_rg(self, c, v):   # c - conf text (adc descriptor), t - entered editLine text
        logging.info("In write_rg: c={:s} v={:d}".format(c, v))
        try:
            b = adcRg[c][0]                       # Register number (b - begin)
        except LookupError:
            txt = 'PROG ERROR: set_ctrl_bit(): No par \'{:s}\' in ADC descriptor'.format(c)
            logging.error(txt)
            return
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

    def on_pb_main_left_pressed(self): print("main_left"); self.sw_pages.setCurrentIndex(MAIN_PAGE)

    def on_pb_main_right_pressed(self): print("main_right"); self.sw_pages.setCurrentIndex(MAIN_PAGE)

    def on_pb_pars_left_pressed(self): print("pars_left"); self.sw_pages.setCurrentIndex(PARS_PAGE)

    def on_pb_pars_right_pressed(self): print("pars_right"); self.sw_pages.setCurrentIndex(PARS_PAGE)

    def on_pb_clbr_left_pressed(self): print("clbr_left"); self.sw_pages.setCurrentIndex(CLBR_PAGE)

    def on_pb_clbr_right_pressed(self): print("clbr_right"); self.sw_pages.setCurrentIndex(CLBR_PAGE)

    def on_pb_manu_left_pressed(self): print("manu_left"); self.sw_pages.setCurrentIndex(MANU_PAGE)

    def on_pb_manu_right_pressed(self): print("manu_right"); self.sw_pages.setCurrentIndex(MANU_PAGE)

    def on_pb_logo_left_pressed(self): print("logo_left"); self.sw_pages.setCurrentIndex(LOGO_PAGE)

    def on_pb_logo_right_pressed(self): print("logo_right"); self.sw_pages.setCurrentIndex(LOGO_PAGE)

    def on_pb_dose_nom_pressed(self): print("dose_nom"); self.show_numpad('DOZA1')



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
    ui = Main()
    sys.exit(app.exec_())
