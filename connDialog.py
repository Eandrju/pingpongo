from imports import *


class ConnDialog(QtWidgets.QDialog):
    acceptSignal = QtCore.pyqtSignal()

    def __init__(self,gui):
        super().__init__()
        QtCore.QObject.__init__(self)
        uic.loadUi('connDialog.ui',self)
        self.setWindowTitle("Connection Settings")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.gui = gui
        self.acceptSignal.connect(lambda x=self: self.gui.endDialog(x))
        self.exec_()


    def accept(self):
        #TODO checks
        self.acceptSignal.emit()
        super().accept()


