from imports import *
import ast

class SendThread(QtCore.QThread):
    createdSignal = QtCore.pyqtSignal()
    updateElements = QtCore.pyqtSignal()
    restarSignal = QtCore.pyqtSignal()

    def __init__(self,scene,client,conn,gui):
        super().__init__()
        self.scene = scene
        self.gui = gui
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
        self.createdSignal.connect(self.gui.gameLoop.connectsignal)
        self.restarSignal.connect(self.gui.gameLoop.restart_scene)

    def afterinit(self):
        self.createdSignal.emit()

    def clientfunc(self):
        x = self.conn.recv(1024)
        if '[' in x.decode():
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
        if '[' in x.decode():
            self.data = ast.literal_eval(x.decode())
            self.updateElements.disconnect()
            self.updateElements.connect(lambda x=self.data: self.scene.updatePaddleNet(x))
            self.updateElements.emit()
        self.data = None

    def boxprint(self,st):
        self.gui.connStatus.append("st")

    @QtCore.pyqtSlot()
    def endscene(self):
        self.boxprint("AHHHHHH")
        if not self.sc:
            flag = True

            while (flag):
                self.conn.send("kafel".encode())
                x = self.conn.recv(1024)
                if "kafel" in x.decode():
                    flag = False
                    self.sc = True
                    self.gui.gameLoop.ingame = True
        else:
            self.sc = False


    def run(self):
        while 1:
            if self.sc:
                self.runfunc()
            else:
                time.sleep(1/60)
                pass
