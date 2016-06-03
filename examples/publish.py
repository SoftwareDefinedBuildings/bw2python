from bw2python import potypes
from bw2python.bwtypes import PayloadObject
from bw2python.client import Client

bw_client = Client('localhost', 28589)
bw_client.connect()
bw_client.setEntityFromEnviron()

po = PayloadObject(potypes.PO_DF_TEXT, None, "Hello, World!")
for i in range(10):
    bw_client.publish("scratch.ns/demo", auto_chain=True, payload_objects=(po,))
