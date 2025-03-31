"""
Dictionnaires  but_i <-> [minute, seconde, id_buteur, team]
"""

buts_rcl_mhsc = { "but_1": [15, 4, 154048, 1], "but_2": [25, 11, 106821, 1], "but_3" : [35, 23, 186796, 0], "but_4" : [49, 55, 59325, 0], "but_5" : [68, 10, 167443, 1] }
buts_mhsc_metz = { "but_1": [23, 50, 98826, 1], "but_2": [69, 46, 442793, 1], "but_3" : [79, 3, 78275, 0], "but_4" : [90, 50, 477724, 0] }
buts_rcsa_mhsc = { "but_1": [35, 15, 167443, 1], "but_2": [45, 36, 73965, 1], "but_3" : [48, 51, 167443, 1], "but_4" : [68, 32, 168539, 0], "but_5" : [94, 38, 433640, 0] }


def convertir_temps(buts):
    """
    Conversion en ms des timers de buts
    """
    timers_buts = []
    for value in buts.values() :
        timers_buts.append((value[0]*60+value[1])*1000)
    return timers_buts

def convertir_temps(buts):
    """
    Conversion en minutes
    """
    timers_buts = []
    for value in buts.values() :
        timers_buts.append(value[0]+1)
    return timers_buts
