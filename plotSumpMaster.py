#!/usr/bin/env python

"""
Copyright(C) 2021, BrucesHobbies
All Rights Reserved

AUTHOR: BruceHobbies
DATE: 3/25/2021
REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------


OVERVIEW:
    This program plots CSV files generated by sumpMaster.py

LICENSE:
    This program code and documentation are for personal private use only. 
    No commercial use of this code is allowed without prior written consent.

    This program is free for you to inspect, study, and modify for your 
    personal private use. 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

INSTALLATION:
Requires:
   sudo pip3 install matplotlib

"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import math
import os
import time
import datetime
import csv

# fig.savefig(filename, bbox_inches='tight')   # save the figure to file


PGMNAME = 'sumpMaster'


#
# Read in a comma seperated variable file. Assumes a header row exists.
#   Time series with time in seconds in first column.
#   Ignore text string with date/time from second column
#   data is columns [2:]
#
def importCsv(filename) :
    print("Reading " + filename)

    with open(filename, 'r') as csvfile :
        csvData = list(csv.reader(csvfile))

    hdr = csvData[0]
    # print(hdr)

    tStamp = []
    for row in csvData[1:] :
        tStamp.append(float(row[0]))

    data = {name : [] for name in hdr[2:]}
    # print(data)

    for row in csvData[1:] :
        for idx in range(2,len(hdr)) :
            data[hdr[idx]].append(float(row[idx]))

    return hdr[2:], tStamp, data


#
# Plot single or multiple variables {"key":[]} on common subplot
#
def plotMultiVar(tStamp, data, title) :

    t = [datetime.datetime.fromtimestamp(ts) for ts in tStamp]

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    for item in data :
        # print(item)
        ax1.plot(t, data[item], label=item)
        # ax1.plot(t, data[item], marker='d', label=item)

    ax1.set_title(title)
    ax1.set_xlabel('Time')

    if len(data) > 1 :
        ax1.legend(loc='upper right', shadow=True)
    else :
        ax1.set_ylabel(item)

    ax1.grid(which='both')

    plt.gcf().autofmt_xdate()    # slant labels
    dateFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plt.gca().xaxis.set_major_formatter(dateFmt)

    plt.show(block=False)



#
# Plot On-Off Cycles and Energy
#
def plotCyclesEnergy(tStamp, y1, y2, y1Lbl, y2Lbl, titleStr, timeFmt = mdates.DateFormatter('%m-%d %Hh')) :
    fig = plt.figure()
    axTop = fig.add_subplot(2, 1, 1)
    axBot = fig.add_subplot(2, 1, 2)

    t = [datetime.datetime.fromtimestamp(ts) for ts in tStamp]

    axTop.plot(t, y1, marker='d')
    axBot.plot(t, y2, 'k', marker='d')

    axTop.set_title(titleStr)
    axTop.set_ylabel(y1Lbl)
    axTop.grid(which='both')
   
    axBot.set_ylabel(y2Lbl)
    axBot.grid(which='both')

    plt.gcf().autofmt_xdate()
    # timeFmt = mdates.DateFormatter('%Y-%m-%d')
    # timeFmt = mdates.DateFormatter('%m-%d %Hh')
    # timeFmt = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(timeFmt)

    plt.subplots_adjust(hspace=0.6)

    plt.show(block=False)	# non-blocking



#
# Plot On-Off Cycles and Energy
#
def plotCyclesEnergyErrorbar(tStamp, y1, y2, y2err, \
            y1Lbl, y2Lbl, titleStr, timeFmt = mdates.DateFormatter('%m-%d %Hh')) :
    fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True)

    t = [datetime.datetime.fromtimestamp(ts) for ts in tStamp]

    axs[0].plot(tStamp, y1, marker='d')

    axs[1].errorbar(tStamp, y2, yerr=y2err)

    axs[0].set_title(titleStr)
    axs[0].set_ylabel(y1Lbl)
    axs[0].grid(which='both')
   
    axs[1].set_ylabel(y2Lbl)
    axs[1].grid(which='both')

    plt.gcf().autofmt_xdate()
    # plt.gca().xaxis.set_major_formatter(timeFmt) # Need to debug error

    plt.subplots_adjust(hspace=0.6)

    plt.show(block=False)	# non-blocking



#
# consolidateData()
# ptsToSum = number of rows to sum together: 4, 4*24, 4*24*7, 4*24*30
# maxPts = number of summed data points to plot
#
def consolidateData(tStamp, inData, ptsToSum, maxPts = 0) :
    t = []
    data = {name : [] for name in inData}

    # offset = round(ptToSum/2)    # to center in time interval add offset to x in append(tStamp[x])
    for x in range(0, len(tStamp), ptsToSum):
        t.append(tStamp[x])

    for item in inData :
        for x in range(0, len(tStamp), ptsToSum):
            data[item].append(sum(inData[item][x:x+ptsToSum]))

    # Maximum number of data points
    if maxPts :
        maxPts += 1
        t = t[-maxPts:]
        for item in data :
            data[item] = data[item][-maxPts:]

    """ # debug
    print('Consolidated len(t): ',len(t))
    for item in data :
        print('Result: ', item, len(data[item]), sum(inData[item]), sum(data[item]))
    """

    return t, data


def get_files_sw(path, sw) :
    # sw is file name starts with
    result = []
    for f in os.scandir(path) :
        if f.name.startswith(sw) :
            result.append(f.name)

    return result
    

#
# Plot the files
#
if __name__ == "__main__" :

    if 0 :
        # A lot of detailed data, so will take some time to plot...
        # Log Details per motor
        path = '.'
        filenames = get_files_sw(path, PGMNAME+'_logDetails_')
        print(filenames)

        for file in filenames :
            hdr, tStamp, data = importCsv(file)
            # hdr = ["Chan","Voltage","Amps","Watts","","Freq","PF","Status"]
            hdrIdx  = range(1,len(hdr))
            print(hdrIdx)

            for item in hdrIdx :
                # Single variable plots {"key" : []}
                var = {hdr[item] : data[hdr[item]]}
                plotMultiVar(tStamp, var, file)

    # Log Energy
    # hdr = ["Runtime (s)","Energy (Wh)",...]
    filename = PGMNAME + "_logEnergy.csv"
    hdr, tStamp, data = importCsv(filename)
    print(hdr)
    print('Cols: ',len(data))
    print('Rows: ',len(data[hdr[0]]))

    title = "15-minute interval: "
    print(title + "plotted")
    for idx in range(0, len(hdr), 2) :
        plotCyclesEnergy(tStamp, data[hdr[idx]], data[hdr[idx+1]], hdr[idx], hdr[idx+1], title+filename)

    # Hourly for 48 hours
    ptsToSum = 4
    maxPts = 48
    title = "Hourly for 48-hours: "
    print(title + "plotted")
    toutStamp, outData = consolidateData(tStamp, data, ptsToSum, maxPts)
    for idx in range(0, len(hdr), 2) :
        plotCyclesEnergy(toutStamp, outData[hdr[idx]], outData[hdr[idx+1]], hdr[idx], hdr[idx+1], title+filename)

    # Daily for 14 days if more than 7 days are available
    ptsToSum = 24*4
    maxPts = 14
    title = "Daily for 14-days: "
    if len(tStamp) > ptsToSum * maxPts // 2 :
        print(title + "plotted")
        toutStamp, outData = consolidateData(tStamp, data, ptsToSum, maxPts)
        for idx in range(0, len(hdr), 2) :
            plotCyclesEnergy(toutStamp, outData[hdr[idx]], outData[hdr[idx+1]], hdr[idx], hdr[idx+1], \
                    title+filename, timeFmt = mdates.DateFormatter('%Y-%m-%d'))
    else :
        print(title[:-2] + 'Lacking enough data')

    # Daily for 30 days if more than 15 days are available
    ptsToSum = 24*4
    maxPts = 30
    title = "Daily for 30-days: "
    if len(tStamp) > ptsToSum * maxPts // 2 :
        print(title + "plotted")
        toutStamp, outData = consolidateData(tStamp, data, ptsToSum, maxPts)
        for idx in range(0, len(hdr), 2) :
            plotCyclesEnergy(toutStamp, outData[hdr[idx]], outData[hdr[idx+1]], hdr[idx], hdr[idx+1], \
                    title+filename, timeFmt = mdates.DateFormatter('%Y-%m-%d'))
    else :
        print(title[:-2] + 'Lacking enough data')

    # Weekly for 12 months if more than 3 months are available
    ptsToSum = 7*24*4
    maxPts = 12
    title = "Weekly for 12-months: "
    if len(tStamp) > ptsToSum * maxPts // 4 :
        print(title + "plotted")
        toutStamp, outData = consolidateData(tStamp, data, ptsToSum, maxPts)
        for idx in range(0, len(hdr), 2) :
            plotCyclesEnergy(toutStamp, outData[hdr[idx]], outData[hdr[idx+1]], hdr[idx], hdr[idx+1], \
                    title+filename, timeFmt = mdates.DateFormatter('%Y-%m-%d'))
    else :
        print(title[:-2] + 'Lacking enough data')

    # Monthly for two years if more 6 months are available
    ptsToSum = 30*24*4
    maxPts = 24
    title = "Monthly for 2-years: "
    if len(tStamp) > ptsToSum * maxPts // 4 :
        print(title + "plotted")
        toutStamp, outData = consolidateData(tStamp, data, ptsToSum, maxPts)
        for idx in range(0, len(hdr), 2) :
            plotCyclesEnergy(toutStamp, outData[hdr[idx]], outData[hdr[idx+1]], hdr[idx], hdr[idx+1], \
                    title+filename, timeFmt = mdates.DateFormatter('%Y-%m-%d'))
    else :
        print(title[:-2] + 'Lacking enough data')


    """
    # Log Stats Runtime, Average Watts, StdDev Bar chart
    # hdr = ["ChanName","Runtime (s)","Avg (W)","StdDev (W)"]
    path = '.'
    filenames = get_files_sw(path, PGMNAME+'_logStats_')
    print(filenames)

    for file in filenames :
        hdr, tStamp, data = importCsv(file)
        idx = 0
        plotCyclesEnergyErrorbar(tStamp, data[hdr[idx]], data[hdr[idx+1]], data[hdr[idx+2]], hdr[idx], hdr[idx+1], file)
    """

    # Pause to view, then close plots
    input("Press [enter] key to close plots...")
    print("Done...")
