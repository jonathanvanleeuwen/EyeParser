# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 10:09:12 2017

@author: Jonathan
"""
#==============================================================================
# Imports
#==============================================================================
import re
import math
import numpy as np
import pandas as pd
from collections import deque
from itertools import izip
import traceback

#==============================================================================
# Functions
#==============================================================================
def distBetweenPointsInArray(point1X, point1Y, point2X, point2Y):
	'''
	'''
	dist = np.sqrt( (point1X-point2X)**2 + (point1Y - point2Y)**2 )
	return dist

def distBetweenPoints(point1, point2):
	'''
	'''
	dist = np.sqrt( (point1[0]-point2[0])**2 + (point1[1] - point2[1])**2 )
	return dist

def determineAngle(p1, p2):
	'''
	'''
	normx = ((p2[0] - p1[0]))
	normy = ((p2[1] - p1[1]))
	narcdeg = math.atan2(normy, normx)
	sdegree = ((narcdeg * 180)/math.pi)
	return sdegree

def getFixQual(fixX, fixY, pxPerDeg):
    '''
    Calculates the standard deviation and RMS in pixels 
    and in degrees for each fixation in a list of fixations
    Retuns False for a specific fixation if there are less than
    5 samples in the fixation
    
    Parameters
    ------------
    fixX : np.array with np.arrays 
        List of lists containing the x positions of the gaze for each sample
    fixY : np.array with np.arrays 
        List of lists containing the y positions of the gaze for each sample
    pxPerDeg : Float or int
        The number of pixels spanning 1 visual degree
        
        
    Returns
    ------------
    stdvPix : list of floats
        The standard deviation of each fixation in pixel values
    stdvDeg : list of floats
        The standard deviation of each fixation in visual degrees
    RMSPix : list of floats
        The RMS of each fixation in pixel values
    RMSDeg : list of floats
        The RMS of each fixation in visual degrees
    
    Examples
    ------------
    >>> pxPerDeg = 48.0
    >>> 
    >>> fixX = np.array([
            np.array([838.4,  838.9,  839.2,  839.6,  840. ,  840.1]), 
            np.array([809.1,  811.5,  813.2,  814.7,  815.8,  816.6,  817.4])
            ])
    >>> 
    >>> fixY = np.array([
            np.array([977.8,  976. ,  975.1,  974.2,  973.3,  971.9]),
            np.array([992.3,   993.9,   997.4,   999.4,  1002.4,  1004.8,  1007.5])
            ])
    >>> 
    >>> stdvPix, stdvDeg, RMSPix, RMSDeg = getFixQual(fixX, fixY, pxPerDeg)
    >>> 
    >>> print 'stdvPix:', stdvPix
    stdvPix: [1.9866918342924882, 5.8657776073403518]
    >>> 
    >>> print 'stdvDeg:', stdvDeg
    stdvDeg: [0.041389413214426837, 0.12220370015292399]
    >>> 
    >>> print 'RMSPix:', RMSPix
    RMSPix: [1.288409872672502, 3.0069364254447883]
    >>> 
    >>> print 'RMSDeg:', RMSDeg
    RMSDeg: [0.026841872347343792, 0.06264450886343309]

    '''
    
    # Initiate lists
    stdvPix = []
    stdvDeg = []
    RMSPix = []
    RMSDeg = []
    
    for i, (x,y) in enumerate(zip(fixX, fixY)):
        if len(x) > 5:
            # Get average position
            avX = np.mean(x)
            avY = np.mean(y)
            
            # Calculate standard deviation
            thetaAv = np.sqrt((x - avX)**2 + (y - avY)**2)
            stdvPix.append(np.sqrt(np.sum(np.square(thetaAv))/len(thetaAv)))
            stdvDeg.append(stdvPix[-1]/float(pxPerDeg))
            
            # Calculate the distance between each sample point in visual degrees
            theta = np.sqrt((x[:-1]-x[1:])**2 + (y[:-1] - y[1:])**2)
            RMSPix.append(np.sqrt(np.sum(np.square(theta))/len(theta)))
            RMSDeg.append(RMSPix[-1]/float(pxPerDeg))
        else:
            stdvPix.append(False)
            stdvDeg.append(False)
            RMSPix.append(False)
            RMSDeg.append(False)
    
    return stdvPix, stdvDeg, RMSPix, RMSDeg

def pointAngle(p1, p2):
    '''
    Determine the angle of a point (360degrees).
    Assumes that x goes from lower to high (left right)
    Assumes that y goes from high to low (bottom top)
    
    Parameters
    ------------
    p1 : tuple or list of ints or floats
        The x,y coordinates of the start point
    p2 : tuple or list of ints or floats
        The x,y coordinates of the end point

    Returns
    ------------
    angle : float
        The Angle between point 1 (p1) and point 2 (p2)

    Examples
    ------------
    >>> p1 = [0,0]
    >>> p2 = [45,45]
    >>> angle = pointAngle(p1, p2)
    >>> print angle
    315.0

    
    '''
    normx = ((p2[0] - p1[0]))
    normy = ((p2[1] - p1[1]))
    narcdeg = math.atan2(normy, normx)
    sdegree = math.degrees(narcdeg)
    angle = sdegree + ((180-sdegree)*2)
    if angle > 360:
        angle -= 360
    return angle

def calculateSaccadeCurvature(xSacc, ySacc, pixPerDegree, ignoreDist = 0.5, flipY = False):
    ''' Calculates the saccade curvature.\n
    Input a list of xSaccade data points as well as a list of ySaccade data points.\n
    Also ignores any data points within the start and end range (degrees)\n

    Parameters
    ----------
    xSacc: List of lists 
        [[],[],[],[],[]], Eeach lists contains xSacc data points
    ySacc: List of lists 
        [[],[],[],[],[]], Each lists contains ySacc data points
    pixPerDegree: Float
        The number of pixels per visual degree
    ignoreDist: Float
        All data points which are closer than this value (visual degrees) to either the start or end of saccade are ignored

    Returns
    ----------
    curveData: List of lists 
        Containing the saccade curvature for all points in the saccades
    saccAngle: List of Floats
        The angle of the saccade


    Assumptions
    ----------
    Values:
        0 - 180 degrees (clockwise curvature)\n
        0 - -180 degrees (counterclockwhise curvature)
    X values go from left to right\n
    Y values go from top to bottom\n
    '''    
    curveData = deque([])
    saccAngles = deque([])
    for sacc in range(0,len(xSacc)):
        saccX           = xSacc[sacc]
        # Check if there are enough samples in the saccade to calculate curvature
        if len(saccX) < 4: 
            curveData.append(np.nan)
            saccAngles.append(np.nan)
            continue
        if flipY == True:
            saccY           = [i*-1 for i in ySacc[sacc]]
        else:
            saccY           = ySacc[sacc]
        startPos        = (saccX[0], saccY[0])
        endPos          = (saccX[-1], saccY[-1])
        saccadeAngle    = determineAngle(startPos,endPos) *-1

        # we calculate point angle for all points except the last point (also exclude first point)
        pointAngles     = np.zeros(len(saccX)-2)
        for pointNr in range(0,len(saccX)-2):
            point                   = (saccX[pointNr+1], saccY[pointNr+1])
            startDist               = distBetweenPoints(startPos, point) / pixPerDegree
            endDist                 = distBetweenPoints(endPos, point) / pixPerDegree
            # check if the sample is far enough away from start and end position
            # We have the problem with overshoots, the overshoot is sometimes more than ignoreDist
            # this causes the cuvature analysis to be done for then stopped, started and stopped again
            # [0,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0,0,] Where 1 has calculated curvature and 0 is to close
            if min([startDist, endDist]) < ignoreDist:
                pointAngles[pointNr] = 9999
            else:
                pointCurv = (determineAngle(startPos,point) *-1) - saccadeAngle
                if pointCurv > 180:
                    pointCurv -=360
                elif pointCurv < -180:
                    pointCurv +=360
                pointAngles[pointNr] = pointCurv
        pointAngles = pointAngles[pointAngles < 9999]
        curveData.append(pointAngles)
        # Append saccadeAngles
        if saccadeAngle > 180:
            saccadeAngle -=360
        elif saccadeAngle < -180:
            saccadeAngle +=360
        saccAngles.append(saccadeAngle)
    return curveData, saccAngles

def parseToLongFormat(data, duplicate = 'No'):
    '''
    Turn a parsed datafile into long data file:
    Deletes the raw data and only keeps events
    '''
    data = data.copy()
    #==============================================================================
    # Delete al the keys with raw data
    #==============================================================================
    LargeData = ['saccTraceTime', 'saccTraceX', 'saccTraceY', 'saccTracePup', 
                 'euclidDist', 'rawPupSize', 'rawTime', 'rawX', 'rawY', 
                 'fixTraceTime', 'fixTraceX', 'fixTraceY', 'fixTracePup']
    LargeData = ['DK_'+i for i in LargeData]
    LargeData.append('DV_description')
    for key in LargeData:
        if key in data.keys():
            del data[key]
        elif key[3:] in data.keys():
            del data[key[3:]]

    # Delete all headers with spaces
    for key in data.keys():    
        if len(key.split()) > 1:
            del data[key]
            
    # Get the largest number of events for each trial
    trialLengths = np.zeros(len(data))
    for trial in xrange(len(data)):
        for key in data.keys():        
            try: 
                if isinstance(data[key][trial], basestring): 
                    keyLen = 1
                else:
                    keyLen = len(data[key][trial])
            except:
                keyLen = 1
                pass
            
            if keyLen > trialLengths[trial]:
                trialLengths[trial] = keyLen
    
    # Initiate a long format data frame
    dataL = pd.DataFrame(index = xrange(int(np.sum(trialLengths))), columns = data.keys())
    
    # Itterate through each key and populate the long format data
    for key in data.keys():
        strtIndex = 0
        stopIndex = int(trialLengths[0])
        keyVector = np.empty(len(dataL[key]))
        keyVector[:] = np.NAN
        keyVector = pd.Series(keyVector)
        for trial in xrange(len(data)):
            try:
                dataLen = len(data[key][trial])
                if isinstance(data[key][trial], basestring): 
                    if duplicate == 'Yes':
                        keyVector[strtIndex:stopIndex] = data[key][trial]
                    else:
                        keyVector[strtIndex] = data[key][trial]
                else:
                    keyVector[strtIndex:strtIndex+dataLen] = data[key][trial]
            except:
                if duplicate == 'Yes':
                    keyVector[strtIndex:stopIndex] = data[key][trial]
                else:
                    keyVector[strtIndex] = data[key][trial]
            # Update the index for the next data trial indexl
            if trial < len(data)-1:
                strtIndex += int(trialLengths[trial])
                stopIndex  = int(strtIndex + trialLengths[trial+1])
                
        # Store the new vector in the dataframe
        dataL[key] = keyVector
    return dataL

def filterDF(df, deleteKeys):
    keys = df.keys()   
    for key in keys:
        for delKey in deleteKeys:
            if delKey in key:
                del df[key]
    return df


#==============================================================================
#  Parser
#==============================================================================
def parseWrapper(f, kwargs):
    results = eyeLinkDataParser(f, **kwargs)
    return results

def eyeLinkDataParser(FILENAME, **par):
    try:
        #==========================================================================
        # Extract parameters, set defaults if parameeter is not given
        #==========================================================================
        regSamples = par.pop('regExpSamp', r'(\d{3,12})\t\s+(\d+\..)\t\s+(\d+\..)\t\s+(\d+\..).+\n')
        regEfix = par.pop('regExpEfix', r'EFIX\s+[LR]\s+(\d+)\t(\d+)\t(\d+)\t\s+(.+)\t\s+(.+)\t\s+(\d+)\n')
        regEsacc = par.pop('regExpEsacc', r'ESACC\s+[LR]\s+(\d+)\t(\d+)\t(\d+)\t\s+(\d+.?\d+)\t\s+(\d+.?\d+)\t\s+(\d+.?\d+)\t\s+(\d+.?\d+)\t\s+(\d+.?\d+)\t\s+(\d+)\n')
        regEblink = par.pop('regExpEblink', r'EBLINK\s+[LR]\s+(\d+)\t(\d+)\t(\d+)\n')
        # Makes experiment specific expressions for var/start and stop
        var = par.pop('variableKey', 'var')
        startTrial = par.pop('startTrialKey', 'start_trial')
        stopTrial = par.pop('stopTrialKey', 'stop_trial')
        # RegExp for start trial
        if par.pop('regExpStartNew', False) == True:
            regStart = par.pop('regExpStart')
        else:
            regStart = 'MSG\\t(\d+)\s+('+startTrial+').*\\n'
        # RegExp for stop trial
        if  par.pop('regExpStopNew', False) == True:
            regStop = par.pop('regExpStop')
        else:
            regStop = 'MSG\\t(\d+)\s+('+stopTrial+').*\\n'
        # RegExp for variables
        if par.pop('regExpVarNew', False) == True:
            regVar = par.pop('regExpVar')
        else:
            regVar = 'MSG\\t(\d+)\s+('+var+')\s+(.+).*\\n'
        # RegExp for messages
        if par.pop('regExpMsgNew', False) == True:
            regMsg = par.pop('regExpMsg')
        else:
            regMsg = 'MSG\\t(\d+)\s+(?!'+var+'|'+startTrial+'|'+stopTrial+')(.+).*\\n'
    
        # Get px per degree settings
        pxPerDegMode = par.pop('pxMode', 'Automatic')
        pxPerDegManual = par.pop('pxPerDeg', 48)
        
        # Get the information about long format
        convertToLong = par.pop('longFormat', 'No')
        duplicateValues = par.pop('duplicateValues', 'No')
        
        #==============================================================================
        # Define keywords
        #==============================================================================
        keyPrefix = 'DK_'
        varPrefix = 'DV_'
        rawKw = ['rawTime', 'rawX', 'rawY', 'rawPupSize']
        fixKw = ['sFix','eFix','durFix','fixX', 'fixY', 'fixPup']
        saccKw = ['ssacc','esacc','durSacc','ssaccX', 'ssaccY', 'esaccX', \
                  'esaccY', 'saccAmp', 'peakVelocity']
        blinkKw = ['sBlink','eBlink','durBlink']
        FixTraceKw = ['fixTraceTime', 'fixTraceX', 'fixTraceY', 'fixTracePup']
        SaccTraceKw= ['saccTraceTime', 'saccTraceX', 'saccTraceY', \
                      'saccTracePup']
        prsKw = ['trialNr', 'sTrial', 'eTrial', 'sMsg', 'eMsg',\
                    'esacc', 'ssacc', 'durSacc', 'ssaccX', 'ssaccY', \
                    'esaccX', 'esaccY', 'saccAmp', 'peakVelocity', \
                    'saccTraceTime', 'saccTraceX','saccTraceY',\
                    'saccTracePup', 'fixTraceTime', 'fixTraceX', 'fixTraceY', \
                    'fixTracePup','sFix', 'eFix', 'durFix', 'fixX', \
                    'fixY', 'fixPup', 'sBlink', 'eBlink', 'durBlink', \
                    'rawX', 'rawY', 'rawTime', 'rawPupSize', 'euclidDist', \
                    'curvature', 'saccAngle']
    
        # Add prefix to avoid double columns
        rawKw  = [keyPrefix + k for k in rawKw ]
        fixKw = [keyPrefix + k for k in fixKw]
        saccKw = [keyPrefix + k for k in saccKw]
        blinkKw = [keyPrefix + k for k in blinkKw]
        fixTraceKw = [keyPrefix + k for k in FixTraceKw]
        saccTraceKw = [keyPrefix + k for k in SaccTraceKw]
        prsKw = [keyPrefix + k for k in prsKw]
    
        # columns to delete from parsed dataframe
        deleteColumns = ['VALIDATE','!CAL','!MODE','ELCL','RECCFG','GAZE_COORDS',\
                     'DISPLAY_COORDS','THRESHOLDS', 'DRIFTCORRECT', 'parserDummyVar']
        
        #==============================================================================
        # Load data ASCII data to memory
        #==============================================================================
        raw = open(FILENAME, 'r').read()
        
        #==============================================================================
        # Check if \r\n is in raw, in that case replace \n in regular expression 
        # with \r (only saccade events)
        #==============================================================================
        if '\r\n' in raw:
            regEfix = regEfix[:-1]+'r'
            regEsacc = regEsacc[:-1]+'r'
            regEblink = regEblink[:-1]+'r'    
            
        #==============================================================================
        # Exract data with regular expressions then delete raw
        #==============================================================================
        # Get all samples
        rawSamples = re.findall(regSamples, raw)
        rawSamples = np.array(rawSamples, dtype = float)
        rawData = pd.DataFrame(rawSamples, columns = rawKw , dtype = 'float64')
        
        # Get fixation info
        efixData = re.findall(regEfix, raw)
        efixData = np.array(efixData, dtype = float)
        if len(efixData) == 0:
            efixData = np.array([[0 for i in range(len(fixKw))]])
        fixData = pd.DataFrame(efixData, columns = fixKw, dtype = 'float64')
        
        # Get saccade info
        esaccData = re.findall(regEsacc, raw)
        esaccData = np.array(esaccData, dtype = float)
        if len(esaccData) == 0:
            esaccData = np.array([[0 for i in range(len(saccKw))]])
        saccData = pd.DataFrame(esaccData, columns = saccKw, dtype = 'float64')
        
        # Get blink info
        blinkData = re.findall(regEblink, raw)
        blinkData = np.array(blinkData, dtype = float)
        if len(blinkData) == 0:
            blinkData = np.array([[0 for i in range(len(blinkKw))]])
        blinkData = pd.DataFrame(blinkData, columns = blinkKw, dtype = 'float64')
            
        # Get start and stop messages
        startData = re.findall(regStart, raw)
        startTimes = np.array(startData)[:,0].astype(float)
        startMsg = np.array(startData)[:,1]
        stopData = re.findall(regStop, raw)
        stopTimes = np.array(stopData)[:,0].astype(float)
        stopMsg = np.array(stopData)[:,1]
        trialNrs = np.arange(1,len(startTimes)+1)
        
        # Get variables
        varData = re.findall(regVar, raw)
        varData.append(('000000', 'var', 'parserDummyVar dummy')) 
        varData = np.array(varData)
        varTimes = np.array(varData[:,0], dtype = float)
        varKey = np.array(varData[:,1], dtype = str)
        del varKey
        varMsg = np.array(varData[:,2], dtype = str)
        
        # Handle all other messages 
        msgData = re.findall(regMsg, raw)
        msgData = np.array(msgData)
        msgTimes = np.array(msgData[:,0], dtype = float)
        msg = np.array(msgData[:,1], dtype = str)
        msgVars = deque([])
        msgVarTimes = deque([])
        delIdx = np.ones(len(msg), dtype = bool)
        for i, ms in enumerate(msg):
            msLis = ms.split()
            if len(msLis) == 2:
                msgVars.append(ms)
                msgVarTimes.append(msgTimes[i])
                delIdx[i] = False

        # Append the msgVars and msgVarTimes to the variable array
        varMsg = np.hstack((varMsg, np.array(msgVars)))
        varTimes = np.hstack((varTimes, np.array(msgVarTimes)))
        
        # Delete the excess data
        msg = msg[delIdx]
        msgTimes = msgTimes[delIdx]
        
        # Extract all unique messages
        unMSG = np.unique(msg)
        uniqueMSG = []
        for m in unMSG:
            delete = False
            for dc in deleteColumns:
                if dc in m:
                    delete = True
            if delete == False:
                uniqueMSG.append(m)
        uniqueMSGHeaders = [varPrefix+h for h in uniqueMSG]
        
        # Del raw data for speed and memory handeling
        del raw
    
        # =============================================================================
        # Prealocations and extract some info from data
        # =============================================================================   
        # Determine pixels per degree (using amplitude)
        if pxPerDegMode == 'Automatic':
            dist = distBetweenPointsInArray(saccData[saccKw[3]].values, saccData[saccKw[4]].values, saccData[saccKw[5]].values, saccData[saccKw[6]].values)
            saccAmp = saccData[saccKw[7]].values
            dist = dist[saccAmp != 0]
            saccAmp = saccAmp[saccAmp != 0]
            pixPerDegree = np.median(dist/saccAmp)
            
        elif pxPerDegMode == 'Manual':
            pixPerDegree = float(pxPerDegManual)        
        
        # Deal with the variables
        varMsg = np.array([i.split() for i in varMsg])
        varHeaders = np.array([varPrefix + i[0] for i in varMsg])
        varHeadersUnique = np.unique(varHeaders)

        # Prealocate the parsed data dataframe
        msgHeadersUniqueT = [h+'TimeStamp' for h in varHeadersUnique]
        cols = np.hstack((prsKw, varHeadersUnique, msgHeadersUniqueT, uniqueMSGHeaders))
        pData = pd.DataFrame(index = range(len(trialNrs)), columns=np.unique(cols))
        
        #==============================================================================
        # Start populating the output dataframe. 
        #==============================================================================
        # Make sure that the number of start and stop  messages match
        # NB: This assumes that if there are unequal numbers there are more stops
        if len(startTimes) != len(stopTimes):
            stopTimes = stopTimes[0:len(startTimes)]
            stopMsg = stopMsg[0:len(startTimes)]
    
        # start populating the parsed Dataframe with the values defining epochs/trials
        pData[prsKw[0]] = trialNrs # pData.trialNr
        pData[prsKw[1]] = startTimes # pData.sTrial
        pData[prsKw[2]] = stopTimes # pData.eTrial
        pData[prsKw[3]] = startMsg # pData.sMsg
        pData[prsKw[4]] = stopMsg # pData.eMsg
    
        #==============================================================================
        # Epoch all data for each trial
        #==============================================================================
        for i, (start, stop) in enumerate(zip(startTimes, stopTimes)):
            # Epoch fixations
            fixStartEpoch = np.logical_or(fixData[fixKw[0]] >= start, fixData[fixKw[1]] >= start)
            fixEndEpoch = np.logical_or(fixData[fixKw[0]] <= stop, fixData[fixKw[1]] <= stop)
            fixEpoch = fixData.loc[np.logical_and(fixStartEpoch, fixEndEpoch)]
            for key in fixKw:
                pData.at[i, key] = fixEpoch[key].values
        
            # Epoch saccades  
            saccStartEpoch = np.logical_or(saccData[saccKw[0]] >= start, saccData[saccKw[1]] >= start)
            saccStopEpoch = np.logical_or(saccData[saccKw[0]] <= stop, saccData[saccKw[1]] <= stop)
            saccEpoch   = saccData.loc[np.logical_and(saccStartEpoch, saccStopEpoch)]
            for key in saccKw:
                pData.at[i, key] = saccEpoch[key].values
            
            # Epoch blinks
            blinkEpoch  = blinkData.loc[np.logical_and(blinkData[blinkKw[0]] >= start, blinkData[blinkKw[1]] <= stop)]
            for key in blinkKw:
                pData.at[i, key] = blinkEpoch[key].values
        
            # Get the start and stop time for the trial (to include all data)
            if len(fixEpoch[fixKw[0]]) > 0 and len(saccEpoch[saccKw[0]]) > 0:
                eStart = np.min([start, fixEpoch[fixKw[0]][fixEpoch.index.min()], saccEpoch[saccKw[0]][saccEpoch.index.min()]])
                eStop = np.max([stop, fixEpoch[fixKw[1]][fixEpoch.index.max()], saccEpoch[saccKw[1]][saccEpoch.index.max()]])
            else:
                eStart = start
                eStop = stop
            epochData = rawData.loc[np.logical_and(rawData[rawKw[0]] >= eStart, rawData[rawKw[0]] <= eStop)]
            
            # Extract the raw data
            for key in rawKw:
                pData.at[i, key] = epochData[key].values
            
            # Extract fixation traces
            sFix = pData[fixKw[0]][i]
            eFix = pData[fixKw[1]][i]
            epTime = epochData[rawKw[0]].values
            fixBools = [np.logical_and(epTime >= s, epTime <= e) for (s,e) in zip(sFix, eFix)]
            for key, rKey in zip(fixTraceKw, rawKw):
                fixTraces = [epochData[rKey][b].values for b in fixBools]
                pData.at[i, key] = fixTraces
            
            # Extract Saccade traces
            sSacc = pData[saccKw[0]][i]
            eSacc = pData[saccKw[1]][i]
            saccBools = [np.logical_and(epTime >= s, epTime <= e) for (s,e) in zip(sSacc, eSacc)]
            for key, rKey in zip(saccTraceKw, rawKw):
                saccTraces = [epochData[rKey][b].values for b in saccBools]
                pData.at[i, key] = saccTraces
                    
            # Calculate euclidian distance between samples (if more than 4 samples)
            if len(pData[rawKw[1]][i]) > 4:
                p1X = np.append(pData[rawKw[1]][i],0)[:-1]
                p1Y = np.append(pData[rawKw[2]][i],0)[:-1]
                p2X = np.append(pData[rawKw[1]][i][0], pData[rawKw[1]][i])[:-1]
                p2Y = np.append(pData[rawKw[2]][i][0], pData[rawKw[2]][i])[:-1]
                pData.at[i, keyPrefix+'euclidDist'] = distBetweenPointsInArray(p1X, p1Y, p2X, p2Y)
            else:
                pData.at[i, keyPrefix+'euclidDist'] = []
                
            # Add saccade curvature
            if not np.array(pd.isnull(pData[saccTraceKw[1]][i])).all():
                curv, ang = calculateSaccadeCurvature(pData[saccTraceKw[1]][i], pData[saccTraceKw[2]][i], pixPerDegree, flipY = True)
                pData.at[i, keyPrefix+'curvature'] = [np.median(sacc) for sacc in curv]
                pData.at[i, keyPrefix+'saccAngle'] = ang
               
            # Epoch variables
            varBool = np.logical_and(varTimes >= start, varTimes <= stop)
            varEpochT = varTimes[varBool]
            varEpochMsg = varMsg[varBool]
            varEpochHead= varHeaders[varBool]
            for it, (times, key) in enumerate(izip(varEpochT, varEpochHead)):
                if len(varEpochMsg[it]) == 1:
                    pData.at[i,key] = 'NA'
                elif len(varEpochMsg[it]) == 2:
                    pData.at[i,key] = varEpochMsg[it][1]
                elif len(varEpochMsg[it]) > 2:
                    pData.at[i,key] = varEpochMsg[it][1:]
                pData.at[i,key+'TimeStamp'] = times
    
            # Epoch messages
            msgBool = np.logical_and(msgTimes >= start, msgTimes <= stop)
            msgEpochT = msgTimes[msgBool]
            msgEpoch = msg[msgBool]
            for times, key in izip(msgEpochT, msgEpoch):
                if key in uniqueMSG:
                    pData.at[i,varPrefix+key] = times
                
        # =============================================================================
        # Add included trial column
        # =============================================================================
        pData[keyPrefix+'includedTrial'] = True

        # Filter the columns we dont want
        pData = filterDF(pData, deleteColumns)
        pData.columns = pData.columns.str.replace("\r", '')
        
        # Turn values into numeric if possible
        for k in pData.keys():
            pData[k] = pd.to_numeric(pData[k], errors = 'ignore')
        
        # Convert data to long format
        if convertToLong == 'Yes':
            parsedLong = parseToLongFormat(pData, duplicateValues)
        else:
            parsedLong = False
            
        # No error
        error = False
        
    except:# Exception as e: 
        pData = False
        rawData = False
        parsedLong = False
        error = traceback.format_exc()
        
    return FILENAME, pData, rawData, parsedLong, error



