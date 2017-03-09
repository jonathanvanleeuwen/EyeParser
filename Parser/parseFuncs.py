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

#==============================================================================
#  Parser
#==============================================================================
def parseWrapper(f, kwargs):
    results = eyeLinkDataParser(f, **kwargs)
    return results

def eyeLinkDataParser(FILENAME, **par):
    #==========================================================================
    # Define regular expressions for data extraction
    #==========================================================================
    regSamples          = par.pop('regExpSamp', r'(\d{3,12})\t\s+(\d+\..)\t\s+(\d+\..)\t\s+(\d+\..).+\n')
    regEfix             = par.pop('regExpEfix', r'EFIX\s+[LR]\s+(\d+)\t(\d+)\t(\d+)\t\s+(.+)\t\s+(.+)\t\s+(\d+)\n')
    regEsacc            = par.pop('regExpEsacc', r'ESACC\s+[LR]\s+(\d+)\t(\d+)\t(\d+)\t\s+(\d+.?\d+)\t\s+(\d+.?\d+)\t\s+(\d+.?\d+)\t\s+(\d+.?\d+)\t\s+(\d+.?\d+)\t\s+(\d+)\n')
    regEblink           = par.pop('regExpEblink', r'EBLINK\s+[LR]\s+(\d+)\t(\d+)\t(\d+)\n')
    # Makes experiment specific expressions for var/start and stop
    var                 = par.pop('variableKey', 'var')
    startTrial          = par.pop('startTrialKey', 'start_trial')
    stopTrial           = par.pop('stopTrialKey', 'stop_trial')
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
        regVar = 'MSG\\t(\d+)\s+('+var+')\s+(.+)[\s+]?.*\\n'
    # RegExp for messages
    if par.pop('regExpMsgNew', False) == True:
        regMsg = par.pop('regExpMsg')
    else:
        regMsg = 'MSG\\t(\d+)\s+(?!'+var+'|'+startTrial+'|'+stopTrial+')(.+)[\s+]?.*\\n'

    # Get px per degree settings
    pxPerDegMode = par.pop('pxMode', 'Automatic')
    pxPerDegManual = par.pop('pxPerDeg', 48)
    
    #==============================================================================
    # Define keywords
    #==============================================================================
    keyPrefix = 'DK_'
    varPrefix = 'DV_'
    rawKw = ['rawTime','rawX','rawY','rawPupSize']
    newRawKw = ['timeStamp','xPos','yPos','pupSize']
    fixKw = ['sFix','eFix','durFix','fixX', 'fixY', 'fixPup']
    saccKw = ['ssacc','esacc','durSacc','ssaccX', 'ssaccY', 'esaccX', 'esaccY', 'saccAmp', 'peakVelocity']
    blinkKw = ['sBlink','eBlink','durBlink']
    fixTraceKw = rawKw [:]
    newFixTraceKw = ['fixTraceTime', 'fixTraceX', 'fixTraceY', 'fixTracePup']
    saccTraceKw = rawKw [:]
    newSaccTraceKw= ['saccTraceTime', 'saccTraceX', 'saccTraceY', 'saccTracePup']
    prsKw = ['trialNr', 'sTrial', 'eTrial', 'sMsg', 'eMsg',\
                'esacc', 'ssacc', 'durSacc', 'ssaccX', 'ssaccY', 'esaccX', \
                'esaccY', 'saccAmp', 'peakVelocity', 'saccTraceTime', 'saccTraceX','saccTraceY',\
                'saccTracePup','sFix', 'eFix', 'durFix', 'fixX', \
                'fixY', 'fixPup', 'sBlink', 'eBlink', 'durBlink', \
                'rawX', 'rawY' , 'rawTime', 'rawPupSize', 'euclidDist', 'curvature', 'saccAngle']

    # Add prefix to avoid double columns
    rawKw  = [keyPrefix + k for k in rawKw ]
    newRawKw = [keyPrefix + k for k in newRawKw]
    fixKw = [keyPrefix + k for k in fixKw]
    saccKw = [keyPrefix + k for k in saccKw]
    blinkKw = [keyPrefix + k for k in blinkKw]
    fixTraceKw = [keyPrefix + k for k in fixTraceKw]
    newFixTraceKw = [keyPrefix + k for k in newFixTraceKw]
    saccTraceKw = [keyPrefix + k for k in saccTraceKw]
    newSaccTraceKw = [keyPrefix + k for k in newSaccTraceKw]
    prsKw = [keyPrefix + k for k in prsKw]

    #==============================================================================
    # Load data ASCII data to memory
    #==============================================================================
    raw = open(FILENAME, 'r').read()

    #==============================================================================
    # Exract data with regular expressions then delete raw
    #==============================================================================
    # Get all samples
    rawSamples          = re.findall(regSamples, raw)
    rawSamples          = np.array(rawSamples, dtype = float)
    # Get fixation info
    efixData            = re.findall(regEfix, raw)
    efixData            = np.array(efixData, dtype = float)
    # Get saccade info
    esaccData           = re.findall(regEsacc, raw)
    esaccData           = np.array(esaccData, dtype = float)
    # Get blink info
    blinkData           = re.findall(regEblink, raw)
    blinkData           = np.array(blinkData, dtype = float)
    # Get start and stop messages
    startData           = re.findall(regStart, raw)
    startTimes          = np.array(startData)[:,0].astype(float)
    startMsg            = np.array(startData)[:,1]
    stopData            = re.findall(regStop, raw)
    stopTimes           = np.array(stopData)[:,0].astype(float)
    stopMsg             = np.array(stopData)[:,1]
    trialNrs            = np.arange(1,len(startTimes)+1)
    # Get variables
    varData             = re.findall(regVar, raw)
    varData             = np.array(varData)
    varTimes            = np.array(varData[:,0], dtype = float)
    varKey              = np.array(varData[:,1], dtype = str)
    del varKey
    varMsg              = np.array(varData[:,2], dtype = str)
    # Get messages
    msgData             = re.findall(regMsg, raw)
    msgData             = np.array(msgData)
    msgTimes            = np.array(msgData[:,0], dtype = float)
    msg                 = np.array(msgData[:,1], dtype = str)

    # Del raw data for speed and memory handeling
    del raw

    #==============================================================================
    # Put data into pandas dataframes for easy data extraction
    #==============================================================================
    rawData             = pd.DataFrame(rawSamples,  columns = rawKw , dtype = 'float64')
    fixData             = pd.DataFrame(efixData,    columns = fixKw, dtype = 'float64')
    saccData            = pd.DataFrame(esaccData,   columns = saccKw, dtype = 'float64')
    blinkData           = pd.DataFrame(blinkData,   columns = blinkKw, dtype = 'float64')
    parsedData          = pd.DataFrame(index = xrange(0,len(trialNrs)),columns = prsKw)

    # Make sure that the number of start and stop  messages match
    # NB: This assumes that if there are unequal numbers there are more stops
    if len(startTimes) != len(stopTimes):
        stopTimes = stopTimes[0:len(startTimes)]
        stopMsg = stopMsg[0:len(startTimes)]

    # start populating the parsed Dataframe with the values defining epochs/trials
    parsedData[prsKw[0]] = trialNrs # parsedData.trialNr
    parsedData[prsKw[1]] = startTimes # parsedData.sTrial
    parsedData[prsKw[2]] = stopTimes # parsedData.eTrial
    parsedData[prsKw[3]] = startMsg # parsedData.sMsg
    parsedData[prsKw[4]] = stopMsg # parsedData.eMsg

    #==============================================================================
    # Extract all trial data
    #==============================================================================
    # Create placeholders
    rawDict             = {key: [] for key in rawKw}
    fixDict             = {key: [] for key in fixKw}
    saccDict            = {key: [] for key in saccKw}
    blinkDict           = {key: [] for key in blinkKw}
    fixTraceDict        = {key: [] for key in fixTraceKw}
    saccTraceDict       = {key: [] for key in saccTraceKw}
    euclidDistance      = deque([])
    saccCurvature       = deque([])
    saccAngles          = deque([])

    # Create placeholders to deal with the variables sent to the eye-tracker
    varBools            = np.logical_and(varTimes >= startTimes[0], varTimes <= stopTimes[-1])
    varTimes            = varTimes[varBools]
    varMsg              = np.array([i.split() for i in varMsg[varBools]])
    msgHeaders          = np.array([varPrefix + i[0] for i in varMsg])
    msgHeadersUnique    = np.unique(msgHeaders)
    varLists            = np.zeros([len(parsedData[prsKw[1]]),], dtype = bool)
    varDict             = {key:deque(varLists) for key in msgHeadersUnique}
    varDict.update({key+'TimeStamp':deque(varLists) for key in msgHeadersUnique})

    # Create variables to deal with the sent messages
    msgUnique           = np.unique(msg)
    msgLists            = np.zeros([len(parsedData[prsKw[1]]),], dtype = bool)
    msgDict             = {varPrefix+key:deque(msgLists) for key in msgUnique}

    # Determine pixels per degree (using amplitude)
    if pxPerDegMode == 'Automatic':
        dist                = np.sqrt( (saccData[saccKw[3]].values-saccData[saccKw[5]].values)**2 + (saccData[saccKw[4]].values - saccData[saccKw[6]].values)**2 )
        pixPerDegree        = np.median(dist/saccData[saccKw[7]].values)
    elif pxPerDegMode == 'Manual':
        pixPerDegree = float(pxPerDegManual)
        
    #==============================================================================
    # Itterate through all trials (this is a huge time thief)
    # Spesificaly running through all saccades and fixations geting the
    # saccade and fixation traces take a whole lot of time
    #==============================================================================
    for i, (start, stop) in enumerate(izip(parsedData[prsKw[1]], parsedData[prsKw[2]])):
        # Epoch fixations
        fixStartEpoch = np.logical_or(fixData[fixKw[0]] >= start, fixData[fixKw[1]] >= start)
        fixEndEpoch = np.logical_or(fixData[fixKw[0]] <= stop, fixData[fixKw[1]] <= stop)
        fixEpoch    = fixData.loc[np.logical_and(fixStartEpoch, fixEndEpoch)]
        for key in fixDict:
            fixDict[key].append(fixEpoch[key].values)
            
        # Epoch saccades  
        saccStartEpoch = np.logical_or(saccData[saccKw[0]] >= start, saccData[saccKw[1]] >= start)
        saccStopEpoch = np.logical_or(saccData[saccKw[0]] <= stop, saccData[saccKw[1]] <= stop)
        saccEpoch   = saccData.loc[np.logical_and(saccStartEpoch, saccStopEpoch)]
        #saccEpoch   = saccData.loc[np.logical_and(saccData[saccKw[0]] >= start, saccData[saccKw[0]] <= stop)]
        for key in saccDict:
            saccDict[key].append(saccEpoch[key].values)

        # Epoch blinks
        blinkEpoch  = blinkData.loc[np.logical_and(blinkData[blinkKw[0]] >= start, blinkData[blinkKw[1]] <= stop)]
        for key in blinkDict:
            blinkDict[key].append(blinkEpoch[key].values)

        # First we extract the raw samples for each trial (to include all data)
        if len(fixEpoch[fixKw[0]]) > 0 and len(saccEpoch[saccKw[0]]) > 0:
            eStart = np.min([start, fixEpoch[fixKw[0]][fixEpoch.index.min()], saccEpoch[saccKw[0]][saccEpoch.index.min()]])
            eStop = np.max([stop, fixEpoch[fixKw[1]][fixEpoch.index.max()], saccEpoch[saccKw[1]][saccEpoch.index.max()]])
        else:
            eStart = start
            eStop = stop
        epochData   = rawData.loc[np.logical_and(rawData[rawKw[0]] >= eStart, rawData[rawKw[0]] <= eStop)]
        for key in rawDict:
            rawDict[key].append(epochData[key].values)
            fixTraceDict[key].append(deque([]))
            for sFix, eFix in izip(fixDict[fixKw[0]][-1], fixDict[fixKw[1]][-1]):
                fixTraceDict[key][-1].append(epochData[key][np.logical_and(epochData[rawKw[0]].values >= sFix, epochData[rawKw[0]].values <= eFix)].values)

            # Get saccade traces
            saccTraceDict[key].append(deque([]))
            for ssacc, esacc in izip(saccDict[saccKw[0]][-1], saccDict[saccKw[1]][-1]):
                saccTraceDict[key][-1].append(epochData[key][np.logical_and(epochData[rawKw[0]].values >= ssacc, epochData[rawKw[0]].values <= esacc)].values)
                # Delete empty lists
                if len(saccTraceDict[key][-1][-1]) == 0:
                    del saccTraceDict[key][-1][-1]
                                        
        # Calculate euclidian distance between samples (if more than 4 samples)
        if len(rawDict[rawKw[1]][-1]) > 1:
            p1X         = np.append(rawDict[rawKw[1]][-1], 0)[:-1]
            p1Y         = np.append(rawDict[rawKw[2]][-1], 0)[:-1]
            p2X         = np.append(rawDict[rawKw[1]][-1][0], rawDict[rawKw[1]][-1])[:-1]
            p2Y         = np.append(rawDict[rawKw[2]][-1][0], rawDict[rawKw[2]][-1])[:-1]
            euclidDistance.append(distBetweenPointsInArray(p1X, p1Y, p2X, p2Y))
        else:
            euclidDistance.append([])

        # Add saccade curvature
        curv, ang = calculateSaccadeCurvature(saccTraceDict[saccTraceKw[1]][-1], saccTraceDict[saccTraceKw[2]][-1], pixPerDegree, flipY = True)
        saccCurvature.append([np.median(sacc) for sacc in curv])
        saccAngles.append(ang)
        
        # Epoch variables
        varBool     = np.logical_and(varTimes >= start, varTimes <= stop)
        varEpochT   = varTimes[varBool]
        varEpochMsg = varMsg[varBool]
        varEpochHead= msgHeaders[varBool]
        for it, (times, key) in enumerate(izip(varEpochT, varEpochHead)):
            if len(varEpochMsg[it]) == 1:
                varDict[key][i] = 'NA'
            elif len(varEpochMsg[it]) == 2:
                varDict[key][i] = varEpochMsg[it][1]
            elif len(varEpochMsg[it]) > 2:
                varDict[key][i] = varEpochMsg[it][1:]
            varDict[key+'TimeStamp'][i] = times

        # Epoch messages
        msgBool     = np.logical_and(msgTimes >= start, msgTimes <= stop)
        msgEpochT   = msgTimes[msgBool]
        msgEpoch    = msg[msgBool]
        for times, key in izip(msgEpochT, msgEpoch):
            msgDict[varPrefix+key][i] = times

    #==============================================================================
    # Populate the parsed data dataframe
    #==============================================================================
    for key in rawDict:
        parsedData[key] = rawDict[key]
    for key in fixDict:
        parsedData[key] = fixDict[key]
    for key in saccDict:
        parsedData[key] = saccDict[key]
    for key in blinkDict:
        parsedData[key] = blinkDict[key]
    for oldKey, newKey in izip(fixTraceKw, newFixTraceKw):
        parsedData[newKey] = fixTraceDict[oldKey]
    for oldKey, newKey in izip(saccTraceKw, newSaccTraceKw):
        parsedData[newKey] = saccTraceDict[oldKey]
    parsedData[keyPrefix+'euclidDist'] = euclidDistance
    parsedData[keyPrefix+'curvature'] = saccCurvature
    parsedData[keyPrefix+'saccAngle'] = saccAngles
    parsedData[keyPrefix+'includedTrial'] = True
    
    varDf   = pd.DataFrame(varDict)
    msgDf   = pd.DataFrame(msgDict)
    parsedData = pd.concat([parsedData, varDf, msgDf], axis=1)
    rawData.rename(columns=dict(zip(rawKw , newRawKw)), inplace=True)

    return FILENAME, parsedData, rawData