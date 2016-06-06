from bw2python import ponames
from bw2python.bwtypes import PayloadObject
from bw2python.client import Client

bw_client = Client()
bw_client.setEntityFromEnviron()

for i in range(10):
    msg = "{}: Hello, World!".format(i)
    po = PayloadObject(ponames.PODFText, None, msg)
    bw_client.publish("scratch.ns/demo", auto_chain=True, payload_objects=(po,))
