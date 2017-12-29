#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" The module communicates with ADC
    Відкриває послідовний порт при створенні.
    Має 4 основних метода:
    get_regs - читає регістри з АЦП
    write_rg - пише 1 регістр
    write_db - пише 1 подвійний регістр
    write_coil - пише 1 біт
    Дескріптори регістрів не використовує зовсім, тому у викликах методів
    треба перевіряти і права доступу, і права зміни, і границі номерів
"""

import logging

import modbus_tk.defines as cst
import modbus_tk.modbus as error_def
import modbus_tk.modbus_rtu as mb_rtu
import modbus_tk.utils as mb_utils
import serial

from brd14Descriptor import *

# Open for MB diagnostics.
# When setLevel(logging.DEBUG):
#   If set_verbose(True) - logs all transactions
#   If set_verbose(False) - logs only "RtuMaster /dev/ttyUSB0 is opened"
# When setLevel(logging.INFO): as if set_verbose(False)
logger = mb_utils.create_logger("console")
logger.setLevel(logging.INFO)

# execute:
# pdu = struct.pack(">BHH", function_code, starting_address, quantity_of_x)

#data = response_pdu[1:]
# returns the data as a tuple according to the data_format
# (calculated based on the function or user-defined)
#quantity_of_x=0
#data_format = ">" + (quantity_of_x * "H")
#result = struct.unpack(data_format, data)


class ModbusChannel(mb_rtu.RtuMaster):
    def __init__(self,
                 port='/dev/ttyUSB0',
                 baudrate=9600,
                 bytesize=8,
                 parity='E',
                 stopbits=1):
        mb_rtu.RtuMaster.__init__(self, serial.Serial(port, baudrate, bytesize, parity,
                                                      stopbits, timeout=2.5, xonxoff=0,
                                                      rtscts=0))
        self.set_timeout(1.5)
        self.set_verbose(False)
        logging.basicConfig(level=logging.ERROR)

    # returns '' and binary tuple. To read all: get_regs(0, adc['TOTAL_REGS'])
    def get_regs(self, slave, begin, length):
        txt = ''
        got = ()
        try:
            got = self.execute(slave, cst.READ_HOLDING_REGISTERS,
                               begin, length)
        except error_def.ModbusError as e:
            txt = '%s- Code=%d' % (e, e.get_exception_code())
            logging.error(txt)
        except error_def.ModbusInvalidResponseError:
            txt = 'Modbus command execution error (no link?)'
            logging.error(txt)
        logging.debug('get_regs OK')
        return txt, got

    # dbBegin, dbNumber - double registers' bias and number
    def get_db(self, slave, dbBegin, dbNumber):
        txt = ''
        got1 = ()
        got2 = ()
        got = ()
        if dbNumber > 120:
            return 'Modbus command execution error (too many registers)', got
        if dbNumber > 60:
            try:
                got1 = self.execute(slave, cst.READ_HOLDING_REGISTERS,
                                   dbBegin << 1, 120)
            except error_def.ModbusError as e:
                txt = '%s- Code=%d' % (e, e.get_exception_code())
                logging.error(txt)
            except error_def.ModbusInvalidResponseError:
                txt = 'Modbus command execution error (no link?)'
                logging.error(txt)
            logging.debug('get_regs 60 OK')
            dbBegin += 60
            dbNumber -= 60
        try:
            got2 = self.execute(slave, cst.READ_HOLDING_REGISTERS,
                               dbBegin << 1, dbNumber << 1)
        except error_def.ModbusError as e:
            txt = '%s- Code=%d' % (e, e.get_exception_code())
            logging.error(txt)
        except error_def.ModbusInvalidResponseError:
            txt = 'Modbus command execution error (no link?)'
            logging.error(txt)
        logging.debug('get_regs OK')
        got = got1 + got2
        doubles = []
        i = 0
        #print(got)
        while i < len(got):
            value = (got[i + 1] << 16) | got[i]
            #if (got[i+1] & 0x8000) != 0:
            if value > 0x7fffffff:
                value -= 0x100000000
            doubles.append(value)
            i += 2
        #print(tuple(doubles))
        return txt, tuple(doubles)

    def write_rg(self, slave, begin, val):
        try:
            txt = 'Try to write Register:{:2d} val:{:d}'.format(begin, val)
            logging.debug(txt)
            r = self.execute(slave,
                             function_code=cst.WRITE_SINGLE_REGISTER,
                             starting_address=begin, output_value=val)
            txt = 'write Register result: RG:%d val:%d' % (r[0], r[1])
            logging.debug(txt)
            txt = ''
        except error_def.ModbusError as e:
            txt = '%s- Code=%d' % (e, e.get_exception_code())
            logging.error(txt)
        except error_def.ModbusInvalidResponseError:
            txt = 'Modbus command execution error (no link?)'
            logging.error(txt)
        return txt, begin

    def write_db(self, slave, begin, dval):  # Увага! Тут begin - номер подійного р-ра!
        try:
            hi = dval >> 16
            lo = dval & 0xffff
            txt = 'write Double Reg sent: dbRGbegin:%d regs:%d %d' % (begin, lo, hi)
            logging.debug(txt)
            r = self.execute(slave,
                             function_code=cst.WRITE_MULTIPLE_REGISTERS,
                             starting_address=begin << 1,
                             output_value=(lo, hi))
            txt = 'write Double Reg result: RG:%d regs:%d' % (r[0], r[1])
            logging.debug(txt)
            txt = ''                    # No error flag
        except error_def.ModbusError as e:
            txt = '%s- Code=%d' % (e, e.get_exception_code())
            logging.error(txt)
        except error_def.ModbusInvalidResponseError:
            txt = 'Modbus command execution error (no link?)'
            logging.error(txt)
        return txt, begin

    def write_coil(self, slave, begin, val):
        try:
            r = self.execute(slave, function_code=cst.WRITE_SINGLE_COIL, starting_address=begin,
                             output_value=val)
            txt = 'write Coil result: Coil:%d val:%x' % (r[0], r[1])
            logging.debug(txt)
            txt = ''
        except error_def.ModbusError as e:
            txt = '%s- Code=%d' % (e, e.get_exception_code())
            logging.error(txt)
        except error_def.ModbusInvalidResponseError:
            txt = 'Modbus command execution error (no link?)'
            logging.error(txt)
        return txt, begin

# тест
if __name__ == '__main__':
    # from adc_descriptor import adc_bits, adc_rg, nregs

    import time
    logging.basicConfig(level=logging.INFO)
    m = ModbusChannel()
    #tup = m.get_regs(1, 0, 106)
    while True:
        time.sleep(0.2)
        tup = m.get_regs(1, 0, nregs)
        for j in range(len(tup[1])):
            i = j
            if i == (i // 2) * 2:
                val = tup[1][j] + tup[1][j+1] * 65536
                tx = '{:2d} {:6} {:9d}  0x{:04X}'.format(i, map[i//2], val, val)
                print(tx)
        tup = m.get_regs(1, nregs, nregs)
        for j in range(len(tup[1])):
            i = j + nregs
            if i == (i // 2) * 2:
                val = tup[1][j] + tup[1][j + 1] * 65536
                tx = '{:2d} {:6} {:9d}  0x{:04X}'.format(i, map[i // 2], val, val)
                print(tx)
        #reg = int(input('Enter reg number: '))
        #if reg > len(tup[1]):
#            continue
#        val = int(input('Enter reg value:  '))
#        m.write_rg(1, reg, val)
