# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 14:35:24 2018

@author: User1
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import os
import pandas as pd
import numpy as np
from plotCode import plotTrial
from GUICode import Ui_Eyelinkplotter

class Window(QtWidgets.QMainWindow):
    #==============================================================================
    # Build GUI
    #==============================================================================
    def __init__(self, parent=None):
        #======================================================================
        # Initiate main features of the GUI
        #======================================================================
        super(QtWidgets.QMainWindow, self).__init__()
        self.ui = Ui_Eyelinkplotter()
        self.ui.setupUi(self)
                
        _translate = QtCore.QCoreApplication.translate
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon('eye.png'))
        self.setWindowTitle(_translate("Eyelinkplotter", "Eyelink data plotter", None))
        
        self.imDir = None
        self.populateLists()
        # Run button press initiation
        self.defineButtonPresses()
        
        # set background color
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
        self.setPalette(palette)
        
        # Set tab color 
        self.ui.heatmapTab.setStyleSheet('QTabBar::tab {color: rgb(0,0,0)}')
        self.ui.heatmapTab.setVisible(False)
        self.ui.settingsLabel.setVisible(False)
        
        
        # Set key bindings
        self.left = QtWidgets.QShortcut(QtGui.QKeySequence('left'), self)
        self.left.activated.connect(self.backButtonClick)
        self.right = QtWidgets.QShortcut(QtGui.QKeySequence('right'), self)
        self.right.activated.connect(self.nextButtonClick)
        self.space = QtWidgets.QShortcut(QtGui.QKeySequence('space'), self)
        self.space.activated.connect(self.toggleIncludedTrial)
        
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
            'spectral',	'spring', 'summer', 'terrain', 'viridis', 'winter']
        #[self.kernelCM.addItem(i) for i in cmapList]
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
        
    def defineButtonPresses(self):
        self.ui.selectFile.clicked.connect(self.selectDataFile)
        self.ui.saveFile.clicked.connect(self.saveDataFile)
        self.ui.actionSelect_file.triggered.connect(self.selectDataFile)
        self.ui.selectImageFolder.clicked.connect(self.selectImDir)
        self.ui.backButton.clicked.connect(self.backButtonClick)
        self.ui.updateButton.clicked.connect(self.updateButtonClick)
        self.ui.nextButton.clicked.connect(self.nextButtonClick)
        self.ui.jumpToTrial.clicked.connect(self.plotSpecificTrial)
        self.ui.resetVariables.clicked.connect(self.resetVars)
        self.ui.trialScroll.valueChanged.connect(self.trialScrollChange)
        self.ui.toggleIncluded.clicked.connect(self.toggleIncludedTrial)
        self.ui.trialsToPlot.activated.connect(self.toggleTrialsToPlot)
        
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
        
    def selectDataFile(self):
        self.fileName = QtWidgets.QFileDialog.getOpenFileName(None, 'Select file')[0]
        if self.fileName:
            fileBase = os.path.basename(self.fileName)
            self.ui.selectedFile.setText(fileBase[:-2])
            self.data = pd.read_pickle(self.fileName)
            self.allowedIndexes = self.data.index.get_values()
            
            # Trial counters
            self.previousTrial = 0
            self.currTrial = 1
            self.nextTrial = 2
            self.maxTrialNr = len(self.data)
            self.trialIndex = self.currTrial - 1
            
            # Set background variable options
            self.data.keys()
            keys = [key for key in self.data.keys() if key[:3] == 'DK_' or key[:3] == 'DV_']
            keys = [key for key in keys if len(key.split()) == 1]
            self.ui.bgImageVariable.addItems(keys)
            self.ui.trialScroll.setMinimum(1)
            self.ui.trialScroll.setMaximum(self.maxTrialNr)
            
            # Initiate counters
            self.setCounters()
            self.plotData()
            
            # Initiate save file button
            self.ui.saveFile.setEnabled(True)
        
    def saveDataFile(self):
        self.data.to_pickle(self.fileName)
            
    def selectImDir(self):
        self.imDir = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select image folder')
        self.imDir +='/'
        
    def setCounters(self):
        # Set counters
        self.ui.currentTrialDisp.display(self.currTrial)
        self.ui.trialScroll.setValue(self.currTrial)
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
        if self.currTrial-1 not in self.allowedIndexes and self.currTrial-1 > np.min(self.allowedIndexes):
            self.backButtonClick()
        elif self.currTrial-1 < np.min(self.allowedIndexes):
            self.nextTrial = np.min(self.allowedIndexes)+2
            self.previousTrial = self.nextTrial-2
            self.currTrial = self.nextTrial-1
            self.setCounters()
            self.plotData()
        else:
            self.setCounters()
            self.plotData()
    
    def updateButtonClick(self):
        if self.currTrial-1 not in self.allowedIndexes:
            self.currTrial = self.allowedIndexes.flat[np.abs(self.allowedIndexes - (self.currTrial-1)).argmin()]+1
            self.nextTrial = self.currTrial+1
            self.previousTrial = self.currTrial-1
        self.setCounters()
        self.plotData()
    
    def nextButtonClick(self):
        if self.nextTrial <= self.maxTrialNr:
            self.nextTrial += 1
            self.previousTrial = self.nextTrial-2
            self.currTrial = self.nextTrial-1
        if self.nextTrial > self.maxTrialNr:
            self.nextTrial -= 1
        # check if the trial is in the allowed list
        if self.currTrial-1 not in self.allowedIndexes and self.currTrial-1 < np.max(self.allowedIndexes):
            self.nextButtonClick()
        elif self.currTrial-1 > np.max(self.allowedIndexes):
            self.nextTrial = np.max(self.allowedIndexes)+2
            self.previousTrial = self.nextTrial-2
            self.currTrial = self.nextTrial-1
            self.setCounters()
            self.plotData()
        else:
            self.setCounters()
            self.plotData()
            
    def plotSpecificTrial(self):
        trialToPlot = self.ui.jumpToTrialNr.value()
        if trialToPlot-1 not in self.allowedIndexes:
            trialToPlot = self.allowedIndexes.flat[np.abs(self.allowedIndexes - (trialToPlot-1)).argmin()]+1
            self.ui.jumpToTrialNr.setValue(trialToPlot)
        if trialToPlot >= self.maxTrialNr:
            self.previousTrial = self.maxTrialNr-1
            self.currTrial = self.maxTrialNr
            self.nextTrial = self.maxTrialNr
        else:
            self.previousTrial = trialToPlot-1
            self.currTrial = trialToPlot
            self.nextTrial = trialToPlot+1
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
            self.data.loc[self.trialIndex, 'DK_includedTrial']  = True
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
        self.trialIndex = self.currTrial-1
        self.time = self.data.DK_rawTime[self.trialIndex]
        self.x = self.data.DK_rawX[self.trialIndex]
        self.y = self.data.DK_rawY[self.trialIndex]
        self.ssacc = self.data.DK_ssacc[self.trialIndex]
        self.saccDur = self.data.DK_durSacc[self.trialIndex] 
        self.euclidDist = self.data.DK_euclidDist[self.trialIndex]
        
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
            
        # Build the final parameter dict
        self.par ={\
            'pltType': self.ui.plotType.currentText().split()[0],\
            'pltBg': pltBg,\
            'bgImage': bgImage,\
            'bgAspect': self.ui.aspectRatio.currentText().split()[0],\
            'trial': self.trialIndex,\
            'dataScaling': self.ui.kernelScale.value(),\
            'kernel': self.ui.kernel.currentText().split()[0],\
            'kernelPar': self.ui.kernelParameter.value(),\
            'kernelCM': self.ui.kernelCM.currentText().split()[0],\
            'kernelCMInverse': inverseKernel,\
            'kernelThreshold': self.ui.kernelThreshold.value(),\
            'kernelAlpha': self.ui.kernelAlpha.value(),\
            'xMax': self.ui.xMaxValue.value(),\
            'xMin': self.ui.xMinValue.value(),\
            'yMax': self.ui.yMaxValue.value(),\
            'yMin': self.ui.yMinValue.value(),\
            'included': str(self.data.DK_includedTrial[self.trialIndex])}
            
        # Plot the trial 
        plotTrial(self.time, self.x, self.y, self.ssacc, self.saccDur, 
                  self.euclidDist, **self.par)
   

def run():
    if __name__ == "__main__":
        import sys
        import ctypes
        myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        app = QtWidgets.QApplication(sys.argv)
        ui = Window()
        sys.exit(app.exec_())
run()