# -*- coding: utf-8 -*-
"""
Tables, constants
"""
MAX_DIG = 9
MAX_VAL = 999999999     # 9 nines

point_table = {
            -1: ('{: 011d}', '{:d}', "0x{:04x}", 1, 1),
            0: ('{: 011d}.', '{:d}.', "0x{:04x}", 1, 1),
            1: ('{: 011.1f}', '{:11.1f}', "0x{:04x}", 10, 0.1),
            2: ('{: 011.2f}', '{:11.2f}', "0x{:04x}", 100, 0.01),
            3: ('{: 011.3f}', '{:11.3f}', "0x{:04x}", 1000, 0.001),
            4: ('{: 011.4f}', '{:11.4f}', "0x{:08x}", 10000, 0.0001),
            5: ('{: 011.5f}', '{:11.5f}', "0x{:08x}", 100000, 0.00001),
            6: ('{: 011.6f}', '{:11.6f}', "0x{:08x}", 1000000, 0.000001),
            7: ('{: 011.7f}', '{:11.7f}', "0x{:08x}", 10000000, 0.0000001),
            8: ('{: 011.8f}', '{:11.8f}', "0x{:08x}", 100000000, 0.00000001),
            9: ('{: 011.9f}', '{:11.9f}', "0x{:08x}", 1000000000, 0.000000001),
        }
FORMAT_POS = 0
FORMATSHRT = 1
FORMATHEX = 2
LEFT_SHIFT = 3
RIGHT_SHIFT = 4
# Use samples:
# point10Power[self.point][FORMAT_POS]
# point10Power[self.point][LEFT_SHIFT]
# point10Power[self.point][RIGHT_SHIFT]



# tables for Window
bauds = [2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 76800, 115200]
ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/serial0', 'COM1', 'COM2']
pointFormat5 = {
            0: ('{: 06d}', 1),
            1: ('{: 06.1f}', 0.1),
            2: ('{: 06.2f}', 0.01),
            3: ('{: 06.3f}', 0.001),
        }
pointFormat9 = {
            0: ('{: 011d}', 1),
            1: ('{: 011.1f}', 0.1),
            2: ('{: 011.2f}', 0.01),
            3: ('{: 011.3f}', 0.001),
        }
fixed_point = 2         # Const in the project (all weight data depends on it)

MAIN_PAGE = 0
PARS_PAGE = 1
CLBR_PAGE = 2
MANU_PAGE = 3
LOGO_PAGE = 4
