import unittest

from bw2python.bwtypes import PayloadObject
from bw2python.client import Client
from threading import Semaphore

MESSAGES = [
    "Hello, world!",
    "Bosswave 2",
    "Lorem ipsum",
    "dolor sit amet"
]
PAC = "lGhzBEz_uyAz2sOjJ9kmfyJEl1MakBZP3mKC-DNCNYE="
KEY_FILE = "test.key"
URI = "castle.bw2.io/bar/baz"

class TestPubSubscribe(unittest.TestCase):
    def onSetEntityResponse(self, response):
        self.assertEqual("okay", response.status)
        self.semaphore.release()

    def onSubscribeResponse(self, response):
        self.assertEqual("okay", response.status)
        self.semaphore.release()

    def onPublishResponse(self, response):
        self.assertEqual("okay", response.status)

    def onMessage(self, message):
        self.assertTrue(len(message.payload_objects) > 0)
        msg_body = message.payload_objects[0].content
        self.assertIn(msg_body, MESSAGES)
        self.counter += 1
        if self.counter == len(MESSAGES):
            self.semaphore.release()

    def setUp(self):
        self.counter = 0
        self.semaphore = Semaphore(0)
        self.bw_client = Client('localhost', 28589)
        self.bw_client.connect()
        self.bw_client.setEntityFromFile(KEY_FILE, self.onSetEntityResponse)
        self.semaphore.acquire()
        self.bw_client.subscribe(URI, self.onSubscribeResponse, self.onMessage,
                primary_access_chain=PAC, elaborate_pac="full", expiry_delta=3600000)
        self.semaphore.acquire()

    def tearDown(self):
        self.bw_client.close()

    def testPublishSubscribe(self):
        for msg in MESSAGES:
            po = PayloadObject((64, 0, 0, 0), None, msg)
            self.bw_client.publish(URI, self.onPublishResponse, payload_objects=(po,),
                    primary_access_chain=PAC, elaborate_pac="full")
        self.semaphore.acquire()

if __name__ == "__main__":
    unittest.main()
