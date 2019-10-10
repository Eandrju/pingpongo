from PyQt5 import QtCore, QtWidgets
from scenes.end_scene import *
import numpy as np
import time

### GAME AND
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 1000
NUMBER_OF_RECTANGLES = 9
PERSPECTIVE_PARAMETER = 0.8   # change it when u notice that ball looks creepy
PLANE_POSITION= 2000    # z coord of the plane on which game is projected
START_POSITION = 2200  # z coord at which room starts
END_POSITION = 9000  # z coord at which room ends

### BALL PARAMS
BALL_SPEED = 50.0
BALL_SPIN_PARAMETER = 100    # the lower parameter is, the greater influence of spin on trajectory
BALL_SPIN_PARAMETER_DOS = 50   # more spin, more fun!
BALL_PRECISION = 25  # the grater it is , the more polygons create ball
MAX_SPIN = 0.3

### RACKET PARAMS
RACKET_WIDTH = 300
RACKET_HEIGHT = 200

### STAR PARAMS
STAR_RADIUS = 100

### BOT_PARAMS
BOT_SPEED = 7
BALL_DETECTION_NOISE = 5
MOVE_NOISE = 3

### function that gets points and applies perspective to them
def magicPerspectiveProjector(points, distanceFromPlane = PLANE_POSITION* PERSPECTIVE_PARAMETER):  
    # points -> ndarray with shape [x, 3]
    try:
        pointsPrim = points * distanceFromPlane / points[:, 2]
        pointsPrim[:, 2] = points[:, 2]
    except ValueError:
        pointsPrim = points * distanceFromPlane / points[:, 2, np.newaxis]
        pointsPrim[:, 2] = points[:, 2]
    return pointsPrim



class AThread(QtCore.QThread):
    sceneSignal = QtCore.pyqtSignal()
    updateScoreSignal = QtCore.pyqtSignal()

    def __init__(self, view, window):
        super().__init__()
        self.view = view
        self.window = window
        self.ingame = True
        self.start_scene = view.graphicsscene
        self.enemyendscene = EndScreen(self.view.scenesize, view,"point player one")
        self.myendscene = EndScreen(self.view.scenesize, view,"point player two")
        self.game_scene = Scene(view.scenesize, view,'pingpongo')
        self.updateScoreSignal.connect(self.game_scene.updateCounters)

    @QtCore.pyqtSlot()
    def connectsignal(self):
        self.sceneSignal.connect(self.window.connThread.endscene)

    def run(self):
        while 1:
            if self.view.myPoint == True:
                self.sceneSignal.emit()
                self.view.setCursor(QtCore.Qt.ArrowCursor)
                self.view.score[1]  = self.view.score[1] + 1
                self.view.setScene(self.myendscene)
                self.view.myPoint = False
                self.ingame = False
                self.updateScoreSignal.emit()

            elif self.view.enemyPoint == True:
                self.sceneSignal.emit()
                self.view.setCursor(QtCore.Qt.ArrowCursor)
                self.view.score[0]  = self.view.score[0] + 1
                self.view.setScene(self.enemyendscene)
                self.view.enemyPoint = False
                self.ingame = False
                self.updateScoreSignal.emit()

            if self.view.starForEnemy == True:
                self.view.score[0]  = self.view.score[0] + 1
                self.updateScoreSignal.emit()
                self.view.starForEnemy = False

            if self.view.starForMe == True:
                self.view.score[1]  = self.view.score[1] + 1
                self.updateScoreSignal.emit()
                self.view.starForMe = False

            if self.view.restart:
                self.view.setCursor(QtCore.Qt.BlankCursor)
                self.game_scene.restart()
                self.view.setScene(self.game_scene)
                self.view.restart = False
                self.sceneSignal.emit()
                self.ingame = True
            if self.ingame:
                self.game_scene.run()
            time.sleep(1./120)

class Star(QtWidgets.QGraphicsItem):
    def __init__(self, windowSize,scene, color, radius, offsetAngle, position):
        super().__init__()
        self.windowSize = windowSize
        self.position = position
        self.radius = radius
        self.offsetAngle = offsetAngle
        self.nodes = None
        self.projectedNodes = None
        self.setZValue(1 / self.position[2])
        self.createNodes()
        self.color = color
        self.origin = windowSize / 2
        scene.addItem(self)

    def move(self, newPosition):
        self.position = newPosition
        self.createNodes()
        self.projectedNodes = magicPerspectiveProjector(self.nodes)

    def createNodes(self):
        buffer = []
        r = self.radius
        R = self.radius * 2.6180388
        for index, alpha in enumerate(np.linspace(self.offsetAngle, 2 * np.pi + self.offsetAngle, 10, endpoint=False)):
            if index % 2 == 0:
                buffer.append([np.cos(alpha) * R + self.position[0], np.sin(alpha)* R + self.position[1], self.position[2]])
            else:
                buffer.append([np.cos(alpha) * r + self.position[0], np.sin(alpha)* r + self.position[1], self.position[2]])
        self.nodes = np.array(buffer)
        self.projectedNodes = magicPerspectiveProjector(self.nodes)

    def boundingRect(self):
        return QtCore.QRectF(self.origin[0] + self.position[0] - self.radius * 2,
                             self.origin[1] + self.position[1] - self.radius * 2,
                             self.radius * 4, self.radius * 4)

    def paint(self, qp, o, widgets=None):
        pen = QtGui.QPen(self.color, 2, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(self.color)

        qp.setPen(pen)
        qp.setBrush(brush)
        pN = self.projectedNodes
        o = self.origin

        qp.drawPolygon(QtCore.QPoint(pN[0][0] + o[0], pN[0][1] + o[1]),
                       QtCore.QPoint(pN[1][0] + o[0], pN[1][1] + o[1]),
                       QtCore.QPoint(pN[2][0] + o[0], pN[2][1] + o[1]),
                       QtCore.QPoint(pN[3][0] + o[0], pN[3][1] + o[1]),
                       QtCore.QPoint(pN[4][0] + o[0], pN[4][1] + o[1]),
                       QtCore.QPoint(pN[5][0] + o[0], pN[5][1] + o[1]),
                       QtCore.QPoint(pN[6][0] + o[0], pN[6][1] + o[1]),
                       QtCore.QPoint(pN[7][0] + o[0], pN[7][1] + o[1]),
                       QtCore.QPoint(pN[8][0] + o[0], pN[8][1] + o[1]),
                       QtCore.QPoint(pN[9][0] + o[0], pN[9][1] + o[1]))


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
        self.setZValue(1 / zPosition)
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

class JustSomeLines(QtWidgets.QGraphicsItem):
    def __init__(self, windowSize,scene,color = QtCore.Qt.green,style=QtCore.Qt.SolidLine):
        super().__init__()
        self.origin = windowSize // 2
        self.windowSize = windowSize
        self.color = color
        self.style = style
        self.penWidth = 1
        self.nodes = None
        self.projectedNodes = None
        self.createNodes()
        scene.addItem(self)

    def createNodes(self):
        s = START_POSITION * PERSPECTIVE_PARAMETER
        e = END_POSITION * PERSPECTIVE_PARAMETER
        w = self.windowSize
        self.nodes = np.array([[w[0] // 2, w[1] // 2, s],
                               [w[0] // 2, w[1] // 2, e],
                               [-w[0] // 2, w[1] // 2, s],
                               [-w[0] // 2, w[1] // 2, e],
                               [-w[0] // 2, -w[1] // 2, s],
                               [-w[0] // 2, -w[1] // 2, e],
                               [w[0] // 2, -w[1] // 2, s],
                               [w[0] // 2, -w[1] // 2, e]]
                              )
        self.projectedNodes = magicPerspectiveProjector(self.nodes)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.windowSize[0], self.windowSize[1])


    def paint(self,p ,o ,widgets=None):
        pen = QtGui.QPen(self.style)
        pen.setColor(self.color)
        pen.setWidth(self.penWidth)
        p.setPen(pen)
        o = self.origin
        pN = self.projectedNodes

        p.drawLine(pN[0][0] + o[0], pN[0][1] + o[1], pN[1][0] + o[0], pN[1][1] + o[1])
        p.drawLine(pN[2][0] + o[0], pN[2][1] + o[1], pN[3][0] + o[0], pN[3][1] + o[1])
        p.drawLine(pN[4][0] + o[0], pN[4][1] + o[1], pN[5][0] + o[0], pN[5][1] + o[1])
        p.drawLine(pN[6][0] + o[0], pN[6][1] + o[1], pN[7][0] + o[0], pN[7][1] + o[1])


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
        self.setZValue(1 / END_POSITION)
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
        self.setZValue(1 / self.position[2])
        scene.addItem(self)

    def move(self):
        self.position += self.velocityVector
        self.velocityVector += np.array([-self.rotationVector[1], self.rotationVector[0], 0]) / BALL_SPIN_PARAMETER * BALL_SPIN_PARAMETER_DOS
        self.velocityVector = self.velocityVector / np.linalg.norm(self.velocityVector) * BALL_SPEED
        self.rotateSphere()
        self.setZValue(1 /self.position[2])

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


class Bot:
    def __init__(self, racket, velocity=BOT_SPEED):
        self.racket = racket
        self.velocity = velocity

    def timeToMakeAMove(self, ballPosition):
        vector = ballPosition[:2] - self.racket.position[:2]
        if np.linalg.norm(vector) > self.velocity:
            vector = vector / np.linalg.norm(vector)
            vector = vector * self.velocity
        newX = self.racket.position[0] + vector[0]
        newY = self.racket.position[1] + vector[1]
        self.racket.move(np.array([newX, newY,self.racket.position[2]]))



class Scene(QtWidgets.QGraphicsScene):
    def __init__(self,size,view, canIcreteStars):
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
        self.shittyLines = JustSomeLines(self.windowSize, self)
        self.ball = Ball(self.windowSize, 60, self)
        self.bot = Bot(self.enemyRacket, 10)
        starPosition = None
        if canIcreteStars:
            newX = np.random.randint(-self.windowSize[0] // 2 + STAR_RADIUS, self.windowSize[0] // 2 - STAR_RADIUS)
            newY = np.random.randint(-self.windowSize[1] // 2 + STAR_RADIUS, self.windowSize[1] // 2 - STAR_RADIUS)
            starPosition = np.array([newX, newY, PERSPECTIVE_PARAMETER * (START_POSITION + (END_POSITION - START_POSITION) / 2)])
        self.star = Star(self.windowSize, self, QtGui.QColor(255,140,0), 50, 0.1, starPosition)
        self.ballRect = BackgroundRect(self.windowSize, 60,self, color=QtCore.Qt.white)
        self.myRacket = Racket(self.windowSize,self.startDistance,self,QtCore.Qt.red)
        self.scoreText = TextItem("{} : {}".format(self.view.score[0], self.view.score[1]), [self.scenesize[0] - 100, -20], False, self, size=29)
        self.scoreText.setPos(self.scenesize[0] - 100, -20)
        self.myPoint = False
        self.enemyPoint = False
        self.moveracket = True
        self.canIcreteStars = canIcreteStars

    @QtCore.pyqtSlot()
    def updateCounters(self):
        self.scoreText.setPlainText(" {} : {}".format(self.view.score[0], self.view.score[1]))

    def run(self):
        self.update()
        self.moveBall()
        self.checkCollision()
        self.bot.timeToMakeAMove(self.ball.position)

    def mouseMoveEvent(self, event):
        if self.moveracket :
            self.myRacket.move(np.array([event.scenePos().x() - self.origin[0],
                                         event.scenePos().y() - self.origin[1], self.myRacket.position[2]]))

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
            if ballX > rect[0] and ballX < rect[0]+rect[2] and ballY > rect[1] and ballY < rect[1]+rect[3]:
                self.ball.velocityVector[2] *= -1
                self.ball.rotationVector = 0.2 * self.ball.rotationVector + (np.array([-self.myRacket.velocity[1],  self.myRacket.velocity[0], 0]) / BALL_SPIN_PARAMETER_DOS)
            else:
                self.ball.velocityVector[2] *= 0
                self.view.enemyPoint = True

        elif ballZ  > meta:
            rect = self.enemyRacket.getRacketRect()
            if ballX > rect[0] and ballX < rect[0]+rect[2] and ballY > rect[1] and ballY < rect[1]+rect[3]:
                self.ball.velocityVector[2] *= -1
                self.ball.rotationVector = 0.2 * self.ball.rotationVector + (np.array([-self.enemyRacket.velocity[1],  self.enemyRacket.velocity[0], 0]) / BALL_SPIN_PARAMETER_DOS )
            else:
                self.ball.velocityVector[2] *= -1
                self.view.myPoint = True

        # STAR CAPTURE
        if self.canIcreteStars:
            starX = self.star.position[0]
            starY = self.star.position[1]
            starZ = self.star.position[2]
            starR = self.star.radius * 2

            if ballX - rad < starX + starR and ballX + rad > starX - starR and ballY - rad < starY + starR and ballY + rad > starY - starR and ballZ - rad < starZ + starR and ballZ + rad > starZ - starR:
                if self.ball.velocityVector[2] > 0:
                    self.view.starForMe = True
                else:
                    self.view.starForEnemy = True
                starPosition = None
                if self.canIcreteStars:
                    newX = np.random.randint(-self.windowSize[0] // 2 + STAR_RADIUS,   self.windowSize[0] // 2 - STAR_RADIUS)
                    newY = np.random.randint(-self.windowSize[1] // 2 + STAR_RADIUS,  self.windowSize[1] // 2 - STAR_RADIUS)
                    starPosition = np.array([newX, newY, PERSPECTIVE_PARAMETER * (START_POSITION + (END_POSITION - START_POSITION) / 2)])
                self.star.move(starPosition)
