# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 14:35:24 2018

@author: User1
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QSizePolicy, QFrame
import os
import pandas as pd
import numpy as np
from plotCode_GUI import plotTrial as pltGUI
from plotterGUICode import Ui_Eyelinkplotter
import scipy
import scipy.io
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec

# ==============================================================================
# Functions for reading mat files
# ==============================================================================
def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    
    from: `StackOverflow <http://stackoverflow.com/questions/7008608/scipy-io-loadmat-nested-structures-i-e
    -dictionaries>`_
    '''
    data = scipy.io.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)


def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], scipy.io.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict


def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, scipy.io.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict


def saveToMat(df, fn):
    import scipy
    a_dict = {col_name: df[col_name].values for col_name in df.columns.values}
    scipy.io.savemat(fn, {'data': a_dict})


# =============================================================================
# Plot things in the GUI
# =============================================================================
class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        gs = gridspec.GridSpec(4, 3)
        gs.update(wspace=0.3, hspace=0.5)
        self.ax1 = fig.add_subplot(gs[-1,0])
        self.ax2 = fig.add_subplot(gs[-1,1])
        self.ax3 = fig.add_subplot(gs[-1,2])
        self.ax4 = fig.add_subplot(gs[:-1,:])
        
        self.Axis = [self.ax1, self.ax2, self.ax3, self.ax4]
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.figAx = [fig, self.ax1, self.ax2, self.ax3, self.ax4]

    def compute_initial_figure(self):
        for ax in self.Axis:
            ax.plot([], [])
            ax.set_xticks([])
            ax.set_yticks([])

    def updateFig(self):
        self.draw()

    def clearFig(self):
        for ax in self.Axis:
            ax.clear()

# ==============================================================================
# Build the GUI
# ==============================================================================
class MyMessageBox(QtWidgets.QMessageBox):
    def __init__(self):
        QtWidgets.QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QtWidgets.QMessageBox.event(self, e)

        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        textEdit = self.findChild(QtWidgets.QTextEdit)
        if textEdit != None:
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        return result


class Window(QtWidgets.QMainWindow):
    # ==============================================================================
    # Build GUI
    # ==============================================================================
    def __init__(self, parent=None):
        # ======================================================================
        # Initiate main features of the GUI
        # ======================================================================
        super(QtWidgets.QMainWindow, self).__init__()
        self.ui = Ui_Eyelinkplotter()
        self.ui.setupUi(self)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon('eye.png'))

        self.imDir = None
        self.data = []
        self.populateLists()

        # Run button press initiation
        self.ui.selectFile.clicked.connect(self.selectDataFile)

        # set background color
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        self.setPalette(palette)

        # Set tab color 
        self.ui.heatmapTab.setStyleSheet('QTabBar::tab {color: rgb(0,0,0)}')
        self.ui.heatmapTab.setVisible(False)

        # Set animation flag
        self.animationOn = False

        # Set key bindings
        self.left = QtWidgets.QShortcut(QtGui.QKeySequence('left'), self)
        self.left.activated.connect(self.backButtonClick)
        self.right = QtWidgets.QShortcut(QtGui.QKeySequence('right'), self)
        self.right.activated.connect(self.nextButtonClick)
        self.space = QtWidgets.QShortcut(QtGui.QKeySequence('space'), self)
        self.space.activated.connect(self.toggleIncludedTrial)

        # Init plot area
        frame = QFrame(self)
        self.Canvas = MyMplCanvas(frame)
        self.ui.plotGrid.addWidget(self.Canvas)
        self.ui.plotGrid.addWidget(frame)
        self.Canvas.compute_initial_figure()

        # Display GUI
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()
        self.activateWindow()

    def populateLists(self):
        # Set plot type options
        pltTypeList = ['gaze', 'heat']
        self.ui.plotType.clear()
        self.ui.plotType.addItems(pltTypeList)
        self.ui.plotType.setCurrentIndex(0)

        # Set aspect ratio options
        bgAspectList = ['equal', 'auto']
        self.ui.aspectRatio.clear()
        self.ui.aspectRatio.addItems(bgAspectList)
        self.ui.aspectRatio.setCurrentIndex(0)

        # Set colormap options
        cmapList = ['Accent', 'Blues', 'BrBG', 'BuGn', 'BuPu', 'CMRmap', 'Dark2',
                    'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PRGn', 'Paired',
                    'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd',
                    'Purples', 'RdBu', 'RdGy', 'RdPu', 'RdYlBu', 'RdYlGn', 'Reds',
                    'Set1', 'Set2', 'Set3', 'Spectral', 'Wistia', 'YlGn', 'YlGnBu',
                    'YlOrBr', 'YlOrRd', 'afmhot', 'autumn', 'binary', 'bone', 'brg',
                    'bwr', 'cool', 'coolwarm', 'copper', 'cubehelix', 'flag',
                    'gist_earth', 'gist_gray', 'gist_heat', 'gist_ncar',
                    'gist_rainbow', 'gist_stern', 'gist_yarg', 'gnuplot', 'gnuplot2',
                    'gray', 'hot', 'hsv', 'inferno', 'jet', 'magma', 'nipy_spectral',
                    'ocean', 'pink', 'plasma', 'prism', 'rainbow', 'seismic', 'spec',
                    'spectral', 'spring', 'summer', 'terrain', 'viridis', 'winter']
        # [self.kernelCM.addItem(i) for i in cmapList]
        self.ui.kernelCM.clear()
        self.ui.kernelCM.addItems(cmapList)
        self.ui.kernelCM.setCurrentIndex(cmapList.index('hot'))

        # Set kernel options
        kernelList = ['AiryDisk2DKernel (Radius)', 'Box2DKernel (Width)',
                      'Gaussian2DKernel (Std)', 'MexicanHat2DKernel (Width)',
                      'Tophat2DKernel (Radius)', 'TrapezoidDisk2DKernel (Radius)']
        self.ui.kernel.clear()
        self.ui.kernel.addItems(kernelList)
        self.ui.kernel.setCurrentIndex(2)

        # Set inverse color
        inverse = ['True', 'False']
        self.ui.kernelCMInverse.clear()
        self.ui.kernelCMInverse.addItems(inverse)
        self.ui.kernelCMInverse.setCurrentIndex(1)

        # Initiate variables
        self.varInitiation()

        # plot style
        self.ui.plotStyle.setCurrentIndex(0)
        self.ui.highlightEvent.setCurrentIndex(0)
        self.ui.plotBackground.setCurrentIndex(0)
        self.ui.showTrace.setCurrentIndex(0)

        # Animation settings
        self.ui.showTrace.setCurrentIndex(0)
        self.ui.useAperture.setCurrentIndex(0)

        # Add extra settings if data has been loaded 
        if len(self.data) > 2:
            keys = [key for key in self.data.keys() if key[:3] == 'DK_' or key[:3] == 'DV_']
            keys = [key for key in keys if len(key.split()) == 1]
            keys = sorted(keys)
            # Clear variables first
            # Set variables for additional info
            self.ui.addInfo.setCurrentIndex(0)
            # Set plot data
            self.ui.time.setCurrentIndex(keys.index("DK_rawTime"))
            self.ui.xCoords.setCurrentIndex(keys.index("DK_rawX"))
            self.ui.yCoords.setCurrentIndex(keys.index("DK_rawY"))
            self.ui.speed.setCurrentIndex(keys.index("DK_euclidDist"))

    def defineButtonPresses(self):

        self.ui.saveFile.clicked.connect(self.saveDataFile)
        self.ui.actionSelect_file.triggered.connect(self.selectDataFile)
        self.ui.selectImageFolder.clicked.connect(self.selectImDir)
        self.ui.backButton.clicked.connect(self.backButtonClick)
        self.ui.updateButton.clicked.connect(self.updateButtonClick)
        self.ui.nextButton.clicked.connect(self.nextButtonClick)
        self.ui.jumpToTrial.clicked.connect(self.plotSpecificTrial)
        self.ui.resetVariables.clicked.connect(self.resetVars)
        self.ui.trialScroll.sliderReleased.connect(self.trialScrollChange)
        self.ui.trialScroll.sliderMoved.connect(self.scrollDrag)
        self.ui.toggleIncluded.clicked.connect(self.toggleIncludedTrial)
        self.ui.trialsToPlot.activated.connect(self.toggleTrialsToPlot)
        self.ui.animateButton.clicked.connect(self.animateButtonClick)
        self.ui.saveAnimButton.clicked.connect(self.saveAnimation)

    def scrollDrag(self):
        self.ui.currentTrialDisp.display(self.ui.trialScroll.value())

    def varInitiation(self):
        # imageDirectory
        if self.imDir is None:
            self.imDir = ''

        # Plot lims
        self.ui.xMinValue.setValue(0)
        self.ui.xMaxValue.setValue(1680)
        self.ui.yMinValue.setValue(0)
        self.ui.yMaxValue.setValue(1050)

        # Kernel values
        self.ui.kernelParameter.setValue(20)
        self.ui.kernelScale.setValue(1)
        self.ui.kernelThreshold.setValue(0.00)
        self.ui.kernelAlpha.setValue(0.50)

        # Animation values
        self.ui.blackDotSize.setValue(50)
        self.ui.redDotSize.setValue(20)
        self.ui.frameStepSize.setValue(5)

        # Gauss values
        self.ui.apertureR.setValue(75)  # complete opcity circle
        self.ui.apertureOpac.setValue(1)
        self.ui.edgeR.setValue(10)  # gaussian radius
        self.ui.edgeOpac.setValue(0.25)

    def readFile(self, fName):
        dType = os.path.splitext(fName)[1]
        if dType == '.p':
            data = pd.read_pickle(fName)
        elif dType == '.hdf':
            data = pd.read_hdf(fName)
        elif dType == '.json':
            data = pd.read_json(fName)
            # Reformat lists to np.array
            ls = ['rawX', 'rawY', 'rawTime', 'euclidDist']
            for i in ls:
                data['DK_' + i] = [np.array(x) for x in data['DK_' + i].values]
        elif dType == '.mat':
            data = loadmat(fName)
            data = pd.DataFrame(data['data'])
        return data

    def selectDataFile(self):
        self.fileName = QtWidgets.QFileDialog.getOpenFileName(None, 'Select file(s)', "","Pickle (*.p);;All Files (*)")[0]
        if self.fileName:
            fileBase = os.path.basename(self.fileName)
            self.ui.selectedFile.setText(os.path.splitext(fileBase)[0])
            self.data = self.readFile(self.fileName)
            self.allowedIndexes = self.data.index.get_values()

            # Trial counters
            self.previousTrial = 0
            self.currTrial = 1
            self.nextTrial = 2
            self.maxTrialNr = len(self.data)
            self.trialIndex = self.currTrial - 1

            # Set background variable options
            keys = [key for key in self.data.keys() if key[:3] == 'DK_' or key[:3] == 'DV_']
            keys = [key for key in keys if len(key.split()) == 1]
            keys = sorted(keys)
            self.ui.bgImageVariable.addItems(keys)
            self.ui.trialScroll.setMinimum(1)
            self.ui.trialScroll.setMaximum(self.maxTrialNr)

            # Set variables for additional info
            self.ui.addInfo.addItems(['False'] + keys)
            # Set plot data
            self.ui.time.addItems(keys)
            self.ui.time.setCurrentIndex(keys.index("DK_rawTime"))
            self.ui.xCoords.addItems(keys)
            self.ui.xCoords.setCurrentIndex(keys.index("DK_rawX"))
            self.ui.yCoords.addItems(keys)
            self.ui.yCoords.setCurrentIndex(keys.index("DK_rawY"))
            self.ui.speed.addItems(keys)
            if 'DK_speed' in keys:
                self.ui.speed.setCurrentIndex(keys.index("DK_speed"))
            else:
                self.ui.speed.setCurrentIndex(keys.index("DK_euclidDist"))
            # Initiate counters
            self.defineButtonPresses()
            self.setCounters()
            self.plotData()
            # Initiate save file button
            self.ui.saveFile.setEnabled(True)
            
    def saveDataFile(self):
        dType = os.path.splitext(self.fileName)[1]
        if dType == '.p':
            self.data.to_pickle(self.fileName)
        elif dType == '.hdf':
            self.data.to_hdf(self.fileName, 'w')
        elif dType == '.json':
            self.data.to_json(self.fileName)
        elif dType == '.csv':
            self.data.to_csv(self.fileName, index=False, na_rep='#N/A')
        elif dType == '.mat':
            saveToMat(self.data, self.fileName)

    def selectImDir(self):
        self.imDir = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select image folder')
        self.imDir += '/'

    def setCounters(self):
        # Set counters
        self.ui.currentTrialDisp.display(self.currTrial)
        self.ui.trialScroll.setValue(self.currTrial)
        self.ui.jumpToTrialNr.setValue(self.currTrial)
        # Set included trial
        included = str(self.data.DK_includedTrial[self.trialIndex])
        self.ui.includedOrExcluded.setText(included)

    def backButtonClick(self):
        if self.previousTrial > 0:
            self.previousTrial -= 1
            self.currTrial -= 1
            self.nextTrial -= 1
        if self.nextTrial == self.currTrial:
            self.nextTrial += 1

        # check if the trial is in the allowed list
        if self.currTrial - 1 not in self.allowedIndexes and self.currTrial - 1 > np.min(self.allowedIndexes):
            self.backButtonClick()
        elif self.currTrial - 1 < np.min(self.allowedIndexes):
            self.nextTrial = np.min(self.allowedIndexes) + 2
            self.previousTrial = self.nextTrial - 2
            self.currTrial = self.nextTrial - 1
            self.setCounters()
            self.plotData()
        else:
            self.setCounters()
            self.plotData()

    def updateButtonClick(self):
        if self.currTrial - 1 not in self.allowedIndexes:
            self.currTrial = self.allowedIndexes.flat[np.abs(self.allowedIndexes - (self.currTrial - 1)).argmin()] + 1
            self.nextTrial = self.currTrial + 1
            self.previousTrial = self.currTrial - 1
        self.setCounters()
        self.plotData()

    def animateButtonClick(self):
        if self.currTrial - 1 not in self.allowedIndexes:
            self.currTrial = self.allowedIndexes.flat[np.abs(self.allowedIndexes - (self.currTrial - 1)).argmin()] + 1
            self.nextTrial = self.currTrial + 1
            self.previousTrial = self.currTrial - 1
        self.setCounters()
        self.runAni()

    def nextButtonClick(self):
        if self.nextTrial <= self.maxTrialNr:
            self.nextTrial += 1
            self.previousTrial = self.nextTrial - 2
            self.currTrial = self.nextTrial - 1
        if self.nextTrial > self.maxTrialNr:
            self.nextTrial -= 1
        # check if the trial is in the allowed list
        if self.currTrial - 1 not in self.allowedIndexes and self.currTrial - 1 < np.max(self.allowedIndexes):
            self.nextButtonClick()
        elif self.currTrial - 1 > np.max(self.allowedIndexes):
            self.nextTrial = np.max(self.allowedIndexes) + 2
            self.previousTrial = self.nextTrial - 2
            self.currTrial = self.nextTrial - 1
            self.setCounters()
            self.plotData()
        else:
            self.setCounters()
            self.plotData()

    def plotSpecificTrial(self):
        trialToPlot = self.ui.jumpToTrialNr.value()
        if trialToPlot - 1 not in self.allowedIndexes:
            trialToPlot = self.allowedIndexes.flat[np.abs(self.allowedIndexes - (trialToPlot - 1)).argmin()] + 1
            self.ui.jumpToTrialNr.setValue(trialToPlot)
        if trialToPlot >= self.maxTrialNr:
            self.previousTrial = self.maxTrialNr - 1
            self.currTrial = self.maxTrialNr
            self.nextTrial = self.maxTrialNr
        else:
            self.previousTrial = trialToPlot - 1
            self.currTrial = trialToPlot
            self.nextTrial = trialToPlot + 1
        self.setCounters()
        self.plotData()

    def trialScrollChange(self):
        self.ui.jumpToTrialNr.setValue(self.ui.trialScroll.value())
        self.plotSpecificTrial()

    def resetVars(self):
        self.populateLists()
        self.plotData()

    def toggleIncludedTrial(self):
        if self.data.DK_includedTrial.loc[self.trialIndex] == True:
            self.data.loc[self.trialIndex, 'DK_includedTrial'] = False
        elif self.data.DK_includedTrial[self.trialIndex] == False:
            self.data.loc[self.trialIndex, 'DK_includedTrial'] = True
        self.toggleTrialsToPlot()
        self.setCounters()
        self.updateButtonClick()

    def toggleTrialsToPlot(self):
        if self.ui.trialsToPlot.currentText() == 'All':
            self.allowedIndexes = self.data.index.get_values()
        elif self.ui.trialsToPlot.currentText() == 'Included':
            self.allowedIndexes = self.data.loc[self.data.DK_includedTrial == True, :].index.get_values()
        elif self.ui.trialsToPlot.currentText() == 'Excluded':
            self.allowedIndexes = self.data.loc[self.data.DK_includedTrial == False, :].index.get_values()
        if len(self.allowedIndexes) == 0:
            self.allowedIndexes = self.data.index

    def plotData(self):
        self.trialIndex = self.currTrial - 1
        self.time = self.data[self.ui.time.currentText().split()[0]][self.trialIndex]
        self.x = self.data[self.ui.xCoords.currentText().split()[0]][self.trialIndex]
        self.y = self.data[self.ui.yCoords.currentText().split()[0]][self.trialIndex]
        self.speed = self.data[self.ui.speed.currentText().split()[0]][self.trialIndex]
        
        # Do some sanity checks on settings
        pltBg = self.ui.plotBackground.currentText()
        if pltBg == 'True':
            pltBg = True
        elif pltBg == 'False':
            pltBg = False

        # Check where to find background image
        bgImage = ''
        if not self.imDir:
            pltBg = False
        elif pltBg == True:
            bgImage = self.imDir + os.path.basename(self.data[self.ui.bgImageVariable.currentText()][self.trialIndex])
        # Check kernel inverse color
        inverseKernel = self.ui.kernelCMInverse.currentText()
        if inverseKernel == 'True':
            inverseKernel = True
        elif inverseKernel == 'False':
            inverseKernel = False
        
        # Compatibility mode
        durSaccKey = 'DK_durSacc'
        durFixKey = 'DK_durFix'
        if 'DK_saccDur' in self.data.keys():
            durSaccKey = 'DK_saccDur'
        if 'DK_fixDur' in self.data.keys():
            durFixKey = 'DK_fixDur'
        
        # Build the final parameter dict
        self.par = {
            'pltType': self.ui.plotType.currentText().split()[0],
            'pltStyle': self.ui.plotStyle.currentText().split()[0],
            'pltBg': pltBg,
            'bgImage': bgImage,
            'bgAspect': self.ui.aspectRatio.currentText().split()[0],
            'trial': self.trialIndex,
            'dataScaling': self.ui.kernelScale.value(),
            'kernel': self.ui.kernel.currentText().split()[0],
            'kernelPar': self.ui.kernelParameter.value(),
            'kernelCM': self.ui.kernelCM.currentText().split()[0],
            'kernelCMInverse': inverseKernel,
            'kernelThreshold': self.ui.kernelThreshold.value(),
            'kernelAlpha': self.ui.kernelAlpha.value(),
            'xMax': self.ui.xMaxValue.value(),
            'xMin': self.ui.xMinValue.value(),
            'yMax': self.ui.yMaxValue.value(),
            'yMin': self.ui.yMinValue.value(),
            'included': str(self.data.DK_includedTrial[self.trialIndex]),
            'highlight': str(self.ui.highlightEvent.currentText()),
            'ssacc': self.data.DK_ssacc[self.trialIndex],
            'saccDur': self.data[durSaccKey][self.trialIndex],
            'sFix': self.data.DK_sFix[self.trialIndex],
            'fixDur': self.data[durFixKey][self.trialIndex],
            'xLabel': self.ui.xCoords.currentText().split()[0],
            'yLabel': self.ui.yCoords.currentText().split()[0],
            'speedLabel': self.ui.speed.currentText().split()[0]}
        
        self.par['addLabel'] = self.ui.addInfo.currentText().split()[0]
        if self.par['addLabel'] != 'False':
            self.par['addInfo'] = self.data[self.par['addLabel']][self.trialIndex]

        # Disable animation if running
        if self.animationOn == True:
            self.anim.event_source.stop()
            del self.anim
            self.animationOn = False
        
        self.Canvas.clearFig()
        self.par['figAx'] = self.Canvas.figAx
        self.figAx = pltGUI(self.time, self.x, self.y, self.speed, **self.par)
        self.Canvas.updateFig()

    def runAni(self):
        # Run animation
        if len(self.figAx) == 5:
            self.fig, self.ax1, self.ax2, self.ax3, self.ax4 = self.figAx
            xMin, xMax = self.ax4.get_xlim()
            yMin, yMax = self.ax4.get_ylim()

            # Get gaussian dot variables
            runGuass = self.ui.useAperture.currentText()
            if runGuass == 'True':
                self.runGaussAnim = True
            elif runGuass == 'False':
                self.runGaussAnim = False
            self.gaussCircR = self.ui.apertureR.value()  # complete opcity circle
            self.gaussOpac = self.ui.apertureOpac.value()
            self.gaussR = self.ui.edgeR.value()  # gaussian radius
            self.gaussShade = self.ui.edgeOpac.value()

            self.ax4.clear()
            self.ax4.set_title('Gaze position')
            self.ax4.set_xlabel('X position (px)')
            self.ax4.set_ylabel('Y position (px)')
            self.line1, = self.ax1.plot([], [], lw=2, c='k')
            self.line2, = self.ax2.plot([], [], lw=2, c='k')
            self.line3, = self.ax3.plot([], [], lw=2, c='k')
            self.line4, = self.ax4.plot([], [], lw=2, c='k')
            self.ax4.axis([xMin, xMax, yMin, yMax])
            self.ax4.set(aspect=self.par['bgAspect'])
            self.dot = self.ax4.scatter([], [], c='k', s=50)
            self.dot2 = self.ax4.scatter([], [], c='r', s=20)

            self.bgRect = [xMin, xMax, yMin, yMax]
            if self.par['pltBg'] == True:
                bgIm = plt.imread(self.par['bgImage'])
                self.bgIm = bgIm
                self.bgAnimIm = self.ax4.imshow(bgIm, aspect=self.par['bgAspect'],
                                                extent=self.bgRect,
                                                animated=self.runGaussAnim)

            if self.animationOn == True:
                self.anim.event_source.stop()
                del self.anim
                self.animationOn = False

            self.animationOn = True
            self.sampleStep = self.ui.frameStepSize.value()

            # Set draw trace
            drawTrace = self.ui.showTrace.currentText()
            if drawTrace == 'True':
                self.drawTrace = True
            elif drawTrace == 'False':
                self.drawTrace = False

            # Set dot size for animation
            self.blackDotSize = self.ui.blackDotSize.value()
            self.redDotSize = self.ui.redDotSize.value()

            if self.runGaussAnim:
                # Make the gaussian circle image
                self.MaskL = np.zeros((self.par['yMax'] * 3, self.par['xMax'] * 3))
                mask = np.rot90(self.gaussMask())
                self.MaskL[self.par['yMax']:self.par['yMax'] * 2, self.par['xMax']:self.par['xMax'] * 2] = mask
                self.MaskL = self.rescale(self.MaskL, self.gaussShade, self.gaussOpac)
                self.MaskL = np.dstack([self.MaskL, self.MaskL, self.MaskL])

                if self.par['pltBg'] == False:
                    self.MaskL *= 255
                    gMask = self.MaskL[self.par['yMax']:self.par['yMax'] * 2, self.par['xMax']:self.par['xMax'] * 2]
                    gMask = np.array(gMask, dtype=np.uint8)
                    self.bgAnimIm = self.ax4.imshow(gMask, aspect=self.par['bgAspect'],
                                                    extent=self.bgRect,
                                                    animated=self.runGaussAnim,
                                                    cmap='gray')
            # Start animation
            self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init,
                                                frames=np.arange(0, len(self.x), self.sampleStep), interval=1,
                                                blit=True)

    # ==========================================================================
    # Functions for Making the gaussian image
    # ==========================================================================
    def rescale(self, data, minV, maxV):
        # normalzie
        ran = np.max(data) - np.min(data)
        m = (data - np.min(data)) / ran
        # rescale
        ran2 = np.abs(np.diff([maxV, minV]))
        m *= ran2
        m += minV
        return m

    def circMask(self):
        cy = int(((self.par['xMax'] / 2) / float(self.par['xMax'])) * self.par['xMax'])
        cx = int(((self.par['yMax'] / 2) / float(self.par['yMax'])) * self.par['yMax'])
        x = np.arange(self.par['xMax'])
        y = np.arange(self.par['yMax'])
        xx, yy = np.meshgrid(x, y)
        condition = (xx - cx) ** 2 + (yy - cy) ** 2 <= self.gaussCircR ** 2
        mask = np.zeros(condition.shape)
        mask[condition] = 1
        return np.where(mask > 0)

    def gaussMask(self):
        import astropy.convolution as krn
        mask = np.zeros((self.par['xMax'], self.par['yMax']))
        xx, yy = self.circMask()
        mask[xx, yy] = 1
        gaus = krn.Gaussian2DKernel(self.gaussR)
        gmap = krn.convolve_fft(mask, gaus)
        return gmap

    def getGaussRect(self, cx, cy, bigIm):
        xS = self.par['xMax']
        yS = self.par['yMax']
        xrect = [(xS + xS - cx) - xS / 2, (xS + xS - cx) + xS / 2]
        yrect = [(yS + yS - cy) - yS / 2, (yS + yS - cy) + yS / 2]
        return bigIm[int(yrect[0]):int(yrect[1]), int(xrect[0]):int(xrect[1])]

    # ==========================================================================
    # Functions for running animations
    # ==========================================================================
    def init(self):
        self.line1.set_data([], [])
        self.line2.set_data([], [])
        self.line3.set_data([], [])
        self.line4.set_data([], [])
        return self.line1, self.line2, self.line3, self.line4,

    # animation function. This is called sequentially
    def animate(self, i):
        sampT = self.time - self.time[0]
        # Draw moving line
        self.line1.set_data([sampT[i], sampT[i]], [self.par['xMin'], self.par['xMax']])
        self.line2.set_data([sampT[i], sampT[i]], [self.par['yMin'], self.par['yMax']])
        self.line3.set_data([sampT[i], sampT[i]], [np.min(self.speed) - 20, np.max(self.speed) + 20])

        # Remove the two dots
        self.dot.remove()
        self.dot2.remove()

        # Draw moving dot
        self.dot = self.ax4.scatter(self.x[i], self.y[i], marker='o', c='k', s=self.blackDotSize)
        self.dot2 = self.ax4.scatter(self.x[i], self.y[i], marker='o', c='r', s=self.redDotSize)

        # Draw Guassian
        if self.runGaussAnim:
            gMask = self.getGaussRect(self.x[i], self.y[i], self.MaskL)
            if self.par['pltBg'] == True:
                bgIm = np.array(self.bgIm * gMask, dtype=np.uint8)
            else:
                bgIm = np.array(gMask, dtype=np.uint8)
            self.bgAnimIm.set_data(bgIm)
        # Draw trace
        if i > 1 and self.drawTrace == True:
            x = [[self.x[ii], self.x[ii + 1]] for ii in range(i - 1)]
            y = [[self.y[ii], self.y[ii + 1]] for ii in range(i - 1)]
            self.line4.set_data(x, y)

        if self.runGaussAnim:
            return self.bgAnimIm, self.line1, self.line2, self.line3, self.line4, self.dot, self.dot2,
        else:
            return self.line1, self.line2, self.line3, self.line4, self.dot, self.dot2,

    def dispSaveAnim(self, txt):
        doc = MyMessageBox()
        doc.setWindowTitle("Saving Animation, Please wait! (Don't click the GUI)")
        doc.setText(txt)
        doc.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        doc.setWindowIcon(QtGui.QIcon('eye.png'))
        doc.show()
        return doc

    def getVidSaveName(self):
        dir_path = os.path.dirname(self.fileName)
        fileBase = os.path.splitext(os.path.basename(self.fileName))[0]
        trialNr = str(self.par['trial'] + 1)
        defDir = dir_path + '\\' + fileBase + '_Trial' + trialNr + '.mp4'
        save = QtWidgets.QFileDialog.getSaveFileName(None, 'Save as:', directory=defDir)[0]

        if len(save) == 0:
            saveDir = defDir
        else:
            ext = os.path.splitext(save)[1]
            lExt = len(ext)
            newExt = '.mp4'
            saveDir = os.path.abspath(save)[:-lExt] + newExt
        return saveDir

    def saveAnimation(self):
        # if self.animationOn == True:
        fName = self.getVidSaveName()
        txt = 'Saving animation, please wait...\nThis may take a while...' \
              + '\n\n\nAnimation saved as:\n' + fName
        doc = self.dispSaveAnim(txt)
        # Save animation
        try:
            self.plotData()
            self.runAni()
            self.anim.save(fName, fps=30, extra_args=['-vcodec', 'libx264'])
        except:
            'Error, video not saved!'
            pass
        # Hide message box
        doc.hide()


def run():
    if __name__ == "__main__":
        import sys
        import ctypes
        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            pass
        if not QtWidgets.QApplication.instance():
            app = QtWidgets.QApplication(sys.argv)
            ui = Window()
            sys.exit(app.exec_())
        else:
            app = QtWidgets.QApplication.instance()
            ui = Window()
            sys.exit(app.exec_())
run()
