from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import os

import logging

logging.basicConfig(filename="traps.log", filemode="w", format="%(asctime)s === %(message)s", level=logging.INFO)

snmpEngine = engine.SnmpEngine()

traps_host = "192.168.0.10"

config.addTransport(snmpEngine, udp.domainName + (1,), udp.UdpTransport().openServerMode((traps_host, 162)))

config.addV1System(snmpEngine,"ro_R1","ro_R1")
def cbTraps(sE, stRef, ctxId, ctxName, varBinds, cbCtx):
    print("Mensaje recibido")
    logging.info("Nuevo mensaje recibido")
    for name, val in varBinds:
        logging.info(f"{name.prettyPrint()} = {val.prettyPrint()}")

ntfrcv.NotificationReceiver(snmpEngine, cbTraps)
snmpEngine.transportDispatcher.jobStarted(1)


def get_interface_status():
    int_status = []
    if os.path.isfile("traps.log"):
        with open("traps.log") as traps:
            all_lines = traps.readlines()
            int_status = list(filter(lambda x: x.find("1.3.6.1.4.1.9.2.2.1.1.20.2") != -1, all_lines))
    else:
        return None
        
    return int_status

def run_trap_service():
    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except Exception as ex:
        print(ex)
        logging.info(ex)
        snmpEngine.transportDispatcher.closeDispatcher()
        raise

if __name__ == "__main__":
    logging.info("Traps listening to " + traps_host + " on port 162")
    logging.info("-" * 100)
    run_trap_service()
