from socket import *
from threading import Thread
import Server, os

def Thread_(target, args=[]):
    thread = Thread(target=target, args=args)
    thread.start()

cls = lambda: os.system('cls')

class TCP_Server:
    def getUnpackedPort(self):
        vals = list(self.requestsMapping.values())
        n = min(vals)
        port = self.requestsMapping[vals.index(n)]
        self.requestsMapping[port] += 1
        return port
    def releasePortCount(self, port):
        self.requestsMapping[port] -= 1
    def getInfoByConn(self, conn):
        addr = list(self.activeConnections1.keys())[list(self.activeConnections1.values()).index(conn)]
        num = list(self.activeConnections2.keys())[list(self.activeConnections2.values()).index(addr)]
        return num, addr
    def getInfoByNum(self, num):
        addr = self.activeConnections2[num]
        conn = self.activeConnections1[addr]
        return conn, addr
    def getInfoByAddr(self, addr):
        conn = self.activeConnections1[addr.__str__()]
        num = list(self.activeConnections2.keys())[list(self.activeConnections2.values()).index(addr.__str__())]
        return conn, num
    def generateNum(self):
        if self.indexingGaps != []:
            num = self.indexingGaps[0]
            self.indexingGaps.remove(num)
            return num
        else:
            self.currentNum += 1
            return self.currentNum
    def setHost(self, host):
        self.HOST = host
    def CloseActiveConnection(self, conn, addr, num):
        self.indexingGaps += [num]
        self.activeConnections1.pop(addr.__str__())
    def manageActiveConnections(self, conn, addr, num):
        while True:
            try:
                data = conn.recv(1)
                if data == b'0': # Request
                    port = self.getUnpackedPort()
                    conn.send(f"({self.HOST}, {port})".encode('utf-8'))
                elif data == b'1': # Close connection
                    self.CloseActiveConnection(conn, addr, num)
                    break
            except ConnectionError and ConnectionAbortedError and ConnectionRefusedError and ConnectionResetError:
                self.CloseActiveConnection(conn, addr, num)
                break
    def startRouter(self):
        self.currentNum = 0
        self.indexingGaps = []
        def main():
            self.router = socket(AF_INET, SOCK_STREAM)
            self.router.bind((self.HOST, self.PORT_R))
            getNextPort = lambda: self.PORT[self.portMap.index(min(self.portMap))]
            while True:
                self.router.listen(1) 
                conn, addr = self.router.accept()
                self.activeConnections1[addr.__str__()] = conn
                num = self.generateNum()
                self.activeConnections2[num] = addr.__str__()
                Thread_(self.manageActiveConnections, [conn, addr, num])
        self.startActiveSockets()
        Thread_(main)
    def activeConsole():
        def main():
            while True:
                try:
                    exec(input(), globals())
                except Exception as e: print(e)
        Thread_(main)
    def runServer(self):
        # server vars:
        self.activeConnections1 = dict()
        self.activeConnections2 = dict()
        self.requestsMapping = dict()
        for port in self.PORT: self.requestsMapping[port] = 0
        self.crypto = Server.Crytography
        self.operations = Server.Operations(self)
        # server activation:
        print("[SERVER] Initializing...")
        self.startRouter()
        print("[SERVER] Server has been successfully Initialized...")

server = TCP_Server()
host = gethostbyname(gethostname())
server.setHost(host)
server.PORT = range(8000, 8011)
server.PORT_R = 80
server.activeConsole()
server.runServer()
