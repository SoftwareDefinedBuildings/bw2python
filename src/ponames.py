# Double (1.0.2.0/32): Double
# This payload is an 8 byte long IEEE 754 double floating point value encoded in
# little endian. This should only be used if the semantic meaning is obvious in
# the context, otherwise a PID with a more specific semantic meaning should be
# used.
PONumDouble = 16777728
PODFMaskDouble = "1.0.2.0/32"
PODFDouble = (1, 0, 2, 0)
POMaskDouble = 32

# BWMessage (1.0.1.1/32): Packed Bosswave Message
# This object contains an entire signed and encoded bosswave message
PONumBWMessage = 16777473
PODFMaskBWMessage = "1.0.1.1/32"
PODFBWMessage = (1, 0, 1, 1)
POMaskBWMessage = 32

# SpawnpointSvcHb (2.0.2.2/32): SpawnPoint Service Heartbeat
# A heartbeat from spawnpoint about a currently running service. It is a msgpack
# dictionary that contains the keys "SpawnpointURI", "Name", "Time", "MemAlloc",
# and "CpuShares".
PONumSpawnpointSvcHb = 33554946
PODFMaskSpawnpointSvcHb = "2.0.2.2/32"
PODFSpawnpointSvcHb = (2, 0, 2, 2)
POMaskSpawnpointSvcHb = 32

# Wavelet (1.0.6.1/32): Wavelet binary
# This object contains a BOSSWAVE Wavelet
PONumWavelet = 16778753
PODFMaskWavelet = "1.0.6.1/32"
PODFWavelet = (1, 0, 6, 1)
POMaskWavelet = 32

# SpawnpointHeartbeat (2.0.2.1/32): SpawnPoint heartbeat
# A heartbeat message from spawnpoint. It is a msgpack dictionary that contains
# the keys "Alias", "Time", "TotalMem", "TotalCpuShares", "AvailableMem", and
# "AvailableCpuShares".
PONumSpawnpointHeartbeat = 33554945
PODFMaskSpawnpointHeartbeat = "2.0.2.1/32"
PODFSpawnpointHeartbeat = (2, 0, 2, 1)
POMaskSpawnpointHeartbeat = 32

# ROPermissionDChain (0.0.0.18/32): Permission DChain
# A permission dchain
PONumROPermissionDChain = 18
PODFMaskROPermissionDChain = "0.0.0.18/32"
PODFROPermissionDChain = (0, 0, 0, 18)
POMaskROPermissionDChain = 32

# ROEntityWKey (0.0.0.50/32): Entity with signing key
# An entity with signing key
PONumROEntityWKey = 50
PODFMaskROEntityWKey = "0.0.0.50/32"
PODFROEntityWKey = (0, 0, 0, 50)
POMaskROEntityWKey = 32

# ROAccessDOT (0.0.0.32/32): Access DOT
# An access DOT
PONumROAccessDOT = 32
PODFMaskROAccessDOT = "0.0.0.32/32"
PODFROAccessDOT = (0, 0, 0, 32)
POMaskROAccessDOT = 32

# ROOriginVK (0.0.0.49/32): Origin verifying key
# The origin VK of a message that does not contain a PAC
PONumROOriginVK = 49
PODFMaskROOriginVK = "0.0.0.49/32"
PODFROOriginVK = (0, 0, 0, 49)
POMaskROOriginVK = 32

# RODRVK (0.0.0.51/32): Designated router verifying key
# a 32 byte designated router verifying key
PONumRODRVK = 51
PODFMaskRODRVK = "0.0.0.51/32"
PODFRODRVK = (0, 0, 0, 51)
POMaskRODRVK = 32

# Binary (0.0.0.0/4): Binary protocols
# This is a superclass for classes that are generally unreadable in their plain
# form and require translation.
PONumBinary = 0
PODFMaskBinary = "0.0.0.0/4"
PODFBinary = (0, 0, 0, 0)
POMaskBinary = 4

# ROAccessDChainHash (0.0.0.1/32): Access DChain hash
# An access dchain hash
PONumROAccessDChainHash = 1
PODFMaskROAccessDChainHash = "0.0.0.1/32"
PODFROAccessDChainHash = (0, 0, 0, 1)
POMaskROAccessDChainHash = 32

# ROAccessDChain (0.0.0.2/32): Access DChain
# An access dchain
PONumROAccessDChain = 2
PODFMaskROAccessDChain = "0.0.0.2/32"
PODFROAccessDChain = (0, 0, 0, 2)
POMaskROAccessDChain = 32

# HamiltonBase (2.0.4.0/24): Hamilton Messages
# This is the base class for messages used with the Hamilton motes. The only key
# guaranteed is "#" that contains a uint16 representation of the serial of the
# mote the message is destined for or originated from.
PONumHamiltonBase = 33555456
PODFMaskHamiltonBase = "2.0.4.0/24"
PODFHamiltonBase = (2, 0, 4, 0)
POMaskHamiltonBase = 24

# YAML (67.0.0.0/8): YAML
# This class is for schemas that are represented in YAML
PONumYAML = 1124073472
PODFMaskYAML = "67.0.0.0/8"
PODFYAML = (67, 0, 0, 0)
POMaskYAML = 8

# RORevocation (0.0.0.80/32): Revocation
# A revocation for an Entity or a DOT
PONumRORevocation = 80
PODFMaskRORevocation = "0.0.0.80/32"
PODFRORevocation = (0, 0, 0, 80)
POMaskRORevocation = 32

# JSON (65.0.0.0/8): JSON
# This class is for schemas that are represented in JSON
PONumJSON = 1090519040
PODFMaskJSON = "65.0.0.0/8"
PODFJSON = (65, 0, 0, 0)
POMaskJSON = 8

# InterfaceDescriptor (2.0.6.1/32): InterfaceDescriptor
# This object is used to describe an interface. It contains "uri",
# "iface","svc","namespace" "prefix" and "metadata" keys.
PONumInterfaceDescriptor = 33555969
PODFMaskInterfaceDescriptor = "2.0.6.1/32"
PODFInterfaceDescriptor = (2, 0, 6, 1)
POMaskInterfaceDescriptor = 32

# ROEntity (0.0.0.48/32): Entity
# An entity
PONumROEntity = 48
PODFMaskROEntity = "0.0.0.48/32"
PODFROEntity = (0, 0, 0, 48)
POMaskROEntity = 32

# HSBLightMessage (2.0.5.1/32): HSBLight Message
# This object may contain "hue", "saturation", "brightness" fields with a float
# from 0 to 1. It may also contain an "state" key with a boolean. Omitting fields
# leaves them at their previous state.
PONumHSBLightMessage = 33555713
PODFMaskHSBLightMessage = "2.0.5.1/32"
PODFHSBLightMessage = (2, 0, 5, 1)
POMaskHSBLightMessage = 32

# SMetadata (2.0.3.1/32): Simple Metadata entry
# This contains a simple "val" string and "ts" int64 metadata entry. The key is
# determined by the URI. Other information MAY be present in the msgpacked object.
# The timestamp is used for merging metadata entries.
PONumSMetadata = 33555201
PODFMaskSMetadata = "2.0.3.1/32"
PODFSMetadata = (2, 0, 3, 1)
POMaskSMetadata = 32

# LogDict (2.0.1.0/24): LogDict
# This class is for log messages encoded in msgpack
PONumLogDict = 33554688
PODFMaskLogDict = "2.0.1.0/24"
PODFLogDict = (2, 0, 1, 0)
POMaskLogDict = 24

# ROPermissionDOT (0.0.0.33/32): Permission DOT
# A permission DOT
PONumROPermissionDOT = 33
PODFMaskROPermissionDOT = "0.0.0.33/32"
PODFROPermissionDOT = (0, 0, 0, 33)
POMaskROPermissionDOT = 32

# BWRoutingObject (0.0.0.0/24): Bosswave Routing Object
# This class and schema block is reserved for bosswave routing objects represented
# using the full PID.
PONumBWRoutingObject = 0
PODFMaskBWRoutingObject = "0.0.0.0/24"
PODFBWRoutingObject = (0, 0, 0, 0)
POMaskBWRoutingObject = 24

# BW2Chat_ChatMessage (2.0.7.2/32): BW2Chat_ChatMessage
# A textual message to be sent to all members of a chatroom. This is a dictionary
# with three keys: 'Room', the name of the room to publish to (this is actually
# implicit in the publishing), 'From', the alias you are using for the chatroom,
# and 'Message', the actual string to be displayed to all users in the room.
PONumBW2Chat_ChatMessage = 33556226
PODFMaskBW2Chat_ChatMessage = "2.0.7.2/32"
PODFBW2Chat_ChatMessage = (2, 0, 7, 2)
POMaskBW2Chat_ChatMessage = 32

# BW2Chat_CreateRoomMessage (2.0.7.1/32): BW2Chat_CreateRoomMessage
# A dictionary with a single key "Name" indicating the room to be created. This
# will likely be deprecated.
PONumBW2Chat_CreateRoomMessage = 33556225
PODFMaskBW2Chat_CreateRoomMessage = "2.0.7.1/32"
PODFBW2Chat_CreateRoomMessage = (2, 0, 7, 1)
POMaskBW2Chat_CreateRoomMessage = 32

# CapnP (3.0.0.0/8): Captain Proto
# This class is for captain proto interfaces. Schemas below this should include
# the key "schema" with a url to their .capnp file
PONumCapnP = 50331648
PODFMaskCapnP = "3.0.0.0/8"
PODFCapnP = (3, 0, 0, 0)
POMaskCapnP = 8

# FMDIntentString (64.0.1.1/32): FMD Intent String
# A plain string used as an intent for the follow-me display service.
PONumFMDIntentString = 1073742081
PODFMaskFMDIntentString = "64.0.1.1/32"
PODFFMDIntentString = (64, 0, 1, 1)
POMaskFMDIntentString = 32

# ROPermissionDChainHash (0.0.0.17/32): Permission DChain hash
# A permission dchain hash
PONumROPermissionDChainHash = 17
PODFMaskROPermissionDChainHash = "0.0.0.17/32"
PODFROPermissionDChainHash = (0, 0, 0, 17)
POMaskROPermissionDChainHash = 32

# AccountBalance (64.0.1.2/32): Account balance
# A comma seperated representation of an account and its balance as
# addr,decimal,human_readable. For example
# 0x49b1d037c33fdaad75d2532cd373fb5db87cc94c,57203431159181996982272,57203.4311
# Ether  . Be careful in that the decimal representation will frequently be bigger
# than an int64.
PONumAccountBalance = 1073742082
PODFMaskAccountBalance = "64.0.1.2/32"
PODFAccountBalance = (64, 0, 1, 2)
POMaskAccountBalance = 32

# SpawnpointConfig (67.0.2.0/32): SpawnPoint config
# A configuration file for SpawnPoint (github.com/immesys/spawnpoint)
PONumSpawnpointConfig = 1124073984
PODFMaskSpawnpointConfig = "67.0.2.0/32"
PODFSpawnpointConfig = (67, 0, 2, 0)
POMaskSpawnpointConfig = 32

# BW2Chat_LeaveRoom (2.0.7.4/32): BW2Chat_LeaveRoom
# Notify users in the chatroom that you have left. Dictionary with a single key
# "Alias" that has a value of your nickname
PONumBW2Chat_LeaveRoom = 33556228
PODFMaskBW2Chat_LeaveRoom = "2.0.7.4/32"
PODFBW2Chat_LeaveRoom = (2, 0, 7, 4)
POMaskBW2Chat_LeaveRoom = 32

# ROExpiry (0.0.0.64/32): Expiry
# Sets an expiry for the message
PONumROExpiry = 64
PODFMaskROExpiry = "0.0.0.64/32"
PODFROExpiry = (0, 0, 0, 64)
POMaskROExpiry = 32

# BinaryActuation (1.0.1.0/32): Binary actuation
# This payload object is one byte long, 0x00 for off, 0x01 for on.
PONumBinaryActuation = 16777472
PODFMaskBinaryActuation = "1.0.1.0/32"
PODFBinaryActuation = (1, 0, 1, 0)
POMaskBinaryActuation = 32

# BW2ChatMessages (2.0.7.0/24): BW2ChatMessages
# These are MsgPack dictionaries sent for the BW2Chat program
# (https://github.com/gtfierro/bw2chat)
PONumBW2ChatMessages = 33556224
PODFMaskBW2ChatMessages = "2.0.7.0/24"
PODFBW2ChatMessages = (2, 0, 7, 0)
POMaskBW2ChatMessages = 24

# Blob (1.0.0.0/8): Blob
# This is a class for schemas that do not use a public encoding format. In general
# it should be avoided. Schemas below this should include the key "readme" with a
# url to a description of the schema that is sufficiently detailed to allow for a
# developer to reverse engineer the protocol if required.
PONumBlob = 16777216
PODFMaskBlob = "1.0.0.0/8"
PODFBlob = (1, 0, 0, 0)
POMaskBlob = 8

# SpawnpointLog (2.0.2.0/32): Spawnpoint stdout
# This contains stdout data from a spawnpoint container. It is a msgpacked
# dictionary that contains a "service" key, a "time" key (unix nano timestamp) and
# a "contents" key and a "spalias" key.
PONumSpawnpointLog = 33554944
PODFMaskSpawnpointLog = "2.0.2.0/32"
PODFSpawnpointLog = (2, 0, 2, 0)
POMaskSpawnpointLog = 32

# BW2Chat_JoinRoom (2.0.7.3/32): BW2Chat_JoinRoom
# Notify users in the chatroom that you have joined. Dictionary with a single key
# "Alias" that has a value of your nickname
PONumBW2Chat_JoinRoom = 33556227
PODFMaskBW2Chat_JoinRoom = "2.0.7.3/32"
PODFBW2Chat_JoinRoom = (2, 0, 7, 3)
POMaskBW2Chat_JoinRoom = 32

# XML (66.0.0.0/8): XML
# This class is for schemas that are represented in XML
PONumXML = 1107296256
PODFMaskXML = "66.0.0.0/8"
PODFXML = (66, 0, 0, 0)
POMaskXML = 8

# HamiltonTelemetry (2.0.4.64/26): Hamilton Telemetry
# This object contains a "#" field for the serial number, as well as possibly
# containing an "A" field with a list of X, Y, and Z accelerometer values. A "T"
# field containing the temperature as an integer in degrees C multiplied by 10000,
# and an "L" field containing the illumination in Lux.
PONumHamiltonTelemetry = 33555520
PODFMaskHamiltonTelemetry = "2.0.4.64/26"
PODFHamiltonTelemetry = (2, 0, 4, 64)
POMaskHamiltonTelemetry = 26

# Text (64.0.0.0/4): Human readable text
# This is a superclass for classes that are moderately understandable if they are
# read directly in their binary form. Generally these are protocols that were
# designed specifically to be human readable.
PONumText = 1073741824
PODFMaskText = "64.0.0.0/4"
PODFText = (64, 0, 0, 0)
POMaskText = 4

# MsgPack (2.0.0.0/8): MsgPack
# This class is for schemas that are represented in MsgPack
PONumMsgPack = 33554432
PODFMaskMsgPack = "2.0.0.0/8"
PODFMsgPack = (2, 0, 0, 0)
POMaskMsgPack = 8

# TSTaggedMP (2.0.3.0/24): TSTaggedMP
# This superclass describes "ts"->int64 tagged msgpack objects. The timestamp is
# used for merging entries and determining which is later and should be the final
# value.
PONumTSTaggedMP = 33555200
PODFMaskTSTaggedMP = "2.0.3.0/24"
PODFTSTaggedMP = (2, 0, 3, 0)
POMaskTSTaggedMP = 24

# String (64.0.1.0/32): String
# A plain string with no rigid semantic meaning. This can be thought of as a print
# statement. Anything that has semantic meaning like a process log should use a
# different schema.
PONumString = 1073742080
PODFMaskString = "64.0.1.0/32"
PODFString = (64, 0, 1, 0)
POMaskString = 32

