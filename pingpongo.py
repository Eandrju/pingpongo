from PyQt5 import QtWidgets,QtGui,QtCore,uic
import sys
import numpy as np
import time

def magicPerspectiveProjector(points, distanceFromPlane = 200):  # points -> ndarray with shape [x, 3]
    try:
        pointsPrim = points * distanceFromPlane / points[:, 2]
    except ValueError:
        pointsPrim = points * distanceFromPlane / points[:, 2, np.newaxis]
    # return pointsPrim.astype(int)
    return pointsPrim


class AThread(QtCore.QThread):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene

    def run(self):
        while 1:
            self.scene.update()
            self.scene.moveBall()
            self.scene.checkCollision()
            time.sleep(1./600)


class Racket(QtWidgets.QGraphicsItem):

    def __init__(self, windowSize, zPosition,scene, color, width=300, height=200):
        super().__init__()
        self.xLimit = windowSize[0] / 2 - width / 2
        self.yLimit = windowSize[1] / 2 - height / 2
        self.origin = windowSize/2
        self.width = width
        self.height = height
        self.nodes = None
        self.position = np.array([0, 0, zPosition])
        self.createNodes()
        self.color = color
        scene.addItem(self)

    def move(self, newPosition):
        if newPosition[0] > self.xLimit:
            newPosition[0] = self.xLimit
        elif newPosition[0] < -self.xLimit:
            newPosition[0] = -self.xLimit
        if newPosition[1] > self.yLimit:
            newPosition[1] = self.yLimit
        elif newPosition[1] < -self.yLimit:
            newPosition[1] = -self.yLimit
        self.position = np.array([newPosition[0], newPosition[1], self.position[2]])
        self.createNodes()


    def createNodes(self):
        x = self.width // 2
        y = self.height // 2
        z = self.position[2]
        self.nodes = np.array([[-x + self.position[0], -y + self.position[1], z],
                               [-x + self.position[0], y + self.position[1], z],
                               [x + self.position[0], y + self.position[1], z],
                               [x + self.position[0], -y + self.position[1], z]])
        self.projectedNodes = magicPerspectiveProjector(self.nodes)

    def boundingRect(self):
        return QtCore.QRectF(self.origin[0] + self.projectedNodes[0][0],self.origin[1] + self.projectedNodes[0][1],
                            abs(self.projectedNodes[0][0])+abs(self.projectedNodes[2][0]),
                             abs(self.projectedNodes[0][1]) + abs(self.projectedNodes[2][1]))

    def paint(self, qp, o, widgets=None):
        pen = QtGui.QPen(self.color, 2, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        qp.setPen(pen)
        qp.setBrush(brush)
        qp.drawRect(self.origin[0] + self.projectedNodes[0][0], self.origin[1] + self.projectedNodes[0][1],
                    abs(self.projectedNodes[0][0] - self.projectedNodes[2][0]), abs(self.projectedNodes[0][1] - self.projectedNodes[2][1]))

        qp.drawLine(self.origin[0] + self.projectedNodes[0][0], self.origin[1] + (self.projectedNodes[0][1] + self.projectedNodes[2][1]) / 2,
                    self.origin[0] + self.projectedNodes[2][0], self.origin[1] + (self.projectedNodes[0][1] + self.projectedNodes[2][1]) / 2)

        qp.drawLine(self.origin[0] + (self.projectedNodes[0][0] + self.projectedNodes[2][0]) / 2, self.origin[1] + self.projectedNodes[0][1],
                    self.origin[0] + (self.projectedNodes[0][0] + self.projectedNodes[2][0]) / 2, self.origin[1] + self.projectedNodes[1][1])



class BackgroundRect(QtWidgets.QGraphicsItem):
    '''def __init__(self,position,size,scene,):
        super().__init__()
        self.rect = QtCore.QRectF(position[0],position[1],size[0],size[1])
        self.color = color
        #self.nodes = QtCore.QRectF(magicPerspectiveProjector([0,0,size[0],size[1]]))
        self.style = style
        self.setPos(position[0],position[1])
        scene.clearSelection()
        scene.addItem(self)
        '''

    def __init__(self, windowSize, zPosition,scene,color = QtCore.Qt.green,style=QtCore.Qt.SolidLine):
        super().__init__()
        self.width = windowSize[0]
        self.height = windowSize[1]
        self.position = np.array([0, 0, zPosition])
        self.zPosition = zPosition
        self.origin = windowSize/2
        self.nodes = None
        self.color = color
        self.style = style
        self.createNodes()
        scene.addItem(self)

    def createNodes(self):
        h = self.height
        w = self.width
        self.nodes = np.array([[-w // 2, -h // 2, self.zPosition],
                               [-w // 2, h // 2, self.zPosition],
                               [w // 2, h // 2, self.zPosition],
                               [w // 2, -h // 2, self.zPosition]])
        self.projectedNodes = magicPerspectiveProjector(self.nodes)

    def boundingRect(self):
        return QtCore.QRectF(self.origin[0] + self.projectedNodes[0][0],self.origin[1] + self.projectedNodes[0][1],
                            abs(self.projectedNodes[0][0])+abs(self.projectedNodes[2][0]),
                             abs(self.projectedNodes[0][1]) + abs(self.projectedNodes[2][1]))

    def paint(self,p ,o ,widgets=None):
        pen = QtGui.QPen(self.style)
        pen.setColor(self.color)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawLine(self.origin[0] + self.projectedNodes[0][0], self.origin[1] + self.projectedNodes[0][1],
                    self.origin[0] + self.projectedNodes[1][0], self.origin[1] + self.projectedNodes[1][1])
        p.drawLine(self.origin[0] + self.projectedNodes[1][0], self.origin[1] + self.projectedNodes[1][1],
                    self.origin[0] + self.projectedNodes[2][0], self.origin[1] + self.projectedNodes[2][1])
        p.drawLine(self.origin[0] + self.projectedNodes[2][0], self.origin[1] + self.projectedNodes[2][1],
                    self.origin[0] + self.projectedNodes[3][0], self.origin[1] + self.projectedNodes[3][1])
        p.drawLine(self.origin[0] + self.projectedNodes[3][0], self.origin[1] + self.projectedNodes[3][1],
                    self.origin[0] + self.projectedNodes[0][0], self.origin[1] + self.projectedNodes[0][1])


class Ball(QtWidgets.QGraphicsItem):
    def __init__(self, windowSize, radius, scene, color=QtCore.Qt.yellow):
        super().__init__()
        self.origin = windowSize/2
        self.velocityVector = np.array([-1., 2.0, 1.15])
        self.position = np.array([5, 5, 280])
        self.radius = radius
        self.color = color
        self.nodes = None
        self.createNodes()
        scene.addItem(self)

    def move(self):
        self.position = self.position + self.velocityVector
        self.createNodes()

    def boundingRect(self):
        projectedRadius = np.linalg.norm(self.projectedNodes[0] - self.projectedNodes[1])
        return QtCore.QRectF(self.projectedNodes[0][0] + self.origin[0] - projectedRadius, self.projectedNodes[0][1] + self.origin[1] - projectedRadius,
                       projectedRadius * 2, projectedRadius * 2)

    def paint(self,p ,o ,widgets=None):
        pen = QtGui.QPen(self.color, 2, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(self.color)
        p.setPen(pen)
        p.setBrush(brush)
        projectedRadius = np.linalg.norm(self.projectedNodes[0] - self.projectedNodes[1])
        # print(projectedRadius)
        p.drawEllipse(self.projectedNodes[0][0] + self.origin[0] - projectedRadius, self.projectedNodes[0][1] + self.origin[1] - projectedRadius,
                       projectedRadius * 2, projectedRadius * 2)

    def createNodes(self):
        self.nodes = np.array([self.position, [self.position[0] + self.radius, self.position[1], self.position[2]]])
        self.projectedNodes = magicPerspectiveProjector(self.nodes)
        # print(self.projectedNodes)


class Game(QtWidgets.QGraphicsView):
    def __init__(self,parent = None):
        QtWidgets.QGraphicsView.__init__(self)
        self.resize(1100,750)
        self.setMouseTracking(True)
        self.graphicsscene = Scene((1000,700))
        self.moveracket = False
        self.setScene(self.graphicsscene)


    def mouseMoveEvent(self,e):
        if self.moveracket : self.graphicsscene.moveRacket(e)

    def mousePressEvent(self,e):
        if self.moveracket:
            self.moveracket = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        else:
            self.moveracket = True
            self.setCursor(QtCore.Qt.BlankCursor)

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super(App,self).__init__()
        self.setWindowTitle("pong")
        self.graphicsView = Game()
        self.setCentralWidget(self.graphicsView)
        self.show()



class Scene(QtWidgets.QGraphicsScene):
    def __init__(self,size):
        super().__init__()
        self.scenesize = size
        self.startDistance = 220
        self.endDistance = 700
        self.perspectiveRects = []
        self.windowSize = np.array([1000,700])
        self.origin = self.windowSize/2
        gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(100, 100))
        gradient.setColorAt(0, QtCore.Qt.black)
        painter = QtGui.QPainter()
        self.setBackgroundBrush(QtGui.QBrush(gradient))
        self.drawBackground(painter,QtCore.QRectF())
        self.createPerspectiveRects()
        self.enemyRacket = Racket(self.windowSize, self.endDistance, self, QtCore.Qt.blue)
        self.ball = Ball(self.windowSize, 60, self)
        self.myRacket = Racket(self.windowSize,self.startDistance,self,QtCore.Qt.red)

    def createPerspectiveRects(self):
        N = 8
        for dist in np.linspace(self.startDistance, self.endDistance, N):
            self.perspectiveRects.append(BackgroundRect(np.array([1000,700]), dist,self))

    def moveRacket(self,event):
        self.myRacket.move(np.array([event.x() - self.origin[0], event.y() - self.origin[1]], dtype=int))
        self.update()

    def moveBall(self):
        self.ball.move()

    def checkCollision(self):
        rad = self.ball.radius
        ballX = self.ball.position[0]
        ballY = self.ball.position[1]
        ballZ = self.ball.position[2]
        start = self.startDistance
        meta = self.endDistance
        width = self.perspectiveRects[0].width
        height = self.perspectiveRects[0].height

        print('ballZ', ballZ)

        if ballX - rad < -width/2 or ballX + rad > width/2:
            self.ball.velocityVector[0] *= -1

        if ballY - rad < -height/2 or ballY + rad > height/2:
            self.ball.velocityVector[1] *= -1

        if ballZ - rad < start or ballZ + rad > meta:
            self.ball.velocityVector[2] *= -1

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    gameLoop = AThread(ex.graphicsView.graphicsscene)
    gameLoop.start()
    sys.exit(app.exec_())
