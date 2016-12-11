import json
import sys
import time

from bw2python import ponames
from bw2python.bwtypes import PayloadObject
from bw2python.client import Client

if len(sys.argv) != 2:
    print "Usage: {} <num_iterations>".format(sys.argv[0])
    sys.exit(1)

with open("params.json") as f:
    try:
        params = json.loads(f.read())
    except ValueError:
        print "Invalid parameter file"
        sys.exit(1)

dest_uri = params.get("dest_uri")
if dest_uri is None:
    print "No 'dest_uri' parameter specified"
    sys.exit(1)
message = params.get("message")
if message is None:
    print "No 'message' parameter specified"
    sys.exit(1)

try:
    num_iters = int(sys.argv[1])
except ValueError:
    print "Invalid number of iterations specified"
    sys.exit(1)

bw_client = Client()
bw_client.setEntityFromEnviron()
bw_client.overrideAutoChainTo(True)

for i in range(num_iters):
    msg = "({}) {}".format(i, message)
    po = PayloadObject(ponames.PODFString, None, msg)
    bw_client.publish(dest_uri, payload_objects=(po,))
    time.sleep(1)

print "Emitted {} messages. Terminating".format(num_iters)
