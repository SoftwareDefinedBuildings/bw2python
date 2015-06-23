class RoutingObject(object):
    def __init__(self, number, content):
        if number < 0 or number > 255:
            raise ValueError("Routing object number must be between 0 and 255")

        self.number = number
        self.content = content

# TODO Need to fix constructors here
class PayloadObject(object):
    def __init__(self, type_dotted, content):
        if not _validate_dotted_form(type_dotted):
            raise ValueError("Dotted payload type must contain four elements between 0 and 255")

        self.type_dotted = type_dotted
        self.type_num = None
        self.content = content

    def __init__(self, type_num, content):
        if not _validate_type_num():
            raise ValueError("Payload type number must contain 1 or 2 digits")

        self.type_dotted = None
        self.type_num = type_num
        self.content = content

    def __init__(self, type_dotted, type_num, content):
        if not _validate_dotted_form(type_dotted):
            raise ValueError("Dotted payload type must contain four elements between 0 and 255")
        if not _validate_type_num(type_num):
            raise ValueError("Payload type number must contain 1 or 2 digits")

        self.type_dotted = type_dotted
        self.type_num = type_num
        self.content = content

    def _validate_type_num(type_num):
        return 0 < type_num < 100

    def _validate_dotted_form(type_dotted):
        return len(type_dotted) == 4 and all([0 < x < 255 for x in type_dotted])

class Frame(object):
    def __init__(self, command, seq_no):
        self.command = command
        self.seq_no = seq_no
        self.kv_pairs = []
        self.routing_objects = []
        self.payload_objects = []

    def addKVPair(key, value):
        kv_pairs.append((key, value))

    def addRoutingObject(ro):
        self.routing_objects.append(ro)

    def addPayloadObject(po):
        self.payload_objects.append(po)

    def getFirstValue(key):
        matchingValues = [y for x,y in self.kv_pairs if x == key]
        if len(matchingValues) > 0:
            return matches[0]
        else:
            return None

    def writeToSocket(self, sock):
        body = "{0} 0000000000 {0:010d}\n".format(command, seqNo)
        for (key, value) in self.kv_pairs:
            body += "kv {0} {1}\n".format(key, len(value))
            body.extend(value + "\n")

        for ro in self.routing_objects:
            body += "ro {0} {1}\n".format(ro.number, len(ro.content))
            body += ro.content + "\n"

        for po in self.payload_objects:
            typeStr = ""
            if po.typeOctet is not None:
                typeStr += "{0}.{1}.{2}.{3}".format(*po.typeOctet)
            typeStr += ":"
            if po.typeNum is not None:
                typeStr += str(po.typeNum)

            body += "po {0} {1}\n".format(typeStr, len(po.content))
            body += po.content + "\n"

        body += "\n"
        socket.sendall(body)

    @classmethod
    def readFromSocket(cls, socket):
        with socket.makefile() as f:
            frame_header = f.readline()
            header_items = f.split(' ')
            if len(header_items) != 3:
                raise ValueError("Frame header must contain 3 fields")

            command = header_items[0]
            frame_length = int(header_items[1])
            if frame_length < 0:
                raise ValueError("Negative frame length")
            seq_no = int(header_items[2])
            frame = cls(command, seq_no)

            current_line = reader.readline()
            while current_line != '\n':
                fields = current_line.split(' ')
                if len(fields) != 3:
                    raise ValueError("Invalid item header: " + current_line)

                if fields[0] == "kv":
                    key = fields[1]
                    value_len = int(fields[2])

                    value = f.read(value_len)
                    frame.addKVPair(key, value)
                    f.read(1) # Strip trailing \n

                elif fields[0] == "ro":
                    ro_num = int(fields[1])
                    body_len = int(fields[2])
                    body = f.read(body_len)
                    ro = RoutingObject(ro_num, value)
                    frame.addRoutingObject(ro)
                    f.read(1) # Strip trailing \n

                elif fields[0] == "po":
                    body_len = int(fields[2])
                    body = f.read(body_len)

                    po_type = fields[1]
                    if ':' not in po_type:
                        raise ValueError("Inavlid payload object type: " + po_type)
                    if po_type.startswith(':'):
                        po_type_num = int(po_type[1:])
                        po = PayloadObject(po_type_num, body)
                    elif po_type.endswith(':'):
                        po_type_dotted = [int(x) for x in po_type[:-1].split('.')]
                        po = PayloadObject(po_type_dotted, content)
                    else:
                        type_tokens = po_type.split(':')
                        if len(type_tokens) != 2:
                            raise ValueError("Invalid payload object type: " + po_type)
                        po_type_dotted = [int(x) for x in type_tokens[0].split('.')]
                        po_type_num = int(type_tokens[1])
                        po = PayloadObject(po_type_dotted, po_type_num, content)

                    frame.addPayloadObject(po)
                    f.read(1) # Strip trailing \n

                else:
                    raise ValueError("Invalid item header: " + current_line)

                current_line = f.readline()
            return frame

    @staticmethod
    def generateSequenceNumber():
        return random.randint(0, 1e10) #TODO: Okay to exceed INT_MAX?
