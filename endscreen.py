from imports import *

class EndScreen(QtWidgets.QGraphicsScene):
    def __init__(self, size, view):
        super().__init__()
        self.scenesize = size
        self.view = view
        self.windowSize = np.array(size)
        self.setSceneRect(QtCore.QRectF(0, 0, size[0], size[1]))
        self.view.setCursor(QtCore.Qt.ArrowCursor)
        gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(100, 100))
        gradient.setColorAt(0, QtCore.Qt.black)
        painter = QtGui.QPainter()
        self.setBackgroundBrush(QtGui.QBrush(gradient))
        self.drawBackground(painter, QtCore.QRectF())
        self.textItem1 = TextItem("Point player one", [size[0] / 2 - 150, size[1] / 2 - 100], False, self)
        self.textItem2 = TextItem("continue", [size[0] / 2 - 75, size[1] / 2 ], True, self)
        self.scoreText = TextItem("Score: {0} : {1}".format(self.view.score[0], self.view.score[1]),
                                  [self.scenesize[0] - 100, -20], False, self, size=29)


    def updateCounters(self):
        self.removeItem(self.scoreText)
        self.scoreFUCK = TextItem("Score: {0} : {1}".format(self.view.score[0], self.view.score[1]),
                                  [self.scenesize[0] - 100, -20], False, self, size=29)

class TextItem(QtWidgets.QGraphicsTextItem):
    def __init__(self,text ,position, hoverable, scene, size = 30,
                 font = QtGui.QFont("Times",30)):
        super(TextItem,self).__init__(text)
        if size != 30:
            font = QtGui.QFont("Times,",size)
        self.setFont(font)
        self.setDefaultTextColor(QtCore.Qt.red)
        self.setAcceptHoverEvents(hoverable)
        self.setPos(position[0],position[1])
        self.scene = scene
        scene.addItem(self)
        #self.setPos(QtCore.QPointF(position[0],position[1]))


    def hoverEnterEvent(self,e):
        self.setDefaultTextColor(QtCore.Qt.blue)

    def hoverLeaveEvent(self,e):
        self.setDefaultTextColor(QtCore.Qt.red)

    def setPlainText(self,text):
        super().setPlainText(text)

    def mousePressEvent(self, e):
        self.scene.view.restart = True






