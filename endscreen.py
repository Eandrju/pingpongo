from imports import *

class EndScreen(QtWidgets.QGraphicsScene):
    def __init__(self, size, text):
        print("AHH")
        super().__init__()
        self.scenesize = size
        self.windowSize = np.array(size)
        #self.scene.setSceneRect(QtCore.QRectF(0, 0, size[0], size[1]))
        print("inscene")
        gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(100, 100))
        gradient.setColorAt(0, QtCore.Qt.black)
        painter = QtGui.QPainter()
        self.setBackgroundBrush(QtGui.QBrush(gradient))
        self.drawBackground(painter,QtCore.QRectF())
        self.textItem = TextItem(text,[size[0]/2,size[1]/2],self)


class TextItem(QtWidgets.QGraphicsTextItem):
    def __init__(self,text ,position, scene,
                 font = QtGui.QFont("Times",30)):
        super(TextItem,self).__init__(text)
        print("inwidg")
        self.setFont(font)
        self.setDefaultTextColor(QtCore.Qt.red)
        self.setPos(QtCore.QPointF(position[0],position[1]))
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        scene.addItem(self)




