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

        self.synchronous_results = {}
        self.synchronous_results_lock = threading.Lock()
        self.synchronous_cond_vars = {}

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

    def setEntity(self, key, result_handler):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("sete", seq_num)
        po = PayloadObject((1, 0, 1, 2), None, key)
        frame.addPayloadObject(po)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def synchronousSetEntity(self, key):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("sete", seq_num)
        po = PayloadObject((1, 0, 1, 2), None, key)
        frame.addPayloadObject(po)

        def responseHandler(result):
            with self.synchronous_results_lock:
                self.synchronous_results[seq_num] = result
                self.synchronous_cond_vars[seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = responseHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            result = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        return result

    def setEntityFromFile(self, key_file_name, result_handler):
        with open(key_file_name) as f:
            f.read(1) # Strip leading byte
            key = f.read()
        self.setEntity(key, result_handler)

    def synchronousSetEntityFromFile(self, key_file_name):
        with open(key_file_name) as f:
            f.read(1) # Strip leading byte
            key = f.read()
        return self.synchronousSetEntity(key)

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

    @staticmethod
    def _createListFrame(uri, expiry, expiry_delta, elaborate_pac, auto_chain,
                         routing_objects):
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

        return frame

    def list(self, uri, response_handler, list_result_handler, primary_access_chain=None,
                expiry=None, expiry_delta=None, elaborate_pac=None, auto_chain=False,
                routing_objects=None):
        frame = _createListFrame(uri, primary_access_chain, expiry, expiry_delta,
                                elaborate_pac, auto_chain, routing_objects)

        with self.resonse_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        with self.list_result_handlers_lock:
            self.list_result_handlers[frame.seq_num] = list_result_handler
        frame.writeToSocket(self.socket)

    def synchronousList(self, uri, primary_access_chain=None, expiry=None,
                         expiry_delta=None, elaborate_pac=None, auto_chain=False,
                         routing_objects=None):
        frame = _createListFrame(uri, primary_access_chain, expiry, expiry_delta,
                                elaborate_pac, auto_chain, routing_objects)

        def responseHandler(response):
            if response.status != "okay":
                with synchronous_results_lock:
                    self.synchronous_results[frame.seq_num] = response.reason
                    self.synchronous_cond_vars[frame.seq_num].notify()

        children = []
        def listResultHandler(child):
            with synchronous_results_lock:
                if child is None:
                    self.synchronous_results[frame.seq_num] = children
                    self.synchronous_cond_vars[frame.seq_num].notify()
                else:
                    children.append(child)

        with self.response_handers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.list_result_handlers_lock:
            self.list_result_handlers[frame.seq_num] = listResultHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            result = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        # The result will be a string if an error has occurred
        if type(result) is str:
            raise RuntimeError(result)
        else:
            return result

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

    @staticmethod
    def _createMakeEntityFrame(contact, comment, expiry, expiry_delta, revokers,
                               omit_creation_date):
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

        return frame

    def makeEntity(self, response_handler, result_hanlder, contact=None, comment=None,
                   expiry=None, expiry_delta=None, revokers=None, omit_creation_date=False):
        frame = _createMakeEntityFrame(contact, comment, expiry, expiry_delta, revokers,
                                       omit_creation_date)
        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def synchronousMakeEntity(self, contact=None, comment=None, expiry=None,
                              expiry_delta=None, revokers=None, omit_creation_date=False):
        frame = _createMakeEntityFrame(contact, comment, expiry, expiry_delta, revokers,
                                       omit_creation_date)

        def responseHandler(response):
            if response.status != "okay":
                with self.synchronous_results_lock:
                    self.synchronous_results[frame.seq_num] = response.reason
                    self.synchronous_cond_vars[frame.seq_num].notify()

        def resultHandler(result):
            with self.synchronous_results_lock:
                self.synchronous_results[frame.seq_num] = result
                self.synchronous_cond_vars[frame.seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = resultHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            result = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        # The result will be a BosswaveResult object unless an error has occurred
        if type(result) is str:
            raise RuntimeError(result)
        else:
            return result

    @staticmethod
    def _createMakeDotFrame(to, ttl, is_permission, contact, comment, expiry,
                            expiry_delta, revokers, omit_creation_date,
                            access_permissions, uri):
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

        return frame

    def makeDot(self, response_handler, result_hanlder, to, ttl=None, is_permission=False,
                contact=None, comment=None, expiry=None, expiry_delta=None, revokers=None,
                omit_creation_date=False, access_permissions=None, uri=None):
        frame = _createMakeDotFrame(to, ttl, is_permission, contact, comment, expiry,
                                    expiry_delta, revokers, omit_creation_date,
                                    access_permissions, uri)

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def synchronousMakeDot(self, to, ttl=None, is_permission=False, contact=None,
                           comment=None, expiry=None, expiry_delta=None, revokers=None,
                           omit_creation_date=False, access_permissions=None, uri=None):
        frame = _createMakeDotFrame(to, tll, is_permission, contact, comment, expiry,
                                    expiry_delta, revokers, omit_creation_date,
                                    access_permissions, uri)

        def responseHandler(response):
            if response.status != "okay":
                with self.synchronous_results_lock:
                    self.synchronous_results[frame.seq_num] = response.reason
                    self.synchronous_cond_vars[frame.seq_num].notify()

        def resultHandler(result):
            with self.synchronous_results_lock:
                self.synchronous_results[frame.seq_num] = result
                self.synchronous_cond_vars[frame.seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = resultHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
            threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            result = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        # Result will be a BosswaveResponse object unless an error has occurred
        if type(result) is str:
            raise RuntimeError(result)
        else:
            return result

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

    def synchronousMakeChain(self, is_permission=False, unelaborate=False, dot=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("makc", seq_num)

        if is_permission:
            frame.addKVPair("ispermission", "true")

        if unelaborate:
            frame.addKVPair("unelaborate", "true")

        if dot is not None:
            for d in dot:
                frame.addKVPair("dot", d)

        def responseHandler(response):
            if response.status != "okay":
                with self.synchronous_results_lock:
                   self.synchronous_results[seq_num] = response.reason
                   self.synchronous_cond_vars[seq_num].notify()

        def resultHandler(result):
            with self.synchronous_results_lock:
                self.synchronous_results[seq_num] = result
                self.synchronous_cond_vars[seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            result = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        # Result is a BosswaveResultObject unless an error has occurred
        if type(result) is str:
            raise RuntimeError(result)
        else:
            return result
