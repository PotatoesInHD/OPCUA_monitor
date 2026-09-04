import time
import json
import os
import datetime

from opcua import Client
from random import randint, randrange

def opcua_connect(url: str)-> "Client":
    try:
        client = Client(url)
        client.connect()
        print("Client connected")
        return client
    except TimeoutError as err:
        print(f"Error: {err}...Retrying connection")
    except Exception as err:
        print(f"Unexpected Error: {err}...Retrying connection")

def opcua_read(node) -> int:
    return node.get_value()

def opcua_write(node, value: int) -> None:
    node.set_value()


def main() -> None:

    url = "opc.tcp://10.0.0.114:4840"
    #client = opcua_connect(url)
    #while client is None:
      # client = opcua_connect(url)
       #time.sleep(5)

    #conn_monitor = client.get_node("ns=2;i=4")
    #opcua_write(conn_monitor, 1)


    #date = datetime.datetime.now()

    # "nt" means windows otherwise use "-"
    pad = "#" if os.name == "nt" else "-"
    date = datetime.date.today()
    bs_filename = date.strftime(f"%{pad}m-%{pad}d-%Y-BS.mdb")

    time.sleep(5)

    while True:

        #print(str(date)[0:11])
        #print(day_of_week)
        #print(date)
        print(bs_filename)
        time.sleep(5)

if __name__ == "__main__":
    main()
