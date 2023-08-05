# -*- coding: utf-8 -*-
#!/usr/bin/python
# Cross Wavelet Analysis (CWA) based on Maraun and Kurths(2004).
# http://www.nonlin-processes-geophys.net/11/505/2004/npg-11-505-2004.pdf
# author: Mabel Calim Costa
# INPE
# 23/01/2013

"""
Created on Mon Jun 17 2013

@author: Mabel Calim Costa
"""
import numpy as np
import pylab
from pylab import *
import matplotlib.pyplot as plt



def cross_wavelet (wave1,wave2):
    	""" Computes the cross wavelet analysis.
        A normalized time and scale resolved measure for the relationship 
        between two time series x1(ti) and x2(ti) is the wavelet coherency (WCO),
        which is defined as the amplitude of the WCS(wavelet cross spectrum) 
        normalized to the two single WPS(wavelet power spectrum) (Maraun and Kurths,2004).
         	WCOi(s) = |WCSi(s) |/ (WPSi1(s) WPSi2(s)) ˆ1/2 
        _____________________________________________________________________
        Inputs:  
		wave1 - wavelet transform of time series x1
                wave2 - wavelet transform of time series x2
        Outputs:
		cohere - wavelet coherency (WCO)
 	Call function:
		cohere = cross_wavelet(wave1,wave2)
    	""" 
    	cross_power = np.abs(wave1.real*wave2.imag)
   	coherence = np.sqrt(cross_power*cross_power)/np.sqrt(np.abs(wave1.real*wave1.imag)* np.abs(wave2.real*wave2.imag))
   	return cross_power, coherence


def plot_cross (cross_power,time,result):
	fig = plt.figure(figsize=(15,10), dpi=100)
	contourf(time,np.log2(result['period']),cross_power)
	colorbar()
	ax = gca()                                                      # handle to the current axes
	ax.set_ylim(ax.get_ylim()[::-1])                                # reverse plot along y axis
	yt =  range(int(np.log2(result['period'][0])),int(np.log2(result['period'][-1]))+1) # create the vector of periods
	Yticks = [(math.pow(2,p)) for p in yt]         		        # make 2^periods
	yticks(yt, map(str,Yticks))
	xlim(time[0],time[-1])                                          # date on the x axis 
	xlabel('Time')
	ylabel('Period')
	title('Cross Power')
        plot(time,np.log2(result['coi']),'k')
        ax.fill_between(time,np.log2(result['coi']),int(np.log2(result['period'][-1])+1), alpha =0.5, hatch = '/')
	pylab.show()
	return

def plot_cohere (coherence,time,result):
        fig = plt.figure(figsize=(15,10), dpi=100)
        lev = list(np.linspace(0,1.0, 6))
        contourf(time,np.log2(result['period']),coherence)
        colorbar(ticks=lev)
        ax = gca()                                                      # handle to the current axes
        ax.set_ylim(ax.get_ylim()[::-1])                                # reverse plot along y axis
        yt =  range(int(np.log2(result['period'][0])),int(np.log2(result['period'][-1]))+1) # create the vector of periods
        Yticks = [(math.pow(2,p)) for p in yt]                          # make 2^periods
        yticks(yt, map(str,Yticks))
        xlim(time[0],time[-1])                                          # date on the x axis 
        xlabel('Time')
        ylabel('Period')
        title('Coherence')
        plot(time,np.log2(result['coi']),'k')
        ax.fill_between(time,np.log2(result['coi']),int(np.log2(result['period'][-1])+1), alpha =0.5, hatch = '/')
        pylab.show()
        return

