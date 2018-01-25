# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eyelinkplotter.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import os
import pandas as pd
import numpy as np
from plottingGUI import plotTrial

class Ui_Eyelinkplotter(object):
    def setupUi(self, Eyelinkplotter):
        Eyelinkplotter.setObjectName("Eyelinkplotter")
        Eyelinkplotter.setEnabled(True)
        Eyelinkplotter.resize(798, 635)
        self.centralwidget = QtWidgets.QWidget(Eyelinkplotter)
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(240, 80, 447, 124))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(12)
        self.gridLayout.setObjectName("gridLayout")
        self.jumpToTrialNr = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.jumpToTrialNr.setMinimum(1)
        self.jumpToTrialNr.setMaximum(1000000)
        self.jumpToTrialNr.setObjectName("jumpToTrialNr")
        self.gridLayout.addWidget(self.jumpToTrialNr, 2, 4, 1, 1)
        self.backButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.backButton.setEnabled(True)
        self.backButton.setObjectName("backButton")
        self.gridLayout.addWidget(self.backButton, 4, 1, 1, 1)
        self.nextButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.nextButton.setEnabled(True)
        self.nextButton.setObjectName("nextButton")
        self.gridLayout.addWidget(self.nextButton, 4, 3, 1, 1)
        self.updateButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.updateButton.setEnabled(True)
        self.updateButton.setObjectName("updateButton")
        self.gridLayout.addWidget(self.updateButton, 4, 2, 1, 1)
        self.jumpToTrial = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.jumpToTrial.setObjectName("jumpToTrial")
        self.gridLayout.addWidget(self.jumpToTrial, 4, 4, 1, 1)
        self.trialsToPlot = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.trialsToPlot.setObjectName("trialsToPlot")
        self.trialsToPlot.addItem("")
        self.trialsToPlot.addItem("")
        self.trialsToPlot.addItem("")
        self.gridLayout.addWidget(self.trialsToPlot, 4, 0, 1, 1)
        self.trialScroll = QtWidgets.QScrollBar(self.gridLayoutWidget)
        self.trialScroll.setMaximum(0)
        self.trialScroll.setOrientation(QtCore.Qt.Horizontal)
        self.trialScroll.setObjectName("trialScroll")
        self.gridLayout.addWidget(self.trialScroll, 5, 0, 1, 5)
        self.includedOrExcluded = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.includedOrExcluded.setEnabled(False)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.includedOrExcluded.setFont(font)
        self.includedOrExcluded.setObjectName("includedOrExcluded")
        self.gridLayout.addWidget(self.includedOrExcluded, 2, 0, 1, 1)
        self.currentTrialDisp = QtWidgets.QLCDNumber(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.currentTrialDisp.setFont(font)
        self.currentTrialDisp.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.currentTrialDisp.setObjectName("currentTrialDisp")
        self.gridLayout.addWidget(self.currentTrialDisp, 2, 2, 1, 1)
        self.toggleIncluded = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.toggleIncluded.setObjectName("toggleIncluded")
        self.gridLayout.addWidget(self.toggleIncluded, 2, 1, 1, 1)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 160, 121))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.selectFile = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.selectFile.setAutoDefault(False)
        self.selectFile.setDefault(False)
        self.selectFile.setFlat(False)
        self.selectFile.setObjectName("selectFile")
        self.gridLayout_2.addWidget(self.selectFile, 0, 0, 1, 1)
        self.selectedFile = QtWidgets.QLineEdit(self.gridLayoutWidget_2)
        self.selectedFile.setEnabled(False)
        self.selectedFile.setObjectName("selectedFile")
        self.gridLayout_2.addWidget(self.selectedFile, 2, 0, 1, 1)
        self.unLockSettings = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.unLockSettings.setObjectName("unLockSettings")
        self.gridLayout_2.addWidget(self.unLockSettings, 4, 0, 1, 1)
        self.saveFile = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.saveFile.setEnabled(False)
        self.saveFile.setObjectName("saveFile")
        self.gridLayout_2.addWidget(self.saveFile, 3, 0, 1, 1)
        self.heatmapTab = QtWidgets.QTabWidget(self.centralwidget)
        self.heatmapTab.setEnabled(False)
        self.heatmapTab.setGeometry(QtCore.QRect(10, 210, 771, 381))
        self.heatmapTab.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.heatmapTab.setObjectName("heatmapTab")
        self.windowTab = QtWidgets.QWidget()
        self.windowTab.setObjectName("windowTab")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.windowTab)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 20, 261, 71))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.plotType = QtWidgets.QComboBox(self.gridLayoutWidget_3)
        self.plotType.setObjectName("plotType")
        self.gridLayout_3.addWidget(self.plotType, 1, 0, 1, 1)
        self.aspectRatio = QtWidgets.QComboBox(self.gridLayoutWidget_3)
        self.aspectRatio.setObjectName("aspectRatio")
        self.gridLayout_3.addWidget(self.aspectRatio, 1, 1, 1, 1)
        self.plotTypeLabel = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.plotTypeLabel.setObjectName("plotTypeLabel")
        self.gridLayout_3.addWidget(self.plotTypeLabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.aspectRatioLabel = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.aspectRatioLabel.setObjectName("aspectRatioLabel")
        self.gridLayout_3.addWidget(self.aspectRatioLabel, 0, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.gridLayoutWidget_5 = QtWidgets.QWidget(self.windowTab)
        self.gridLayoutWidget_5.setGeometry(QtCore.QRect(10, 220, 471, 81))
        self.gridLayoutWidget_5.setObjectName("gridLayoutWidget_5")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.gridLayoutWidget_5)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.plotBackground = QtWidgets.QComboBox(self.gridLayoutWidget_5)
        self.plotBackground.setObjectName("plotBackground")
        self.plotBackground.addItem("")
        self.plotBackground.addItem("")
        self.gridLayout_5.addWidget(self.plotBackground, 1, 0, 1, 1)
        self.backgroundMainLabel = QtWidgets.QLabel(self.gridLayoutWidget_5)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.backgroundMainLabel.setFont(font)
        self.backgroundMainLabel.setObjectName("backgroundMainLabel")
        self.gridLayout_5.addWidget(self.backgroundMainLabel, 0, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.bgImageVariable = QtWidgets.QComboBox(self.gridLayoutWidget_5)
        self.bgImageVariable.setObjectName("bgImageVariable")
        self.gridLayout_5.addWidget(self.bgImageVariable, 1, 2, 1, 1)
        self.selectImageFolder = QtWidgets.QPushButton(self.gridLayoutWidget_5)
        self.selectImageFolder.setObjectName("selectImageFolder")
        self.gridLayout_5.addWidget(self.selectImageFolder, 1, 1, 1, 1)
        self.gridLayoutWidget_6 = QtWidgets.QWidget(self.windowTab)
        self.gridLayoutWidget_6.setGeometry(QtCore.QRect(10, 120, 471, 71))
        self.gridLayoutWidget_6.setObjectName("gridLayoutWidget_6")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.gridLayoutWidget_6)
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.xMaxValue = QtWidgets.QSpinBox(self.gridLayoutWidget_6)
        self.xMaxValue.setMinimum(-10000)
        self.xMaxValue.setMaximum(10000)
        self.xMaxValue.setObjectName("xMaxValue")
        self.gridLayout_6.addWidget(self.xMaxValue, 1, 1, 1, 1)
        self.xMinValue = QtWidgets.QSpinBox(self.gridLayoutWidget_6)
        self.xMinValue.setMinimum(-10000)
        self.xMinValue.setMaximum(10000)
        self.xMinValue.setObjectName("xMinValue")
        self.gridLayout_6.addWidget(self.xMinValue, 1, 0, 1, 1)
        self.yMinValue = QtWidgets.QSpinBox(self.gridLayoutWidget_6)
        self.yMinValue.setMinimum(-10000)
        self.yMinValue.setMaximum(10000)
        self.yMinValue.setObjectName("yMinValue")
        self.gridLayout_6.addWidget(self.yMinValue, 1, 2, 1, 1)
        self.yMaxValue = QtWidgets.QSpinBox(self.gridLayoutWidget_6)
        self.yMaxValue.setMinimum(-10000)
        self.yMaxValue.setMaximum(10000)
        self.yMaxValue.setObjectName("yMaxValue")
        self.gridLayout_6.addWidget(self.yMaxValue, 1, 3, 1, 1)
        self.xMinLabel = QtWidgets.QLabel(self.gridLayoutWidget_6)
        self.xMinLabel.setObjectName("xMinLabel")
        self.gridLayout_6.addWidget(self.xMinLabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.xMaxLabel = QtWidgets.QLabel(self.gridLayoutWidget_6)
        self.xMaxLabel.setObjectName("xMaxLabel")
        self.gridLayout_6.addWidget(self.xMaxLabel, 0, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.yMinLabel = QtWidgets.QLabel(self.gridLayoutWidget_6)
        self.yMinLabel.setObjectName("yMinLabel")
        self.gridLayout_6.addWidget(self.yMinLabel, 0, 2, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.yMaxLabel = QtWidgets.QLabel(self.gridLayoutWidget_6)
        self.yMaxLabel.setObjectName("yMaxLabel")
        self.gridLayout_6.addWidget(self.yMaxLabel, 0, 3, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.resetVariables = QtWidgets.QPushButton(self.windowTab)
        self.resetVariables.setGeometry(QtCore.QRect(640, 10, 91, 23))
        self.resetVariables.setObjectName("resetVariables")
        self.heatmapTab.addTab(self.windowTab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.tab_2)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(10, 70, 721, 71))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.kernelThreshold = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget_4)
        self.kernelThreshold.setMinimum(-1.0)
        self.kernelThreshold.setMaximum(1.0)
        self.kernelThreshold.setSingleStep(0.01)
        self.kernelThreshold.setObjectName("kernelThreshold")
        self.gridLayout_4.addWidget(self.kernelThreshold, 1, 5, 1, 1)
        self.kernelScale = QtWidgets.QSpinBox(self.gridLayoutWidget_4)
        self.kernelScale.setMinimum(1)
        self.kernelScale.setMaximum(100)
        self.kernelScale.setObjectName("kernelScale")
        self.gridLayout_4.addWidget(self.kernelScale, 1, 2, 1, 1)
        self.kernelLabel = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.kernelLabel.setObjectName("kernelLabel")
        self.gridLayout_4.addWidget(self.kernelLabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.kernelCMLabel = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.kernelCMLabel.setObjectName("kernelCMLabel")
        self.gridLayout_4.addWidget(self.kernelCMLabel, 0, 3, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.kernel = QtWidgets.QComboBox(self.gridLayoutWidget_4)
        self.kernel.setObjectName("kernel")
        self.gridLayout_4.addWidget(self.kernel, 1, 0, 1, 1)
        self.kernelCM = QtWidgets.QComboBox(self.gridLayoutWidget_4)
        self.kernelCM.setObjectName("kernelCM")
        self.gridLayout_4.addWidget(self.kernelCM, 1, 3, 1, 1)
        self.kernelParameter = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget_4)
        self.kernelParameter.setMaximum(10000.0)
        self.kernelParameter.setSingleStep(0.01)
        self.kernelParameter.setObjectName("kernelParameter")
        self.gridLayout_4.addWidget(self.kernelParameter, 1, 1, 1, 1)
        self.kernelScaleLabel = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.kernelScaleLabel.setObjectName("kernelScaleLabel")
        self.gridLayout_4.addWidget(self.kernelScaleLabel, 0, 2, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.kernelCMInverse = QtWidgets.QComboBox(self.gridLayoutWidget_4)
        self.kernelCMInverse.setObjectName("kernelCMInverse")
        self.gridLayout_4.addWidget(self.kernelCMInverse, 1, 4, 1, 1)
        self.kernelParameterLabel = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.kernelParameterLabel.setObjectName("kernelParameterLabel")
        self.gridLayout_4.addWidget(self.kernelParameterLabel, 0, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.kernelAlpha = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget_4)
        self.kernelAlpha.setMaximum(1.0)
        self.kernelAlpha.setSingleStep(0.01)
        self.kernelAlpha.setObjectName("kernelAlpha")
        self.gridLayout_4.addWidget(self.kernelAlpha, 1, 6, 1, 1)
        self.kernelCMInverseLabel = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.kernelCMInverseLabel.setObjectName("kernelCMInverseLabel")
        self.gridLayout_4.addWidget(self.kernelCMInverseLabel, 0, 4, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.kernelThresholdLabel = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.kernelThresholdLabel.setObjectName("kernelThresholdLabel")
        self.gridLayout_4.addWidget(self.kernelThresholdLabel, 0, 5, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.kernelAlphaLabel = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.kernelAlphaLabel.setObjectName("kernelAlphaLabel")
        self.gridLayout_4.addWidget(self.kernelAlphaLabel, 0, 6, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.heatmapTab.addTab(self.tab_2, "")
        self.settingsLabel = QtWidgets.QLabel(self.centralwidget)
        self.settingsLabel.setGeometry(QtCore.QRect(20, 160, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.settingsLabel.setFont(font)
        self.settingsLabel.setAutoFillBackground(False)
        self.settingsLabel.setObjectName("settingsLabel")
        self.settingsLine = QtWidgets.QFrame(self.centralwidget)
        self.settingsLine.setGeometry(QtCore.QRect(10, 190, 771, 20))
        self.settingsLine.setAutoFillBackground(False)
        self.settingsLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.settingsLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.settingsLine.setObjectName("settingsLine")
        self.gridLayoutWidget.raise_()
        self.gridLayoutWidget_2.raise_()
        self.heatmapTab.raise_()
        self.settingsLine.raise_()
        self.settingsLabel.raise_()
        Eyelinkplotter.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Eyelinkplotter)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 798, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        Eyelinkplotter.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Eyelinkplotter)
        self.statusbar.setObjectName("statusbar")
        Eyelinkplotter.setStatusBar(self.statusbar)
        self.actionSelect_file = QtWidgets.QAction(Eyelinkplotter)
        self.actionSelect_file.setObjectName("actionSelect_file")
        self.menuFile.addAction(self.actionSelect_file)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(Eyelinkplotter)
        self.heatmapTab.setCurrentIndex(0)
        self.unLockSettings.toggled['bool'].connect(self.heatmapTab.setVisible)
        self.unLockSettings.toggled['bool'].connect(self.heatmapTab.setEnabled)
        self.unLockSettings.toggled['bool'].connect(self.settingsLabel.setVisible)
        QtCore.QMetaObject.connectSlotsByName(Eyelinkplotter)
        Eyelinkplotter.setTabOrder(self.selectFile, self.selectedFile)
        Eyelinkplotter.setTabOrder(self.selectedFile, self.unLockSettings)

    def retranslateUi(self, Eyelinkplotter):
        _translate = QtCore.QCoreApplication.translate
        Eyelinkplotter.setWindowTitle(_translate("Eyelinkplotter", "MainWindow"))
        self.backButton.setText(_translate("Eyelinkplotter", "Back"))
        self.nextButton.setText(_translate("Eyelinkplotter", "Next"))
        self.updateButton.setText(_translate("Eyelinkplotter", "Update"))
        self.jumpToTrial.setText(_translate("Eyelinkplotter", "Plot trial number"))
        self.trialsToPlot.setItemText(0, _translate("Eyelinkplotter", "All"))
        self.trialsToPlot.setItemText(1, _translate("Eyelinkplotter", "Included"))
        self.trialsToPlot.setItemText(2, _translate("Eyelinkplotter", "Excluded"))
        self.toggleIncluded.setText(_translate("Eyelinkplotter", "Include/Exclude"))
        self.selectFile.setText(_translate("Eyelinkplotter", "Select file"))
        self.unLockSettings.setText(_translate("Eyelinkplotter", "Unlock settings"))
        self.saveFile.setText(_translate("Eyelinkplotter", "Save file"))
        self.plotTypeLabel.setText(_translate("Eyelinkplotter", "Plot type"))
        self.aspectRatioLabel.setText(_translate("Eyelinkplotter", "Aspect ratio"))
        self.plotBackground.setItemText(0, _translate("Eyelinkplotter", "False"))
        self.plotBackground.setItemText(1, _translate("Eyelinkplotter", "True"))
        self.backgroundMainLabel.setText(_translate("Eyelinkplotter", "Plot image behind gaze"))
        self.selectImageFolder.setText(_translate("Eyelinkplotter", "Select folder with background images"))
        self.xMinLabel.setText(_translate("Eyelinkplotter", "xMin"))
        self.xMaxLabel.setText(_translate("Eyelinkplotter", "xMax"))
        self.yMinLabel.setText(_translate("Eyelinkplotter", "yMin"))
        self.yMaxLabel.setText(_translate("Eyelinkplotter", "yMax"))
        self.resetVariables.setText(_translate("Eyelinkplotter", "Reset settings"))
        self.heatmapTab.setTabText(self.heatmapTab.indexOf(self.windowTab), _translate("Eyelinkplotter", "Window"))
        self.kernelLabel.setText(_translate("Eyelinkplotter", "Kernel"))
        self.kernelCMLabel.setText(_translate("Eyelinkplotter", "Kernel colormap"))
        self.kernelScaleLabel.setText(_translate("Eyelinkplotter", "Kernel scaling"))
        self.kernelParameterLabel.setText(_translate("Eyelinkplotter", "Kernel (parameter)"))
        self.kernelCMInverseLabel.setText(_translate("Eyelinkplotter", "Inverse color"))
        self.kernelThresholdLabel.setText(_translate("Eyelinkplotter", "Kernel threshold"))
        self.kernelAlphaLabel.setText(_translate("Eyelinkplotter", "Kernel alpha"))
        self.heatmapTab.setTabText(self.heatmapTab.indexOf(self.tab_2), _translate("Eyelinkplotter", "Heatmap"))
        self.settingsLabel.setText(_translate("Eyelinkplotter", "Settings"))
        self.menuFile.setTitle(_translate("Eyelinkplotter", "File"))
        self.actionSelect_file.setText(_translate("Eyelinkplotter", "Select file"))

#==============================================================================
#         # Initiate drop down menus
#         # From here its my own code
#==============================================================================        
        Eyelinkplotter.setWindowTitle(_translate("Eyelinkplotter", "Eyelink data plotter", None))
        Eyelinkplotter.setWindowIcon(QtGui.QIcon("eye.png"))
        self.imDir = None
        self.populateLists()
        # Run button press initiation
        self.defineButtonPresses()
        
        # set background color
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
        Eyelinkplotter.setPalette(palette)
        
        # Set tab color 
        self.heatmapTab.setStyleSheet('QTabBar::tab {color: rgb(0,0,0)}')
        self.heatmapTab.setVisible(False)
        self.settingsLabel.setVisible(False)
        
    def populateLists(self):
        # Set plot type options
        pltTypeList = ['gaze', 'heat']
        self.plotType.clear()
        self.plotType.addItems(pltTypeList)
        self.plotType.setCurrentIndex(0)
        
        # Set aspect ratio options
        bgAspectList = ['equal', 'auto']
        self.aspectRatio.clear()
        self.aspectRatio.addItems(bgAspectList)
        self.aspectRatio.setCurrentIndex(0)        
        
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
        self.kernelCM.clear()
        self.kernelCM.addItems(cmapList)
        self.kernelCM.setCurrentIndex(cmapList.index('hot'))

        # Set kernel options
        kernelList = ['AiryDisk2DKernel (Radius)', 'Box2DKernel (Width)', 
                      'Gaussian2DKernel (Std)', 'MexicanHat2DKernel (Width)', 
                      'Tophat2DKernel (Radius)', 'TrapezoidDisk2DKernel (Radius)']
        self.kernel.clear()
        self.kernel.addItems(kernelList)
        self.kernel.setCurrentIndex(2)
        
        # Set inverse color
        inverse = ['True', 'False']
        self.kernelCMInverse.clear()
        self.kernelCMInverse.addItems(inverse)
        self.kernelCMInverse.setCurrentIndex(1)
        
        # Initiate variables
        self.varInitiation()
        
    def defineButtonPresses(self):
        self.selectFile.clicked.connect(self.selectDataFile)
        self.saveFile.clicked.connect(self.saveDataFile)
        self.actionSelect_file.triggered.connect(self.selectDataFile)
        self.selectImageFolder.clicked.connect(self.selectImDir)
        self.backButton.clicked.connect(self.backButtonClick)
        self.updateButton.clicked.connect(self.updateButtonClick)
        self.nextButton.clicked.connect(self.nextButtonClick)
        self.jumpToTrial.clicked.connect(self.plotSpecificTrial)
        self.resetVariables.clicked.connect(self.resetVars)
        self.trialScroll.valueChanged.connect(self.trialScrollChange)
        self.toggleIncluded.clicked.connect(self.toggleIncludedTrial)
        self.trialsToPlot.activated.connect(self.toggleTrialsToPlot)
        
    def varInitiation(self):
        # imageDirectory
        if self.imDir is None:
            self.imDir = ''
        
        # Plot lims
        self.xMinValue.setValue(0)
        self.xMaxValue.setValue(1680)
        self.yMinValue.setValue(0)
        self.yMaxValue.setValue(1050)
        
        # Kernel values
        self.kernelParameter.setValue(20)
        self.kernelScale.setValue(1)
        self.kernelThreshold.setValue(0.00)
        self.kernelAlpha.setValue(0.50)
        
    def selectDataFile(self):
        self.fileName = QtWidgets.QFileDialog.getOpenFileName(None, 'Select file')[0]
        if self.fileName:
            fileBase = os.path.basename(self.fileName)
            self.selectedFile.setText(fileBase[:-2])
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
            self.bgImageVariable.addItems(keys)
            self.trialScroll.setMinimum(1)
            self.trialScroll.setMaximum(self.maxTrialNr)
            
            # Initiate counters
            self.setCounters()
            self.plotData()
            
            # Initiate save file button
            self.saveFile.setEnabled(True)
        
    def saveDataFile(self):
        self.data.to_pickle(self.fileName)
            
    def selectImDir(self):
        self.imDir = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select image folder')
        self.imDir +='/'
        
    def setCounters(self):
        # Set counters
        self.currentTrialDisp.display(self.currTrial)
        self.trialScroll.setValue(self.currTrial)
        # Set included trial
        included = str(self.data.DK_includedTrial[self.trialIndex])
        self.includedOrExcluded.setText(included)
        
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
        trialToPlot = self.jumpToTrialNr.value()
        if trialToPlot-1 not in self.allowedIndexes:
            trialToPlot = self.allowedIndexes.flat[np.abs(self.allowedIndexes - (trialToPlot-1)).argmin()]+1
            self.jumpToTrialNr.setValue(trialToPlot)
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
        self.jumpToTrialNr.setValue(self.trialScroll.value())
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

    def toggleTrialsToPlot(self):
        if self.trialsToPlot.currentText() == 'All':
            self.allowedIndexes = self.data.index.get_values()
        elif self.trialsToPlot.currentText() == 'Included':
            self.allowedIndexes = self.data.loc[self.data.DK_includedTrial == True, :].index.get_values()
        elif self.trialsToPlot.currentText() == 'Excluded':
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
        pltBg = self.plotBackground.currentText()
        if pltBg == 'True':
            pltBg = True
        elif pltBg == 'False':
            pltBg = False
            
        # Check where to find background image
        bgImage = ''
        if not self.imDir:
            pltBg = False
        elif pltBg == True:
            bgImage = self.imDir + os.path.basename(self.data[self.bgImageVariable.currentText()][self.trialIndex])
        # Check kernel inverse color
        inverseKernel = self.kernelCMInverse.currentText()
        if inverseKernel == 'True':
            inverseKernel = True
        elif inverseKernel == 'False':
            inverseKernel = False
            
        # Build the final parameter dict
        self.par ={\
            'pltType': self.plotType.currentText().split()[0],\
            'pltBg': pltBg,\
            'bgImage': bgImage,\
            'bgAspect': self.aspectRatio.currentText().split()[0],\
            'trial': self.trialIndex,\
            'dataScaling': self.kernelScale.value(),\
            'kernel': self.kernel.currentText().split()[0],\
            'kernelPar': self.kernelParameter.value(),\
            'kernelCM': self.kernelCM.currentText().split()[0],\
            'kernelCMInverse': inverseKernel,\
            'kernelThreshold': self.kernelThreshold.value(),\
            'kernelAlpha': self.kernelAlpha.value(),\
            'xMax': self.xMaxValue.value(),\
            'xMin': self.xMinValue.value(),\
            'yMax': self.yMaxValue.value(),\
            'yMin': self.yMinValue.value()}
            
        # Plot the trial 
        plotTrial(self.time, self.x, self.y, self.ssacc, self.saccDur, 
                  self.euclidDist, **self.par)

if __name__ == "__main__":
    import sys
    import ctypes
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QtWidgets.QApplication(sys.argv)
    Eyelinkplotter = QtWidgets.QMainWindow()
    ui = Ui_Eyelinkplotter()
    ui.setupUi(Eyelinkplotter)
    Eyelinkplotter.show()
    sys.exit(app.exec_())