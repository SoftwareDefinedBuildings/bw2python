import time

from bw2python import ponames
from bw2python.bwtypes import PayloadObject
from bw2python.client import Client

bw_client = Client()
bw_client.setEntityFromEnviron()
bw_client.overrideAutoChainTo(True)

def onMessage(bw_message):
    for po in bw_message.payload_objects:
        if po.type_dotted == ponames.PODFText:
            print po.content

bw_client.subscribe("scratch.ns/demo", onMessage)

print "Subscribing. Ctrl-C to quit."
while True:
    time.sleep(10000)
