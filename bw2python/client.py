import datetime
import socket
import threading

from bwtypes import Frame, RoutingObject, PayloadObject, BosswaveResult, BosswaveResponse

class Client(object):
    def _readFrame(self):
        while True:
            frame = Frame.readFromSocket(self.socket)

            seq_num = frame.seq_num
            if frame.command == "resp":
                with self.response_handlers_lock:
                    handler = self.response_handlers.pop(seq_num, None)
                if handler is not None:
                    status = frame.getFirstValue("status")
                    if status != "okay":
                        reason = frame.getFirstValue("reason")
                    else:
                        reason = None
                response = BosswaveResponse(status, reason)
                handler(response)

            elif frame.command == "rslt":
                with self.result_handlers_lock:
                    handler = self.result_handlers.get(seq_num)
                if handler is not None:
                    from_ = frame.getFirstValue("from")
                    uri = frame.getFirstValue("uri")

                    unpack = frame.getFirstValue("unpack")
                    if unpack is not None and unpack.lower() == "false":
                        result = BosswaveResult(from_, uri, None, None)
                    else:
                        result = BosswaveResult(from_, uri, frame.routing_objects,
                                                frame.payload_objects)
                    handler(result)

            else:
                pass # Ignore frames of any other type

    def __init__(self, host_name, port):
        self.host_name = host_name
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.response_handlers = {}
        self.response_handlers_lock = threading.Lock()
        self.result_handlers = {}
        self.result_handlers_lock = threading.Lock()

    def connect(self):
        self.socket.connect((self.host_name, self.port))
        frame = Frame.readFromSocket(self.socket)
        if frame.command != "helo":
            self.close()
            raise RuntimeError("Received invalid Bosswave ACK")

        self.listener_thread = threading.Thread(target=self._readFrame)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def close(self):
        self.socket.close()

    @staticmethod
    def _utcToRfc3339(dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    def setEntityFromFile(self, key_file_name, result_handler):
        with open(key_file_name) as f:
            f.read(1) # Strip leading byte
            key = f.read()
        self.setEntity(key, result_handler)

    def setEntity(self, key, result_handler):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("sete", seq_num)
        po = PayloadObject((1, 0, 1, 2), key)
        frame.addPayloadObject(po)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def subscribe(self, uri, response_handler, result_handler, primary_access_chain=None,
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

        if routing_objects is not None:
            for ro in routing_objects:
                frame.addRoutingObject(ro)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def publish(self, uri, response_handler, persist=False, primary_access_chain=None,
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

        if routing_objects is not None:
            for ro in routing_objects:
                frame.addRoutingObject(ro)
        if payload_objects is not None:
            for po in payload_objects:
                frame.addPayloadObject(po)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        frame.writeToSocket(self.socket)
