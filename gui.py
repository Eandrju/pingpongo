from imports import *
import pingpongo
import connDialog
import sendthread

class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        QtCore.QObject.__init__(self)
        uic.loadUi('ping.ui', self)
        self.setWindowTitle("pongping")

        self.p1Score.setPlainText("0")
        self.p1Score.setFont(QtGui.QFont("Times",18))
        self.p2Score.setPlainText("0")
        self.p2Score.setFont(QtGui.QFont("Times", 18))

        self.startButton.clicked.connect(self.startclicked)
        self.connButton.clicked.connect(self.setupConn)
        self.testconnButton.clicked.connect(self.establishConn)

        self.ip = socket.gethostname()
        self.port = 10010
        self.server = False
        self.client = True
        self.conn = None
        self.connected = False
        self.connTry = False
        self.connThread = None

        self.graphicsView.setMouseTracking(True)
        self.graphicsView.scenesize = (pingpongo.WINDOW_WIDTH / 15.0 * 14.0, pingpongo.WINDOW_HEIGHT * 0.95)
        self.graphicsView.score = [0, 0]
        self.graphicsView.moveracket = False
        self.graphicsView.myPoint = False
        self.graphicsView.enemyPoint = False
        self.graphicsView.restart = False
        self.graphicsView.graphicsscene = pingpongo.Scene(self.graphicsView.scenesize, self.graphicsView)
        self.graphicsView.setScene(self.graphicsView.graphicsscene)
        self.gameLoop = pingpongo.AThread(self.graphicsView, self)

        self.show()



    @QtCore.pyqtSlot()
    def changep1(self):
        self.p1Score.setPlainText(str(self.graphicsView.score[0]))

    @QtCore.pyqtSlot()
    def changep2(self):
        self.p2Score.setPlainText(str(self.graphicsView.score[1]))

    def startclicked(self):
        if self.connected:
            self.thr = Handshake(self, self.conn)
            self.thr.start()
        elif not(not self.connected and self.connTry):
            print("what the fuck")
            self.startgame()

    @QtCore.pyqtSlot()
    def startgame(self):
        self.gameLoop.start()
        time.sleep(0.1)
        if self.connected:
            self.connThread = sendthread.SendThread(self.graphicsView.graphicsscene,self.client,self.conn)
            self.connThread.start()

    def setupConn(self):
        self.dialog = connDialog.ConnDialog(self)

    @QtCore.pyqtSlot()
    def endDialog(self,dialog):
        self.ip = dialog.addressText.toPlainText()
        self.port = int(dialog.portText.toPlainText())
        self.server = dialog.serverRadio.isChecked()
        self.client = dialog.clientRadio.isChecked()
        print(self.ip,self.port,self.server,self.client)

    @QtCore.pyqtSlot()
    def serverAccepted(self,tup):
        if tup[0] is not None:
            self.conn,self.addr = tup
        self.connStatus.append("Server accepted a connection from {}:{}".format(self.addr, self.port))
        self.connected = True

    def establishConn(self):
        if self.connTry and self.server:
            try:
                self.socket.close()
                self.connStatus.append("Successfully closed socket")
            except Exception as e:
                self.connStatus.append("Socket error: {}".format(e))
            self.connTry = False
            return
        if self.client and not self.connTry:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.ip,self.port))
                self.conn = self.socket
                self.connStatus.append("Connected to server at addr {} and port {}".format(self.ip, self.port))
                self.connected = True
            except Exception as e:
                self.connStatus.append("Socket error: {}".format(e))
        else:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind((socket.gethostname(),self.port))
                self.socket.listen(10)
                self.connStatus.append("Created server on port {}".format(self.port))
                self.connTry = True
                thread = ListenThread(self ,self.socket)
                thread.start()


            except Exception as e:
                self.connStatus.append("Socket error: {}".format(e))


class ListenThread(QtCore.QThread):
    acceptedSignal = QtCore.pyqtSignal()
    def __init__(self, gui, socket):
        super().__init__()
        self.gui = gui
        self.socket = socket
        self.conn = None
        self.addr = None
        self.acceptedSignal.connect(lambda x=(self.conn, self.addr): self.gui.serverAccepted(x))

    def run(self):
        try:
            self.conn,self.addr = self.socket.accept()
        except Exception as e :
            print(e)

        self.acceptedSignal.connect(lambda x=(self.conn, self.addr): self.gui.serverAccepted(x))
        self.acceptedSignal.emit()

class Handshake(QtCore.QThread):
    startGame = QtCore.pyqtSignal()
    def __init__(self,gui,conn):
        super().__init__()
        self.gui = gui
        self.conn = conn
        print("poop")
        self.startGame.connect(self.gui.startgame)
        print('no way its this')

    def run(self):
        self.conn.send("poop".encode())
        x = self.conn.recv(1024).decode()
        if x == "poop":
            print("started from handshake")
            self.startGame.emit()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    app.exec_()
    while 1:
        continue
    sys.exit(app.exec_())

