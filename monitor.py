import os
from threading import Thread
from time import sleep
from pysnmp.entity.rfc3413.oneliner import cmdgen

from trappy import run_trap_service, get_interface_status

cmdGen = cmdgen.CommandGenerator()
community = "ro_R1"
target_host = "192.168.0.1"

def send_snmp_query(oid):
    errorInd, errorStat, errorIdx, varBinds = cmdGen.getCmd(cmdgen.CommunityData(community), cmdgen.UdpTransportTarget((target_host, 161)), oid)
    if errorInd:
        print(errorInd)
        return -1
    else:
        if errorStat:
            print(f"Ha ocurrido un error: {errorStat.prettyPrint()} en {errorIdx and varBinds[int(errorIdx)-1] or '?'}")
        else:
            for _, val in varBinds:
                return str(val)

REFRESH_TIME = 5

FIRST_VALUE = 0
LAST_ACCUMULATED = 0

if __name__ == "__main__":
    Thread(target=run_trap_service).start()

    if os.path.isfile("monitor.log"):
        os.remove("monitor.log")

    while(True):
        data = int(send_snmp_query("1.3.6.1.2.1.2.2.1.10.3"))
        if data != -1: 
           data = int(data/84) - FIRST_VALUE
        with open("monitor.log", "a+") as f:
            interface_status = get_interface_status()
            all_status = [ x.split(" = ")[1].replace("\n", "") for x in interface_status ]
            if len(all_status) > 0:
                # Encontre un status, validar si es Down, si es up, no hay problema
                last_status = all_status[len(all_status) - 1]
                
                if data < 0:
                    f.write(f"{None}\n")
                    sleep(REFRESH_TIME)
                    continue
            f.seek(0)
            all_lines = f.readlines()[::-1]
            if len(all_lines) == 0 and data != -1:
                f.seek(0,2)
                FIRST_VALUE = data
                f.write(f"{0}\n")
            elif data != -1:
                f.seek(0,2)
                print(data)
                to_write = data - LAST_ACCUMULATED
                LAST_ACCUMULATED += to_write
                f.write(f"{to_write}\n")

        sleep(REFRESH_TIME)
