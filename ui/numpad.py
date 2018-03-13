#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Module implementing Numerical Pad
"""

# from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog

from qt_numpad import Ui_Numpad
from data import *

# NumPad result index
VALID = 0
VAL = 1
PNT = 2
SGN = 3


class Numpad(QDialog, Ui_Numpad):
    def __init__(self, va, po, parent=None, mi=0, ma=999999999):    # va may be negative integer
        super(Numpad, self).__init__(parent)
        self.setupUi(self)
        self.new = va
        self.point = po
        self.sign = 1
        self.virgin = True
        self.answer = ()
        self.minimal = mi
        self.maximal = ma
        self.old = 0
        self.digits = 0
        form = point_table[po][FORMAT_POS]
        mult = point_table[po][RIGHT_SHIFT]
        self.lab_rng.setText(
            form.format(mult * self.minimal) +
            "  ...  " +
            form.format(mult * self.maximal)
        )
        self.show_val()

    def show_val(self):
        print("digits:{:d}  point:{: 2d}  value:{:d}".format(self.digits, self.point, self.new))
        form = point_table[self.point][FORMAT_POS]
        mult = point_table[self.point][RIGHT_SHIFT]
        self.lab_val.setText(form.format(mult * self.new))

    def defloration(self):
        if self.virgin:
            self.new = 0
            self.virgin = False

    def digit(self, d):
        if self.virgin:
            self.new = 0
            self.point = -1
            self.sign = 1
            self.digits = 0
        self.defloration()
        if self.digits >= MAX_DIG:
            self.digits = MAX_DIG
            self.new = MAX_VAL
        else:
            self.digits += 1
            self.new = 10 * self.new + d
            if self.point >= 0:
                self.point += 1
        self.show_val()

    def on_pb0_pressed(self): self.digit(0)

    def on_pb1_pressed(self): self.digit(1)

    def on_pb2_pressed(self): self.digit(2)

    def on_pb3_pressed(self): self.digit(3)

    def on_pb4_pressed(self): self.digit(4)

    def on_pb5_pressed(self): self.digit(5)

    def on_pb6_pressed(self): self.digit(6)

    def on_pb7_pressed(self): self.digit(7)

    def on_pb8_pressed(self): self.digit(8)

    def on_pb9_pressed(self): self.digit(9)
    
    def on_pb_del_pressed(self):
        if self.virgin:
            self.new = 0
            self.point = -1
            self.sign = 1
        else:
            self.defloration()
            if self.digits > 1:
                self.digits -= 1
                self.new //= 10     # Right shift
            else:
                self.digits = 0
                self.new = 0
                self.point = -1     # Point is wiped too
                self.sign = 1       # I think that it's more natural to wipe the sign
            if self.point >= 0:
                self.point -= 1
        self.show_val()
        
    def on_pb_pnt_pressed(self):
        self.defloration()
        self.point = 0              # May be many points
        self.show_val()
    
    def on_pb_sign_pressed(self):
        if self.virgin:
            self.new = 0
            self.point = -1
            self.sign = 1
        self.defloration()
        self.sign = -self.sign
        self.show_val()
    
    # @pyqtSlot()
    def on_pb_yes_pressed(self):
        print("Yes")
        self.answer = (1, self.new, self.point, self.sign)
        self.close()
        return
    
    def on_pb_no_pressed(self):
        print("No")
        self.answer = (0, 0, 0, 0)
        self.close()
        return


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    print("Debug launch of Numpad as MAIN")
    np = Numpad()
    np.exec_()
    print("Result:", np.answer)
    np.close()
    sys.exit(app.exec_())
