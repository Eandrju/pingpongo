from imports import *
import ast

class SendThread(QtCore.QThread):
    createdSignal = QtCore.pyqtSignal()
    updateElements = QtCore.pyqtSignal()
    def __init__(self,scene,client,conn):
        super().__init__()
        self.scene = scene
        self.client = client
        self.conn = conn
        self.data = None
        self.sc = True
        if client:
            self.runfunc = self.clientfunc
            self.updateElements.connect(lambda x=self.data:self.scene.updatePaddleBall(x))
        else:
            self.runfunc = self.serverfunc
            self.updateElements.connect(lambda x=self.data:self.scene.updatePaddleNet(x))
        self.createdSignal.connect(self.scene.view.gui.gameLoop.connectsignal)

    def clientfunc(self):
        x = self.conn.recv(1024)
        print("Recieved")
        self.data = ast.literal_eval(x.decode())
        self.updateElements.disconnect()
        self.updateElements.connect(lambda x=self.data: self.scene.updatePaddleBall(x))
        self.updateElements.emit()
        self.data = None
        send_data = [list(self.scene.myRacket.position), list(self.scene.myRacket.velocity)]
        self.conn.send(str(send_data).encode())

    def serverfunc(self):
        send_data = []
        send_data.append(list(self.scene.myRacket.position))
        send_data.append(list(self.scene.myRacket.velocity))
        send_data.append(list(self.scene.ball.velocityVector))
        send_data.append(list(self.scene.ball.position))
        send_data.append(list(self.scene.ball.rotationVector))
        data = str(send_data).encode()
        self.conn.send(data)
        x = self.conn.recv(1024)
        print("Recieved")
        self.data = ast.literal_eval(x.decode())
        self.updateElements.disconnect()
        self.updateElements.connect(lambda x=self.data: self.scene.updatePaddleNet(x))
        self.updateElements.emit()
        self.data = None

    @QtCore.pyqtSlot()
    def endscene(self):
        self.sc = not self.sc


    def run(self):
        while 1:
            if not self.sc:
                self.runfunc()
            else:
                continue
