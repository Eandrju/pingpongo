from imports import *
import pingpongo
import connDialog

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

        self.startButton.clicked.connect(self.startgame)
        self.connButton.clicked.connect(self.setupConn)
        self.testconnButton.clicked.connect(self.establishConn)

        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ip = ''
        self.port = 10010
        self.server = False
        self.client = True
        self.conn = None

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

    def startgame(self):
        self.gameLoop.start()
        time.sleep(0.1)

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
        self.conn,self.addr = tup

        dialog = QtWidgets.QMessageBox.about(self, "Server", "Accepted a connection")
        dialog.show()

    def establishConn(self):
        if self.client:
            try:
                self.socket.connect((self.ip,self.port))
            except Exception as e:
                print("Socket error: ", e)
        else:
            try:
                self.socket.bind((socket.gethostname(),self.port))
                self.socket.listen(1)
                thread = ListenThread(self,self.socket)


            except Exception as e:
                print("Socket error: ", e)


class ListenThread(QtCore.QThread):
    acceptedSignal = QtCore.pyqtSignal()
    def __init__(self,gui,socket):
        super().__init__()
        self.gui = gui
        self.socket = socket
        self.conn = None
        self.addr = None
        self.acceptedSignal.connect(lambda x=(self.conn,self.addr):self.gui.serverAccepted)

    def run(self):
        self.socket.accept()
        self.acceptedSignal.emit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    app.exec_()
    while 1:
        continue
    sys.exit(app.exec_())

