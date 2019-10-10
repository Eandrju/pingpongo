from PyQt5 import QtCore, QtWidgets, uic
import scenes.start_scene as start_scene
import scenes.game_scene as game_scene
import time, sys


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        QtCore.QObject.__init__(self)
        uic.loadUi('templates/mainWindow.ui', self)
        self.setWindowTitle("game_scene")
        self.graphicsView.setMouseTracking(True)
        self.graphicsView.scenesize = (game_scene.WINDOW_WIDTH / 15.0 * 14.0, game_scene.WINDOW_HEIGHT * 0.95)
        self.graphicsView.score = [0, 0]
        self.graphicsView.moveracket = False
        self.graphicsView.restart = False
        self.graphicsView.myPoint = False
        self.graphicsView.enemyPoint = False
        self.graphicsView.starForMe = False
        self.graphicsView.starForEnemy = False
        self.graphicsView.graphicsscene = start_scene.StartScreen(self.graphicsView.scenesize, self.graphicsView, '')
        self.graphicsView.setScene(self.graphicsView.graphicsscene)
        self.gameLoop = game_scene.AThread(self.graphicsView, self)
        self.startgame()
        self.show()

    def closeEvent(self, event):
        sys.exit()

    @QtCore.pyqtSlot()
    def startgame(self):
        self.gameLoop.start()
        time.sleep(0.1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    app.exec_()
    sys.exit()

