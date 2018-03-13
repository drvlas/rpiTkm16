# -*- coding: utf-8 -*-
"""
    Описує регістри АЦП
"""

from enum import Enum
import logging

# Порядок цього енумератора = map1[] у 9mapping.c - це реальні номери регістрів у
# Модбас-зверненнях. Отримано прямим копіюванням ParScriptIndx
class Map(Enum):
    KEYS, TARE, PARN, PARVI, PARV, WEI16, STAT, ERROR, ADC, MINI, MAXI, V_SN, CASH, CTRL, LEV1, LEV2, PHASE, DIO, FLTR, COUNT, SYST, CHANN, SUBW, SUBD, SUBDF, SUBTW, RS485, SCALE, STAB, PCSN, ROUND, REP0, REP1, REP2, REP3, CLB0, CLB1, CLB2, CLB3, ZERO, DIRR, XOR, TUNLD, TFEED, TMEAS, TBTM, TKEYS, TSHRT, TLONG, TSLEEP, TRDY, TCYCL, AUTOS, NSKIP, TARZN, LEV0, TSTRF, TSTRS, TINV, TCONT, TAFTER, TOTW, TOTN, UPR10, UPR20, DOZF0, TOTW0, FFA0, TMIN0, DOZA0, DOZZ0, WEI0, TSLW0, NEXT_CHANNEL = range(74)

nregs = Map.NEXT_CHANNEL.value

ctrl_cmd = {				# Just bit masks in brd14, but let it be called COMMANDS
    'TAREBIT': (0x0001, 0),
    'ZEROBIT': (0x0002, 1),
    'CLB0BIT': (0x0004, 1),
    'CLB1BIT': (0x0008, 1),
    'CLB2BIT': (0x0010, 1),
    'CLB3BIT': (0x0020, 1),
    'DOSTUPP': (0x8000, 0),
    'SAVECMD': (0xD807, 1),  # not used at all
    'RESTORE': (0xD838, 1)
}

# Absolutely all bit (key) commands from the panel. The bitmap is common for all pages
# Key DOSE NOM is excluded since it call numpad() and then write_dregs
# The same is for PARS.PARV and PARS.PARN
keyBit = {
    'K_RUN':    0,      # MAIN.RUN
    'K_STOP':	1,      # MAIN.STOP
    'K_UNLD':   2,      # MAIN.UNLOAD
    'K_TARE':	3,      # constant widget (all pages)
    'K_PREV':   4,      # PARS.PREV
    'K_NEXT':   5,      # PARS.NEXT
    'K_CLB0':	6,      # CLBR.CLBR0
    'K_CLB1':	7,      # CLBR.CLBR1
    'K_CLB2':	8,      # CLBR.CLBR2
    'K_CLB3':	9,      # CLBR.CLBR3
    'K_ZERO':   10,     # CLBR.ZERO
    'K_MAST':   11,     # Menu action CLBR.MASTER or LOGO.radioButton_master
    'K_FAST':   12,     # Menu action: OPER.FAST
    'K_OUT2':   13,     # MANU.radioButton_o6
    'K_OUT3':   14,     # MANU.radioButton_o7
    'K_OUT4':   15,     # MANU.radioButton_o8
    'K_OUT5':   16,     # MANU.radioButton_o9
    'K_OUT6':   17,     # MANU.radioButton_oa
    'K_OUT7':   18,     # MANU.radioButton_ob
}

adcBit = {
    # CTRLRG    побітно, зручно для прямого запису у COIL
    #       номер доступ
    'TAREBIT': (0, 0),  # coil number = 16*adcRg['CTRL'][0] + adcBit['TAREBIT'][0]
    'ZEROBIT': (1, 1),  # must be dostup = adcBit['TAREBIT'][1]
    'CLB0BIT': (2, 1),
    'CLB1BIT': (3, 1),
    'CLB2BIT': (4, 1),
    'CLB3BIT': (5, 1),
    'NEXTPAR': (6, 0),
    'FASTBIT': (7, 0),
    'RUNBIT': (12, 0),
    'STOPBIT': (13, 0),
    'DOSTUPP': (15, 0),  # 271
    'FASTMSK': 128,

    # STATUSRG  побітно, зручно для аналізу у програмі
    'LEV0MSK': 1,  # state = bin[adc['STATUS'][0]] & adc['LEV0MSK']
    'LEV1MSK': 2,
    'LEV2MSK': 4,
    'OVERMSK': 8,
    'STABMSK': 16,
    'DOSTUPMSK': 256,

	# ERRORS
    'LEAKMSK': 512,
}

# Parameters. For debug: const means noe random generated values
# ACCEPT means user's value is accepted if MB is OK
# CALC means value will be calculated in emulator
# CONST means we ignore user's writes
# Просто для контролю поставив у такому порядку, як у ParScriptIndx. Насправді не грає ролі

from ui.data import fixed_point as fp
adp = 3
tim = 3
# indexes
RG_REGNUM = 0
RG_DOUBLE = 1
RG_ACCESS = 2
RG_PARNUM = 3
RG_POINT = 4
RG_DECHEX = 5
# Порядок розташування не грає ролі, але я розташував так, щоб НОМЕР ПАРАМЕТРА
# (член RG_PARNUM) зростав у натуральному порядку. Таким чином, виходить, що
# порядок запису у цьому словнику точно співпадає з map0[] у файлі mapping.c
# проекту brd14
adcRg = {
    # name      map1       size  type       map0 (=ParScriptIndx)
    'TARE': [Map.TARE.value, 1, 'Write', 0, fp, 10],
    'WEI16': [Map.WEI16.value, 1, 'ReadO', 1, fp, 10],
    'STAT': [Map.STAT.value, 1, 'ReadO', 2, -1, 16],
    'ERROR': [Map.ERROR.value, 1, 'ReadO', 3, -1, 16],
    'ADC': [Map.ADC.value, 1, 'ReadO', 4, adp, 10],
    'CTRL': [Map.CTRL.value, 1, 'WriMB', 5, -1, 16],
    'LEV1': [Map.LEV1.value, 1, 'Write', 6, fp, 10],
    'LEV2': [Map.LEV2.value, 1, 'Write', 7, fp, 10],
    'PHASE': [Map.PHASE.value, 1, 'ReadO', 8, -1, 10],
    'DIO': [Map.DIO.value, 1, 'ReadO', 9, -1, 16],
    'COUNT': [Map.COUNT.value, 1, 'ReadO', 10, -1, 10],
    'FLTR': [Map.FLTR.value, 1, 'Write', 11, 1, 10],
    'CHANN': [Map.CHANN.value, 1, 'ReadO', 12, -1, 10],
    'SUBW': [Map.SUBW.value, 1, 'ReadO', 13, fp, 10],
    'SUBD': [Map.SUBD.value, 1, 'ReadO', 14, fp, 10],
    'SUBDF': [Map.SUBDF.value, 1, 'ReadO', 15, fp, 10],
    'SUBTW': [Map.SUBTW.value, 1, 'ReadO', 16, fp, 10],
    'TOTW': [Map.TOTW.value, 1, 'Write', 17, fp, 10],
    'TOTN': [Map.TOTN.value, 1, 'Write', 18, -1, 10],
    'RS485': [Map.RS485.value, 1, 'Write', 19, 3, 10],
    'REP0': [Map.REP0.value, 1, 'WriMB', 20, fp, 10],
    'REP1': [Map.REP1.value, 1, 'WriMB', 21, fp, 10],
    'REP2': [Map.REP2.value, 1, 'WriMB', 22, fp, 10],
    'REP3': [Map.REP3.value, 1, 'WriMB', 23, fp, 10],
    'CLB0': [Map.CLB0.value, 1, 'WriMB', 24, adp, 10],
    'CLB1': [Map.CLB1.value, 1, 'WriMB', 25, adp, 10],
    'CLB2': [Map.CLB2.value, 1, 'WriMB', 26, adp, 10],
    'CLB3': [Map.CLB3.value, 1, 'WriMB', 27, adp, 10],
    'ZERO': [Map.ZERO.value, 1, 'CleMB', 28, fp, 10],     # Хоча там Zer24...
    'PCSN': [Map.PCSN.value, 1, 'WriMB', 29, -1, 10],
    'ROUND': [Map.ROUND.value, 1, 'WriMB', 30, fp, 10],
    'SCALE': [Map.SCALE.value, 1, 'Write', 31, fp, 10],
    'STAB': [Map.STAB.value, 1, 'Write', 32, adp, 10],
    'AUTOS': [Map.AUTOS.value, 1, 'Write', 33, 1, 10],
    'NSKIP': [Map.NSKIP.value, 1, 'Write', 34, -1, 10],
    'TARZN': [Map.TARZN.value, 1, 'Write', 35, fp, 10],
    'LEV0': [Map.LEV0.value, 1, 'Write', 36, fp, 10],
    'XOR': [Map.XOR.value, 1, 'Write', 37, -1, 16],
    'TUNLD': [Map.TUNLD.value, 1, 'Write', 38, tim, 10],
    'TFEED': [Map.TFEED.value, 1, 'Write', 39, tim, 10],
    'TMEAS': [Map.TMEAS.value, 1, 'Write', 40, tim, 10],
    'TBTM': [Map.TBTM.value, 1, 'Write', 41, tim, 10],
    'TSLP': [Map.TSLEEP.value, 1, 'Write', 42, tim, 10],
    'TSHRT': [Map.TSHRT.value, 1, 'Write', 43, tim, 10],
    'TLONG': [Map.TLONG.value, 1, 'Write', 44, tim, 10],
    'TCYCL': [Map.TCYCL.value, 1, 'Write', 45, tim, 10],
    'TSTRF': [Map.TRDY.value, 1, 'Write', 46, tim, 10],
    'TSTRS': [Map.TRDY.value, 1, 'Write', 47, tim, 10],
    'TINV': [Map.TRDY.value, 1, 'Write', 48, tim, 10],
    'TCONT': [Map.TRDY.value, 1, 'Write', 49, tim, 10],
    'TAFTER': [Map.TRDY.value, 1, 'Write', 50, tim, 10],
    'TRDY': [Map.TRDY.value, 1, 'Write', 51, tim, 10],
    'TKEYS': [Map.TKEYS.value, 1, 'Write', 52, -1, 10],
    'SYST': [Map.SYST.value, 1, 'ReadO', 53, 2, 10],
    'DOZA0': [Map.DOZA0.value, 1, 'Write', 54, fp, 10],
    'DOZF0': [Map.DOZF0.value, 1, 'Write', 55, fp, 10],
    'TOTW0': [Map.TOTW0.value, 1, 'Write', 56, fp, 10],
    'UPR10': [Map.UPR10.value, 1, 'Write', 57, fp, 10],
    'UPR20': [Map.UPR20.value, 1, 'Write', 58, fp, 10],
    'DOZZ0': [Map.DOZZ0.value, 1, 'Write', 59, fp, 10],
    'FFA0': [Map.FFA0.value, 1, 'Write', 60, 1, 10],
    'TMIN0': [Map.TMIN0.value, 1, 'Write', 61, tim, 10],
    'TSLW0': [Map.TSLW0.value, 1, 'Write', 62, tim, 10],
    'PARN': [Map.PARN.value, 1, 'Write', -1, -1, 10],
    'PARVI': [Map.PARVI.value, 1, 'Write', -1],
    'PARV': [Map.PARV.value, 1,  'ReadO', -1],
    'MINI': [Map.MINI.value, 1,  'ReadO', -1],
    'MAXI': [Map.MAXI.value, 1,  'ReadO', -1],
    'V_SN': [Map.V_SN.value, 1,  'ReadO', -1],
    'CASH': [Map.CASH.value, 1,  'ReadO', -1],
    'DIRR': [Map.DIRR.value, 1,  'ReadO', -1],
    'WEI0': [Map.WEI0.value, 1,  'ReadO', -1],
    'KEYS': [Map.KEYS.value, 1,  'Write', -1],
    #       REGNUM                  PARNUM
}
npars = len(adcRg)

phaseText = [
    'STOP_ph',
    'CYCLE_ph',
    'T_FEED_ph',
    'T_TARE_ph',
    'M_TARE_ph',
    'C_TARE_ph',
    'E_TARE_ph',
    'CHKBTM_ph',
    'TURB0_ph',
    'FEED0_ph',
    'T_DOZA0_ph',
    'M_DOZA0_ph',
    'TURB1_ph',
    'FEED1_ph',
    'T_DOZA1_ph',
    'M_DOZA1_ph',
    'W_UNLD_ph',
    'T_UNLD_ph',
    'W_LEV0_ph',
    'READY_ph',
    'TOSTOP_ph',
    'PAUSE_ph',
    'LEAK0_ph',
    'LEAK1_ph',
]

# print("nregs = ", nregs)
# print("npars = ", npars)

if nregs != npars:
    for nreg in range(0, nregs):  # all reg numbers
        found = False  # for each try to find a Par script
        for key in adcRg:  # all keys (or par numbers)
            if adcRg[key][RG_REGNUM] == nreg:
                # print(nreg, adcRg[key][RG_PARNUM])
                found = True  # found. This Par script is not interesting
                break
        if found:
            continue  # Next reg numb
        else:  # Here it is!
            msg = "Descriptor error: map has {:d} names, adcRg dictionary has {:d} keys. Exiting".format(nregs, npars)
            logging.error(msg)
            exit(99)
else:
    msg = "Descriptor: map has {:d} names, adcRg dictionary has {:d} keys".format(nregs, npars)
    logging.warning(msg)
