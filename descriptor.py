# -*- coding: utf-8 -*-
"""
    Описує регістри АЦП
"""
# Порядок цього енумератора = map1[] у 9mapping.c - це реальні номери регістрів у Модбас-зверненнях
# Or: these are REGISTERS
class Map:
    KEYS = 0
    ERROR = 1
    MAP = 2
    WEI16 = 3
    PHASE = 4
    SUBD = 5
    PARV = 6
    TOTW = 7
    TOTN = 8
    STAT = 9
    PARN = 10
    PARVI = 11
    MINI = 12
    MAXI = 13
    REP0 = 14
    REP1 = 15
    CLB0 = 16
    CLB1 = 17
    ADC = 18
    REP2 = 19
    REP3 = 20
    CLB2 = 21
    CLB3 = 22
    DIO = 23
    DIRR = 24
    XOR = 25
    V_SN = 26
    CASH = 27
    DOZA1 = 28
    WEI0 = 29
    DOZA2 = 30
    WEI1 = 31
    TARE = 32
    CTRL = 33
    LEV1 = 34
    LEV2 = 35
    FLTR = 36
    CYCLE = 37
    SYST = 38
    CHANN = 39
    SUBW = 40
    SUBDF = 41
    SUBTW = 42
    RS485 = 43
    SCALE = 44
    STAB = 45
    PCSN = 46
    ROUND = 47
    ZERO = 48
    TUNLD = 49
    TFEED = 50
    TMEAS = 51
    TBTM = 52
    TKEYS = 53
    TDIAG = 54
    TSHRT = 55
    TLONG = 56
    TSLP = 57
    TRDY = 58
    TCYCL = 59
    AUTOS = 60
    NSKIP = 61
    TARZN = 62
    LEV0 = 63
    UPR11 = 64
    UPR21 = 65
    DOZF1 = 66
    TOTW1 = 67
    FFA1 = 68
    TOPN1 = 69
    TMIN1 = 70
    DOZZ1 = 71
    TSLW1 = 72
    UPR12 = 73
    UPR22 = 74
    DOZF2 = 75
    TOTW2 = 76
    FFA2 = 77
    TOPN2 = 78
    TMIN2 = 79
    DOZZ2 = 80
    TSLW2 = 81
    NREGS = 82      # This is not a register. It's the number of registers

nregs = Map.NREGS

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
    'K_OUT6':   11,     # MANU.radioButton_o6
    'K_OUT7':   12,     # MANU.radioButton_o7
    'K_OUT8':   13,     # MANU.radioButton_o8
    'K_OUT9':   14,     # MANU.radioButton_o9
    'K_OUTA':   15,     # MANU.radioButton_oa
    'K_OUTB':   16,     # MANU.radioButton_ob
    'K_OUTC':   17,     # MANU.radioButton_oc
    'K_OUTD':   18,     # MANU.radioButton_od
    'K_FAST':   19,     # Menu action: OPER.FAST
    'K_MAST':   20,     # Menu action CLBR.MASTER or LOGO.radioButton_master
    'K_0021':   21,     # Reserved
    'K_0022':   22,     # Reserved
    'K_0023':   23,     # Reserved and it's the last possible LINEAR code
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

adcRg = {
    # name      map1       size  type       map0 (=ParScriptIndx)
    'TARE': [Map.TARE, 1, 'Write', 0, fp, 10],
    'WEI16': [Map.WEI16, 1, 'ReadO', 1, fp, 10],
    'STAT': [Map.STAT, 1, 'ReadO', 2, -1, 16],
    'ERROR': [Map.ERROR, 1, 'ReadO', 3, -1, 16],
    'ADC': [Map.ADC, 1, 'ReadO', 4, adp, 10],
    'CTRL': [Map.CTRL, 1, 'WriMB', 5, -1, 16],
    'LEV1': [Map.LEV1, 1, 'Write', 6, fp, 10],
    'LEV2': [Map.LEV2, 1, 'Write', 7, fp, 10],
    'PHASE': [Map.PHASE, 1, 'ReadO', 8, -1, 10],
    'DIO': [Map.DIO, 1, 'ReadO', 9, -1, 16],
    'CYCLE': [Map.CYCLE, 1, 'ReadO', 10, -1, 10],
    'FLTR': [Map.FLTR, 1, 'Write', 11, 1, 10],
    'CHANN': [Map.CHANN, 1, 'ReadO', 12, -1, 10],
    'SUBW': [Map.SUBW, 1, 'ReadO', 13, fp, 10],
    'SUBD': [Map.SUBD, 1, 'ReadO', 14, fp, 10],
    'SUBDF': [Map.SUBDF, 1, 'ReadO', 15, fp, 10],
    'SUBTW': [Map.SUBTW, 1, 'ReadO', 16, fp, 10],
    'TOTW': [Map.TOTW,  1, 'Write', 17, fp, 10],
    'TOTN': [Map.TOTN,  1, 'Write', 18, -1, 10],
    'RS485': [Map.RS485, 1, 'Write', 19, 3, 10],
    'REP0': [Map.REP0, 1, 'WriMB', 20, fp, 10],
    'REP1': [Map.REP1, 1, 'WriMB', 21, fp, 10],
    'REP2': [Map.REP2, 1, 'WriMB', 22, fp, 10],
    'REP3': [Map.REP3, 1, 'WriMB', 23, fp, 10],
    'CLB0': [Map.CLB0, 1, 'WriMB', 24, adp, 10],
    'CLB1': [Map.CLB1, 1, 'WriMB', 25, adp, 10],
    'CLB2': [Map.CLB2, 1, 'WriMB', 26, adp, 10],
    'CLB3': [Map.CLB3, 1, 'WriMB', 27, adp, 10],
    'ZERO': [Map.ZERO, 1, 'CleMB', 28, fp, 10],     # Хоча там Zer24...
    'PCSN': [Map.PCSN,  1, 'WriMB', 29, -1, 10],
    'ROUND': [Map.ROUND, 1, 'WriMB', 30, fp, 10],
    'SCALE': [Map.SCALE, 1, 'Write', 31, fp, 10],
    'STAB': [Map.STAB, 1, 'Write', 32, adp, 10],
    'AUTOS': [Map.AUTOS, 1, 'Write', 33, 1, 10],
    'NSKIP': [Map.NSKIP, 1, 'Write', 34, -1, 10],
    'TARZN': [Map.TARZN, 1, 'Write', 35, fp, 10],
    'LEV0': [Map.LEV0, 1, 'Write', 36, fp, 10],
    'XOR': [Map.XOR, 1, 'Write', 37, -1, 16],
    'TUNLD': [Map.TUNLD, 1, 'Write', 38, tim, 10],
    'TFEED': [Map.TFEED, 1, 'Write', 39, tim, 10],
    'TMEAS': [Map.TMEAS, 1, 'Write', 40, tim, 10],
    'TBTM': [Map.TBTM, 1, 'Write', 41, tim, 10],
    'TDIAG': [Map.TDIAG, 1, 'Write', 42, tim, 10],
    'TSLP': [Map.TSLP, 1, 'Write', 43, tim, 10],
    'TSHRT': [Map.TSHRT, 1, 'Write', 44, tim, 10],
    'TLONG': [Map.TLONG, 1, 'Write', 45, tim, 10],
    'TCYCL': [Map.TCYCL, 1, 'Write', 46, tim, 10],
    'TRDY': [Map.TRDY, 1, 'Write', 47, tim, 10],
    'TKEYS': [Map.TKEYS, 1, 'Write', 48, -1, 10],
    'SYST': [Map.SYST, 1, 'ReadO', 49, 2, 10],
    'DOZA1': [Map.DOZA1, 1, 'Write', 50, fp, 10],
    'DOZF1': [Map.DOZF1, 1, 'Write', 51, fp, 10],
    'TOTW1': [Map.TOTW1, 1, 'Write', 52, fp, 10],
    'UPR11': [Map.UPR11, 1, 'Write', 53, fp, 10],
    'UPR21': [Map.UPR21, 1, 'Write', 54, fp, 10],
    'DOZZ1': [Map.DOZZ1, 1, 'Write', 55, fp, 10],
    'FFA1': [Map.FFA1, 1, 'Write', 56, 1, 10],
    'TOPN1': [Map.TOPN1, 1, 'Write', 57, tim, 10],
    'TMIN1': [Map.TMIN1, 1, 'Write', 58, tim, 10],
    'TSLW1': [Map.TSLW1, 1, 'Write', 59, tim, 10],
    'DOZA2': [Map.DOZA2, 1, 'Write', 60, fp, 10],
    'DOZF2': [Map.DOZF2, 1, 'Write', 61, fp, 10],
    'TOTW2': [Map.TOTW2, 1, 'Write', 62, fp, 10],
    'UPR12': [Map.UPR12, 1, 'Write', 63, fp, 10],
    'UPR22': [Map.UPR22, 1, 'Write', 64, fp, 10],
    'DOZZ2': [Map.DOZZ2, 1, 'Write', 65, fp, 10],
    'FFA2': [Map.FFA2, 1, 'Write', 66, 1, 10],
    'TOPN2': [Map.TOPN2, 1, 'Write', 67, tim, 10],
    'TMIN2': [Map.TMIN2, 1, 'Write', 68, tim, 10],
    'TSLW2': [Map.TSLW2, 1, 'Write', 69, tim, 10],
    'KEYS': [Map.KEYS,  1, 'ReadO', -1],    # These pars are not visible on PARS page
    'MAP': [Map.MAP,   1, 'ReadO', -1],
    'PARN': [Map.PARN,  1, 'Write', -1, -1, 10],
    'PARVI': [Map.PARVI, 1, 'ReadO', -1],
    'PARV': [Map.PARV,  1, 'ReadO', -1],
    'MINI': [Map.MINI,  1, 'ReadO', -1],
    'MAXI': [Map.MAXI,  1, 'ReadO', -1],
    'V_SN': [Map.V_SN,  1, 'ReadO', -1],
    'CASH': [Map.CASH,  1, 'ReadO', -1],
    'DIRR': [Map.DIRR,  1, 'ReadO', -1],
    'WEI1': [Map.WEI0,  1, 'ReadO', -1],
    'WEI2': [Map.WEI1,  1, 'ReadO', -1],
    #       REGNUM                  PARNUM
}
npars = len(adcRg)
LASTPAR = 69

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

if nregs != npars:
    print("Descripor error! mregs != nregs. Exiting")
    for nreg in range(0, nregs):  # all reg numbers
        found = False  # for each try to find a Par script
        for key in adcRg:  # all keys (or par numbers)
            if adcRg[key][RG_REGNUM] == nreg:
                #print(nreg, adcRg[key][RG_PARNUM])
                found = True  # found. This Par script is not interesting
                break
        if found:
            continue  # Next reg numb
        else:  # Here it is!
            print("adcRg has not Rg number ", nreg)
            exit(99)
