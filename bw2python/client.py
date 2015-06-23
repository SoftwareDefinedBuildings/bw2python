import datetime
import random
import socket
import threading

from bwtypes import Frame, RoutingObject, PayloadObject

class Client(object):
    def __init__(self, host_name, port):
        self.host_name = host_name
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.response_handlers = {}
        self.response_handlers_lock = threading.Lock()
        self.result_handlers = {}
        self.result_handlers_lock = threading.Lock()

        self.listener_thread = threading.Thread(target=_readFrame, args=(self,))
        listener_thread.start()

    def connect(self):
        self.socket.connect((self.host_name, self.port))

    def close(self):
        self.socket.close()

    @staticmethod
    def _utcToRfc3339(dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _readFrame(self):
        while True:
            frame = Frame.readFromSocket(self.socket)

            seq_num = frame.seq_num
            if frame.command == "rslt":
                with response_handlers_lock:
                    handler = response_handlers.get(seq_num)
                if handler is not None:
                    status = frame.getFirstValue("status")
                    if status != "okay":
                        reason = frame.getFirstValue("reason")
                    else:
                        reason = None
                response = BosswaveResponse(status, reason)
                handler(response)

            elif frame.command == "resp":
                with result_handlers_lock:
                    handler = result_handlers.get(seq_num)
                if handler is not None:
                    from_ = frame.getFirstValue("from")
                    uri = frame.getFirstValue("uri")

                    unpack = frame.getFirstValue("unpack")
                    if unpack is not None and unpack.lower() == "true":
                        result = BosswaveResult(fromVal, uri, frame.routing_objects,
                                                frame.payload_objects)
                    else:
                        result = BosswaveResult(from_, uri, None, None)
                    handler(result)

            else:
                pass # Ignore frames of any other type

    def setEntityFromFile(key_file_name, result_handler):
        with open(key_file_name) as f:
            f.read(1) # Strip leading byte
            key = f.read()
        setEntity(key, result_handler)

    def setEntity(key, result_handler):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("sete", seq_num)
        po = PayloadObject((1, 0, 1, 2), key)
        frame.addPayloadObject(po)

        with response_handlers_lock:
            response_handers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def subscribe(uri, response_handler, result_handler, primary_access_chain=None,
                  expiry=None, expiry_delta=None, elaborate_pac=None, unpack=True,
                  routing_objects=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("subs", seq_num)
        frame.addKVPair("uri", uri)

        if primary_access_chain is not None:
            frame.addKVPair("primary_access_chain", primary_access_chain)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utcToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if elaborate_pac is not None:
            if elaborate_pac.lower() == "full":
                frame.addKVPair("elaborate_pac", "full")
            else:
                frame.addKVPair("elaborate_pac", "partial")

        if unpack:
            frame.addKVPair("unpack", "true")
        else:
            frame.addKVPair("unpack", "false")

        for ro in routing_objects:
            frame.addRoutingObject(ro)

        with response_handlers_lock:
            response_handlers[seq_num] = response_handler
        with result_handlers_lock:
            result_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def publish(uri, response_handler, persist=False, primary_access_chain=None,
                expiry=None, expiry_delta=None, elaborate_pac=None, routing_objects=None,
                payload_objects=None):
        seq_num = Frame.generateSequenceNumber()
        if persist:
            frame = Frame("pers", seq_num)
        else:
            frame = Frame("publ", seq_num)
        frame.addKVPair("uri", uri)

        if primary_access_chain is not None:
            frame.addKVPair("primary_access_chain", primary_access_chain)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utcToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if elaborate_pac is not None:
            if elaborate_pac.lower() == "full":
                frame.addKVPair("elaborate_pac", "full")
            else:
                frame.addKVPair("elaborate_pac", "partial")

        for ro in routing_objects:
            frame.addRoutingObject(ro)
        for po in payload_objects:
            frame.addPayloadObjects(po)

        with response_handlers_lock:
            response_handlers[seq_num] = response_handler
        frame.writeToSocket(self.socket)
