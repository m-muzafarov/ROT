#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Messiah'
# based on stomper example for stomping"
import os
import sys
from time import strftime
import uuid
import logging
from twisted.internet import reactor, stdio
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.protocols import basic

import stomper


stomper.utils.log_init(logging.CRITICAL)

HOST = 'localhost'
PORT = 61613
DESTINATION = "/topic/inbox"
MEM = 20
message = "/CONNECT"


class StompProtocol(Protocol, stomper.Engine):
    def __init__(self, username='', password='', nickname=''):
        stomper.Engine.__init__(self)
        self.username = username
        self.password = password
        self.log = logging.getLogger("sender")
        self.nickname = nickname if nickname else str(uuid.uuid4())
        self.buffer = []

    def connected(self, msg):
        stomper.Engine.connected(self, msg)

        self.log.info("Nickname:{} Connected: session {}.".format(
            self.nickname,
            msg['headers']['session'])
        )
        print "\rWelcome to chat!"

        def setup_looping_call():
            lc = LoopingCall(self.send)
            lc.start(0.3)

        reactor.callLater(0, setup_looping_call)

        f = stomper.Frame()
        f.unpack(stomper.subscribe(DESTINATION))
        f.headers['activemq.noLocal'] = 'true'
        return f.pack()

    def ack(self, msg):
        self.log.debug("Received: %s " % (msg['body']))
        self.buffer.append("{}\n".format(msg['body']))
        data = "".join(self.buffer[-MEM:])
        for i in range(len(self.buffer), MEM + 1):
            data += "\n"
        os.system("clear")
        print "{}\n--------------------------".format(data)
        return stomper.NO_REPONSE_NEEDED

    def send(self):
        global message
        if not message:
            return
        self.log.debug("MSG:({}) {}: {}".format(strftime("%H:%M:%S"),
                                                self.nickname,
                                                message))

        if message == "/CONNECT":
            f = stomper.Frame()
            f.unpack(stomper.send(DESTINATION,
                                  "{} just connected".format(self.nickname)))
            self.transport.write(f.pack())
        elif message[:3] == "/ME":
            f = stomper.Frame()
            f.unpack(stomper.send(DESTINATION,
                                  "{} {}".format(self.nickname, message[4:])))
            self.transport.write(f.pack())
        elif message == "/HISTORY":
            data = ">".join(self.buffer)
            for i in range(len(self.buffer), MEM + 1):
                data += "\n"
            os.system("clear")
            print "{}\n--------------------------".format(data)
        elif message == "/QUIT":
            f = stomper.Frame()
            f.unpack(stomper.send(DESTINATION,
                                  "{} just exited".format(self.nickname)))
            reactor.callLater(1, self.closeConnection)
            self.transport.write(f.pack())
        else:
            f = stomper.Frame()
            f.unpack(stomper.send(DESTINATION,
                                  "({}) {}: {}".format(strftime("%H:%M:%S"),
                                                       self.nickname,
                                                       message)))
            self.transport.write(f.pack())
        message = ""

    def connectionMade(self):
        cmd = stomper.connect(self.username, self.password)
        self.transport.write(cmd)

    def dataReceived(self, data):
        msg = stomper.unpack_frame(data)
        returned = self.react(msg)
        if returned:
            self.transport.write(returned)

    def closeConnection(self):
        print "Goodbye!"
        reactor.stop()


class Echo(basic.LineReceiver):
    delimiter = "\n"

    def connectionMade(self):
        self.transport.write(" ")

    def lineReceived(self, line):
        global message
        message = line


class StompClientFactory(ReconnectingClientFactory):
    # Will be set up before the factory is created.
    username, password, nickname = '', '', ''
    stdio.StandardIO(Echo())

    def buildProtocol(self, addr):
        return StompProtocol(self.username, self.password, self.nickname)

    def clientConnectionLost(self, connector, reason):
        """Lost connection
        """
        #print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        """Connection failed
        """
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self,
                                                         connector,
                                                         reason)


def start(host=HOST, port=PORT, username='', password='', nickname=""):
    """Start twisted event loop and the fun should begin...
    """
    StompClientFactory.username = username
    StompClientFactory.password = password
    StompClientFactory.nickname = nickname
    reactor.connectTCP(host, port, StompClientFactory())
    reactor.run()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: {} nickname [MEM]".format(sys.argv[0])
        exit(1)
    if len(sys.argv) > 2:
        try:

            MEM = int(sys.argv[2])
        except:
            print "MEM can be only integers"
            exit(2)
    start(nickname=sys.argv[1])
