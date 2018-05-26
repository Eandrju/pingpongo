from imports import *
import pingpongo

class Window(QtWidgets.QMainWindow):


    def __init__(self):
        super(Window, self).__init__()
        QtCore.QObject.__init__(self)
        uic.loadUi('ping.ui', self)
        self.setWindowTitle("pongping")
        #QtWidgets.QTextBrowser.
        self.p1Score.setPlainText("0")
        self.p1Score.setFont(QtGui.QFont("Times",18))
        self.p2Score.setPlainText("0")
        self.p2Score.setFont(QtGui.QFont("Times", 18))
        self.startButton.clicked.connect(self.startgame)
        self.connButton.clicked.connect(self.startgame)
        self.testconnButton.clicked.connect(self.checkconn)
        self.viewinit()
        #self.changep1score.emit()
        self.show()

    def viewinit(self):
        self.graphicsView.setMouseTracking(True)
        self.graphicsView.scenesize = (pingpongo.WINDOW_WIDTH / 15.0 * 14.0, pingpongo.WINDOW_HEIGHT * 0.95)
        self.graphicsView.score = [0, 0]
        self.graphicsView.moveracket = False
        self.graphicsView.myPoint = False
        self.graphicsView.enemyPoint = False
        self.graphicsView.restart = False
        self.graphicsView.graphicsscene = pingpongo.Scene(self.graphicsView.scenesize, self.graphicsView)
        self.graphicsView.setScene(self.graphicsView.graphicsscene)

    @QtCore.pyqtSlot()
    def changep1(self):
        self.p1Score.setPlainText(str(self.graphicsView.score[0]))

    @QtCore.pyqtSlot()
    def changep2(self):
        self.p2Score.setPlainText(str(self.graphicsView.score[1]))

    def startgame(self):
        #self.setCentralWidget(self.graphicsView)
        gameLoop = pingpongo.AThread(self.graphicsView,self)
        #time.sleep(2)
        gameLoop.start()
        time.sleep(0.1)
        pass

    def setupConn(self):
        pass

    def checkconn(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    app.exec_()
    while 1:
        continue
    sys.exit(app.exec_())

