import sys
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
        self.electrodes = {'AF3': [[], []], 'AF4': [[], []], 'F3': [[], []],
                           'F4': [[], []], 'F7': [[], []], 'F8': [[], []],
                           'FC5': [[], []], 'FC6': [[], []], 'T7': [[], []],
                           'T8': [[], []], 'P7': [[], []], 'P8': [[], []],
                           'O1': [[], []], 'O2': [[], []]
                           }
        self.all_waves = []
        for i in xrange(14):
            self.plotcurve = pg.PlotDataItem()
            self.plotwidget[i].addItem(self.plotcurve)
            self.plotcurve.setPen(self.electrodes_colors[i][1])
            self.all_waves.append(self.plotcurve)
        self.amplitude = 10
        self.t = 0
        self.headset = Emotiv()
        packet = self.headset.dequeue()
        while packet is None:
            packet = self.headset.dequeue()
        for key in self.electrodes.keys():
            data_x = np.zeros(384)
            self.electrodes[key][0] = data_x
            data_y = np.zeros(128 * 3)
            data_y *= packet.sensors[key]['value'] / 4000
            self.electrodes[key][1] = data_y
        self.updateplot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.moveplot)
        self.timer.start(10)

    def init_ui(self):
        self.setWindowTitle('EmoViewer')
        layout = QtGui.QVBoxLayout()
        # layout = QtGui.QGridLayout()
        self.plots_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.plots_widget)
        self.setLayout(layout)
        self.plotwidget = []
        for i in xrange(14):
            if i:
                self.plots_widget.nextRow()
            self.plotwidget.append(self.plots_widget.addPlot())  # pg.PlotWidget())
            if i == 13:
                self.plotwidget[-1].setLabel('bottom', 'Time', 's')
            else:
                self.plotwidget[-1].showAxis('bottom', False)
            #self.plotwidget[-1].showAxis(False)
            #layout.addPlot(self.plotwidget[-1])

        self.increasebutton = QtGui.QPushButton("Increase Amplitude")
        self.decreasebutton = QtGui.QPushButton("Decrease Amplitude")

        # layout.addWidget(self.increasebutton)
        # layout.addWidget(self.decreasebutton)

        self.setGeometry(10, 10, 1000, 600)
        self.show()

    def qt_connections(self):
        self.increasebutton.clicked.connect(self.on_increasebutton_clicked)
        self.decreasebutton.clicked.connect(self.on_decreasebutton_clicked)

    def moveplot(self):
        self.t+=1
        self.plotwidget[-1].setPos(-self.t, 0)
        self.update_electrode()
        self.updateplot()

    def updateplot(self):
        #print "Update"
        # np.sin(np.linspace(0,30,121)+self.t)
        #data1 = self.amplitude*np.sin(np.linspace(0,30,121)+self.t)
        #self.plotcurve.setScale(self.amplitude)
        for i, plot in enumerate(self.all_waves):
            data_x = self.electrodes[self.electrodes_colors[i][0]][0]
            data_y = self.electrodes[self.electrodes_colors[i][0]][1]
            plot.setData(data_y)
            #plot.setPos(data_x[0], 0)

    def update_electrode(self):
        if self.headset.dequeue() is not None:
            for key in self.electrodes.keys():
                data_y = self.electrodes[key][1]
                data_y = np.roll(data_y, -1)
                data_y[-1] = self.headset.dequeue().sensors[key]['value'] - 8192
                data_x = self.electrodes[key][0]
                data_x = np.roll(data_x, -1)
                data_x[-1] = self.t
                self.electrodes[key] = [data_x, data_y]

    def on_increasebutton_clicked(self):
        print ("Amplitude increased")
        self.amplitude += 1
        self.updateplot()

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