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

from descriptor import nregs

#from modbus_tk import LOGGER    # Look __init__.py: LOGGER = logging.getLogger("modbus_tk")
# Logger call: LOGGER.info("msg")

# Open for MB diagnostics.
# When setLevel(logging.DEBUG):
#   If set_verbose(True) - logs all transactions
#   If set_verbose(False) - logs only "RtuMaster /dev/ttyUSB0 is opened"
# When setLevel(logging.INFO): as if set_verbose(False)
logger = mb_utils.create_logger("console")
#logger.setLevel(logging.INFO)   # DEBUG here gives all Modbus traffic

# execute:
# pdu = struct.pack(">BHH", function_code, starting_address, quantity_of_x)

#data = response_pdu[1:]
# returns the data as a tuple according to the data_format
# (calculated based on the function or user-defined)
#quantity_of_x=0
#data_format = ">" + (quantity_of_x * "H")
#result = struct.unpack(data_format, data)


class ModbusChannel(mb_rtu.RtuMaster):
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, bytesize=8, parity='E', stopbits=1):
        try:
            mb_rtu.RtuMaster.__init__(self, serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout=2.5, xonxoff=0, rtscts=0))
        except (OSError, FileNotFoundError, serial.SerialException):
            # print("Serial port cannot be opened")
            raise serial.SerialException
            # raise OSError, FileNotFoundError, serial.SerialException('ERROR1: Port opening fault')
            # raise OSError, FileNotFoundError, serial.SerialException('ERROR1: Port opening fault')
        self.set_timeout(1.5)
        self.set_verbose(True)                      # Вмикає друк трафіка на консоль
        #self.set_verbose(False)                     # Вимикає
        logging.basicConfig(level=logging.INFO)  # Здається, це взагалі не впливає на вивід...

    # dbBegin, dbNumber - double registers' bias and number
    def read_dregs(self, slave, dbBegin, dbNumber):
        _maxd = 60
        txt = ''
        doubles = []    # Prepare alarm exit
        got1 = ()
        got2 = ()
        got = ()
        if dbNumber > (_maxd<<1):
            return 'Modbus command execution error (too many registers)', got
        if dbNumber > _maxd:
            try:
                # ***********************************************************************************
                got1 = self.execute(slave, cst.READ_HOLDING_REGISTERS, dbBegin << 1, _maxd << 1)  # *
                # ***********************************************************************************
            except error_def.ModbusError as e:
                txt = '%s- Code=%d' % (e, e.get_exception_code())
                logging.error(txt)
                return txt, tuple(doubles)
            except error_def.ModbusInvalidResponseError:
                txt = 'ModbusInvalidResponseError, read_dregs 1'
                logging.error(txt)
                return txt, tuple(doubles)
            logging.debug('read_dregs {:d} double Rg OK'.format(_maxd))
            dbBegin += _maxd
            dbNumber -= _maxd
        try:
            # ***************************************************************************************
            got2 = self.execute(slave, cst.READ_HOLDING_REGISTERS, dbBegin << 1, dbNumber << 1)  # **
            # ***************************************************************************************
        except error_def.ModbusError as e:
            txt = '%s- Code=%d' % (e, e.get_exception_code())
            logging.error(txt)
            return txt, tuple(doubles)
        except error_def.ModbusInvalidResponseError:
            txt = 'ModbusInvalidResponseError read_dregs 2'
            logging.error(txt)
            return txt, tuple(doubles)
        logging.debug('read_dregs {:d} double Rg OK'.format(dbNumber))
        got = got1 + got2
        i = 0
        while i < len(got):     # Number 0x12345678 in buffer: 56 78 12 34, RgHi=0x1234, RgLo=0x5678
            value = (got[i + 1] << 16) | got[i]
            if value > 0x7fffffff:
                value -= 0x100000000
            doubles.append(value)
            i += 2
        return txt, tuple(doubles)

    # Write ONE AND ONLY ONE double register
    def write_dregs(self, slave, begin, dval):  # Увага! Тут begin - номер подвійного р-ра!
        try:
            hi = dval >> 16
            lo = dval & 0xffff
            txt = 'write Double Reg sent: double RG begin:%d regs:%d %d' % (begin, hi, lo)
            print(txt)
            logging.debug(txt)
            r = self.execute(slave,
                             function_code=cst.WRITE_MULTIPLE_REGISTERS,
                             starting_address=begin << 1,
                             output_value=(lo, hi))                         # Modbus sends HiRg, LoRg
            txt = 'write Double Reg: from:%d Nregs:%d' % (r[0], r[1])
            logging.info(txt)
            txt = ''                    # No error flag
        except error_def.ModbusError as e:
            txt = '%s- Code=%d' % (e, e.get_exception_code())
            logging.error(txt)
        except error_def.ModbusInvalidResponseError:
            txt = 'Modbus cmd exec error (write_dregs)'
            logging.error(txt)
        return txt, begin

    def write_coils(self, slave, begin, val):
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
            txt = 'Modbus cmd exec error (write_coils)'
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
        tup = m.read_regs(1, 0, nregs)
        for j in range(len(tup[1])):
            i = j
            if i == (i // 2) * 2:
                val = tup[1][j] + tup[1][j+1] * 65536
                tx = '{:2d} {:6} {:9d}  0x{:04X}'.format(i, map[i//2], val, val)
                print(tx)
        tup = m.read_regs(1, nregs, nregs)
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



    """
    # returns '' and binary tuple. To read all: get_regs(0, adc['TOTAL_REGS'])
    def read_regs(self, slave, begin, length):
        txt = ''
        got = ()
        try:
            got = self.execute(slave, cst.READ_HOLDING_REGISTERS,
                               begin, length)
        except error_def.ModbusError as e:
            txt = '%s- Code=%d' % (e, e.get_exception_code())
            logging.error(txt)
        except error_def.ModbusInvalidResponseError:
            txt = 'Modbus cmd exec error (read_regs)'
            logging.error(txt)
        logging.debug('get_regs OK')
        return txt, got
    """
    """
    def write_regs(self, slave, begin, val):
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
            txt = 'Modbus cmd exec error (write_regs)'
            logging.error(txt)
        return txt, begin
    """



