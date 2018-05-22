from imports import *
from endscreen import *

chuj = 0.8

def magicPerspectiveProjector(points, distanceFromPlane = 2000* chuj):  # points -> ndarray with shape [x, 3]
    try:
        pointsPrim = points * distanceFromPlane / points[:, 2]
    except ValueError:
        pointsPrim = points * distanceFromPlane / points[:, 2, np.newaxis]
    # return pointsPrim.astype(int)
    pointsPrim[:, 2] = points[:, 2]
    return pointsPrim


class AThread(QtCore.QThread):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.scene = view.graphicsscene

    def run(self):
        while 1:
            if self.scene.myPoint == True:
                self.view.setScene(EndScreen(self.view.scenesize),"kurwachuj")
            elif self.scene.enemyPoint == True:
                print("pupcia")
               # x = EndScreen(self.view.scenesize)
                self.view.setScene(EndScreen(self.view.scenesize,"kurwachuj"))
                # playsound.playsound('gameover.mp3', True)
            self.scene.update()
            self.scene.moveBall()
            self.scene.checkCollision()
            time.sleep(1./120)


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
        self.velocity = np.array([0, 0, 0])
        self.createNodes()
        self.color = color
        scene.addItem(self)

    def getRacketRect(self):
        return [self.position[0]-(self.width/2),self.position[1] - (self.height/2), self.width, self.height]

    def move(self, newPosition):
        if newPosition[0] > self.xLimit:
            newPosition[0] = self.xLimit
        elif newPosition[0] < -self.xLimit:
            newPosition[0] = -self.xLimit
        if newPosition[1] > self.yLimit:
            newPosition[1] = self.yLimit
        elif newPosition[1] < -self.yLimit:
            newPosition[1] = -self.yLimit
        self.velocity = newPosition - self.position
        self.position = np.array([newPosition[0], newPosition[1], newPosition[2]])
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
        self.penWidth = 1
        self.createNodes()
        scene.addItem(self)

    def moveRect(self,z):
        self.zPosition = z
        self.createNodes()

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
        pen.setWidth(self.penWidth)
        p.setPen(pen)

        p.drawLine(self.origin[0] + self.projectedNodes[0][0], self.origin[1] + self.projectedNodes[0][1],
                    self.origin[0] + self.projectedNodes[1][0], self.origin[1] + self.projectedNodes[1][1])
        p.drawLine(self.origin[0] + self.projectedNodes[1][0], self.origin[1] + self.projectedNodes[1][1],
                    self.origin[0] + self.projectedNodes[2][0], self.origin[1] + self.projectedNodes[2][1])
        p.drawLine(self.origin[0] + self.projectedNodes[2][0], self.origin[1] + self.projectedNodes[2][1],
                    self.origin[0] + self.projectedNodes[3][0], self.origin[1] + self.projectedNodes[3][1])
        p.drawLine(self.origin[0] + self.projectedNodes[3][0], self.origin[1] + self.projectedNodes[3][1],
                    self.origin[0] + self.projectedNodes[0][0], self.origin[1] + self.projectedNodes[0][1])





#
# class Ball(QtWidgets.QGraphicsItem):
#     def __init__(self, windowSize, radius, scene, color=QtCore.Qt.yellow):
    #     super().__init__()
    #     self.origin = windowSize/2
    #     self.velocityVector = np.array([-2.5, 5.0, 3.])
    #     self.position = np.array([5, 5, 280])
    #     self.radius = radius
    #     self.color = color
    #     self.nodes = None
    #     self.createNodes()
    #     scene.addItem(self)
    #
    # def move(self):
    #     self.position = self.position + self.velocityVector
    #     self.createNodes()
    #     return self.position
    #
    # def boundingRect(self):
    #     projectedRadius = np.linalg.norm(self.projectedNodes[0] - self.projectedNodes[1])
    #     return QtCore.QRectF(self.projectedNodes[0][0] + self.origin[0] - projectedRadius, self.projectedNodes[0][1] + self.origin[1] - projectedRadius,
    #                    projectedRadius * 2, projectedRadius * 2)
    #
    # def paint(self,p ,o ,widgets=None):
    #     pen = QtGui.QPen(self.color, 2, QtCore.Qt.SolidLine)
    #     brush = QtGui.QBrush(self.color)
    #     p.setPen(pen)
    #     p.setBrush(brush)
    #     projectedRadius = np.linalg.norm(self.projectedNodes[0] - self.projectedNodes[1])
    #     # print(projectedRadius)
    #     p.drawEllipse(self.projectedNodes[0][0] + self.origin[0] - projectedRadius, self.projectedNodes[0][1] + self.origin[1] - projectedRadius,
    #                    projectedRadius * 2, projectedRadius * 2)
    #
    # def createNodes(self):
    #     self.nodes = np.array([self.position, [self.position[0] + self.radius, self.position[1], self.position[2]]])
    #     self.projectedNodes = magicPerspectiveProjector(self.nodes)
    #     # print(self.projectedNodes)


class Ball(QtWidgets.QGraphicsItem):
    def __init__(self, windowSize, radius, scene, color=QtCore.Qt.yellow):
        super().__init__()
        self.origin = windowSize / 2
        self.velocityVector = np.array([5, 5.0, 15])
        self.position = np.array([5, 5, 2201 * chuj])
        self.radius = radius
        self.color = color
        self.rotationVector = np.array([0, 0, 0])
        self.nodes = None
        self.points = None
        self.precision = 25
        # self.createNodes()
        self.generateSphere()
        scene.addItem(self)

    def move(self):
        self.position = self.position + self.velocityVector
        self.rotateSphere()
        # self.points = self.points + self.velocityVector

    def getRotationMatrix(self, rotationVector):
        angle = np.linalg.norm(rotationVector)
        if angle == 0:
            return np.identity(3)
        unitVector = rotationVector / angle
        s = np.sin(angle)
        c = np.cos(angle)
        u = unitVector[0]
        v = unitVector[1]
        w = unitVector[2]
        return np.array([[u*u + (v*v + w*w)*c, u*v*(1 - c) - w*s, u*w*(1 - c) + v*s],
                         [u*v*(1 - c) + w*s, v*v + (u*u + w*w)*c, u*w*(1 - c) - u*s],
                         [u*w*(1 - c) - v*s, u*w*(1 - c) + u*s, w*w + (u*u + v*v)*c]])

    def setRotationVector(self, rotationVector):
        self.rotationVector = rotationVector

    def generateSphere(self):
        phis = np.linspace(0, 2 * np.pi,  self.precision)
        thetas = np.linspace(-np.pi, np.pi,  self.precision / 2)

        points = np.zeros((phis.size, thetas.size, 3))
        for i, phi in enumerate(phis):
            for j, theta in enumerate(thetas):
                x = self.radius * np.cos(phi) * np.cos(theta)
                y = self.radius * np.cos(phi) * np.sin(theta)
                z = self.radius * np.sin(phi)
                # print(z)
                points[i][j] = np.array([x, y, z])

        self.points = points

    def rotateSphere(self):
        self.points = self.points.dot(self.getRotationMatrix(self.rotationVector))

    # def boundingRect(self):
    #     projectedRadius = np.linalg.norm(self.projectedNodes[0] - self.projectedNodes[1])
    #     return QtCore.QRectF(self.projectedNodes[0][0] + self.origin[0] - projectedRadius,
    #                          self.projectedNodes[0][1] + self.origin[1] - projectedRadius,
    #                          projectedRadius * 2, projectedRadius * 2)

    def boundingRect(self):
        return QtCore.QRectF(self.position[0] + self.origin[0] - self.radius,
                             self.position[1] + self.origin[1] - self.radius,
                             self.radius * 2, self.radius * 2)

    def paint(self, p, o, widgets=None):
        pen = QtGui.QPen(QtCore.Qt.black, 0.3, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(self.color)
        p.setPen(pen)
        p.setBrush(brush)
        # projectedRadius = np.linalg.norm(self.projectedNodes[0] - self.projectedNodes[1])
        # # print(projectedRadius)
        # p.drawEllipse(self.projectedNodes[0][0] + self.origin[0] - projectedRadius,
        #               self.projectedNodes[0][1] + self.origin[1] - projectedRadius,
        #               projectedRadius * 2, projectedRadius * 2)
        shapeBuffer = self.points.shape
        points = np.reshape(magicPerspectiveProjector(np.reshape(self.points + self.position, (-1, 3))), shapeBuffer)
        # points = self.points + self.position
        x0 = self.origin[0]
        y0 = self.origin[1]
        for i in range(1, len(points)):
            for j in range(1, len(points[0])):
                # print(self.points[i][j][2])
                if (self.points[i][j][2] + self.points[i-1][j-1][2]) < 0:
                    p.drawConvexPolygon(QtCore.QPoint(points[i][j][0] + x0, points[i][j][1] + y0),
                                        QtCore.QPoint(points[i-1][j][0] + x0, points[i-1][j][1] + y0),
                                        QtCore.QPoint(points[i-1][j-1][0] + x0, points[i-1][j-1][1] + y0),
                                        QtCore.QPoint(points[i][j-1][0] + x0, points[i][j-1][1] + y0))









class Game(QtWidgets.QGraphicsView):
    def __init__(self,parent = None):
        QtWidgets.QGraphicsView.__init__(self)
        self.resize(1500,1000)
        self.setMouseTracking(True)
        self.scenesize = (1400,950)
        self.graphicsscene = Scene(self.scenesize)
        self.moveracket = False
        self.setScene(self.graphicsscene)


    def mouseMoveEvent(self,e):
        if self.moveracket :
            self.graphicsscene.moveRacket(e)

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
        self.resize(1500,1000)
        self.graphicsView = Game()
        self.setCentralWidget(self.graphicsView)
        self.show()


class Scene(QtWidgets.QGraphicsScene):
    def __init__(self,size):
        super().__init__()
        self.scenesize = size
        self.startDistance = 2200 * chuj
        self.endDistance = 7000 * chuj
        self.perspectiveRects = []
        self.windowSize = np.array(size)
        self.origin = self.windowSize/2
        gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(100, 100))
        gradient.setColorAt(0, QtCore.Qt.black)
        painter = QtGui.QPainter()
        self.setBackgroundBrush(QtGui.QBrush(gradient))
        self.drawBackground(painter,QtCore.QRectF())
        self.createPerspectiveRects()
        self.enemyRacket = Racket(self.windowSize, self.endDistance, self, QtCore.Qt.blue)
        self.ball = Ball(self.windowSize, 60, self)
        self.ballRect = BackgroundRect(self.windowSize, 60,self, color=QtCore.Qt.white)
        self.myRacket = Racket(self.windowSize,self.startDistance,self,QtCore.Qt.red)
        self.myPoint = False
        self.enemyPoint = False

    def createPerspectiveRects(self):
        N = 8
        for dist in np.linspace(self.startDistance, self.endDistance, N):
            self.perspectiveRects.append(BackgroundRect(self.windowSize, dist,self))

    def moveRacket(self,event):
        self.myRacket.move(np.array([event.x() - self.origin[0], event.y() - self.origin[1], self.myRacket.position[2]], dtype=int))
        #self.update()

    def moveBall(self):
        self.ball.move()
        position = self.ball.position
        self.ballRect.moveRect(position[2])
        self.enemyRacket.move([position[0],position[1], self.enemyRacket.position[2]])
        self.myRacket.move([position[0],position[1],  self.myRacket.position[2]])

    def checkCollision(self):
        rad = self.ball.radius
        ballX = self.ball.position[0]
        ballY = self.ball.position[1]
        ballZ = self.ball.position[2]
        start = self.startDistance
        meta = self.endDistance
        width = self.perspectiveRects[0].width
        height = self.perspectiveRects[0].height

        #print('ballZ', ballZ)

        if ballX - rad < -width/2 or ballX + rad > width/2:
            self.ball.velocityVector[0] *= -1

        if ballY - rad < -height/2 or ballY + rad > height/2:
            self.ball.velocityVector[1] *= -1

        if ballZ  < start:
            rect = self.myRacket.getRacketRect()
            print(self.myRacket.velocity)
            if ballX > rect[0] and ballX < rect[0]+rect[2] and ballY > rect[1] and ballY < rect[1]+rect[3]:
                self.ball.velocityVector[2] *= -1
                self.ball.rotationVector = np.array([ -self.myRacket.velocity[1],  self.myRacket.velocity[0], 0]) / 100
            else:
                self.ball.velocityVector[2] *= 0
                self.enemyPoint = True

        elif ballZ  > meta:
            rect = self.enemyRacket.getRacketRect()
            if ballX > rect[0] and ballX < rect[0]+rect[2] and ballY > rect[1] and ballY < rect[1]+rect[3]:
                self.ball.velocityVector[2] *= -1
                self.ball.rotationVector = np.array([ -self.enemyRacket.velocity[1],  self.enemyRacket.velocity[0], 0]) / 100
            else:
                self.ball.velocityVector[2] *= -1
                self.myPoint = True



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    gameLoop = AThread(ex.graphicsView)
    gameLoop.start()
    sys.exit(app.exec_())
