# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:01:49 2017

@author: User1
"""

#==============================================================================
#==============================================================================
# # Eyelink 1000 parser with PyQt5 GUI
#==============================================================================
#==============================================================================
import sys
import os
import pandas as pd
import json
from collections import OrderedDict
from PyQt5 import QtGui, QtCore, QtWidgets
import psutil
import multiprocessing
if sys.version_info[0] < 3:
    from parseFuncs import parseWrapper
else:
    from parseFuncs3x import parseWrapper
import time
from eyeParserBuilder import Ui_eyeTrackerSelection

#==============================================================================
# Functions used by the parser
#==============================================================================
def getSys():
    return psutil.cpu_percent(1), psutil.virtual_memory()[2]

def saveToMat(df, fn):
    import scipy
    import scipy.io
    a_dict = {col_name : df[col_name].values for col_name in df.columns.values}  
    scipy.io.savemat(fn, {'data':a_dict})

def saveResults(data, name, dType):
    if dType == '.p':
        data.to_pickle(name+dType)
    elif dType == '.hdf':
        data.to_hdf(name+dType, 'w')
    elif dType == '.json':
        data.to_json(name+dType)
    elif dType == '.csv':
        data.to_csv(name+dType, index = False, na_rep = '#N/A')
    elif dType == '.mat':
        saveToMat(data, name)

def readFile(fName):
    with open(fName) as json_file:  
        content = json.load(json_file)       
    return content

def writeFile(fName, data):
    with open(fName, 'w') as outfile:  
        json.dump(data, outfile, indent=4)

def sortDict(data):
    d = OrderedDict({})
    for (key, value) in sorted(data.items()):
        d[key] = value
    return d

def cleanDict(dirtyDict, cleanDict):
    cleaned = OrderedDict({})
    for key in dirtyDict.keys():
        if key in cleanDict.keys():
            cleaned[key] = dirtyDict[key]
    return cleaned

#==============================================================================
#==============================================================================
# #  GUI code
#==============================================================================
#==============================================================================
class ThreadClass(QtCore.QThread):
    sysVals = QtCore.pyqtSignal(tuple)
    
    def __init__(self, parent = None):
        super(ThreadClass, self).__init__(parent)
        
    def run(self):
        while 1:
            time.sleep(1)
            sysval = getSys()
            self.sysVals.emit(sysval)

class workerClass(QtCore.QThread):
    prog = QtCore.pyqtSignal(int)
    def __init__(self, parent = None):
        super(workerClass, self).__init__(parent)
        self.par = {}
        self.files = []

    def run(self):
        #Do the analysis single core
        for indx, FILENAME in enumerate(self.files):
            FILENAME, parsedData, rawData, parsedLong, error = parseWrapper(self.files[indx], self.par)
            if error == False:
                # Save data
                saveResults(parsedData, self.par['savefileNames'][indx], self.par['formatType'])
                if self.par['saveRawFiles'] == 'Yes':
                    saveResults(rawData, self.par['saveFileNamesRaw'][indx], self.par['rawFormatType'])
                if self.par['longFormat'] == 'Yes':
                    saveResults(parsedLong, self.par['saveFileNamesLong'][indx], self.par['longFormatType'])
            else:
                print("\n\nUnfortunatly an Error occured!")
                print(os.path.basename(FILENAME), "Was not saved")
                print("Please try to parse this file again")
                print("Error Message:")
                print(error)
                print('\n')
                
            # Send progress
            self.prog.emit(1)

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
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        return result
    
class Window(QtWidgets.QMainWindow):
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
        self.progressValue = 0

        #======================================================================
        # Initiate main features of the GUI
        #======================================================================
        super(QtWidgets.QMainWindow, self).__init__()
        self.ui = Ui_eyeTrackerSelection()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon('eye.png'))
        
        # Set background color
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
        self.setPalette(palette)

        # Hide tabs
        self.ui.optionsTab.setVisible(False)
        
        # Load settings
        self.loadSettings()
        
        #======================================================================
        # Set the menu bar triggers
        #======================================================================
        # Select file(s) for parsing
        self.ui.openFile.triggered.connect(self.selectFile)
        # Exit parser
        self.ui.quitParser.triggered.connect(self.close_application)
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
        # The trigger for pixels per degree mode
        self.ui.pixMode.currentIndexChanged.connect(self.setPxMode)
        # Trigger loading of data
        self.ui.TobiiBox.clicked.connect(self.changeEyetracker)
        self.ui.EyelinkBox.clicked.connect(self.changeEyetracker)
        
        #======================================================================
        # Initiate options tab
        #======================================================================
        # Parallel processing
        self.ui.paralell.addItem("Yes")
        self.ui.paralell.addItem("No")
        idx = self.ui.paralell.findText(self.par['runParallel'])
        if idx != -1:
            self.ui.paralell.setCurrentIndex(idx)
        #Number of cores
        maxCores = psutil.cpu_count()
        if int(self.par['nrCores']) > maxCores-1:
            self.par['nrCores'] = str(maxCores-1)
        self.ui.nrCores.setText(str(int(self.par['nrCores'])))
        
        # Pixels per degree
        if self.par['pxMode'] == 'Automatic':
            self.ui.pixMode.setCurrentIndex(0)
        else:
            self.ui.pixMode.setCurrentIndex(1)

        #======================================================================
        # Initiate Save options tab
        #======================================================================
        #Parsed name
        self.ui.parsedName.setText(self.par['saveExtension'])
        #Parsed Raw name
        self.ui.rawName.setText(self.par['saveRawExtension'])
        # Longformat name 
        self.ui.longName.setText(self.par['saveLongExtension'])
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
        # Save as dropDowns
        idx = self.ui.fileTypeBtn.findText(self.par['saveAs'])
        if idx != -1:
            self.ui.fileTypeBtn.setCurrentIndex(idx)
        idx = self.ui.fileTypeRawBtn.findText(self.par['rawSaveAs'])
        if idx != -1:
            self.ui.fileTypeRawBtn.setCurrentIndex(idx)
        idx = self.ui.fileTypeLongBtn.findText(self.par['longSaveAs'])
        if idx != -1:
            self.ui.fileTypeLongBtn.setCurrentIndex(idx)
        
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
        # Set start time of parser
        self.finished = False
        
        # Start threading System resources       
        self.threadclass = ThreadClass()
        self.threadclass.sysVals.connect(self.updateSystemBars)
        self.threadclass.start()

        # Display GUI
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()
        self.activateWindow()
        
    #==============================================================================
    # Define button actions
    #==============================================================================   
    def changeEyetracker(self):
        if self.ui.TobiiBox.isChecked():
            self.ui.pixMode.setCurrentIndex(1)
            self.ui.pixMode.setEnabled(False)
            self.par = self.tobii
            self.eyeTracker = 'Tobii'
        elif self.ui.EyelinkBox.isChecked():
            self.ui.pixMode.setEnabled(True)
            self.par = self.eyelink
            self.eyeTracker = 'Eyelink'
        self.updateGUI()
        
    def loadSettings(self):
        settings = readFile('settings.txt')
        self.eyeTracker = settings['Eyetracker']
        self.eyelink = sortDict(settings['Eyelink']['par'])
        self.eyelinkDF = sortDict(settings['Eyelink']['default'])
        self.tobii = sortDict(settings['Tobii']['par'])
        self.tobiiDF = sortDict(settings['Tobii']['default'])
        
        # Set the general settings
        if self.eyeTracker == 'Tobii':
            self.ui.TobiiBox.setChecked(True)
            self.ui.EyelinkBox.setChecked(False)
            self.par = self.tobii
        elif self.eyeTracker == 'Eyelink':
            self.ui.TobiiBox.setChecked(False)
            self.ui.EyelinkBox.setChecked(True)
            self.par = self.eyelink
        self.updateGUI()

    def saveSettings(self):
        data = OrderedDict({})
        # Clean data
        if self.eyeTracker == 'Tobii':
            self.tobii = self.par
        elif self.eyeTracker == 'Eyelink':
            self.eyelink = self.par
        self.eyelink = cleanDict(self.eyelink, self.eyelinkDF)
        self.tobii = cleanDict(self.tobii, self.tobiiDF)
        data['Eyetracker'] = self.eyeTracker
        data['Eyelink'] = {'par':self.eyelink, 'default':self.eyelinkDF}
        data['Tobii'] = {'par':self.tobii, 'default':self.tobiiDF}
        writeFile('settings.txt', data)
    
    def saveDefaultSettings(self):
        data = OrderedDict({})  
        data['Eyetracker'] = self.eyeTracker
        data['Eyelink'] = {'par':self.eyelinkDF, 'default':self.eyelinkDF}
        data['Tobii'] = {'par':self.tobiiDF, 'default':self.tobiiDF}
        writeFile('settings.txt', data)
    
    def loadDefaultSettings(self):
        choice = QtWidgets.QMessageBox.question(self, 'Default settings',
                                            "Loading default settings permanently\n"+\
                                            "deletes any changed settings!\n\n"+\
                                            "Do you really want to load default settings?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            # Write and load the deffault settings
            self.saveDefaultSettings()
            self.loadSettings()
        else:
            pass
            
    def updateGUI(self):
        # Sets the default textbox settings 
        self.ui.startKey.setText(self.par['startTrialKey'])
        self.ui.stopKey.setText(self.par['stopTrialKey'])
        self.ui.varKey.setText(self.par['variableKey'])
        self.ui.textbox.setText('')
        self.ui.Parsebtn.setEnabled(False)
        self.files = []
        self.ui.parsedName.setText(self.par['saveExtension'])
        self.ui.rawName.setText(self.par['saveRawExtension'])
        maxCores = psutil.cpu_count()
        if int(self.par['nrCores']) > maxCores-1:
            self.par['nrCores'] = str(maxCores-1)
        self.ui.nrCores.setText(str(int(self.par['nrCores'])))

        
        # Set button defaults
        # Parallel button is not set, sets depending on file number
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
        # Save as dropDowns
        idx = self.ui.fileTypeBtn.findText(self.par['saveAs'])
        if idx != -1:
            self.ui.fileTypeBtn.setCurrentIndex(idx)
        idx = self.ui.fileTypeRawBtn.findText(self.par['rawSaveAs'])
        if idx != -1:
            self.ui.fileTypeRawBtn.setCurrentIndex(idx)
        idx = self.ui.fileTypeLongBtn.findText(self.par['longSaveAs'])
        if idx != -1:
            self.ui.fileTypeLongBtn.setCurrentIndex(idx)
        idx = self.ui.paralell.findText(self.par['runParallel'])
        if idx != -1:
            self.ui.paralell.setCurrentIndex(idx)
        # Set input values         
        self.ui.screenDist.setValue(float(self.par['screenDist']))
        self.ui.screenW.setValue(float(self.par['screenW']))
        self.ui.resolutionX.setValue(float(self.par['screenX']))
        self.ui.resolutionY.setValue(float(self.par['screenY']))
        self.ui.sampleFreq.setValue(float(self.par['sampFreq']))
        

    def updateSystemBars(self, sysval):
        self.ui.cpuBar.setValue(sysval[0])
        self.ui.memBar.setValue(sysval[1])
        self.ui.progressBar.setValue(self.progressValue)
        if self.progressValue == len(self.files) and len(self.files) > 0:
            self.stopBussyBar()
            self.ui.statusL.setText(self.DONEL)
            self.ui.statusL.show()
            if self.finished == False:
                dur = time.time() - self.parseStartTime
                timem = int(dur/60)
                times = dur%60
                print("Finished!")
                print("Duration: %d minutes, %d seconds" %(timem, times))
                self.finished = True

    def startBussyBar(self):
        self.ui.bussyBar.setRange(0,0)

    def stopBussyBar(self):
        self.ui.bussyBar.setRange(0,1)

    def setPxMode(self):
        if self.ui.pixMode.currentText() == 'Automatic':
            self.ui.screenDist.setEnabled(False)
            self.ui.screenW.setEnabled(False)
            self.ui.resolutionX.setEnabled(False)
            self.ui.resolutionY.setEnabled(False)
        elif self.ui.pixMode.currentText() == 'Manual' or self.ui.TobiiBox.isChecked():
            self.ui.screenDist.setEnabled(True)
            self.ui.screenW.setEnabled(True)
            self.ui.resolutionX.setEnabled(True)
            self.ui.resolutionY.setEnabled(True)

    def selectFile(self):
        if self.ui.EyelinkBox.isChecked():
            tempFiles = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select file(s)', "","ASC (*.asc);;All Files (*)")[0]
        elif self.ui.TobiiBox.isChecked(): 
            tempFiles = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select file(s)', "","TSV (*.tsv);;All Files (*)")[0]
        else:
            tempFiles = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select file(s)', "","All Files (*)")[0]
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

    def documentation(self):
        text=open(self.docLoc).read()
        doc = MyMessageBox()
        doc.setWindowIcon(QtGui.QIcon('eye.png'))
        doc.setWindowTitle("Documentation")
        doc.setIcon(QtWidgets.QMessageBox.Information)
        doc.setStandardButtons(QtWidgets.QMessageBox.Close)
        doc.setText('Documentation'+'\t'*10)
        doc.setDetailedText(text)
        doc.exec_()

    def setValues(self):
        # Initiate bussy label
        self.ui.progressBar.setRange(0,len(self.files))
        self.ui.progressBar.setValue(0)
        self.progressValue = 0
        self.ui.statusL.hide()
        self.repaint()

        #======================================================================
        # Get settings for parsing
        #======================================================================
        # Get file type 
        fileType = self.ui.fileTypeBtn.currentText()
        if fileType == 'pickle':
            self.par['formatType'] = '.p'
        elif fileType == 'HDF':
            self.par['formatType'] = '.hdf'
        elif fileType == 'json':
            self.par['formatType'] = '.json'
        elif fileType == 'MAT':
            self.par['formatType'] = '.mat'
        fileType = self.ui.fileTypeRawBtn.currentText()
        if fileType == 'pickle':
            self.par['rawFormatType'] = '.p'
        elif fileType == 'HDF':
            self.par['rawFormatType'] = '.hdf'
        elif fileType == 'json':
            self.par['rawFormatType'] = '.json'
        elif fileType == 'MAT':
            self.par['rawFormatType'] = '.mat'
        fileType= self.ui.fileTypeLongBtn.currentText()
        if fileType == 'pickle':
            self.par['longFormatType'] = '.p'
        elif fileType == 'HDF':
            self.par['longFormatType'] = '.hdf'
        elif fileType == 'json':
            self.par['longFormatType'] = '.json'
        elif fileType == 'CSV':
            self.par['longFormatType'] = '.csv'
        elif fileType == 'MAT':
            self.par['longFormatType'] = '.mat'
        
        # File name handling
        self.par['saveExtension'] = self.ui.parsedName.toPlainText()
        self.par['saveRawExtension'] = self.ui.rawName.toPlainText()
        self.par['saveLongExtension'] = self.ui.longName.toPlainText()
        self.par['savefileNames'] = [f[:-4] + self.par['saveExtension'] for f in self.files]
        self.par['saveFileNamesRaw'] = [f[:-4] + self.par['saveExtension'] + self.par['saveRawExtension'] for f in self.files]
        self.par['saveFileNamesLong'] = [f[:-4] + self.par['saveExtension'] + self.par['saveLongExtension'] for f in self.files]

        # Get regular expression info
        self.par['startTrialKey'] = self.ui.startKey.toPlainText().strip()
        self.par['stopTrialKey'] = self.ui.stopKey.toPlainText().strip()
        self.par['variableKey'] = self.ui.varKey.toPlainText().strip()

        # Screen info
        self.par['screenDist'] = self.ui.screenDist.value()
        self.par['screenW'] = self.ui.screenW.value()
        self.par['screenRes'] = (float(self.ui.resolutionX.value()), float(self.ui.resolutionY.value()))
        self.par['sampFreq'] = self.ui.sampleFreq.value()
        self.par['screenX'] = float(self.ui.resolutionX.value())
        self.par['screenY'] = float(self.ui.resolutionY.value())
        
        # Processing info
        self.par['saveRawFiles'] = self.ui.saveRawbtn.currentText()
        self.par['runParallel'] = self.ui.paralell.currentText()
        self.par['nrCores'] = self.ui.nrCores.toPlainText()
        self.par['pxMode'] = self.ui.pixMode.currentText()
        self.par['longFormat'] = self.ui.longbtn.currentText()
        self.par['duplicateValues'] = self.ui.duplicLongbtn.currentText()
        
        # Number of available cores
        maxCores = psutil.cpu_count()
        if int(self.par['nrCores']) > maxCores:
            self.par['nrCores'] = int(maxCores)
        self.ui.nrCores.setText(str(int(self.par['nrCores'])))  
        self.pool = multiprocessing.Pool(processes=int(self.par['nrCores']))
        
        #======================================================================
        # Save settings
        #======================================================================
        self.saveSettings()

        #======================================================================
        # Run parser
        #======================================================================
        self.parse()
        
    def updateProgress(self, value):
        self.progressValue += value

    def callbackParser(self, results):
        # Set save names
        savefileName = results[0][:-4] + self.par['saveExtension']
        saveFileNamesRaw = results[0][:-4] + self.par['saveExtension'] + self.par['saveRawExtension']
        saveFileNameslong = results[0][:-4] + self.par['saveExtension'] + self.par['saveLongExtension']
        
        if results[-1] == False:
            # Save data 
            saveResults(results[1], savefileName, self.par['formatType'])
            if self.par['saveRawFiles'] == 'Yes':
                saveResults(results[2], saveFileNamesRaw, self.par['rawFormatType'])
            if self.par['longFormat'] == 'Yes':
                saveResults(results[3], saveFileNameslong, self.par['longFormatType'])
        else:
            print("\n\nUnfortunatly an Error occured!")
            print(os.path.basename(savefileName), "Was not saved")
            print("Please try to parse this file again")
            print("Error Message:")
            print(results[-1])
            print('\n')
        del results
        # Update progressbar       
        self.progressValue += 1
                
    def parse(self):
        self.startBussyBar()        
        self.parseStartTime = time.time()
        # Only run parallel if system version is lover than 3.7
        if (self.par['runParallel'] == 'Yes' and sys.version_info[0] < 3) \
        or self.par['runParallel'] == 'Yes' and (sys.version_info[0] == 3 and sys.version_info[1] < 7):
            try:
                self.ui.statusL.setText(self.MCPL)
                self.ui.statusL.show()
                self.repaint()
                # Start threading System resources
                results = []
                for sub in self.files:
                    results.append(self.pool.apply_async(parseWrapper,
                                               args = (sub, self.par, ),
                                               callback=self.callbackParser))  
            except:
                self.ui.statusL.setText(self.MCERRORL)
                self.ui.statusL.show()
                self.parseSingleCore()
        else:
            self.parseSingleCore()
            
        if len(self.files) == 0:
            self.stopBussyBar()
            self.ui.progressBar.setRange(0,1)

    def parseSingleCore(self):
        try:
            # Start threading System resources
            self.ui.statusL.setText(self.SCPL)
            self.ui.statusL.show()
            self.repaint()
            self.worker = workerClass()
            self.worker.par = self.par
            self.worker.files = self.files
            self.worker.prog.connect(self.updateProgress)
            self.worker.start()
        except:
            self.ui.statusL.setText(self.ERRORL)
            self.ui.statusL.show()
            self.repaint()
            time.sleep(5)
            sys.exit()

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, 'Quit?',
                                            "Exit parser?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
        else:
            pass

def run():
    if __name__ == "__main__":
        import sys
        import ctypes
        myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
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