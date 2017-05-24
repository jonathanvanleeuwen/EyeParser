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
from eyeParserBuilder import Ui_MainWindow
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
    def __init__(self, parent=None):
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
        super(QtGui.QMainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon('eye.png'))
        
        # Set background color
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
        self.setPalette(palette)

        #======================================================================
        # Set the menu bar triggers
        #======================================================================
        # Select file(s) for parsing
        self.ui.openFile.triggered.connect(self.selectFile)
        # Exit parser
        self.ui.quitParser.triggered.connect(self.close_application)
        # Settings (lock unlock)
        self.ui.unlockSettingsM.triggered.connect(self.unlockSettings)
        self.ui.lockSettingsM.triggered.connect(self.lockSettings)
        # Default settings
        self.ui.defSett.triggered.connect(self.loadDefaultSettings)
        # Documentation
        self.ui.openDoc.triggered.connect(self.documentation)

        #======================================================================
        # Initiate main parser button triggers
        #======================================================================
        # Start key
        self.ui.startKey.setText(self.par['startTrialKey'])
        # Stop key
        self.ui.stopKey.setText(self.par['stopTrialKey'])
        # Variable key
        self.ui.varKey.setText(self.par['variableKey'])
        # Parse button
        self.ui.Parsebtn.clicked.connect(self.setValues)
        # textbox displaying the selected files
        self.ui.filebtn.clicked.connect(self.selectFile)
        
        #======================================================================
        # Initiate Settings section for regular rexpressions
        #======================================================================
        #regSamples
        self.ui.regSamp.setText(self.par['regExpSamp'])
        #regEfix
        self.ui.regEfix.setText(self.par['regExpEfix'])
        #regEsacc
        self.ui.regEsacc.setText(self.par['regExpEsacc'])
        #regEblink
        self.ui.regEblink.setText(self.par['regExpEblink'])
        #regStart
        self.ui.regStart.setText(self.par['regExpStart'])
        #regStop
        self.ui.regStop.setText(self.par['regExpStop'])
        #regVar
        self.ui.regVar.setText(self.par['regExpVar'])
        #regMsg
        self.ui.regMsg.setText(self.par['regExpMsg'])

        #======================================================================
        # Initiate section for various settings
        #======================================================================
        #Parsed name
        self.ui.parsedName.setText(self.par['saveExtension'])
        #Parsed name
        self.ui.rawName.setText(self.par['saveRawExtension'])
        #Merged name
        self.ui.mergedName.setText(self.par['mergedFileNames'])
        # Merged yes/no
        # Save Merged files button
        self.ui.mergebtn.addItem("No")
        self.ui.mergebtn.addItem("Yes")
        if self.par['saveMergedFiles'] == 'No':
            self.ui.mergebtn.setCurrentIndex(0)
        else:
            self.ui.mergebtn.setCurrentIndex(1)
        # Save raw button 
        self.ui.saveRawbtn.addItem("No")
        self.ui.saveRawbtn.addItem("Yes")
        if self.par['saveRawFiles'] == 'No':
            self.ui.saveRawbtn.setCurrentIndex(0)
        else:
            self.ui.saveRawbtn.setCurrentIndex(1)
        # Save longformat yes/no
        # Save long format button
        self.ui.longbtn.addItem("No")
        self.ui.longbtn.addItem("Yes")
        if self.par['longFormat'] == 'No':
            self.ui.longbtn.setCurrentIndex(0)
        else:
            self.ui.longbtn.setCurrentIndex(1)
        # Duplicate values for long format 
        self.ui.duplicLongbtn.addItem("No")
        self.ui.duplicLongbtn.addItem("Yes")
        if self.par['duplicateValues'] == 'No':
            self.ui.duplicLongbtn.setCurrentIndex(0)
        else:
            self.ui.duplicLongbtn.setCurrentIndex(1)
        # Parallel processing
        self.ui.paralell.addItem("Yes")
        self.ui.paralell.addItem("No")
        #Number of cores
        maxCores = psutil.cpu_count()
        if int(self.par['nrCores']) > maxCores-1:
            self.par['nrCores'] = str(maxCores-1)
        self.ui.nrCores.setText(self.par['nrCores'])
        # Pixels per degree
        self.ui.pixMode.addItem("Automatic")
        self.ui.pixMode.addItem("Manual")
        if self.par['pxMode'] == 'Automatic':
            self.ui.pixMode.setCurrentIndex(0)
        else:
            self.ui.pixMode.setCurrentIndex(1)
        #Number of pixels per degree
        self.ui.pixPerDeg.setText(self.par['pxPerDeg'])
        # Close button
        self.ui.closebtn.clicked.connect(self.close_application)
        #======================================================================
        # Status labels
        #======================================================================
        self.ui.statusL.hide()
        self.MCPL = "Parallel processing!" 
        self.SCPL = "Single core processing!"
        self.DONEL = "Finished!"
        self.MCERRORL = "Multi core error, using single core!"
        self.ERRORL = "ERROR!! Try again!"

        #======================================================================
        # Progress bars
        #======================================================================
        # Bussy bar
        self.ui.bussyBar.setRange(0,100)
        # Progress bar
        self.ui.progressBar.setRange(0,100)
        # Cpu bar
        self.ui.cpuBar.setRange(0,100)
        self.ui.cpuBar.setValue(getSys()[0])
        #Memory bar
        self.ui.memBar.setRange(0,100)
        self.ui.memBar.setValue(getSys()[1])

        #======================================================================
        # Finishing touches
        #======================================================================
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
            self.ui.startKey.setText(self.par['startTrialKey'])
            self.ui.stopKey.setText(self.par['stopTrialKey'])
            self.ui.varKey.setText(self.par['variableKey'])
            self.ui.textbox.setText('')
            self.ui.regSamp.setText(self.par['regExpSamp'])
            self.ui.regEfix.setText(self.par['regExpEfix'])
            self.ui.regEsacc.setText(self.par['regExpEsacc']) 
            self.ui.regEblink.setText(self.par['regExpEblink'])
            self.ui.regStart.setText(self.par['regExpStart'])
            self.ui.regStop.setText(self.par['regExpStop'])
            self.ui.regVar.setText(self.par['regExpVar'])
            self.ui.regMsg.setText(self.par['regExpMsg'])
            self.ui.parsedName.setText(self.par['saveExtension'])
            self.ui.rawName.setText(self.par['saveRawExtension'])
            self.ui.mergedName.setText(self.par['mergedFileNames'])
            self.ui.pixPerDeg.setText(self.par['pxPerDeg'])
            maxCores = psutil.cpu_count()
            if int(self.par['nrCores']) > maxCores-1:
                self.par['nrCores'] = str(maxCores-1)
            self.ui.nrCores.setText(self.par['nrCores'])

            
            # Set button defaults
            # Parallel button is not set, sets depending on file number
            if self.par['saveMergedFiles'] == 'No':
                self.ui.mergebtn.setCurrentIndex(0)
            else:
                self.ui.mergebtn.setCurrentIndex(1)
            if self.par['saveRawFiles'] == 'No':
                self.ui.saveRawbtn.setCurrentIndex(0)
            else:
                self.ui.saveRawbtn.setCurrentIndex(1)
            if self.par['pxMode'] == 'Automatic':
                self.ui.pixMode.setCurrentIndex(0)
            else:
                self.ui.pixMode.setCurrentIndex(1)
            if self.par['longFormat'] == 'No':
                self.ui.longbtn.setCurrentIndex(0)
            else:
                self.ui.longbtn.setCurrentIndex(1)
            if self.par['duplicateValues'] == 'No':
                self.ui.duplicLongbtn.setCurrentIndex(0)
            else:
                self.ui.duplicLongbtn.setCurrentIndex(1)
        else:
            pass

    def updateSystemBars(self, sysval):
        self.ui.cpuBar.setValue(sysval[0])
        self.ui.memBar.setValue(sysval[1])
        if self.progressValue == len(self.files) and len(self.files) > 0:
            self.stopBussyBar()
            self.ui.statusL.setText(self.DONEL)
            self.ui.statusL.show()

    def updateProgress(self, value):
        self.progressValue += value
        if self.progressValue == len(self.files):
            if self.ui.mergebtn.currentText() == 'Yes':
                self.savedMergedFiles()
        self.ui.progressBar.setValue(self.progressValue)
        
        print time.time() - self.STARTTIME

    def startBussyBar(self):
        self.ui.bussyBar.setRange(0,0)

    def stopBussyBar(self):
        self.ui.bussyBar.setRange(0,1)

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
            self.ui.textbox.setText('\n'.join(fileNames))

            # Activate the parsing button
            self.ui.Parsebtn.setEnabled(True)

            # Set parallel processing
            if len(self.files) < 2:
                self.ui.paralell.setCurrentIndex(1)
            else:
                self.ui.paralell.setCurrentIndex(0)

    def unlockSettings(self):
        # Enable all settings
        self.ui.regSamp.setEnabled(True)
        self.ui.regEfix.setEnabled(True)
        self.ui.regEsacc.setEnabled(True)
        self.ui.regEblink.setEnabled(True)
        self.ui.regStart.setEnabled(True)
        self.ui.regStop.setEnabled(True)
        self.ui.regVar.setEnabled(True)
        self.ui.regMsg.setEnabled(True)
        self.ui.parsedName.setEnabled(True)
        self.ui.rawName.setEnabled(True)
        self.ui.mergedName.setEnabled(True)
        self.ui.mergebtn.setEnabled(True)
        self.ui.nrCores.setEnabled(True)
        self.ui.paralell.setEnabled(True)
        self.ui.saveRawbtn.setEnabled(True)
        self.ui.pixMode.setEnabled(True)
        self.ui.pixPerDeg.setEnabled(True)
        self.ui.longbtn.setEnabled(True)
        self.ui.duplicLongbtn.setEnabled(True)

        # Enable lock button
        self.ui.lockSettingsM.setEnabled(True)
        # Disable unlock button
        self.ui.unlockSettingsM.setEnabled(False)

    def lockSettings(self):
        self.ui.regSamp.setEnabled(False)
        self.ui.regEfix.setEnabled(False)
        self.ui.regEsacc.setEnabled(False)
        self.ui.regEblink.setEnabled(False)
        self.ui.regStart.setEnabled(False)
        self.ui.regStop.setEnabled(False)
        self.ui.regVar.setEnabled(False)
        self.ui.regMsg.setEnabled(False)
        self.ui.parsedName.setEnabled(False)
        self.ui.rawName.setEnabled(False)
        self.ui.mergedName.setEnabled(False)
        self.ui.mergebtn.setEnabled(False)
        self.ui.nrCores.setEnabled(False)
        self.ui.paralell.setEnabled(False)
        self.ui.saveRawbtn.setEnabled(False)
        self.ui.pixMode.setEnabled(False)
        self.ui.pixPerDeg.setEnabled(False)
        self.ui.longbtn.setEnabled(False)
        self.ui.duplicLongbtn.setEnabled(False)

        # disable lock button
        self.ui.lockSettingsM.setEnabled(False)
        # Enable unlock button
        self.ui.unlockSettingsM.setEnabled(True)
        # Enable parse button
        if len(self.files) > 0:
            self.ui.Parsebtn.setEnabled(True)

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
        self.ui.progressBar.setRange(0,len(self.files))
        self.ui.progressBar.setValue(0)
        self.progressValue = 0
        self.lockSettings()
        self.ui.statusL.hide()
        self.repaint()

        #======================================================================
        # Get settings for parsing
        #======================================================================
        # File name handling
        self.par['saveExtension'] = self.ui.parsedName.toPlainText()
        self.par['saveRawExtension'] = self.ui.rawName.toPlainText()
        self.par['savefileNames'] = [f[:-4] + self.par['saveExtension']+'.p' for f in self.files]
        self.par['saveFileNamesRaw'] = [f[:-4] + self.par['saveExtension'] + self.par['saveRawExtension']+'.p' for f in self.files]

        # Get regular expression info
        self.par['startTrialKey'] = self.ui.startKey.toPlainText().strip()
        self.par['stopTrialKey'] = self.ui.stopKey.toPlainText().strip()
        self.par['variableKey'] = self.ui.varKey.toPlainText().strip()
        self.par['regExpSamp'] = self.ui.regSamp.toPlainText()
        self.par['regExpEfix'] = self.ui.regEfix.toPlainText()
        self.par['regExpEsacc'] = self.ui.regEsacc.toPlainText()
        self.par['regExpEblink'] = self.ui.regEblink.toPlainText()
        # Set regular expressions for start/stop/var/msg
        if self.par['DFregExpStart'] != self.ui.regStart.toPlainText():
            self.par['regExpStart'] = self.ui.regStart.toPlainText()
            self.par['regExpStartNew'] = True
        else:
            self.par['regExpStartNew'] = False
        if self.par['DFregExpStop'] != self.ui.regStop.toPlainText():
            self.par['regExpStop'] = self.ui.regStop.toPlainText()
            self.par['regExpStopNew'] = True
        else:
            self.par['regExpStopNew'] = False
        if self.par['DFregExpVar'] != self.ui.regVar.toPlainText():
            self.par['regExpVar'] = self.ui.regVar.toPlainText()
            self.par['regExpVarNew'] = True
        else:
            self.par['regExpVarNew'] = False
        if self.par['DFregExpMsg'] != self.ui.regMsg.toPlainText():
            self.par['regExpMsg'] = self.ui.regMsg.toPlainText()
            self.par['regExpMsgNew'] = True
        else:
            self.par['regExpMsgNew'] = False

        # Processing info
        self.par['saveMergedFiles'] = self.ui.mergebtn.currentText()
        self.par['saveRawFiles'] = self.ui.saveRawbtn.currentText()
        self.par['runParallel'] = self.ui.paralell.currentText()
        self.par['nrCores'] = self.ui.nrCores.toPlainText()
        self.par['pxMode'] = self.ui.pixMode.currentText()
        self.par['pxPerDeg'] = self.ui.pixPerDeg.toPlainText()
        self.par['longFormat'] = self.ui.longbtn.currentText()
        self.par['duplicateValues'] = self.ui.duplicLongbtn.currentText()
        
        # Number of available cores
        maxCores = psutil.cpu_count()
        if int(self.par['nrCores']) > maxCores:
            self.par['nrCores'] = str(maxCores)
        self.ui.nrCores.setText(self.par['nrCores'])
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
        self.STARTTIME = time.time()
        self.startBussyBar()
        if self.par['runParallel'] == 'Yes':
            try:
                self.ui.statusL.setText(self.MCPL)
                self.ui.statusL.show()
                self.repaint()
                # Start threading System resources
                for sub in self.files:
                    results = self.pool.apply_async(parseWrapper,
                                               args = (sub, self.par),
                                               callback=self.callbackParser)
            except:
                self.ui.statusL.setText(self.MCERRORL)
                self.ui.statusL.show()
                self.parseSingleCore()

        else:
            self.parseSingleCore()

    def parseSingleCore(self):
        try:
            # Start threading System resources
            self.ui.statusL.setText(self.SCPL)
            self.ui.statusL.show()
            self.repaint()
            self.worker = workerClass()
            self.worker.par = self.par
            self.worker.files = self.files
            self.worker.start()
            self.connect(self.worker, QtCore.SIGNAL('PROGRESS'), self.updateProgress)
        except:
            self.ui.statusL.setText(self.ERRORL)
            self.ui.statusL.show()
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