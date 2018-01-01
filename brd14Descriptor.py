# -*- coding: utf-8 -*-
"""
    Описує регістри АЦП
"""
# Порядок цього енумератора = map1[] у 9mapping.c - це реальні номери регістрів у Модбас-зверненнях
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
    NREGS = 82

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

keyBit = {
    'K_RUN':    0,
    'K_STOP':	1,
    'K_UNLD':   2,
    'K_FED0':   3,  # reserved
    'K_FED1':   4,
    'K_BTM':    5
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

# registers. For debug: const means noe random generated values
# ACCEPT means user's value is accepted if MB is OK
# CALC means value will be calculated in emulator
# CONST means we ignore user's writes
# Просто для контролю поставив у такому порядку, як у ParScriptIndx. Насправді не грає ролі
adcRg = {
    # name    Rg#       MB from Master var   init
    'KEYS':     [Map.KEYS,  1, 'ReadO', 'accept',   0],    # (0) ParScriptIndx
    'MAP':      [Map.MAP,   1, 'ReadO', 'accept',   0],
    'TARE':     [Map.TARE,  1, 'Write', 'accept',   0],
    'PARN':     [Map.PARN,  1, 'Write', 'calc',     11],
    'PARVI':    [Map.PARVI, 1, 'ReadO', 'accept',   0],
    'PARV':     [Map.PARV,  1, 'ReadO', 'calc',     0000],
    'WEI16':    [Map.WEI16, 1, 'ReadO', 'calc',     0],
    'STAT':     [Map.STAT,  1, 'ReadO', 'calc',     0],
    'ERROR':    [Map.ERROR, 1, 'ReadO', 'calc',     0],
    'ADC':      [Map.ADC,   1, 'ReadO', 'accept',   1234],
    'MINI':     [Map.MINI,  1, 'ReadO', 'calc',     0],      # (10)
    'MAXI':     [Map.MAXI,  1, 'ReadO', 'calc',     0],
    'V_SN':     [Map.V_SN,  1, 'ReadO', 'const',    2210],
    'CASH':     [Map.CASH,  1, 'ReadO', 'const',    1313],
    'CTRL':     [Map.CTRL,  1, 'WriMB', 'accept',   0],
    'LEV1':     [Map.LEV1,  1, 'Write', 'accept',   0],
    'LEV2':     [Map.LEV2,  1, 'Write', 'accept',   0],
    'PHASE':    [Map.PHASE, 1, 'ReadO', 'accept',   0],
    'DIO':      [Map.DIO,   1, 'ReadO', 'accept',   0],
    'FLTR':     [Map.FLTR,  1, 'Write', 'accept',   0],
    'CYCLE':    [Map.CYCLE, 1, 'ReadO', 'accept',   0],     # (20)
    'SYST':     [Map.SYST,  1, 'ReadO', 'accept',   0],
    'CHANN':    [Map.CHANN, 1, 'ReadO', 'accept',   0],
    'SUBW':     [Map.SUBW,  1, 'ReadO', 'accept',   0],
    'SUBD':     [Map.SUBD,  1, 'ReadO', 'accept',   0],
    'SUBDF':    [Map.SUBDF, 1, 'ReadO', 'accept',   0],
    'SUBTW':    [Map.SUBTW, 1, 'ReadO', 'accept',   0],
    'RS485':    [Map.RS485, 1, 'Write', 'accept',   2001],
    'SCALE':    [Map.SCALE, 1, 'Write', 'accept',   32767],
    'STAB':     [Map.STAB,  1, 'Write', 'accept',   555],
    'PCSN':     [Map.PCSN,  1, 'WriMB', 'calc',     1],      # (30)
    'ROUND':    [Map.ROUND, 1, 'WriMB', 'calc',     1],
    'REP0':     [Map.REP0,  1, 'WriMB', 'accept',   0],
    'REP1':     [Map.REP1,  1, 'WriMB', 'accept',   10000],
    'REP2':     [Map.REP2,  1, 'WriMB', 'accept',   20000],
    'REP3':     [Map.REP3,  1, 'WriMB', 'accept',   30000],
    'CLB0':     [Map.CLB0,  1, 'WriMB', 'accept',   0],
    'CLB1':     [Map.CLB1,  1, 'WriMB', 'accept',   0],
    'CLB2':     [Map.CLB2,  1, 'WriMB', 'accept',   0],
    'CLB3':     [Map.CLB3,  1, 'WriMB', 'accept',   0],
    'ZERO':     [Map.ZERO,  1, 'CleMB', 'accept',   0],     # (40)
    'DIRR':     [Map.DIRR,  1, 'ReadO', 'accept',   0],
    'XOR':      [Map.XOR,   1, 'Write', 'accept',   127],
    'TUNLD':    [Map.TUNLD, 1, 'Write', 'accept',   0],
    'TFEED':    [Map.TFEED, 1, 'Write', 'accept',   0],
    'TMEAS':    [Map.TMEAS, 1, 'Write', 'accept',   0],
    'TBTM':     [Map.TBTM,  1, 'Write', 'accept',   0],
    'TKEYS':    [Map.TKEYS, 1, 'Write', 'accept',   0],
    'TDIAG':    [Map.TDIAG, 1, 'Write', 'accept',   0],
    'TSHRT':    [Map.TSHRT, 1, 'Write', 'accept',   0],
    'TLONG':    [Map.TLONG, 1, 'Write', 'accept',   0],     # (50)
    'TSLP':     [Map.TSLP,  1, 'Write', 'accept',   0],
    'TRDY':     [Map.TRDY,  1, 'Write', 'accept',   0],
    'TCYCL':    [Map.TCYCL, 1, 'Write', 'accept',   0],
    'AUTOS':    [Map.AUTOS, 1, 'Write', 'accept',   0],
    'NSKIP':    [Map.NSKIP, 1, 'Write', 'accept',   0],
    'TARZN':    [Map.TARZN, 1, 'Write', 'accept',   0],
    'LEV0':     [Map.LEV0,  1, 'Write', 'accept',   0],
    'TOTW':     [Map.TOTW,  1, 'Write', 'accept',   2],
    'TOTN':     [Map.TOTN,  1, 'Write', 'accept',   3],
    'UPR11':    [Map.UPR11, 1, 'Write', 'accept', 0],     # (60)
    'UPR21':    [Map.UPR21, 1, 'Write', 'accept', 0],
    'DOZF1':    [Map.DOZF1, 1, 'Write', 'accept', 0],
    'TOTW1':    [Map.TOTW1, 1, 'Write', 'accept', 0],
    'FFA1':     [Map.FFA1, 1, 'Write', 'accept', 0],
    'TOPN1':    [Map.TOPN1, 1, 'Write', 'accept', 0],
    'TMIN1':    [Map.TMIN1, 1, 'Write', 'accept', 0],
    'DOZA1':    [Map.DOZA1, 1, 'Write', 'accept', 0],
    'DOZZ1':    [Map.DOZZ1, 1, 'Write', 'accept', 0],
    'WEI1':     [Map.WEI0,  1, 'ReadO', 'calc',     0],
    'TSLW1':    [Map.TSLW1, 1, 'Write', 'accept', 0],     # (70)
    'UPR12':    [Map.UPR12, 1, 'Write', 'accept', 0],
    'UPR22':    [Map.UPR22, 1, 'Write', 'accept', 0],
    'DOZF2':    [Map.DOZF2, 1, 'Write', 'accept', 0],
    'TOTW2':    [Map.TOTW2, 1, 'Write', 'accept', 0],
    'FFA2':     [Map.FFA2, 1, 'Write', 'accept', 0],
    'TOPN2':    [Map.TOPN2, 1, 'Write', 'accept', 0],
    'TMIN2':    [Map.TMIN2, 1, 'Write', 'accept', 0],
    'DOZA2':    [Map.DOZA2, 1, 'Write', 'accept', 0],
    'DOZZ2':    [Map.DOZZ2, 1, 'Write', 'accept', 0],
    'WEI2':     [Map.WEI1,  1, 'ReadO', 'calc',     0],     # (80)
    'TSLW2':    [Map.TSLW2, 1, 'Write', 'accept', 0]
}
#nregs = len(adcRg)

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
