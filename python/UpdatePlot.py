import sys
import os
from PyQt4 import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from emokit.emotiv import Emotiv


class emo_waves(QtGui.QWidget):
    def __init__(self):
        super(emo_waves, self).__init__()
        self.init_ui()
        self.qt_connections()
        self.electrodes_colors = (('AF3', (15, 150, 255)), ('AF4', (150, 255, 15)), ('F3', (255, 15, 150)),
                                  ('F4', (15, 150, 255)), ('F7', (150, 255, 15)), ('F8', (255, 15, 150)),
                                  ('FC5', (15, 150, 255)), ('FC6', (150, 255, 15)), ('T7', (255, 15, 150)),
                                  ('T8', (15, 150, 255)), ('P7', (150, 255, 15)), ('P8', (255, 15, 150)),
                                  ('O1', (15, 150, 255)), ('O2', (150, 255, 15))
                                  )
        self.electrodes = {'AF3': ([], []), 'AF4': ([], []), 'F3': ([], []),
                           'F4': ([], []), 'F7': ([], []), 'F8': ([], []),
                           'FC5': ([], []), 'FC6': ([], []), 'T7': ([], []),
                           'T8': ([], []), 'P7': ([], []), 'P8': ([], []),
                           'O1': ([], []), 'O2': ([], [])
                           }
        self.all_waves = []
        for i in xrange(14):
            self.plotcurve = pg.PlotDataItem()  # downsample=10)
            self.plotwidget[i].addItem(self.plotcurve)
            self.plotcurve.setPen(self.electrodes_colors[i][1])
            self.all_waves.append(self.plotcurve)
        self.amplitude = 2
        self.t = 0
        self.headset = Emotiv()
        packet = self.headset.dequeue()
        while packet is None:
            packet = self.headset.dequeue()
        for key in self.electrodes.keys():
            data_x = np.arange(-128, 0)
            data_y = np.ones(128 * 1)
            data_y *= packet.sensors[key]['value'] / 400
            self.electrodes[key] = (data_x, data_y)
        self.update_electrode()
        self.updateplot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.moveplot)
        self.timer.start(1)

    def init_ui(self):
        self.setWindowTitle('EmoViewer')
        pic = QtGui.QLabel()
        pic.setGeometry(10, 10, 100, 100)
        # use full ABSOLUTE path to the image, not relative
        pic.setPixmap(QtGui.QPixmap(os.getcwd() + "\\image.jpg"))

        layout = QtGui.QGridLayout()
        waveform_layout = QtGui.QVBoxLayout()
        layout.addWidget(pic, 0, 0)
        layout.addLayout(waveform_layout, 0, 1)
        self.plots_widget = pg.GraphicsLayoutWidget()
        waveform_layout.addWidget(self.plots_widget)
        self.setLayout(layout)
        self.plotwidget = []
        for i in xrange(14):
            if i:
                self.plots_widget.nextRow()
            self.plotwidget.append(self.plots_widget.addPlot())
            left_axis = self.plotwidget[-1].getAxis('left')
            self.plotwidget[-1].disableAutoRange(pg.ViewBox.YAxis)
            #self.plotwidget[-1].getViewBox().setRange(yRange=(10.25, 10.75))
            left_axis.setStyle(autoExpandTextSpace=False)
            # left_axis.setGrid(126)  # Slows down too much
            left_axis.setRange(9, 11)
            if i == 13:
                self.plotwidget[-1].setLabel('bottom', 'Time', 's')
            else:
                self.plotwidget[-1].showAxis('bottom', False)


        self.increasebutton = QtGui.QPushButton("Increase Amplitude")
        self.decreasebutton = QtGui.QPushButton("Decrease Amplitude")

        # layout.addWidget(self.increasebutton)
        # layout.addWidget(self.decreasebutton)

        self.setGeometry(100, 100, 1000, 600)
        self.show()

    def qt_connections(self):
        self.increasebutton.clicked.connect(self.on_increasebutton_clicked)
        self.decreasebutton.clicked.connect(self.on_decreasebutton_clicked)

    def moveplot(self):
        self.t+=1
        #self.plotwidget[-1].setPos(-self.t, 0)
        self.update_electrode()
        self.updateplot()

    def updateplot(self):
        for i, plot in enumerate(self.all_waves):
            plot.setData(*self.electrodes[self.electrodes_colors[i][0]])

    def update_electrode(self):
        #TODO create buffer to try speeding up display refresh
        if self.headset.dequeue() is not None:
            for key in self.electrodes.keys():
                data_y = self.electrodes[key][1]
                #data_y = np.roll(data_y, -1)
                data_y[:-1] = data_y[1:]
                data_y[-1] = self.headset.dequeue().sensors[key]['value'] / 400  # - 8192
                data_x = self.electrodes[key][0]
                data_x = np.roll(data_x, -1)
                data_x[-1] = self.t
                self.electrodes[key] = (data_x, data_y)  # * self.amplitude)

    def on_increasebutton_clicked(self):
        print '============='
        print ("Amplitude increased")
        self.amplitude += 1
        #self.updateplot()
        print self.electrodes['F7'][0].shape
        print self.all_waves[0]
        print '============='

    def on_decreasebutton_clicked(self):
        print ("Amplitude decreased")
        self.amplitude -= 1
        self.updateplot()

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Sinuswave')
    ex = emo_waves()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()