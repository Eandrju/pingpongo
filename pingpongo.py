from imports import *
from endscreen import *

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 1000
NUMBER_OF_RECTANGLES = 9
PERSPECTIVE_PARAMETER = 0.8   # change it when u notice that ball looks creepy
PLANE_POSITION= 2000
START_POSITION = 2200
END_POSITION = 9000
BALL_SPEED = 40.0
BALL_SPIN_PARAMETER = 120    # the lower parameter is, the greater influence of spin on trajectory
BALL_SPIN_PARAMETER_DOS = 80   # more spin, more fun!
BALL_PRECISION = 25
MAX_SPIN = 0.5
RACKET_WIDTH = 300
RACKET_HEIGHT = 200

def magicPerspectiveProjector(points, distanceFromPlane = PLANE_POSITION* PERSPECTIVE_PARAMETER):  # points -> ndarray with shape [x, 3]
    try:
        pointsPrim = points * distanceFromPlane / points[:, 2]
    except ValueError:
        pointsPrim = points * distanceFromPlane / points[:, 2, np.newaxis]
    # return pointsPrim.astype(int)
    return pointsPrim


class AThread(QtCore.QThread):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.scene = view.graphicsscene
        self.ingame = True
        self.endscene = EndScreen(self.view.scenesize,view)

    def updateCounters(self):
        #del self.scene.scoreText
       # del self.endscene.scoreText
        #self.scene.scoreText = TextItem("Score: {0} : {1}".format(self.view.score[0], self.view.score[1]),
                               #  [self.scene.scenesize[0] - 100, -20], False, self.scene, size=29)
        #self.endscene.scoreText = TextItem("Score: {0} : {1}".format(self.view.score[0], self.view.score[1]),
                                      #  [self.endscene.scenesize[0] - 100, -20], False, self.endscene, size=29)
        #self.scene.removeItem(self.scene.scoreText)
        #self.endscene.removeItem(self.endscene.scoreText)
        self.scene.updateCounters()
        self.endscene.updateCounters()
        #self.endscene.scoreText = TextItem("Score: {0} : {1}".format(self.view.score[0], self.view.score[1]),
         #                                   [self.endscene.scenesize[0] - 100, -20], False, self.endscene, size=29)
        pass

    def run(self):
        while 1:
            if self.view.myPoint == True:
                self.view.score[1]  = self.view.score[1] + 1
                self.updateCounters()
                self.view.setCursor(QtCore.Qt.ArrowCursor)
                self.view.setScene(EndScreen(self.view.scenesize,"pupcia"))
                self.view.myPoint = False
                self.ingame = False

            elif self.view.enemyPoint == True:
                self.view.score[0]  = self.view.score[0] + 1
                self.updateCounters()
                self.view.setCursor(QtCore.Qt.ArrowCursor)
                self.view.setScene(self.endscene)
                self.view.enemyPoint = False
                self.ingame = False

            if self.view.restart:
                self.scene.restart()
                self.view.setScene(self.scene)
                self.view.restart = False
                self.ingame = True

            if self.ingame:
                # print(self.view.score)
                self.scene.run()
            time.sleep(1./120)


class Racket(QtWidgets.QGraphicsItem):

    def __init__(self, windowSize, zPosition,scene, color,  width=RACKET_WIDTH, height=RACKET_HEIGHT):
        super().__init__()
        self.xLimit = windowSize[0] / 2 - width / 2
        self.yLimit = windowSize[1] / 2 - height / 2
        self.origin = windowSize/2
        self.width = width
        self.height = height
        self.nodes = None
        self.zPos = zPosition
        self.position = np.array([0, 0, zPosition])
        self.velocity = np.array([0, 0, 0])
        self.createNodes()
        self.color = color
        scene.addItem(self)

    def getRacketRect(self):
        return [self.position[0]-(self.width/2),self.position[1] - (self.height/2), self.width, self.height]

    def startingPos(self):
        self.position = np.array([0, 0, self.zPos])

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


class Ball(QtWidgets.QGraphicsItem):
    def __init__(self, windowSize, radius, scene, color=QtCore.Qt.yellow):
        super().__init__()
        self.origin = windowSize / 2
        self.velocityVector = np.array([0.0, 0.0, BALL_SPEED])
        self.position = np.array([0, 0, (START_POSITION + 1) * PERSPECTIVE_PARAMETER])
        self.radius = radius
        self.color = color
        self.rotationVector = np.array([0.0, 0.0, 0.0])
        self.points = None
        self.generateSphere()
        scene.addItem(self)

    def move(self):
        self.position += self.velocityVector
        self.velocityVector += np.array([-self.rotationVector[1], self.rotationVector[0], 0]) / BALL_SPIN_PARAMETER * BALL_SPIN_PARAMETER_DOS
        self.rotateSphere()

    def startingPos(self):
        self.position = np.array([0, 0, (START_POSITION + 1) * PERSPECTIVE_PARAMETER])
        self.rotationVector = np.array([0.0, 0.0, 0.0])
        self.velocityVector = np.array([0.0, 0.0, BALL_SPEED])

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

    def generateSphere(self):
        phis = np.linspace(0, 2 * np.pi,  BALL_PRECISION)
        thetas = np.linspace(-np.pi, np.pi,  BALL_PRECISION / 2)

        points = np.zeros((phis.size, thetas.size, 3))
        for i, phi in enumerate(phis):
            for j, theta in enumerate(thetas):
                x = self.radius * np.cos(phi) * np.cos(theta)
                y = self.radius * np.cos(phi) * np.sin(theta)
                z = self.radius * np.sin(phi)
                points[i][j] = np.array([x, y, z])
        self.points = points

    def rotateSphere(self):
        if np.linalg.norm(self.rotationVector) > MAX_SPIN:
            self.rotationVector = self.rotationVector / np.linalg.norm(self.rotationVector) * MAX_SPIN
        self.points = self.points.dot(self.getRotationMatrix(self.rotationVector))

    def boundingRect(self):
        return QtCore.QRectF(self.position[0] + self.origin[0] - self.radius,
                             self.position[1] + self.origin[1] - self.radius,
                             self.radius * 2, self.radius * 2)

    def paint(self, p, o, widgets=None):
        pen = QtGui.QPen(QtCore.Qt.black, 0.3, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(self.color)
        p.setPen(pen)
        p.setBrush(brush)
        shapeBuffer = self.points.shape
        points = np.reshape(magicPerspectiveProjector(np.reshape(self.points + self.position, (-1, 3))), shapeBuffer)
        x0 = self.origin[0]
        y0 = self.origin[1]
        for i in range(1, len(points)):
            for j in range(1, len(points[0])):
                if (self.points[i][j][2] + self.points[i-1][j-1][2]) < 0:
                    p.drawConvexPolygon(QtCore.QPoint(points[i][j][0] + x0, points[i][j][1] + y0),
                                        QtCore.QPoint(points[i-1][j][0] + x0, points[i-1][j][1] + y0),
                                        QtCore.QPoint(points[i-1][j-1][0] + x0, points[i-1][j-1][1] + y0),
                                        QtCore.QPoint(points[i][j-1][0] + x0, points[i][j-1][1] + y0))



class Game(QtWidgets.QGraphicsView):
    def __init__(self,parent = None):
        QtWidgets.QGraphicsView.__init__(self)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMouseTracking(True)
        self.scenesize = (WINDOW_WIDTH / 15.0 * 14.0, WINDOW_HEIGHT * 0.95)
        self.score = [0, 0]
        self.moveracket = False
        self.myPoint = False
        self.enemyPoint = False
        self.restart = False
        self.graphicsscene = Scene(self.scenesize,self)
        self.setScene(self.graphicsscene)



class App(QtWidgets.QMainWindow):
    def __init__(self):
        super(App,self).__init__()
        self.setWindowTitle("pong")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.graphicsView = Game()
        self.setCentralWidget(self.graphicsView)
        self.show()


class Scene(QtWidgets.QGraphicsScene):
    def __init__(self,size,view):
        super().__init__()
        self.scenesize = size
        self.view = view
        self.startDistance = START_POSITION * PERSPECTIVE_PARAMETER
        self.endDistance = END_POSITION * PERSPECTIVE_PARAMETER
        self.perspectiveRects = []
        self.windowSize = np.array(size)
        self.origin = self.windowSize/2
        self.setSceneRect(QtCore.QRectF(0, 0, size[0], size[1]))
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
        self.scoreText = TextItem("FUCK: {0} : {1}".format(self.view.score[0], self.view.score[1]), [self.scenesize[0] - 100, -20], False, self, size=29)
        self.scoreText.setPlainText("censore")
        self.scoreText.setPos(self.scenesize[0] - 100, -20)
        self.addItem(self.scoreText)
        #self.connect()
        self.myPoint = False
        self.enemyPoint = False
        self.moveracket = False

        #self.objects = [self.enemyRacket,self.ball]
        #self.objects = list(zip(self.objects,self.perspectiveRects))

    def updateCounters(self):
        self.removeItem(self.scoreText)
        self.scorePOOP =TextItem("FUCK: {0} : {1}".format(self.view.score[0], self.view.score[1]),
                                        [self.scenesize[0] - 100, -20], False, self, size=29)

    def run(self):
        self.update()
        #self.scoreText.setPlainText(QtCore."Score: {0} : {1}".format(self.view.score[0],self.view.score[1]))
        self.moveBall()
        self.checkCollision()

    def mouseMoveEvent(self, event):
        if self.moveracket :
            self.myRacket.move(np.array([event.scenePos().x() - self.origin[0], event.scenePos().y() - self.origin[1], self.myRacket.position[2]]))

    def mousePressEvent(self, e):
        if self.moveracket:
            self.moveracket = False
            self.view.setCursor(QtCore.Qt.ArrowCursor)
        else:
            self.moveracket = True
            self.view.setCursor(QtCore.Qt.BlankCursor)

    def createPerspectiveRects(self):
        for dist in np.linspace(self.startDistance, self.endDistance, NUMBER_OF_RECTANGLES):
            self.perspectiveRects.append(BackgroundRect(self.windowSize, dist,self))

    def restart(self):
        print('restart !!!!!')
        self.myRacket.startingPos()
        self.enemyRacket.startingPos()
        self.ball.startingPos()

    def moveBall(self):
        self.ball.move()
        position = self.ball.position
        self.ballRect.moveRect(position[2])
        self.enemyRacket.move([position[0],position[1], self.enemyRacket.position[2]])

    def invisible(self):
        for i in self.perspectiveRects:
            i.setVisible(False)
        self.ball.setVisible(False)
        self.enemyRacket.setVisible(False)
        self.myRacket.setVisible(False)

    def checkCollision(self):
        rad = self.ball.radius
        ballX = self.ball.position[0]
        ballY = self.ball.position[1]
        ballZ = self.ball.position[2]
        start = self.startDistance
        meta = self.endDistance
        width = self.perspectiveRects[0].width
        height = self.perspectiveRects[0].height


        if ballX - rad < -width/2 or ballX + rad > width/2:
            self.ball.velocityVector[0] *= -1

        if ballY - rad < -height/2 or ballY + rad > height/2:
            self.ball.velocityVector[1] *= -1

        if ballZ  < start:
            rect = self.myRacket.getRacketRect()
            # print(self.myRacket.velocity)
            if ballX > rect[0] and ballX < rect[0]+rect[2] and ballY > rect[1] and ballY < rect[1]+rect[3]:
                # print(self.ball.rotationVector.dtype,  self.myRacket.velocity.dtype)
                self.ball.velocityVector[2] *= -1
                self.ball.rotationVector += (np.array([-self.myRacket.velocity[1],  self.myRacket.velocity[0], 0]) / BALL_SPIN_PARAMETER_DOS)
                print(np.linalg.norm(self.ball.rotationVector))
            else:
                self.ball.velocityVector[2] *= 0
                self.view.enemyPoint = True

        elif ballZ  > meta:
            rect = self.enemyRacket.getRacketRect()
            if ballX > rect[0] and ballX < rect[0]+rect[2] and ballY > rect[1] and ballY < rect[1]+rect[3]:
                print(self.ball.rotationVector.dtype,  self.myRacket.velocity.dtype, self.enemyRacket.velocity.dtype)
                self.ball.velocityVector[2] *= -1
                self.ball.rotationVector += (np.array([-self.enemyRacket.velocity[1],  self.enemyRacket.velocity[0], 0]) / BALL_SPIN_PARAMETER_DOS )
                print(np.linalg.norm(self.ball.rotationVector))
            else:
                self.ball.velocityVector[2] *= -1
                self.view.myPoint = True

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    gameLoop = AThread(ex.graphicsView)
    gameLoop.start()
    sys.exit(app.exec_())
