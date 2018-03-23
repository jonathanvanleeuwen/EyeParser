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
        fig = plt.figure(2)
        plt.clf()
        plt.title('Raw trial Data')
        # lets plot x position over time
        ax1 = plt.subplot(3,2,1)
        plt.title('Xgaze(time)')
        plt.ylabel(xLabel)
        plt.ylim([xMin,xMax])
        if pltStyle == 'Line':
            plt.plot(xTime, xPos)
        elif pltStyle == 'Scatter':
            plt.scatter(xTime, xPos,marker = 'p', s = 1)
        plt.xlim([xTime[0], xTime[-1]])
        ax = plt.gca()
        if highlight != 'None':
            # Add rectangles for Saccades
            for i in range(0,len(sHighL)):
                ax.add_patch(patches.Rectangle((sHighL[i] - trialStart, ax.get_ylim()[0]),
                                               durHighL[i],
                                               abs(ax.get_ylim()[1] - ax.get_ylim()[0]),
                                               fill=True, alpha = 0.3))
    
        # lets plot y position over time
        if len(normTime) == len(yPos):
            yTime = normTime
        else:
            yTime = np.arange(len(yPos))
        ax2 = plt.subplot(3,2,3)
        plt.title('Ygaze(time)')
        plt.ylabel(ylabel)
        plt.ylim([yMin,yMax])
        if pltStyle == 'Line':
            plt.plot(yTime, yPos)
        elif pltStyle == 'Scatter':
            plt.scatter(yTime, yPos, marker = 'p', s = 1)
        plt.xlim([yTime[0], yTime[-1]])
        ax = plt.gca()
        if highlight != 'None':
            # Add rectangles for Saccades
            for i in range(0,len(sHighL)):
                ax.add_patch(patches.Rectangle((sHighL[i] - trialStart, ax.get_ylim()[0]),
                                               durHighL[i],
                                               abs(ax.get_ylim()[1] - ax.get_ylim()[0]),
                                               fill=True, alpha = 0.3))
    
        # Lets plot speed over time (distance between points)
        if len(normTime) == len(euclidDist):
            speedTime = normTime
        else:
            speedTime = np.arange(len(euclidDist))
        ax3 = plt.subplot(3,2,5)
        plt.title('Speed(time)')
        plt.xlabel('Time (ms)')
        plt.ylabel(speedLabel)
        if pltStyle == 'Line':
            plt.plot(speedTime, euclidDist)
        elif pltStyle == 'Scatter':        
            plt.scatter(speedTime, euclidDist, marker = 'p', s = 1)
        plt.xlim([speedTime[0], speedTime[-1]])
        plt.ylim([np.min(euclidDist)-20,np.max(euclidDist)+20])
        ax = plt.gca()
        if highlight != 'None':
            # Add rectangles for Saccades
            for i in range(0,len(sHighL)):
                ax.add_patch(patches.Rectangle((sHighL[i] - trialStart, ax.get_ylim()[0]),
                                               durHighL[i],
                                               abs(ax.get_ylim()[1] - ax.get_ylim()[0]),
                                               fill=True, alpha = 0.3))
    
        # Lets get make a timeseries to plot over time.
        timeCol = np.linspace(1,0,len(xPos))
        # Lets plot the gaze position during trial
        ax4 = plt.subplot(1,2,2)
        plt.title('Gaze position')
        plt.xlabel('X position (px)')
        plt.ylabel('Y position (px)')
        ax = plt.gca()
        plt.axis([xMin, xMax, yMin, yMax])
        if pltType == 'gaze':
            if pltBg == True:
                bgIm = plt.imread(bgImLoc)
                ax.imshow(np.flipud(bgIm), aspect=bgAspect, extent = [xMin, xMax, yMin, yMax])
                if pltStyle == 'Line':
                        ax.plot(xPos, yPos)
                elif pltStyle == 'Scatter':
                    ax.scatter(xPos, yPos, c = timeCol, edgecolors = 'face', marker = 'p', s = 5, cmap = 'hot')
            else:
                if pltStyle == 'Line':
                    plt.plot(xPos, yPos)
                elif pltStyle == 'Scatter':
                    plt.scatter(xPos, yPos,c = timeCol, edgecolors = 'face', marker = 'p', s = 5, cmap='hot')            
            ax.set(aspect = bgAspect)
    
        elif pltType == 'heat' :
            #======================================================================
            # Make gaussian image
            #======================================================================
            if pltBg == True:
                bgIm = plt.imread(bgImLoc)
                plt.imshow(np.flipud(bgIm), aspect=bgAspect, extent = [xMin, xMax, yMin, yMax])
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
            plt.imshow(newHeatmap, cmap=cmap, extent=[xMin,xMax,yMin,yMax], alpha = kernelAlpha, aspect=bgAspect)
        # invert Axis
        ax.invert_yaxis()
        pltTitle = 'Plotting trial: ' + str(trial+1) + ', index number: ' + str(trial)+'\nIncluded: '+included
        if addLabel != 'False':
            pltTitle += '\n'+addLabel+': '+addInfo
        plt.suptitle(pltTitle)
        plt.draw()
        return fig, ax1, ax2, ax3, ax4
    except:
        plt.close('all')
        fig = plt.figure(2)
        plt.clf()
        plt.title('Error, try different settings!')
        print traceback.format_exc()
        return fig
        
#import pandas as pd
#from matplotlib import animation
#
#
#plt.close('all')
#data = pd.read_pickle('C:/Work/PhD Vu/Conferences/Dep PsychoLink -2018/images/exampleFile.p')
#timeStamp = data.DK_rawTime[10]
#xPos = data.DK_rawX[10]
#yPos = data.DK_rawY[10] 
#euclidDist = data.DK_euclidDist[10]
#par = {}
#
#figAx = plotTrial(timeStamp, xPos, yPos, euclidDist, **par)
#
#if len(figAx) == 5:
#    fig,ax1,ax2,ax3,ax4 = figAx
#    xMin, xMax = ax4.get_xlim()
#    yMin, yMax = ax4.get_ylim()
#    speedMin, speedMax = ax3.get_ylim()
#    
#    ax4.clear()
#    plt.title('Gaze position')
#    plt.xlabel('X position (px)')
#    plt.ylabel('Y position (px)')
#    line1, = ax1.plot([0,0], [xMin, xMax], lw=2, c='k')
#    line2, = ax2.plot([0,0], [yMin, yMax], lw=2, c='k')
#    line3, = ax3.plot([0,0], [speedMin, speedMax], lw=2, c='k')
#    #dot = ax4.scatter([],[], marker = 'p')
#    ax4.axis([xMin, xMax, yMin, yMax])
#    ax4.set(aspect = 'equal')
#    
##def init():
##    line1.set_data([0,0], [xMin, xMax])
##    line2.set_data([0,0], [yMin, yMax])
##    line3.set_data([0,0], [speedMin, speedMax])
##    return line1, line2, line3,
#
#def init():
#    line1.set_data([],[])
#    line2.set_data([],[])
#    line3.set_data([],[])
#    return line1, line2, line3,
#
## animation function. This is called sequentially
#def animate(i):    
#    # Draw moving line
#    line1.set_data([i,i], [xMin, xMax])
#    line2.set_data([i,i], [yMin, yMax])
#    line3.set_data([i,i], [speedMin, speedMax])
#    # Draw moving dot
#    dot = ax4.scatter(xPos[i],yPos[i], c= 'k')
#
#    return line1, line2, line3, dot
#anim = animation.FuncAnimation(fig, animate, init_func=init,
#                               frames=len(xPos), interval=1, blit=True)
##anim.save('trajectories.mp4', fps=15, extra_args=['-vcodec', 'libx264'])
##anim.save('trajectories.mp4', fps=200, extra_args=['-vcodec', 'libx264'])
#
#plt.show()
## Stop animation
##anim.event_source.stop()


