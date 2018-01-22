import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
from roboclaw import RoboClaw
import CalibrationMotorFunctions as CMF
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class App(QMainWindow):
    def __init__(self, parent, rc):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########

        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)
        self.rc = rc
        self.starttime = time.time()
        # self.view = self.canvas.addViewBox()
        # self.view.setAspectLocked(True)
        # self.view.setRange(QtCore.QRectF(0,0, 100, 100))

        #  image plot
        # self.img = pg.ImageItem(border='w')
        # self.view.addItem(self.img)

        self.canvas.nextRow()
        #  line plot
        self.otherplot = self.canvas.addPlot()
        self.h2 = self.otherplot.plot(pen='y')
        self.button = QPushButton('Test', self)
        self.label = QLabel(self)
        self.signal_start_background_job = QtCore.pyqtSignal()
        self.worker = WorkerObject()
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)

        self.signal_start_background_job.connect(self.worker.background_job)

        self.button.clicked.connect(self.start_background_job)

        #### Set Data  #####################

        self.xdata = []
        # self.X, self.Y = np.meshgrid(self.x, self.x)
        self.ydata = []
        self.counter = 0
        # self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):

        # self.data = np.sin(self.X / 3. + self.counter / 9.) * \
        #    np.cos(self.Y / 3. + self.counter / 9.)
        self.ydata.append(CMF.readInCurrent(self.rc))

        # self.img.setImage(self.data)

        now = time.time()
        currTime = (now - self.starttime)
        self.xdata.append(currTime)
        self.h2.setData(self.xdata, self.ydata)
        # if dt <= 0:
        #    dt = 0.000000000001
        # fps2 = 1.0 / dt
        self.lastupdate = now
        # self.fps = self.fps * 0.9 + fps2 * 0.1
        # tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps)
        # self.label.setText(tx)
        QtCore.QTimer.singleShot(1, self._update)
        self.counter += 1

    def start_background_job(self):
        # No harm in calling thread.start() after the thread is already started.
        self.thread.start()
        self.signal_start_background_job.emit()


class WorkerObject(QtCore.QObject):
    @QtCore.pyqtSlot()
    def background_job(self):
        print('yay button')
        # CMF.setMotorSpeed(self.rc, 20)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    rc = RoboClaw('COM7', 0x80)
    thisapp = App(None, rc)
    thisapp.show()
    sys.exit(app.exec_())
