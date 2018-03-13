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

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMenu
from PyQt5 import QtWidgets

import logging

from ui.numpad import Numpad, VALID, VAL, PNT, SGN
from modbus import ModbusChannel
from descriptor import nregs, npars, adcRg, RG_REGNUM, RG_DOUBLE, RG_ACCESS, RG_PARNUM, RG_POINT, RG_DECHEX, adcBit, phaseText, keyBit
from data import bauds, ports, point_table, RIGHT_SHIFT, LEFT_SHIFT, pointFormat5, pointFormat9, fixed_point, FORMATSHRT, FORMATHEX, MAIN_PAGE, PARS_PAGE, CLBR_PAGE, MANU_PAGE, LOGO_PAGE
from qt_window import Ui_Window

# logging.basicConfig(level=logging.INFO)  # Впливає на рівень повідомлень у своїх методах: get_dregs()?

sys.path.append("ui")       # Where several files are placed

class Main(QMainWindow, Ui_Window):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        # Set up the user interface from Designer.
        # xy_screen = QtWidgets.QDesktopWidget().screenGeometry() не бачу різниці з запуском без аргумента...
        xy_screen = QtWidgets.QDesktopWidget().screenGeometry(-1)
        x_screen = xy_screen.width()
        y_screen = xy_screen.height()
        x_app = 480
        y_app = 290
        if x_screen < x_app:
            x_app = x_screen
        if y_screen < y_app:
            y_app = y_screen
        msg = "Detected screen: {:d}x{:d}. Accepted for application: {:d}x{:d}".format(x_screen, y_screen, x_app, y_app)
        # print(" print msg" + msg)
        logging.info(msg)
        self.setupUi(self)
        QMainWindow.setFixedSize(self, x_app, y_app)
        self.sw_pages.setCurrentIndex(0)
        # Serial port
        self.baud = bauds[6]
        self.port = ports[2]                # For RPi
        self.port = ports[0]                # For desktop PC
        self.slave = 1                      # Default Slave ID
        if len(sys.argv) > 1:
            self.port = sys.argv[1]
            if len(sys.argv) > 2:
                self.slave = sys.argv[2]
        # Main loop settings
        self.refresh = QTimer()             # refresh.singleShot() is used for update data rate
        self.status_freeze_timer = QTimer()
        self.modbus_timeout = QTimer()
        self.status_is_free = True
        self.requests_stopped = False       # During port setting dialog request are stopped
        self.modbus_count = 0
        self.inpBin = ()                    # To accept data from ADC
        self.io = None                      # Modbus channel will be opened later
        # Main Loop
        self.sw_pages.setCurrentIndex(0)
        self.update_data()  # почнеться з adc_io.ModbusChannel()
        self.show()

    def update_data(self):
        self.modbus_timeout.singleShot(2000, self.no_port_response)
        if self.requests_stopped:
            self.refresh.singleShot(400, self.update_data)
            return  # To allow dialogs run undisturbed
        if not self.io:
            try:
                logging.info('update data(): opening {:s} : {:d}'.format(self.port, self.baud))
                # Modbus init
                self.io = ModbusChannel(self.port, self.baud)
            except:
                # print("Serial port cannot be opened")
                self.status_refresh('ERROR1: Port opening fault', 2000)
                return
        # ********************************** MODBUS: read all registers as double regs *************
        txt, self.inpBin = self.io.read_dregs(self.slave, 0, nregs)
        # ********************************** END OF MODBUS *****************************************
        self.modbus_count += 1
        if 'error' in txt.lower():  # Modbus command execution error (no link?)
            self.status_refresh('ERROR2: {:s}'.format(txt), 2000)
            return
        if 'code' in txt.lower():  # %s- Code=%d
            self.status_refresh('ERROR3: {:s}'.format(txt), 2000)
            return
        if txt != '':
            self.status_refresh('ERROR4: {:s}'.format(txt), 2000)
            return
        txt = 'Port:{:s}  Baud:{:d}  SlaveID:{:d}  Count:{:d}'.format(self.port, self.baud, self.slave, self.modbus_count)
        self.status_refresh(txt, 100)
        self.fill_window()

    def fill_window(self):
        rg = self.inpBin                        # Для короткості запису створюємо локальну копію буфера Модбас
        statusRg = rg[adcRg['STAT'][RG_REGNUM]]
        ctrlRg = rg[adcRg['CTRL'][RG_REGNUM]]
        form5 = pointFormat5[fixed_point][0]
        deci5 = pointFormat5[fixed_point][1]
        form9 = pointFormat9[fixed_point][0]
        deci9 = pointFormat9[fixed_point][1]
        # Fill widgets
        phase = rg[adcRg['PHASE'][RG_REGNUM]]
        txt = "{:02d}: {:s}".format(phase, phaseText[phase])
        self.lab_phase.setText(txt)
        weight = rg[adcRg['WEI16'][RG_REGNUM]]
        txt = form5.format(weight * deci5)
        self.lab_weight.setText(txt + "kg")
        self.rb_lev0.setChecked(statusRg & adcBit['LEV0MSK'])
        self.rb_lev1.setChecked(statusRg & adcBit['LEV1MSK'])
        self.rb_lev2.setChecked(statusRg & adcBit['LEV2MSK'])
        self.rb_over.setChecked(statusRg & adcBit['OVERMSK'])
        self.rb_stab.setChecked(statusRg & adcBit['STABMSK'])
        tare = rg[adcRg['TARE'][RG_REGNUM]]
        txt = form5.format(tare * deci5)
        if tare == 0:
            self.rb_tare.setChecked(False)
        else:
            self.rb_tare.setChecked(True)
        # Switch by page number
        curr_ind = self.sw_pages.currentIndex()
        if curr_ind == MAIN_PAGE:
            weight = rg[adcRg['DOZA0'][RG_REGNUM]]
            txt = form5.format(weight*deci5)
            self.lab_dose.setText(txt+"kg")
            self.lab_total.setText(form9.format(deci9*rg[adcRg['TOTW'][RG_REGNUM]]) + 'kg')
        elif curr_ind == PARS_PAGE:
            regn = adcRg['PARN'][RG_REGNUM]         # PARN in rg[] buffer keeps curr par regn
            parn = rg[regn]                         # Current Par number
            parv= rg[adcRg['PARV'][RG_REGNUM]]      # Current Par value (Slave keeps control)
            key = ''
            for key in adcRg:
                if adcRg[key][RG_PARNUM] == parn:
                    # parv = rg[parn]
                    break
            pnt = adcRg[key][RG_POINT]
            if pnt > 9 or pnt < -1:
                print("Error: point = ", pnt)
            form = point_table[pnt][FORMATSHRT]
            if adcRg[key][RG_DECHEX] == 16:
                form = point_table[pnt][FORMATHEX]
            deci = point_table[pnt][RIGHT_SHIFT]
            self.lab_parname.setText("{:02d}: ".format(parn) + key)
            self.lab_parameter.setText(form.format(parv*deci))
        elif curr_ind == CLBR_PAGE:
            self.lab_clb0.setText("{:011.3f}".format(0.001*rg[adcRg['CLB0'][RG_REGNUM]]))
            self.lab_clb1.setText("{:011.3f}".format(0.001*rg[adcRg['CLB1'][RG_REGNUM]]))
            self.lab_clb2.setText("{:011.3f}".format(0.001*rg[adcRg['CLB2'][RG_REGNUM]]))
            self.lab_clb3.setText("{:011.3f}".format(0.001*rg[adcRg['CLB3'][RG_REGNUM]]))
            self.lab_adc_code.setText("{:011.3f}".format(0.001*rg[adcRg['ADC'][RG_REGNUM]]))
            self.lab_zero.setText(pointFormat5[fixed_point][0].format(pointFormat5[fixed_point][1]*rg[adcRg['ZERO'][RG_REGNUM]]/256) + "kg")
        elif curr_ind == MANU_PAGE:
            dio = rg[adcRg['CLB0'][RG_REGNUM]]
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
            self.lab_version.setText("Program version: " + "{:d}".format(rg[adcRg['V_SN'][RG_REGNUM]]))
            self.rb_master.setChecked(statusRg & adcBit['DOSTUPMSK'])
            self.lab_cheksum.setText("Check Sum: " + "{:d}".format(rg[adcRg['CASH'][RG_REGNUM]]))
            self.lab_tokom.setText("TOKOM, Kyiv-2018")
            self.lab_mail.setText("tokom2009@gmail.com")
        else:
            print("Page index out of range: " + "{:%d}".format(curr_ind))

    """ ************************************************************************************* 
                                NUMERICAL ENTRY (most of signals lead here)
        *************************************************************************************
    """
    def set_new_parv(self):         # Enter new value to a Par with the number in PARN
        rg = self.inpBin                        # input buffer contains info about thr current Par
        val_old = rg[adcRg['PARV'][RG_REGNUM]]   # Current Par value (Slave keeps control)
        mini = rg[adcRg['MINI'][RG_REGNUM]]     # Min and Max of the current Par value
        maxi = rg[adcRg['MAXI'][RG_REGNUM]]
        parn = rg[adcRg['PARN'][RG_REGNUM]]     # Current Par number. We need a key
        found = False                           # Now we need the point position for Numpad
        print('val_old, parn, mini, maxi', val_old, parn, mini, maxi)
        key = ""                                # Do fetch it, we need tthe Parameter key
        for key in adcRg:                       # Lookup all keys
            if adcRg[key][RG_PARNUM] == parn:
                found = True
                break
        if not found:
            msg = 'Key not found in ParN setting. ParN={:d}'.format(parn)
            logging.error(msg)
            return
        rg_pnt = adcRg[key][RG_POINT]       # Положення крапки потрібно тільки для Numpad
        print('Key-point:', key, rg_pnt)
        val_new = self.enter_rg_value(val_old, rg_pnt, mini, maxi)
        if val_new is None:
            print('Numeric input cancelled')        # DEBUG
            return
        print('PARVI-val:', int(val_new))
        self.check_push_reg_by_key('PARVI', int(val_new))   # Відправимо як регістр PARVI

    def set_new_reg(self, key, mi=0, ma=0):
        struct = adcRg[key]  # The structure describing the register : [Map.TARE.value, 1, 'Write', 0, fp, 10]
        rg_pnt = struct[RG_POINT]                           # По ключу дістанемо положення крапки, а також
        val_in = self.inpBin[struct[RG_REGNUM]]             # ..номер, а по номеру - старе значення з буфера
        # TODO: request Min and Max from ADC: any register
        if mi == 0 and ma == 0:
            new_val = self.enter_rg_value(val_in, rg_pnt)  # mi & ma is too hard to find, let them be default
        else:
            new_val = self.enter_rg_value(val_in, rg_pnt, mi, ma)  # For the PARN these arguments are known
        if new_val is None:
            print('Numeric input cancelled')        # DEBUG
            return
        print('Sent to check_push_reg_by_key', key, int(new_val))
        self.check_push_reg_by_key(key, int(new_val))       # Тепер по своєму ключу відправимо р-г Слейву

    def enter_rg_value(self, oldVal, point, mi=0, ma=999999999):
        val_in = oldVal
        rg_pnt = point
        print("Numpad args: oldVal={:d}, point={:d}, min={:d}, max={:d}".format(mi, ma, val_in, rg_pnt))
        np = Numpad(va=val_in, po=rg_pnt, mi=mi, ma=ma)
        np.exec_()
        print("Numpad answer: ", np.answer)  # DEBUG
        np.close()
        if (len(np.answer) != 0) and (np.answer[VALID] == 1):
            val = np.answer[VAL]
            point = np.answer[PNT]
            sign = np.answer[SGN]
            if point < 0:
                point = 0  # Value -1 means zero (as no point was pressed)
            if rg_pnt < 0:
                rg_pnt = 0  # Value -1 means zero (as no point was pressed)
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
            return int(val)
        else:
            return None


    """ ************************************************************************************* 
                                WRITE REGISTERS TO SLAVE
        *************************************************************************************
    """
    def check_push_reg_by_key(self, key, val):   # c - conf text (adc descriptor), t - entered editLine text
        logging.info("In write_rg: c={:s} v={:d}".format(key, val))
        try:
            beg = adcRg[key][RG_REGNUM]                       # Register number (b - begin)
        except LookupError:
            txt = 'PROG ERROR: set_ctrl_bit(): No par \'{:s}\' in ADC descriptor'.format(key)
            logging.error(txt)
            return
        dostup_set = (self.inpBin[adcRg['STAT'][RG_REGNUM]] & adcBit['DOSTUPMSK'] != 0)
        access = adcRg[key][RG_ACCESS]
        master_protected = (access[3:] == 'MB')
        if master_protected and (not dostup_set):
            txt = 'USER ERROR: write_rg(): Rg{:d} is Masterbit protected'.format(beg)
            logging.error(txt)
            self.hold_status(txt)
            return
        if access == 'ReadO':
            txt = 'USER ERROR: write_rg(): Rg{:d} is READ ONLY'.format(beg)
            logging.error(txt)
            self.hold_status(txt)
            return
        elif (access[:3] == 'Cle') and (val != 0):
            txt = 'USER ERROR: write_rg(): Rg{:d} is CLEAR ONLY'.format(beg)
            logging.error(txt)
            self.hold_status(txt)
            return
        elif (access[:3] == 'Wri') or (access[:3] == 'Cle'):
            if adcRg[key][RG_DOUBLE] == 0:          # single register
                txt = 'ERROR: io.write_rg() tries to write SINGLE register'
                logging.error(txt)
                self.hold_status(txt)
                return
            else:                                   # double register
                # ****************************************** MODBUS: write one double register **********
                t, beg = self.io.write_dregs(self.slave, beg, val)                                  #  **
                # ***************************************************************************************
                if t is not '':
                    txt = 'HARDWARE ERROR: io.write_db() returns error: {:s}'.format(t)
                    logging.error(txt)
                    self.hold_status(txt)
                    return
            return
        else:               # No more suitable cases
            txt = 'PROG ERROR: write_rg(): Rg{:d} is of unknown type'.format(beg)
            self.hold_status(txt)
            return

    """
    Radio buttons and push keys without numpad entry lead here
    Since branch RpiTkm16 there is no more CTRL bit-wise commands.
    All commands are being sent via KEYS register. All checking is laid on the uPLC (Slave)
    Note: KEYS register NEVER keeps bits. As far as the command is get, the bit in the register
    is resert - not depending on will it be accepted or rejected afterwards
    So, send_key() ALWAYS sends a 1-bit register. 
    """
    def send_key(self, c):      # c - keyBit text key ('K_KEYS' etc).
        print('Enter send_key with key=', c)
        r = adcRg['KEYS'][RG_REGNUM]  # Register number is const in this method
        try:
            bit = keyBit[c]  # bit number 0...23
        except LookupError:
            txt = 'USER ERROR: sendKey(): No bit \'{:s}\' in KEYS register'.format(c)
            logging.info(txt)
            self.hold_status(txt)
            return
        print('try to set bit: ', 32 * r + bit)
        # ****************************************************** MODBUS: write one coil *****
        t, b = self.io.write_coils(self.slave, 32 * r + bit, 1)                         #   *
        # ***********************************************************************************
        if t != '':
            txt = 'HARDWARE ERROR: io.write_coil() returns error: {:s}'.format(t)
            logging.error(txt)
            self.hold_status(txt)
        return

    """ ************************************************************************************* 
                                BIT TOGGLE: set via bit, reset via register
        *************************************************************************************
    """
    def tare_toggle(self):
        if self.inpBin[adcRg['TARE'][RG_REGNUM]] == 0:
            self.send_key('K_TARE')                 # Take tare via KEYS command
            # self.write_ctrl_bit('TAREBIT', 1)     # Take tare via CTRL command
        else:
            self.check_push_reg_by_key('TARE', 0)          # reset tare to Null

    def zero_toggle(self):
        if self.inpBin[adcRg['ZERO'][RG_REGNUM]] == 0:
            self.send_key('K_ZERO')
        else:
            self.check_push_reg_by_key('ZERO', 0)          # reset zero to Null

    def fast_toggle(self):
        ctrl = self.inpBin[adcRg['CTRL'][RG_REGNUM]]
        if ctrl & adcBit['FASTMSK'] == 0:
            print('Fast mode ADC')
            self.send_key('K_FAST')
            # self.write_ctrl_bit('FASTBIT', 1)
        else:
            print('Slow mode ADC (default)')
            self.check_push_reg_by_key('CTRL', ctrl | adcBit['FASTMSK'])  # reset FAST bit
            # self.write_ctrl_bit('FASTBIT', 0)

    """ ************************************************************************************* 
                                STATUS LINE CONTROL
        *************************************************************************************
    """
    def hold_status(self, msg):
        self.status_is_free = False
        self.status_freeze_timer.singleShot(4000, self.free_status)
        self.statusbar.showMessage(msg)

    def free_status(self):
        self.status_is_free = True

    def status_refresh(self, msg, next_update):
        if self.status_is_free:
            self.statusbar.showMessage(msg)
        self.refresh.singleShot(next_update, self.update_data)

    def no_port_response(self):
        pass

    """ ************************************************************************************* 
                                S I G N A L S
        *************************************************************************************
    """
    # Page control buttons
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

    # Push Buttons on the pages
    def on_pb_dose_nom_pressed(self): self.set_new_reg('DOZA0')
    def on_pb_run_pressed(self): self.send_key('K_RUN')
    def on_pb_stop_pressed(self): self.send_key('K_STOP')
    def on_pb_unload_pressed(self): self.send_key('K_UNLD')
    def on_pb_parn_pressed(self): self.set_new_reg('PARN', 0, npars)
    def on_pb_parv_pressed(self): self.set_new_parv()
    def on_pb_next_pressed(self): self.send_key('K_NEXT')
    def on_pb_prev_pressed(self): self.send_key('K_PREV')
    def on_pb_clb0_pressed(self): print("clb0"); self.send_key('K_CLB0')
    def on_pb_clb1_pressed(self): self.send_key('K_CLB1')
    def on_pb_clb2_pressed(self): self.send_key('K_CLB2')
    def on_pb_clb3_pressed(self): self.send_key('K_CLB3')
    def on_pb_zero_pressed(self): self.zero_toggle()

    # Checkboxes
    def on_rb_tare_pressed(self): self.tare_toggle()
    def on_rb_master_pressed(self): self.send_key('K_MAST')
    def on_rb_out8_pressed(self): self.send_key('K_OUT8')   # Slave toggles itself
    def on_rb_out9_pressed(self): self.send_key('K_OUT9')
    def on_rb_outa_pressed(self): self.send_key('K_OUTA')
    def on_rb_outb_pressed(self): self.send_key('K_OUTB')
    def on_rb_outc_pressed(self): self.send_key('K_OUTC')
    def on_rb_outd_pressed(self): self.send_key('K_OUTD')

    # Actions (pull-down menu)
    @QtCore.pyqtSlot()  # signal with no arguments. Need it to cut two launches
    def on_action_rep0_triggered(self): self.enter_numeric('REP0')

    @QtCore.pyqtSlot()
    def on_action_rep1_triggered(self): self.enter_numeric('REP1')

    @QtCore.pyqtSlot()
    def on_action_rep2_triggered(self): self.enter_numeric('REP2')

    @QtCore.pyqtSlot()
    def on_action_rep3_triggered(self): self.enter_numeric('REP3')

    @QtCore.pyqtSlot()
    def on_action_clb0_triggered(self): self.enter_numeric('CLB0')

    @QtCore.pyqtSlot()
    def on_action_clb1_triggered(self): self.enter_numeric('CLB1')

    @QtCore.pyqtSlot()
    def on_action_clb2_triggered(self): self.enter_numeric('CLB2')

    @QtCore.pyqtSlot()
    def on_action_clb3_triggered(self): self.enter_numeric('CLB3')

    @QtCore.pyqtSlot()
    def on_action_pcsn_triggered(self): self.enter_numeric('PCSN')

    @QtCore.pyqtSlot()
    def on_action_pcsn_triggered(self): self.enter_numeric('PCSN')

    @QtCore.pyqtSlot()
    def on_action_round_triggered(self): self.enter_numeric('ROUND')

    @QtCore.pyqtSlot()
    def on_action_master_triggered(self): self.send_key('K_MAST')

    @QtCore.pyqtSlot()
    def on_action__triggered(self):
        self.enter_numeric('PCSN')

    @QtCore.pyqtSlot()
    def on_action_fast_triggered(self): self.fast_toggle()

    @QtCore.pyqtSlot()
    def on_action_exit_triggered(self): self.close()

    @QtCore.pyqtSlot()
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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Main()
    sys.exit(app.exec_())

    """
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
    """
    """
    def write_ctrl_bit(self, c, v):  # c - conf text (look adc descriptor), TAREBIT etc.
        r = adcRg['CTRL'][0]  # Register number is const in this method
        try:
            bit = adcBit[c][0]  # bit number 0...15
        except LookupError:
            txt = 'USER ERROR: set_ctrl_bit(): No bit \'{:s}\' in CTRL register'.format(c)
            logging.info(txt)
            return
        dostup_set = 0 != self.inpBin[adcRg['STAT'][RG_REGNUM]] & adcBit['DOSTUPMSK']
        master_protected = 1 == adcBit[c][1]
        if master_protected and (not dostup_set):
            txt = 'USER ERROR: set_ctrl_bit(): Bit \'{:s}\' is Masterbit protected'.format(c)
            logging.error(txt)
            self.freeze_status(txt)
            return
        # # FAST bit may be set or may be reset
        # v = 1
        # if c == 'FASTBIT':
        #     if self.inpBin[adc_rg['CTRL'][RG_REGNUM]] & (1 << adc_bits['FASTBIT'][0]):
        #         v = 0
        print('try to write bit: ', 32 * r + bit, v)
        t, b = self.io.write_coils(self.slave, 32 * r + bit, v)
        if t is not '':
            txt = 'HARDWARE ERROR: io.write_coil() returns error: {:s}'.format(t)
            logging.error(txt)
            self.freeze_status(txt)
        return
    """
    """
        def adc_clbr(self, bit_name):
            menu = QMenu(self)
            setAction = menu.addAction("Click to calibrate ADC or ESC to dismiss")
            pnt = QPoint(50, 250)  # facepalm....
            action = menu.exec_(self.mapToGlobal(pnt))
            if action == setAction:
                self.write_ctrl_bit(bit_name, 1)
    """

    """
    def enter_param(self, key, mi=0, ma=999999999):
        val = self.enter_rg_value(mi=0, ma=999999999)
        if val is None:
            print('Numeric input cancelled')  # DEBUG
            return
        self.check_push_reg_by_key(key, int(val))  # ADC registers are always INTEGER

    def enter_parnum(self):
        key = 'PARN'
        rnum = adcRg[key][RG_REGNUM]
        print("RegNum=", rnum)
        val = self.inpBin[rnum]
        #val = self.inpBin[adcRg[key][RG_REGNUM]]
        rg_pnt = adcRg[key][RG_POINT]
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
        self.check_push_reg_by_key(key, int(val))  # ADC registers are always INTEGER
        """
