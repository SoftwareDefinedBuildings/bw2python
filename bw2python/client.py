import datetime
import socket
import threading

from bwtypes import *

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
                    reason = frame.getFirstValue("reason")
                    response = BosswaveResponse(status, reason)
                    handler(response)

            elif frame.command == "rslt":
                finished = frame.getFirstValue("finished")

                with self.result_handlers_lock:
                    message_handler = self.result_handlers.get(seq_num)
                    if message_handler is not None and finished == "true":
                        del self.result_handlers[seq_num]
                with self.list_result_handlers_lock:
                    list_result_handler = self.list_result_handlers.get(seq_num)
                    if list_result_handler is not None and finished == "true":
                        del self.list_result_handlers[seq_num]
                if message_handler is not None:
                    from_ = frame.getFirstValue("from")
                    uri = frame.getFirstValue("uri")

                    unpack = frame.getFirstValue("unpack")
                    if unpack is not None and unpack.lower() == "false":
                        result = BosswaveResult(from_, uri, None, None)
                    else:
                        result = BosswaveResult(from_, uri, frame.routing_objects,
                                                frame.payload_objects)
                    message_handler(result)
                elif list_result_handler is not None:
                    if finished == "true":
                        list_result_handler(None)
                    else:
                        child = frame.getFirstValue("child")
                        list_result_handler(child)

    def __init__(self, host_name, port):
        self.host_name = host_name
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.response_handlers = {}
        self.response_handlers_lock = threading.Lock()
        self.result_handlers = {}
        self.result_handlers_lock = threading.Lock()
        self.list_result_handlers_lock = threading.Lock()
        self.list_result_handlers = {}

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
        po = PayloadObject((1, 0, 1, 2), None, key)
        frame.addPayloadObject(po)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def subscribe(self, uri, response_handler, result_handler, primary_access_chain=None,
                  expiry=None, expiry_delta=None, elaborate_pac=None, unpack=True,
                  auto_chain=False, routing_objects=None):
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

        if auto_chain:
            frame.addKVPair("autochain", "true")

        if routing_objects is not None:
            for ro in routing_objects:
                frame.addRoutingObject(ro)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def publish(self, uri, response_handler, persist=False, primary_access_chain=None,
                expiry=None, expiry_delta=None, elaborate_pac=None, auto_chain=False,
                routing_objects=None, payload_objects=None):
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

        if auto_chain:
            frame.addKVPair("autochain", "true")

        if routing_objects is not None:
            for ro in routing_objects:
                frame.addRoutingObject(ro)
        if payload_objects is not None:
            for po in payload_objects:
                frame.addPayloadObject(po)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        frame.writeToSocket(self.socket)

    def list(self, uri, response_handler, list_result_handler, primary_access_chain=None,
                expiry=None, expiry_delta=None, elaborate_pac=None, auto_chain=False,
                routing_objects=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("list", seq_num)

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

        if auto_chain:
            frame.addKVPair("autochain", "true")

        if routing_objects is not None:
            for ro in routing_objects:
                frame.addRoutingObject(ro)

        with self.resonse_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.list_result_handlers_lock:
            self.list_result_handlers[seq_num] = list_result_handler
        frame.writeToSocket(self.socket)

    def query(self, uri, response_handler, result_handler, primary_access_chain=None,
                expiry=None, expiry_delta=None, elaborate_pac=None, unpack=True,
                auto_chain=False, routing_objects=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("quer", seq_num)

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

        if auto_chain:
            frame.addKVPair("autochain", "true")


        if routing_objects is not None:
            for ro in routing_objects:
                frame.addRoutingObject(ro)

        with self.resonse_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def makeEntity(self, response_handler, result_hanlder, contact=None, comment=None,
                   expiry=None, expiry_delta=None, revokers=None, omit_creation_date=False):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("make", seq_num)

        if contact is not None:
            frame.addKVPair("contact", contact)
        if comment is not None:
            frame.addKVPair("comment", comment)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utfToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if revokers is not None:
            for revoker in reovkers:
                frame.addKVPair("revoker", revoker)
        if omit_creation_date:
            frame.addKVPair("omitcreationdate", "true")
        else:
            frame.addKVPair("omitcreationdate", "false")

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def makeDot(self, response_handler, result_hanlder, to, ttl=None, is_permission=False,
                contact=None, comment=None, expiry=None, expiry_delta=None, revokers=None,
                omit_creation_date=False, access_permissions=None, uri=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("makd", seq_num)
        frame.addKVPair("to", to)

        if ttl is not None:
            frame.addKVPair("ttl", str(ttl))

        if is_permission:
            frame.addKVPair("ispermission", "true")

        if contact is not None:
            frame.addKVPair("contact", contact)
        if comment is not None:
            frame.addKVPair("comment", comment)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utfToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if revokers is not None:
            for revoker in reovkers:
                frame.addKVPair("revoker", revoker)

        if omit_creation_date:
            frame.addKVPair("omitcreationdate", "true")
        else:
            frame.addKVPair("omitcreationdate", "false")

        if access_permissions is not None:
            frame.addKVPair("accesspermissions", access_permissions)

        if uri is not None:
            frame.addKVPair("uri", uri)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def makeChain(self, response_handler, result_handler, is_permission=False,
                  unelaborate=False, dot=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("makc", seq_num)

        if is_permission:
            frame.addKVPair("ispermission", "true")

        if unelaborate:
            frame.addKVPair("unelaborate", "true")

        if dot is not None:
            for d in dot:
                frame.addKVPair("dot", d)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)
