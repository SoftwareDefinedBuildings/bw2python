import time

from bw2python import potypes
from bw2python.bwtypes import PayloadObject
from bw2python.client import Client

bw_client = Client('localhost', 28589)
bw_client.connect()
bw_client.setEntityFromEnviron()

def onMessage(bw_message):
    for po in bw_message.payload_objects:
        if po.type_dotted == potypes.PO_DF_TEXT:
            print po.content
bw_client.subscribe("scratch.ns/demo", onMessage)

print "Subscribing. Ctrl-C to quit."
while True:
    time.sleep(10000)
