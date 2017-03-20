# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:01:49 2017

@author: User1
"""

#==============================================================================
#==============================================================================
# # Eyelink 1000 parser with PyQt4 GUI
#==============================================================================
#==============================================================================
import sys
import os
import pandas as pd
from PyQt4 import QtGui, QtCore
import psutil
import multiprocessing
from parseFuncs import parseWrapper
import time

#==============================================================================
# Functions used by the parser
#==============================================================================
def getSys():
    return psutil.cpu_percent(1), psutil.virtual_memory()[2]

#==============================================================================
#==============================================================================
# #  GUI code
#==============================================================================
#==============================================================================
class ThreadClass(QtCore.QThread):
    def __init__(self, parent = None):
        super(ThreadClass, self).__init__(parent)

    def run(self):
        while 1:
            sysval = getSys()
            self.emit(QtCore.SIGNAL('SYSVAL'), sysval)

class workerClass(QtCore.QThread):
    def __init__(self, parent = None):
        super(workerClass, self).__init__(parent)
        self.par = {}
        self.files = []

    def run(self):
        #Do the analysis single core
        for indx, FILENAME in enumerate(self.files):
            FILENAME, parsedData, rawData, parsedLong = parseWrapper(self.files[indx], self.par)
            # Save data
            parsedData.to_pickle(self.par['savefileNames'][indx])
            if self.par['saveRawFiles'] == 'Yes':
                rawData.to_pickle(self.par['saveFileNamesRaw'][indx])
            if self.par['longFormat'] == 'Yes':
                parsedLong.to_csv(self.par['savefileNames'][indx][:-2]+'Long.csv', index = False, na_rep = '#N/A')
            # Send progress
            self.emit(QtCore.SIGNAL('PROGRESS'), 1)

class MyMessageBox(QtGui.QMessageBox):
    def __init__(self):
        QtGui.QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QtGui.QMessageBox.event(self, e)

        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        textEdit = self.findChild(QtGui.QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        return result

class Window(QtGui.QMainWindow):
    #==============================================================================
    # Build GUI
    #==============================================================================
    def __init__(self):
        #======================================================================
        # Set constants and flags
        #======================================================================
        # Set variables
        self.files = []
        self.docLoc = 'Documentation.txt'
        self.settingsLoc = 'Settings.txt'
        self.progressValue = 0

        # Load settings
        self.loadSettings()
        #======================================================================
        # Initiate main features of the GUI
        #======================================================================
        super(Window, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(50, 50, 1000, 950)
        self.setWindowTitle("Eyelink 1000 parser")
        self.setWindowIcon(QtGui.QIcon('eye.png'))

        # Set background color
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
        self.setPalette(palette)

        # Select single file for parsing
        openFile = QtGui.QAction("&Select file(s)", self)
        openFile.setStatusTip('Select file(s)')
        openFile.triggered.connect(self.selectFile)

        # Exit parser
        quitParser = QtGui.QAction("&Exit", self)
        quitParser.setShortcut("Ctrl+Q")
        quitParser.setStatusTip('Exit parser')
        quitParser.triggered.connect(self.close_application)

        # Settings
        self.unlockSettingsM = QtGui.QAction("&Unlock settings", self)
        self.unlockSettingsM.setStatusTip('Unlock settings')
        self.unlockSettingsM.triggered.connect(self.unlockSettings)
        self.lockSettingsM = QtGui.QAction("&Lock settings", self)
        self.lockSettingsM.setStatusTip('Lock settings')
        self.lockSettingsM.triggered.connect(self.lockSettings)
        self.lockSettingsM.setEnabled(False)

        # Default settings
        defSett = QtGui.QAction("&Load default settings", self)
        defSett.setStatusTip('Load default setings')
        defSett.triggered.connect(self.loadDefaultSettings)

        # Documentation
        openDoc = QtGui.QAction("&Documentation", self)
        openDoc.setStatusTip('Open documentation')
        openDoc.triggered.connect(self.documentation)

        # Initiate menu bar and status
        self.statusBar()
        mainMenu = self.menuBar()

        # File menu bar
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(quitParser)

        # Settings menu bar
        settingsMenu = mainMenu.addMenu('&Settings')
        settingsMenu.addAction(self.unlockSettingsM)
        settingsMenu.addAction(self.lockSettingsM)
        settingsMenu.addAction(defSett)
        settingsMenu.addAction(openDoc)

        #======================================================================
        # Initiate Main Windows and buttons
        #======================================================================
        # Textbox and label containing the start, stop and variable trial keys
        startKeyL = QtGui.QLabel("Start trial key", self)
        startKeyL.move(50,45)
        startKeyL.resize(startKeyL.minimumSizeHint())
        self.startKey = QtGui.QTextEdit(self)
        self.startKey.move(50, 65)
        self.startKey.resize(100,25)
        self.startKey.setText(self.par['startTrialKey'])

        stopKeyL = QtGui.QLabel("Stop trial key", self)
        stopKeyL.move(175,45)
        stopKeyL.resize(stopKeyL.minimumSizeHint())
        self.stopKey = QtGui.QTextEdit(self)
        self.stopKey.move(175, 65)
        self.stopKey.resize(100,25)
        self.stopKey.setText(self.par['stopTrialKey'])

        varKeyL = QtGui.QLabel("Variable prefix", self)
        varKeyL.move(300,45)
        varKeyL.resize(varKeyL.minimumSizeHint())
        self.varKey = QtGui.QTextEdit(self)
        self.varKey.move(300, 65)
        self.varKey.resize(100,25)
        self.varKey.setText(self.par['variableKey'])

        # Parse button
        self.Parsebtn = QtGui.QPushButton("Parse", self)
        self.Parsebtn.clicked.connect(self.setValues)
        self.Parsebtn.resize(100,25)
        self.Parsebtn.move(425, 65)
        self.Parsebtn.setEnabled(False)

        # textbox displaying the selected files
        filetbn = QtGui.QPushButton("Select file(s)", self)
        filetbn.clicked.connect(self.selectFile)
        filetbn.resize(filetbn.minimumSizeHint())
        filetbn.move(675, 40)
        self.textbox = QtGui.QTextEdit(self)
        self.textbox.move(675, 65)
        self.textbox.resize(300,600)
        self.textbox.setEnabled(False) # Toggle the window

        #======================================================================
        # Initiate Settings section for regular rexpressions
        #======================================================================
        # Sepperator line
        settingsL = QtGui.QLabel("Settings", self)
        settingsL.setFont(QtGui.QFont("Times", 15, QtGui.QFont.Bold))
        settingsL.move(50,125)
        settingsL.resize(settingsL.minimumSizeHint())
        settingsLine = QtGui.QFrame(self)
        settingsLine.setFrameStyle(QtGui.QFrame.HLine)
        settingsLine.setFrameShadow(QtGui.QFrame.Sunken)
        settingsLine.resize(600,5)
        settingsLine.move(50,150)
        settingsLine.setLineWidth(5)

        # Regular expressions for raw data extracting
        regL = QtGui.QLabel("Regular expressions for data extraction", self)
        regL.move(50,170)
        regL.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        regL.resize(regL.minimumSizeHint())

        #regSamples
        regSampL = QtGui.QLabel("Samples", self)
        regSampL.move(50,200)
        regSampL.resize(regSampL.minimumSizeHint())
        self.regSamp = QtGui.QTextEdit(self)
        self.regSamp.move(50, 220)
        self.regSamp.resize(600,25)
        self.regSamp.setText(self.par['regExpSamp'])
        self.regSamp.setEnabled(False)

        #regEfix
        regEfixL = QtGui.QLabel("End fixation", self)
        regEfixL.move(50,260)
        regEfixL.resize(regEfixL.minimumSizeHint())
        self.regEfix = QtGui.QTextEdit(self)
        self.regEfix.move(50, 280)
        self.regEfix.resize(600,25)
        self.regEfix.setText(self.par['regExpEfix'])
        self.regEfix.setEnabled(False)

        #regEsacc
        regEsaccL = QtGui.QLabel("End saccade", self)
        regEsaccL.move(50,320)
        regEsaccL.resize(regEsaccL.minimumSizeHint())
        self.regEsacc = QtGui.QTextEdit(self)
        self.regEsacc.move(50, 340)
        self.regEsacc.resize(600,25)
        self.regEsacc.setText(self.par['regExpEsacc'])
        self.regEsacc.setEnabled(False)

        #regEblink
        regEblinkL = QtGui.QLabel("End blink", self)
        regEblinkL.move(50,380)
        regEblinkL.resize(regEsaccL.minimumSizeHint())
        self.regEblink = QtGui.QTextEdit(self)
        self.regEblink.move(50, 400)
        self.regEblink.resize(600,25)
        self.regEblink.setText(self.par['regExpEblink'])
        self.regEblink.setEnabled(False)

        #regStart
        regStartL = QtGui.QLabel("Start trial", self)
        regStartL.move(50,440)
        regStartL.resize(regStartL.minimumSizeHint())
        self.regStart = QtGui.QTextEdit(self)
        self.regStart.move(50, 460)
        self.regStart.resize(600,25)
        self.regStart.setText(self.par['regExpStart'])
        self.regStart.setEnabled(False)

        #regStop
        regStopL = QtGui.QLabel("Stop trial", self)
        regStopL.move(50,500)
        regStopL.resize(regStopL.minimumSizeHint())
        self.regStop = QtGui.QTextEdit(self)
        self.regStop.move(50, 520)
        self.regStop.resize(600,25)
        self.regStop.setText(self.par['regExpStop'])
        self.regStop.setEnabled(False)

        #regVar
        regVarL = QtGui.QLabel("Variables", self)
        regVarL.move(50,560)
        regVarL.resize(regVarL.minimumSizeHint())
        self.regVar = QtGui.QTextEdit(self)
        self.regVar.move(50, 580)
        self.regVar.resize(600,25)
        self.regVar.setText(self.par['regExpVar'])
        self.regVar.setEnabled(False)

        #regMsg
        regMsgL = QtGui.QLabel("Other messages", self)
        regMsgL.move(50,620)
        regMsgL.resize(regMsgL.minimumSizeHint())
        self.regMsg = QtGui.QTextEdit(self)
        self.regMsg.move(50, 640)
        self.regMsg.resize(600,25)
        self.regMsg.setText(self.par['regExpMsg'])
        self.regMsg.setEnabled(False)

        #======================================================================
        # Initiate section for various settings
        #======================================================================
        # Various settings
        variousL = QtGui.QLabel("Various settings", self)
        variousL.move(50,680)
        variousL.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        variousL.resize(variousL.minimumSizeHint())

        #Parsed name
        parsedNameL = QtGui.QLabel("Parsed name", self)
        parsedNameL.move(50,710)
        parsedNameL.resize(parsedNameL.minimumSizeHint())
        self.parsedName = QtGui.QTextEdit(self)
        self.parsedName.move(50, 730)
        self.parsedName.resize(100,25)
        self.parsedName.setText(self.par['saveExtension'])
        self.parsedName.setEnabled(False)

        #Parsed name
        rawNameL = QtGui.QLabel("Raw name", self)
        rawNameL.move(175,710)
        rawNameL.resize(rawNameL.minimumSizeHint())
        self.rawName = QtGui.QTextEdit(self)
        self.rawName.move(175, 730)
        self.rawName.resize(100,25)
        self.rawName.setText(self.par['saveRawExtension'])
        self.rawName.setEnabled(False)

        #Merged name
        mergedNameL = QtGui.QLabel("Merged name", self)
        mergedNameL.move(300,710)
        mergedNameL.resize(mergedNameL.minimumSizeHint())
        self.mergedName = QtGui.QTextEdit(self)
        self.mergedName.move(300, 730)
        self.mergedName.resize(100,25)
        self.mergedName.setText(self.par['mergedFileNames'])
        self.mergedName.setEnabled(False)

        # Merged yes/no
        # Save Merged files button
        mergeL = QtGui.QLabel("Merge files", self)
        mergeL.move(425,710)
        mergeL.resize(mergeL.minimumSizeHint())
        self.mergebtn = QtGui.QComboBox(self)
        self.mergebtn.addItem("No")
        self.mergebtn.addItem("Yes")
        self.mergebtn.resize(100,25)
        self.mergebtn.move(425, 730)
        self.mergebtn.setEnabled(False)
        if self.par['saveMergedFiles'] == 'No':
            self.mergebtn.setCurrentIndex(0)
        else:
            self.mergebtn.setCurrentIndex(1)

        # Save raw button 
        saveRawL = QtGui.QLabel("Save raw file", self)
        saveRawL.move(550,710)
        saveRawL.resize(saveRawL.minimumSizeHint())
        self.saveRawbtn = QtGui.QComboBox(self)
        self.saveRawbtn.addItem("No")
        self.saveRawbtn.addItem("Yes")
        self.saveRawbtn.resize(100,25)
        self.saveRawbtn.move(550, 730)
        self.saveRawbtn.setEnabled(False)
        if self.par['saveRawFiles'] == 'No':
            self.saveRawbtn.setCurrentIndex(0)
        else:
            self.saveRawbtn.setCurrentIndex(1)
            
#==============================================================================
# Work in progress
#==============================================================================
        # Save longformat yes/no
        # Save long format button
        longL = QtGui.QLabel("Save longformat", self)
        longL.move(425,770)
        longL.resize(longL.minimumSizeHint())
        self.longbtn = QtGui.QComboBox(self)
        self.longbtn.addItem("No")
        self.longbtn.addItem("Yes")
        self.longbtn.resize(100,25)
        self.longbtn.move(425, 790)
        self.longbtn.setEnabled(False)
        if self.par['longFormat'] == 'No':
            self.longbtn.setCurrentIndex(0)
        else:
            self.longbtn.setCurrentIndex(1)

        # Save raw button 
        duplicLongL = QtGui.QLabel("Duplicate values Long", self)
        duplicLongL.move(550,770)
        duplicLongL.resize(duplicLongL.minimumSizeHint())
        self.duplicLongbtn = QtGui.QComboBox(self)
        self.duplicLongbtn.addItem("No")
        self.duplicLongbtn.addItem("Yes")
        self.duplicLongbtn.resize(100,25)
        self.duplicLongbtn.move(550, 790)
        self.duplicLongbtn.setEnabled(False)
        if self.par['duplicateValues'] == 'No':
            self.duplicLongbtn.setCurrentIndex(0)
        else:
            self.duplicLongbtn.setCurrentIndex(1)
#==============================================================================
# Work in progress
#==============================================================================
        # Parallel processing
        paralellL = QtGui.QLabel("Parallel processing", self)
        paralellL.move(50,770)
        paralellL.resize(paralellL.minimumSizeHint())
        self.paralell = QtGui.QComboBox(self)
        self.paralell.addItem("Yes")
        self.paralell.addItem("No")
        self.paralell.resize(100,25)
        self.paralell.move(50, 790)
        self.paralell.setEnabled(False)

        #Number of cores
        nrCoresL = QtGui.QLabel("CPU cores", self)
        nrCoresL.move(50,830)
        nrCoresL.resize(nrCoresL.minimumSizeHint())
        self.nrCores = QtGui.QTextEdit(self)
        self.nrCores.move(50, 850)
        self.nrCores.resize(100,25)
        maxCores = psutil.cpu_count()
        if int(self.par['nrCores']) > maxCores-1:
            self.par['nrCores'] = str(maxCores-1)
        self.nrCores.setText(self.par['nrCores'])
        self.nrCores.setEnabled(False)

        # Pixels per degree
        pixDegL = QtGui.QLabel("Pixels per degree", self)
        pixDegL.move(175,770)
        pixDegL.resize(pixDegL.minimumSizeHint())
        self.pixMode = QtGui.QComboBox(self)
        self.pixMode.addItem("Automatic")
        self.pixMode.addItem("Manual")
        self.pixMode.resize(100,25)
        self.pixMode.move(175, 790)
        self.pixMode.setEnabled(False)
        if self.par['pxMode'] == 'Automatic':
            self.pixMode.setCurrentIndex(0)
        else:
            self.pixMode.setCurrentIndex(1)

        #Number of pixels per degree
        nrCoresL = QtGui.QLabel("Px per deg (manual)", self)
        nrCoresL.move(175,830)
        nrCoresL.resize(nrCoresL.minimumSizeHint())
        self.pixPerDeg = QtGui.QTextEdit(self)
        self.pixPerDeg.move(175, 850)
        self.pixPerDeg.resize(100,25)
        self.pixPerDeg.setText(self.par['pxPerDeg'])
        self.pixPerDeg.setEnabled(False)
        
        #======================================================================
        # Bussy text and run GUI with progressbars
        #======================================================================
        self.parL = QtGui.QLabel("Multi core processing!", self)
        self.parL.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.parL.move(350, 860)
        self.parL.resize(self.parL.minimumSizeHint())
        self.parL.hide()

        self.singleL = QtGui.QLabel("Single core processing!", self)
        self.singleL.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.singleL.move(350, 860)
        self.singleL.resize(self.singleL.minimumSizeHint())
        self.singleL.hide()

        self.doneL = QtGui.QLabel("Finished!", self)
        self.doneL.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.doneL.move(400, 860)
        self.doneL.resize(self.doneL.minimumSizeHint())
        self.doneL.hide()

        self.ErrL = QtGui.QLabel("Multi core error, using single core!", self)
        self.ErrL.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.ErrL.move(325, 860)
        self.ErrL.resize(self.ErrL.minimumSizeHint())
        self.ErrL.hide()

        self.Err2L = QtGui.QLabel("ERROR!! Try again!", self)
        self.Err2L.setFont(QtGui.QFont("Times", 35, QtGui.QFont.Bold))
        self.Err2L.move(350,200)
        self.Err2L.resize(self.Err2L.minimumSizeHint())
        self.Err2L.hide()

        # Bussy bar
        self.bussyBar = QtGui.QProgressBar(self)
        self.bussyBar.setRange(0,1)
        self.bussyBar.resize(300,25)
        self.bussyBar.move(675, 725)
        self.bussyBar.setRange(0,100)
        
        # Progress bar
        self.progressBarL = QtGui.QLabel("% of files finished", self)
        self.progressBarL.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.progressBarL.move(750, 755)
        self.progressBarL.resize(self.progressBarL.minimumSizeHint())
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0,1)
        self.progressBar.resize(300,25)
        self.progressBar.move(675, 775)
        self.progressBar.setRange(0,100)

        # Cpu bar
        self.cpuBarL = QtGui.QLabel("CPU usage", self)
        self.cpuBarL.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.cpuBarL.move(675, 820)
        self.cpuBarL.resize(self.cpuBarL.minimumSizeHint())
        self.cpuBar = QtGui.QProgressBar(self)
        self.cpuBar.setRange(0,1)
        self.cpuBar.resize(300,15)
        self.cpuBar.move(675, 840)
        self.cpuBar.setRange(0,100)
        self.cpuBar.setValue(getSys()[0])

        #Memory bar
        self.memBarL = QtGui.QLabel('Memory usage',self)
        self.memBarL.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.memBarL.move(675, 870)
        self.memBarL.resize(self.memBarL.minimumSizeHint())
        self.memBar = QtGui.QProgressBar(self)
        self.memBar.setRange(0,1)
        self.memBar.resize(300,15)
        self.memBar.move(675, 890)
        self.memBar.setRange(0,100)
        self.memBar.setValue(getSys()[1])

        # Close
        self.closebtn = QtGui.QPushButton("Close", self)
        self.closebtn.clicked.connect(self.close_application)
        self.closebtn.resize(100,25)
        self.closebtn.move(375, 900)

        # Start threading System resources
        self.threadclass = ThreadClass()
        self.threadclass.start()
        self.connect(self.threadclass, QtCore.SIGNAL('SYSVAL'), self.updateSystemBars)

        # Display GUI
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()
        self.activateWindow()
        
    #==============================================================================
    # Define button actions
    #==============================================================================
    def loadSettings(self):
        with open(self.settingsLoc, 'r') as f:
            f = f.read().splitlines()
            keys = []
            values = []
            for line in f:
                key, value = line.split(':')
                # Check for regularExpressions
                if value[0] == '"':
                    value = value.strip('"')
                # Check for True False values
                if value == 'False':
                    value = False
                elif value == 'True':
                    value = True
                keys.append(key)
                values.append(value)
        self.DFSettings = pd.DataFrame([values], columns = keys)
        self.par = {key:self.DFSettings[key][0] for key in self.DFSettings.keys()}

    def writeSettings(self):
        settings = ''
        for key in self.DFSettings.keys():
            if len(str(self.par[key])) == 0:
                self.par[key] = self.par['DF'+key]
            settings += key+':'+str(self.par[key])+'\n' 
        with open(self.settingsLoc, 'w') as f:
            f.write(settings)

    def writeDefaultSettings(self):
        with open(self.settingsLoc, 'w') as f:
            for key in self.DFSettings.keys():
                if key[0:2] != 'DF':
                    self.DFSettings[key] = self.DFSettings['DF'+key]
                f.write(key+':'+str(self.DFSettings[key][0])+'\n')

    def loadDefaultSettings(self):
        choice = QtGui.QMessageBox.question(self, 'Default settings',
                                            "Loading default settings permanently\n"+\
                                            "deletes any changed settings!\n\n"+\
                                            "Do you really want to load default settings?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            # Write and load the deffault settings
            self.writeDefaultSettings()
            self.loadSettings()
            
            # Sets the default textbox settings 
            self.startKey.setText(self.par['startTrialKey'])
            self.stopKey.setText(self.par['stopTrialKey'])
            self.varKey.setText(self.par['variableKey'])
            self.textbox.setText('')
            self.regSamp.setText(self.par['regExpSamp'])
            self.regEfix.setText(self.par['regExpEfix'])
            self.regEsacc.setText(self.par['regExpEsacc']) 
            self.regEblink.setText(self.par['regExpEblink'])
            self.regStart.setText(self.par['regExpStart'])
            self.regStop.setText(self.par['regExpStop'])
            self.regVar.setText(self.par['regExpVar'])
            self.regMsg.setText(self.par['regExpMsg'])
            self.parsedName.setText(self.par['saveExtension'])
            self.rawName.setText(self.par['saveRawExtension'])
            self.mergedName.setText(self.par['mergedFileNames'])
            self.pixPerDeg.setText(self.par['pxPerDeg'])
            maxCores = psutil.cpu_count()
            if int(self.par['nrCores']) > maxCores-1:
                self.par['nrCores'] = str(maxCores-1)
            self.nrCores.setText(self.par['nrCores'])

            
            # Set button defaults
            # Parallel button is not set, sets depending on file number
            if self.par['saveMergedFiles'] == 'No':
                self.mergebtn.setCurrentIndex(0)
            else:
                self.mergebtn.setCurrentIndex(1)
            if self.par['saveRawFiles'] == 'No':
                self.saveRawbtn.setCurrentIndex(0)
            else:
                self.saveRawbtn.setCurrentIndex(1)
            if self.par['pxMode'] == 'Automatic':
                self.pixMode.setCurrentIndex(0)
            else:
                self.pixMode.setCurrentIndex(1)
            if self.par['longFormat'] == 'No':
                self.longbtn.setCurrentIndex(0)
            else:
                self.longbtn.setCurrentIndex(1)
            if self.par['duplicateValues'] == 'No':
                self.duplicLongbtn.setCurrentIndex(0)
            else:
                self.duplicLongbtn.setCurrentIndex(1)
        else:
            pass

    def updateSystemBars(self, sysval):
        self.cpuBar.setValue(sysval[0])
        self.memBar.setValue(sysval[1])
        if self.progressValue == len(self.files) and len(self.files) > 0 and self.doneL.isHidden() == True:
            self.parL.hide()
            self.singleL.hide()
            self.ErrL.hide()
            self.stopBussyBar()
            self.doneL.show()

    def updateProgress(self, value):
        self.progressValue += value
        if self.progressValue == len(self.files):
            if self.mergebtn.currentText() == 'Yes':
                self.savedMergedFiles()
        self.progressBar.setValue(self.progressValue)

    def startBussyBar(self):
        self.bussyBar.setRange(0,0)

    def stopBussyBar(self):
        self.bussyBar.setRange(0,1)

    def savedMergedFiles(self):
        fName = os.path.commonprefix(self.par['savefileNames']) + self.mergedName.toPlainText() + '.p'
        fNameRaw = fName[:-2] + self.rawName.toPlainText() +'.p'
        if self.files > 1:
            # Merge and save regular data
            data = pd.read_pickle(self.par['savefileNames'][0])
            for f in self.par['savefileNames'][1:]:
                data = pd.concat([data, pd.read_pickle(f)])
            data = data.reset_index()
            data.to_pickle(fName)
            del data
            # Merge and save raw data
            if self.par['saveRawFiles'] == 'Yes':
                dataRaw = pd.read_pickle(self.par['saveFileNamesRaw'][0])
                for f in self.par['saveFileNamesRaw'][1:]:
                    dataRaw = pd.concat([dataRaw, pd.read_pickle(f)])
                dataRaw = dataRaw.reset_index()
                dataRaw.to_pickle(fNameRaw)
                del dataRaw

    def selectFile(self):
        self.lockSettings()
        tempFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Select file(s)')
        if len(tempFiles) > 0:
            self.files = tempFiles
        if len(self.files) > 0:
            fileNames = [os.path.basename(f) for f in self.files]
            self.textbox.setText('\n'.join(fileNames))

            # Activate the parsing button
            self.Parsebtn.setEnabled(True)

            # Set parallel processing
            if len(self.files) < 2:
                self.paralell.setCurrentIndex(1)
            else:
                self.paralell.setCurrentIndex(0)

    def unlockSettings(self):
        # Enable all settings
        self.regSamp.setEnabled(True)
        self.regEfix.setEnabled(True)
        self.regEsacc.setEnabled(True)
        self.regEblink.setEnabled(True)
        self.regStart.setEnabled(True)
        self.regStop.setEnabled(True)
        self.regVar.setEnabled(True)
        self.regMsg.setEnabled(True)
        self.parsedName.setEnabled(True)
        self.rawName.setEnabled(True)
        self.mergedName.setEnabled(True)
        self.mergebtn.setEnabled(True)
        self.nrCores.setEnabled(True)
        self.paralell.setEnabled(True)
        self.saveRawbtn.setEnabled(True)
        self.pixMode.setEnabled(True)
        self.pixPerDeg.setEnabled(True)
        self.longbtn.setEnabled(True)
        self.duplicLongbtn.setEnabled(True)

        # Enable lock button
        self.lockSettingsM.setEnabled(True)
        # Disable unlock button
        self.unlockSettingsM.setEnabled(False)

    def lockSettings(self):
        self.regSamp.setEnabled(False)
        self.regEfix.setEnabled(False)
        self.regEsacc.setEnabled(False)
        self.regEblink.setEnabled(False)
        self.regStart.setEnabled(False)
        self.regStop.setEnabled(False)
        self.regVar.setEnabled(False)
        self.regMsg.setEnabled(False)
        self.parsedName.setEnabled(False)
        self.rawName.setEnabled(False)
        self.mergedName.setEnabled(False)
        self.mergebtn.setEnabled(False)
        self.nrCores.setEnabled(False)
        self.paralell.setEnabled(False)
        self.saveRawbtn.setEnabled(False)
        self.pixMode.setEnabled(False)
        self.pixPerDeg.setEnabled(False)
        self.longbtn.setEnabled(False)
        self.duplicLongbtn.setEnabled(False)

        # disable lock button
        self.lockSettingsM.setEnabled(False)
        # Enable unlock button
        self.unlockSettingsM.setEnabled(True)
        # Enable parse button
        if len(self.files) > 0:
            self.Parsebtn.setEnabled(True)

    def documentation(self):
        text=open(self.docLoc).read()
        doc = MyMessageBox()
        doc.setWindowIcon(QtGui.QIcon('eye.png'))
        doc.setWindowIcon(QtGui.QIcon('eye.png'))
        doc.setWindowTitle("Documentation")
        doc.setIcon(QtGui.QMessageBox.Information)
        doc.setStandardButtons(QtGui.QMessageBox.Ok)
        doc.setButtonText(1,'Close')
        doc.setText('Eyelink 1000 parser documentation'+'\t'*10)
        doc.setDetailedText(text)
        doc.exec_()

    def setValues(self):
        # Initiate bussy label
        self.progressBar.setRange(0,len(self.files))
        self.progressBar.setValue(0)
        self.progressValue = 0
        self.lockSettings()
        self.doneL.hide()
        self.repaint()

        #======================================================================
        # Get settings for parsing
        #======================================================================
        # File name handling
        self.par['saveExtension'] = self.parsedName.toPlainText()
        self.par['saveRawExtension'] = self.rawName.toPlainText()
        self.par['savefileNames'] = [f[:-4] + self.par['saveExtension']+'.p' for f in self.files]
        self.par['saveFileNamesRaw'] = [f[:-4] + self.par['saveExtension'] + self.par['saveRawExtension']+'.p' for f in self.files]

        # Get regular expression info
        self.par['startTrialKey'] = self.startKey.toPlainText().strip()
        self.par['stopTrialKey'] = self.stopKey.toPlainText().strip()
        self.par['variableKey'] = self.varKey.toPlainText().strip()
        self.par['regExpSamp'] = self.regSamp.toPlainText()
        self.par['regExpEfix'] = self.regEfix.toPlainText()
        self.par['regExpEsacc'] = self.regEsacc.toPlainText()
        self.par['regExpEblink'] = self.regEblink.toPlainText()
        # Set regular expressions for start/stop/var/msg
        if self.par['DFregExpStart'] != self.regStart.toPlainText():
            self.par['regExpStart'] = self.regStart.toPlainText()
            self.par['regExpStartNew'] = True
        else:
            self.par['regExpStartNew'] = False
        if self.par['DFregExpStop'] != self.regStop.toPlainText():
            self.par['regExpStop'] = self.regStop.toPlainText()
            self.par['regExpStopNew'] = True
        else:
            self.par['regExpStopNew'] = False
        if self.par['DFregExpVar'] != self.regVar.toPlainText():
            self.par['regExpVar'] = self.regVar.toPlainText()
            self.par['regExpVarNew'] = True
        else:
            self.par['regExpVarNew'] = False
        if self.par['DFregExpMsg'] != self.regMsg.toPlainText():
            self.par['regExpMsg'] = self.regMsg.toPlainText()
            self.par['regExpMsgNew'] = True
        else:
            self.par['regExpMsgNew'] = False

        # Processing info
        self.par['saveMergedFiles'] = self.mergebtn.currentText()
        self.par['saveRawFiles'] = self.saveRawbtn.currentText()
        self.par['runParallel'] = self.paralell.currentText()
        self.par['nrCores'] = self.nrCores.toPlainText()
        self.par['pxMode'] = self.pixMode.currentText()
        self.par['pxPerDeg'] = self.pixPerDeg.toPlainText()
        self.par['longFormat'] = self.longbtn.currentText()
        self.par['duplicateValues'] = self.duplicLongbtn.currentText()
        
        # Number of available cores
        maxCores = psutil.cpu_count()
        if int(self.par['nrCores']) > maxCores:
            self.par['nrCores'] = str(maxCores)
        self.nrCores.setText(self.par['nrCores'])
        self.pool = multiprocessing.Pool(processes=int(self.par['nrCores']))

        #======================================================================
        # Save settings
        #======================================================================
        self.writeSettings()

        #======================================================================
        # Run parser
        #======================================================================
        self.parse()

    def callbackParser(self, results):
        savefileName = results[0][:-4] + self.par['saveExtension'] + '.p'
        saveFileNamesRaw = results[0][:-4] + self.par['saveExtension'] + self.par['saveRawExtension'] + '.p'
        results[1].to_pickle(savefileName)
        if self.par['saveRawFiles'] == 'Yes':
            results[2].to_pickle(saveFileNamesRaw)
        if self.par['longFormat'] == 'Yes':
            results[3].to_csv(saveFileNamesRaw[:-2]+'Long.csv', index = False, na_rep = '#N/A')
        self.updateProgress(1)

    def parse(self):
        self.startBussyBar()
        if self.par['runParallel'] == 'Yes':
            try:
                self.parL.show()
                self.repaint()
                # Start threading System resources
                for sub in self.files:
                    results = self.pool.apply_async(parseWrapper,
                                               args = (sub, self.par),
                                               callback=self.callbackParser)
            except:
                self.ErrL.show()
                self.parL.hide()
                self.parseSingleCore()

        else:
            self.parL.hide()
            self.parseSingleCore()

    def parseSingleCore(self):
        try:
            # Start threading System resources
            if self.ErrL.isHidden() == True:
                self.singleL.show()
            self.repaint()
            self.worker = workerClass()
            self.worker.par = self.par
            self.worker.files = self.files
            self.worker.start()
            self.connect(self.worker, QtCore.SIGNAL('PROGRESS'), self.updateProgress)
        except:
            self.Err2L.show()
            self.repaint()
            time.sleep(5)
            sys.exit()

    def close_application(self):
        choice = QtGui.QMessageBox.question(self, 'Quit?',
                                            "Exit parser?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass

def run():
    if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        GUI = Window()
        sys.exit(app.exec_())

run()