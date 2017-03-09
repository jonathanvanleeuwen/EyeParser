# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 18:02:49 2017

@author: JonLee
"""
#==============================================================================
# Eyelink data plotter
#==============================================================================
# Add (to gui):
#   Option to select potting of (in gaze map):
#       start saccades
#       end saccades
#       Saccade traces
#
#       fixation start
#       fixation end
#       fixation trace
#
#       All trial data
#
# Color:
#   Color option for lines and saccades (later)
#
# Bug fix:
# The scalling when using differetnt x/y values in imshow(gauss)

# Import modules
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import izip
import astropy.convolution as krn
from matplotlib import cm
import matplotlib.patches as patches

#fileLoc= 'D:\Work\PhD Vu\Project 6 - PredictableJump\Testing\\'
#fn = 'PP1S1Parsed.p'
#imLoc = 'D:\Work\DivCode\Python experiment codes\GUI testing\\testImage.png'
#
## Get data
#data = pd.read_pickle(fileLoc+fn)

## Constants
#trNr = 55
#pltTypeList = ['heat', 'gaze']
#bgAspectList = ['auto', 'equal']
#cmapList = ['Accent', 'Blues', 'BrBG', 'BuGn', 'BuPu', 'CMRmap', 'Dark2',
#            'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PRGn', 'Paired',
#            'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd',
#            'Purples', 'RdBu', 'RdGy', 'RdPu', 'RdYlBu', 'RdYlGn', 'Reds',
#            'Set1', 'Set2', 'Set3', 'Spectral', 'Wistia', 'YlGn', 'YlGnBu',
#            'YlOrBr', 'YlOrRd', 'afmhot', 'autumn', 'binary', 'bone', 'brg',
#            'bwr', 'cool', 'coolwarm', 'copper', 'cubehelix', 'flag',
#            'gist_earth', 'gist_gray', 'gist_heat', 'gist_ncar',
#            'gist_rainbow', 'gist_stern', 'gist_yarg', 'gnuplot', 'gnuplot2',
#            'gray', 'hot', 'hsv', 'inferno', 'jet', 'magma', 'nipy_spectral',
#            'ocean', 'pink', 'plasma', 'prism', 'rainbow', 'seismic', 'spec',
#            'spectral',	'spring', 'summer', 'terrain', 'viridis', 'winter']
#kernelList = ['AiryDisk2DKernel', 'Box2DKernel', 'Gaussian2DKernel',
#              'MexicanHat2DKernel', 'Tophat2DKernel', 'TrapezoidDisk2DKernel']
#kernelParList = ['Radius', 'Width', 'STD', 'Width', 'Radius', 'Radius']
#dataScalingList = range(1,21)
#
#par ={\
#    'pltType': pltTypeList[0],\
#    'pltBg': True,\
#    'bgImage': imLoc,\
#    'bgAspect': bgAspectList[1],\
#    'trial': trNr,\
#    'dataScaling': dataScalingList[0],\
#    'kernel': kernelList[2],\
#    'kernelPar': 30,\
#    'kernelCM': cmapList[25],\
#    'kernelCMInverse': False,\
#    'kernelThreshold': 0.01,\
#    'alpha': 0.75,\
#    'xMax': 1680,\
#    'xMin': 0,\
#    'yMax': 1050,\
#    'yMin': 0}
#
#time =  data.DK_rawTime[trNr]
#x= data.DK_rawX[trNr]
#y = data.DK_rawY[trNr]
#ssacc =  data.DK_ssacc[trNr]
#saccDur = data.DK_durSacc[trNr]
#euclidDist = data.DK_euclidDist[trNr]

def plotTrial(timeStamp, xPos, yPos, ssacc, durSacc, euclidDist, **par):
    # Get constants
    pltType = par.pop('pltType','gaze') # options: 'gaze', 'heat'
    pltBg = par.pop('pltBg', False)
    bgImLoc = par.pop('bgImage' , False)
    bgAspect = par.pop('bgAspect', 'equal') # 'auto','equal'
    trial = par.pop('trial', 48)
    dataScaling = par.pop('dataScaling', 5)
    kernel = par.pop('kernel', 'Gaussian2DKernel')
    kernelPar = par.pop('kernelPar', 25)
    kernelCM = par.pop('kernelCM', 'hot')
    kernelCMInverse = par.pop('kernelCMInverse', False)
    kernelThreshold = par.pop('kernelThreshold', 0.3)
    kernelAlpha = par.pop('kernelAlpha', 0.75)
    xMax = par.pop('xMax', 1680)
    xMin = par.pop('xMin', 0)
    yMax = par.pop('yMax', 1050)
    yMin = par.pop('yMin', 0)

    #==========================================================================
    # Plotting
    #==========================================================================
    #recalculateTime to zero for each trial
    trialStart = timeStamp[0]
    normTime = timeStamp - trialStart
    plt.figure(2)
    plt.clf()
    plt.title('Raw trial Data')
    # lets plot x position over time
    plt.subplot(3,2,1)
    plt.title('Xgaze(time)')
    plt.ylabel('Pixel position')
    plt.ylim([xMin,xMax])
    plt.scatter(normTime, xPos,marker = 'p', s = 1)
    plt.xlim([normTime[0], normTime[-1]])
    ax = plt.gca()
    # Add rectangles for Saccades
    for i in range(0,len(ssacc)):
        ax.add_patch(patches.Rectangle((ssacc[i] - trialStart, ax.get_ylim()[0]),
                                       durSacc[i],
                                       abs(ax.get_ylim()[1] - ax.get_ylim()[0]),
                                       fill=True, alpha = 0.3))

    # lets plot y position over time
    plt.subplot(3,2,3)
    plt.title('Ygaze(time)')
    plt.ylabel('Pixel position')
    plt.ylim([yMin,yMax])
    plt.scatter(normTime, yPos, marker = 'p', s = 1)
    plt.xlim([normTime[0], normTime[-1]])
    ax = plt.gca()
    # Add rectangles for Saccades
    for i in range(0,len(ssacc)):
        ax.add_patch(patches.Rectangle((ssacc[i] - trialStart, ax.get_ylim()[0]),
                                       durSacc[i],
                                       abs(ax.get_ylim()[1] - ax.get_ylim()[0]),
                                       fill=True, alpha = 0.3))

    # Lets plot speed over time (distance between points)
    plt.subplot(3,2,5)
    plt.title('Speed(time)')
    plt.xlabel('Time (ms)')
    plt.ylabel('Distance between samples (pixels)')
    plt.scatter(normTime, euclidDist, marker = 'p', s = 1)
    plt.xlim([normTime[0], normTime[-1]])
    plt.ylim([0,np.max(euclidDist)])
    ax = plt.gca()
    # Add rectangles for Saccades
    for i in range(0,len(ssacc)):
        ax.add_patch(patches.Rectangle((ssacc[i] - trialStart, ax.get_ylim()[0]),
                                       durSacc[i],
                                       abs(ax.get_ylim()[1] - ax.get_ylim()[0]),
                                       fill=True, alpha = 0.3))

    # Lets plot the gaze position during trial
    plt.subplot(1,2,2)
    plt.title('Gaze position')
    plt.xlabel('X position (px)')
    plt.ylabel('Y position (px)')
    ax = plt.gca()
    plt.axis([xMin, xMax, yMin, yMax])
    if pltType == 'gaze':
        if pltBg == True:
            bgIm = plt.imread(bgImLoc)
            plt.imshow(bgIm, aspect=bgAspect)
            plt.scatter(xPos, yPos, marker = 'p', s = 5, color = 'r')
        plt.scatter(xPos, yPos, marker = 'p', s = 1)
        ax.set(aspect = bgAspect)
    elif pltType == 'heat' :
        #======================================================================
        # Make gaussian image
        #======================================================================
        if pltBg == True:
            bgIm = plt.imread(bgImLoc)
            plt.imshow(bgIm, aspect=bgAspect)
        kernelPar = kernelPar/float(dataScaling)
        xlim = np.logical_and(xPos < xMax, xPos > xMin)
        ylim = np.logical_and(yPos < yMax, yPos > yMin)
        xyLim = np.logical_and(xlim, ylim)
        dataX = xPos[xyLim]/dataScaling
        dataX = np.floor(dataX)
        dataY = yPos[xyLim]/dataScaling
        dataY = np.floor(dataY)

        # initiate map and gauskernel
        gazeMap = np.zeros([(xMax-xMin)/dataScaling,(yMax-yMin)/dataScaling])
        gausKernel = eval('krn.'+kernel)(kernelPar)
        
        # Rescale the position vectors (if xmin or ymin != 0)
        dataX -= xMin
        dataY -= yMin
        
        # populate map
        maxXMap = int(gazeMap.shape[0])
        maxYMap = int(gazeMap.shape[1])
        for x,y in izip(dataX, dataY):
            # make sure the indexes fit the map
            if x >= maxXMap:
                x = maxXMap-1
            if y >= maxYMap:
                y = maxYMap-1
            gazeMap[int(x), int(y)] += 1
        # Convolve the gaze with the gauskernel
        if dataScaling == 1:
            heatMap = np.transpose(krn.convolve_fft(gazeMap,gausKernel))
        else:
            heatMap = np.transpose(krn.convolve(gazeMap,gausKernel))
        heatMap = heatMap/np.max(heatMap)
        newHeatmap = np.repeat(np.repeat(heatMap,dataScaling, axis=0), dataScaling, axis=1)
        newHeatmap = np.ma.masked_where(newHeatmap <= kernelThreshold, newHeatmap)
        newHeatmap = np.flipud(newHeatmap)
        
        # get colormap
        if kernelCMInverse == True:
            cmap = eval('cm.'+kernelCM+'_r')
        else:
            cmap = eval('cm.'+kernelCM)
        # plot
        plt.imshow(newHeatmap, cmap=cmap, extent=[xMin,xMax,yMin,yMax], alpha = kernelAlpha, aspect=bgAspect)
    # invert Axis
    ax.invert_yaxis()
    plt.suptitle('Plotting trial: ' + str(trial+1) + ', index number: ' + str(trial))
    plt.draw()

#plotTrial(time, x, y, ssacc, saccDur, euclidDist, **par)
#s = time.time()
#plotTrial(**par)
#print 'Time:', time.time() - s
#
