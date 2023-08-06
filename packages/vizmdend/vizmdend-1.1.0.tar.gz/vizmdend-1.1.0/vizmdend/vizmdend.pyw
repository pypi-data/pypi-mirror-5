#!/usr/bin/python

import reader
from logger import tr

import numpy

from PyQt4.QtCore import (Qt, pyqtSignature, QStringList)
from PyQt4.QtGui import (QApplication, QDialog, QFileDialog, QSizePolicy)
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import ui_vizmdend

MAC = True
try:
    from PyQt4.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False) # axes cleared every time plot() is called
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class Vizmdend(QDialog, ui_vizmdend.Ui_Vizmdend):
    def __init__(self, vizm, parent=None):
        super(Vizmdend, self).__init__(parent)
        self._vizm = reader.Reader()
        self.setupUi(self)
        self.grapWidget = MyMplCanvas(self.embedGraph, width=7, height=5, dpi=100)
        if not MAC:
            self.browseButton.setFocusPolicy(Qt.NoFocus)
            self.plotButton.setFocusPolicy(Qt.NoFocus)
            self.closeButton.setFocusPolicy(Qt.NoFocus)
        if vizm:
            self.filenameEdit.setText(vizm)
            self.updateUi()

    def plotFigure(self, yfield, xfield):
        axes = self.grapWidget.axes
        axes.set_ylabel(yfield)
        yvalues=self._vizm._parser.getValues(yfield)
        if not xfield:
            xfield='step'
            xvalues=range(1,1+len(yvalues))
        else:
            xvalues=self._vizm._parser.getValues(xfield)
        axes.set_xlabel(xfield)
        axes.plot(xvalues, yvalues)
        self.grapWidget.draw()

    def populate(self, comboBox):
        '''populate the comboBox with the fields'''
        fields = QStringList(['',]+self._vizm.getFields())
        comboBox.addItems(fields)

    def updateUi(self):
        '''Allow plotting only if yComboBox is populated'''
        mdendfile = self.filenameEdit.text()
        self._vizm.parse( mdendfile )
        self.populate(self.yComboBox)
        self.populate(self.xComboBox)
        enable = self.yComboBox.count()
        self.plotButton.setEnabled(enable)

    @pyqtSignature("QString")
    def on_filenameEdit_textChanged(self):
        self.updateUi()

    @pyqtSignature("")
    def on_plotButton_clicked(self):
        yfield = self.yComboBox.currentText()
        xfield = self.xComboBox.currentText()
        self.plotFigure(yfield, xfield)
        
    @pyqtSignature("")
    def on_browseButton_clicked(self):
        self.filenameEdit.setText(QFileDialog.getOpenFileName())
        self.updateUi()

if __name__ == '__main__':
    import argparse
    import sys
    p=argparse.ArgumentParser(description='Plot a field from mdend AMBER file')
    p.add_argument('--mdendfile', help='mdend file name')
    args=p.parse_args()
    
    app = QApplication(sys.argv)
    form = Vizmdend(args.mdendfile)
    form.show()
    app.exec_()
    print('Good luck with your paper, mate!')
   
    
