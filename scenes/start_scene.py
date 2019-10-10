from PyQt5 import QtWidgets, QtGui, QtCore

class StartScreen(QtWidgets.QGraphicsScene):
    def __init__(self, size, view, text):
        super().__init__()
        self.scenesize = size
        self.view = view
        self.setSceneRect(QtCore.QRectF(0, 0, size[0], size[1]))
        self.view.setCursor(QtCore.Qt.ArrowCursor)
        gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(100, 100))
        gradient.setColorAt(0, QtCore.Qt.black)
        painter = QtGui.QPainter()
        self.setBackgroundBrush(QtGui.QBrush(gradient))
        self.drawBackground(painter, QtCore.QRectF())
        self.textItemStart = TextItem('start', [size[0] / 2 - 50, size[1] / 2 - 100], True, self)


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

    def hoverEnterEvent(self,e):
        self.setDefaultTextColor(QtCore.Qt.blue)

    def hoverLeaveEvent(self,e):
        self.setDefaultTextColor(QtCore.Qt.red)

    def setPlainText(self,text):
        super().setPlainText(text)

    def mousePressEvent(self, e):
        self.scene.view.restart = True






