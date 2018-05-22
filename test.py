import numpy as np
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPolygon
from PyQt5.QtCore import Qt, QPoint, QThread
import sys, random, time

PRECISION = 40
r = 250
offset = 400
class AThread(QThread):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.angle = 0
    def run(self):
        while(1):
            points = self.widget.points
            for i, rowOfPoints in enumerate(points):
                for j, point in enumerate(rowOfPoints):
                    self.widget.points[i][j] = point * getRotationMatrix(self.angle, 'x') * getRotationMatrix(self.angle *2, 'y')
            self.widget.points = points
            time.sleep(0.01)

            self.angle += 0.00005
            self.widget.update()


class Point():
    def __init__(self, array):
        self.x = array[0]
        self.y = array[1]
        self.z = array[2]

    def __mul__(self, rotArray):
        return Point(rotArray.dot(np.array([self.x, self.y, self.z]).T))


def getRotationMatrix(phi, axis):
    sin = np.sin(phi)
    cos = np.cos(phi)
    if axis == 'x':
        return np.array([[1, 0, 0],
                         [0, cos, -sin],
                         [0, sin, cos]])
    elif axis == 'y':
        return np.array([[cos, 0, sin],
                         [0, 1, 0],
                         [-sin, 0, cos]])
    elif axis == 'z':
        return np.array([[cos, -sin, 0],
                         [sin, cos, 0],
                         [0, 0, 1]])



# def generateSphere(a):
#     phis = np.linspace(0, 2*np.pi, PRECISION)
#     thetas = np.linspace(-np.pi, np.pi, PRECISION / 2)
#
#     points = [[None for j in range(thetas.size)] for i in range(phis.size)]
#     # print(np.array(points).shape)
#     for i, phi in enumerate(phis):
#         for j, theta in enumerate(thetas):
#              x = r * np.cos(phi) * np.cos(theta)
#              y = r * np.cos(phi) * np.sin(theta)
#              z = r * np.sin(phi)
#              points[i][j] = Point([x, y, z]) * getRotationMatrix(a, 'x')
#     return points


def generateSphere(a):
    phis = np.linspace(0, 2 * np.pi, PRECISION)
    thetas = np.linspace(-np.pi, np.pi, PRECISION / 2)

    points = [[None for j in range(thetas.size)] for i in range(phis.size)]
    for i, phi in enumerate(phis):
        for j, theta in enumerate(thetas):
            x = r * np.cos(phi) * np.cos(theta)
            y = r * np.cos(phi) * np.sin(theta)
            z = r * np.sin(phi)
            points[i][j] =  Point(np.array([x, y, z]))
    return points


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.initUI()
        self.points = generateSphere(0)

    def initUI(self):
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowTitle('Points')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawSphere(qp)
        qp.end()

    def drawSphere(self, qp):
        points = self.points
        for i in range(1, len(points)):
            for j in range(1, len(points[0])):
                x = points[i][j].x
                y = points[i][j].y
                z = points[i][j].z
                ra = r / 6
                # if j < 40:
                #     qp.setPen(Qt.yellow)
                #     qp.setBrush(Qt.yellow)
                # else:
                #     qp.setPen(Qt.black)
                #     qp.setBrush(Qt.black)
                # if x < ra and x > -ra or y < ra and y > -ra  or z < ra and z > -ra:
                #     qp.setPen(Qt.yellow)
                #     qp.setBrush(Qt.yellow)
                # else:
                #     qp.setPen(Qt.black)
                #     qp.setBrush(Qt.black)
                o = offset
                qp.drawConvexPolygon(QPoint(points[i][j].x + o, points[i][j].y + o),
                                QPoint(points[i-1][j].x + o, points[i-1][j].y + o),
                                QPoint(points[i-1][j-1].x + o, points[i-1][j-1].y + o),
                                QPoint(points[i][j-1].x + o, points[i][j-1].y + o))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    thread = AThread(ex)
    thread.start()
    sys.exit(app.exec_())