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

import matplotlib.pyplot as plt
import numpy as np
import astropy.convolution as krn
from matplotlib import cm
import matplotlib.patches as patches
import traceback

def uniqueRows(x):
    y = np.ascontiguousarray(x).view(np.dtype((np.void, x.dtype.itemsize * x.shape[1])))
    _, idx, counts = np.unique(y, return_index=True, return_counts = True)     
    uniques = x[idx]
    return uniques, idx, counts

def plotTrial(timeStamp, xPos, yPos, euclidDist, **par):
    try:
        # Get constants
        pltType = par.pop('pltType','gaze') # options: 'gaze', 'heat'
        pltStyle = par.pop('pltStyle', 'Scatter') # scatter or line
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
        kernelAlpha = par.pop('kernelAlpha', 0.50)
        xMax = par.pop('xMax', 1680)
        xMin = par.pop('xMin', 0)
        yMax = par.pop('yMax', 1050)
        yMin = par.pop('yMin', 0)
        included = par.pop('included', 'True')
        highlight = par.pop('highlight', 'None')
        addLabel = str(par.pop('addLabel', False))
        addInfo = str(par.pop('addInfo', False))
        xLabel = par.pop('xLabel', 'Pixel position')
        ylabel = par.pop('yLabel', 'Pixel position')
        speedLabel = par.pop('speedLabel', 'Speed')
        figAx = par.pop('figAx', False)
      
        if highlight == 'Saccade':
            sHighL = par.pop('ssacc')
            durHighL = par.pop('saccDur')
        elif highlight == 'Fixation':
            sHighL = par.pop('sFix')
            durHighL = par.pop('fixDur')
        elif highlight == 'None':
            sHighL = par.pop('sFix', [])
            durHighL = par.pop('fixDur', [])
            
        #==========================================================================
        # Plotting
        #==========================================================================
        #recalculateTime to zero for each trial
        trialStart = timeStamp[0]
        normTime = timeStamp - trialStart
        if len(normTime) == len(xPos):
            xTime = normTime
        else:
            xTime = np.arange(len(xPos))

        # lets plot x position over time
        ax1 = figAx[1]
        ax1.set_title('Xgaze(time)')
        ax1.set_ylabel(xLabel)
        ax1.set_ylim([xMin,xMax])
        if pltStyle == 'Line':
            ax1.plot(xTime, xPos)
        elif pltStyle == 'Scatter':
            ax1.scatter(xTime, xPos,marker = 'p', s = 1)
        ax1.set_xlim([xTime[0], xTime[-1]])
        if highlight != 'None':
            # Add rectangles for Saccades
            for i in range(0,len(sHighL)):
                ax1.add_patch(patches.Rectangle((sHighL[i] - trialStart, ax1.get_ylim()[0]),
                                               durHighL[i],
                                               abs(ax1.get_ylim()[1] - ax1.get_ylim()[0]),
                                               fill=True, alpha = 0.3))
    
        # lets plot y position over time
        if len(normTime) == len(yPos):
            yTime = normTime
        else:
            yTime = np.arange(len(yPos))
        ax2 = figAx[2]
        ax2.set_title('Ygaze(time)')
        ax2.set_ylabel(ylabel)
        ax2.set_ylim([yMin,yMax])
        if pltStyle == 'Line':
            ax2.plot(yTime, yPos)
        elif pltStyle == 'Scatter':
            ax2.scatter(yTime, yPos, marker = 'p', s = 1)
        ax2.set_xlim([yTime[0], yTime[-1]])
        if highlight != 'None':
            # Add rectangles for Saccades
            for i in range(0,len(sHighL)):
                ax2.add_patch(patches.Rectangle((sHighL[i] - trialStart, ax2.get_ylim()[0]),
                                               durHighL[i],
                                               abs(ax2.get_ylim()[1] - ax2.get_ylim()[0]),
                                               fill=True, alpha = 0.3))
    
        # Lets plot speed over time (distance between points)
        if len(normTime) == len(euclidDist):
            speedTime = normTime
        else:
            speedTime = np.arange(len(euclidDist))
        ax3 = figAx[3]
        ax3.set_title('Speed(time)')
        ax3.set_xlabel('Time (ms)')
        ax3.set_ylabel(speedLabel)
        if pltStyle == 'Line':
            ax3.plot(speedTime, euclidDist)
        elif pltStyle == 'Scatter':        
            ax3.scatter(speedTime, euclidDist, marker = 'p', s = 1)
        ax3.set_xlim([speedTime[0], speedTime[-1]])
        ax3.set_ylim([np.min(euclidDist)-20,np.max(euclidDist)+20])
        if highlight != 'None':
            # Add rectangles for Saccades
            for i in range(0,len(sHighL)):
                ax3.add_patch(patches.Rectangle((sHighL[i] - trialStart, ax3.get_ylim()[0]),
                                               durHighL[i],
                                               abs(ax3.get_ylim()[1] - ax3.get_ylim()[0]),
                                               fill=True, alpha = 0.3))
    
        # Lets get make a timeseries to plot over time.
        timeCol = np.linspace(1,0,len(xPos))
        # Lets plot the gaze position during trial
        ax4 = figAx[4]
        ax4.set_title('Gaze position')
        ax4.set_xlabel('X position (px)')
        ax4.set_ylabel('Y position (px)')
        ax4.axis([xMin, xMax, yMin, yMax])
        if pltType == 'gaze':
            if pltBg == True:
                bgIm = plt.imread(bgImLoc)
                ax4.imshow(np.flipud(bgIm), aspect=bgAspect, extent = [xMin, xMax, yMin, yMax])
                if pltStyle == 'Line':
                        ax4.plot(xPos, yPos)
                elif pltStyle == 'Scatter':
                    ax4.scatter(xPos, yPos, c = timeCol, edgecolors = 'face', marker = 'p', s = 5, cmap = 'hot')
            else:
                if pltStyle == 'Line':
                    ax4.plot(xPos, yPos)
                elif pltStyle == 'Scatter':
                    ax4.scatter(xPos, yPos,c = timeCol, edgecolors = 'face', marker = 'p', s = 5, cmap='hot')            
            ax4.set(aspect = bgAspect)
    
        elif pltType == 'heat' :
            #======================================================================
            # Make gaussian image
            #======================================================================
            if pltBg == True:
                bgIm = plt.imread(bgImLoc)
                ax4.imshow(np.flipud(bgIm), aspect=bgAspect, extent = [xMin, xMax, yMin, yMax])
            kernelPar = kernelPar/float(dataScaling)
            xlim = np.logical_and(xPos < xMax, xPos > xMin)
            ylim = np.logical_and(yPos < yMax, yPos > yMin)
            xyLim = np.logical_and(xlim, ylim)
            dataX = xPos[xyLim]/dataScaling
            dataX = np.floor(dataX)
            dataY = yPos[xyLim]/dataScaling
            dataY = np.floor(dataY)
    
            # initiate map and gauskernel
            gazeMap = np.zeros([(xMax-xMin)/dataScaling,(yMax-yMin)/dataScaling])+0.001
            gausKernel = eval('krn.'+kernel)(kernelPar)
            
            # Rescale the position vectors (if xmin or ymin != 0)
            dataX -= xMin
            dataY -= yMin
            
            # Now extract all the unique positions and number of samples
            xy = np.vstack((dataX, dataY)).T
            uniqueXY, idx, counts = uniqueRows(xy)       
            uniqueXY = uniqueXY.astype(int)
            # populate the gazeMap 
            gazeMap[uniqueXY[:,0], uniqueXY[:,1]] = counts
                        
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
            ax4.imshow(newHeatmap, cmap=cmap, extent=[xMin,xMax,yMin,yMax], alpha = kernelAlpha, aspect=bgAspect)
        # invert Axis
        ax4.invert_yaxis()
        pltTitle = 'Plotting trial: ' + str(trial+1) + ', index number: ' + str(trial)+'\nIncluded: '+included
        if addLabel != 'False':
            pltTitle += '\n'+addLabel+': '+addInfo
        fig = figAx[0]
        fig.suptitle(pltTitle)
        return fig, ax1, ax2, ax3, ax4
    except:
        ax4 = figAx[4]
        ax4.clf()
        ax4.set_title('Error, try different settings!')
        print traceback.format_exc()
        return fig
        

