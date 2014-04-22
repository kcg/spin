#!/usr/bin/env python

"""
spin, a small utility to assist in setting usage modes of laptop-tablet devices

Usage:
    spin.py
    spin.py -h | --help
    spin.py --nogui
    spin.py --fancygui
Options:
    -h,--help      : show this help message
    --nogui        : non-GUI mode
    --fancygui     : fancy-GUY mode
"""
################################################################################
#                                                                              #
# spin                                                                         #
#                                                                              #
# version: 2014-04-22T2007                                                     #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# The program spin provides an interface for control of the usage modes of     #
# laptop-tablet and similar computer interface devices.                        #
#                                                                              #
# copyright (C) 2013 2014 William Breaden Madden  							   #
#				2014 Karl C Goedel (fancygui)                                  #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

from docopt import docopt
import os
import sys
import subprocess
from multiprocessing import Process
import socket
import time
from PyQt4 import QtGui
import logging
import wx

# logging
logger = logging.getLogger(__name__)
logging.basicConfig()
logger.level = logging.INFO

class spinner():
    def __init__(self,):
        logger.info("running spin")
        # engage stylus proximity control
        self.stylusProximityControlOn()
        # engage display position control
        self.displayPositionStatus = "laptop"
        self.displayPositionControlOn()
        self.selectionModeCoord = (0,0)
        self.selectionPositionCoord = (0,0)
    def displayLeft(self):
        logger.info("changing display to left")
        os.system('xrandr -o left')
    def displayRight(self):
        logger.info("changing display to right")
        os.system('xrandr -o right')
    def displayInverted(self):
        logger.info("changing display to inverted")
        os.system('xrandr -o inverted')
    def displayNormal(self):
        logger.info("changing display to normal")
        os.system('xrandr -o normal')
    def touchscreenLeft(self):
        logger.info("changing touchscreen to left")
        os.system('xinput set-prop "ELAN Touchscreen" "Coordinate Transformation Matrix" 0 -1 1 1 0 0 0 0 1')
    def touchscreenRight(self):
        logger.info("changing touchscreen to right")
        os.system('xinput set-prop "ELAN Touchscreen" "Coordinate Transformation Matrix" 0 1 0 -1 0 1 0 0 1')
    def touchscreenInverted(self):
        logger.info("changing touchscreen to inverted")
        os.system('xinput set-prop "ELAN Touchscreen" "Coordinate Transformation Matrix" -1 0 1 0 -1 1 0 0 1')
    def touchscreenNormal(self):
        logger.info("changing touchscreen to normal")
        os.system('xinput set-prop "ELAN Touchscreen" "Coordinate Transformation Matrix" 1 0 0 0 1 0 0 0 1')
    def touchscreenOn(self):
        logger.info("changing touchscreen to on")
        os.system('xinput enable "ELAN Touchscreen"')
    def touchscreenOff(self):
        logger.info("changing touchscreen to off")
        os.system('xinput disable "ELAN Touchscreen"')
    def touchpadOn(self):
        logger.info("changing touchpad to on")
        os.system('xinput enable "SynPS/2 Synaptics TouchPad"')
    def touchpadOff(self):
        logger.info("changing touchpad to off")
        os.system('xinput disable "SynPS/2 Synaptics TouchPad"')
    def nippleOn(self):
        logger.info("changing nipple to on")
        os.system('xinput enable "TPPS/2 IBM TrackPoint"')
    def nippleOff(self):
        logger.info("changing nipple to off")
        os.system('xinput disable "TPPS/2 IBM TrackPoint"')
    def stylusProximityControl(self):
        self.previousStylusProximityStatus = None
        while True:
            stylusProximityCommand = 'xinput query-state "Wacom ISDv4 EC Pen stylus" | grep Proximity | cut -d " " -f3 | cut -d "=" -f2'
            self.stylusProximityStatus = subprocess.check_output(stylusProximityCommand, shell=True).lower().rstrip()
            if (self.stylusProximityStatus == "out") and (self.previousStylusProximityStatus != "out"):
                logger.info("stylus inactive")
                self.touchscreenOn()
            elif (self.stylusProximityStatus == "in") and (self.previousStylusProximityStatus != "in"):
                logger.info("stylus active")
                self.touchscreenOff()
            self.previousStylusProximityStatus = self.stylusProximityStatus
            time.sleep(0.25)
    def stylusProximityControlOn(self):
        logger.info("changing stylus proximity control to on")
        self.processStylusProximityControl = Process(target=self.stylusProximityControl)
        self.processStylusProximityControl.start()
    def stylusProximityControlOff(self):
        logger.info("changing stylus proximity control to off")
        self.processStylusProximityControl.terminate()
    def displayPositionControl(self):
        socketACPI = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        socketACPI.connect("/var/run/acpid.socket")
        logger.info("display position is {a1}".format(a1=self.displayPositionStatus))
	while True:
            eventACPI = socketACPI.recv(4096)
            if eventACPI == 'ibm/hotkey HKEY 00000080 000060c0\n':
                logger.info("display position change")
                if self.displayPositionStatus == "laptop":
                    self.engageModeTablet()
                    self.displayPositionStatus = "tablet"
                    logger.info("display position is {a1}".format(a1=self.displayPositionStatus))
                elif self.displayPositionStatus == "tablet":
                    self.engageModeLaptop()
                    self.displayPositionStatus = "laptop"
                    logger.info("display position is {a1}".format(a1=self.displayPositionStatus))
            time.sleep(0.25)
    def displayPositionControlOn(self):
        logger.info("changing display position control to on")
        self.processDisplayPositionControl = Process(target=self.displayPositionControl)
        self.processDisplayPositionControl.start()
    def displayPositionControlOff(self):
        logger.info("changing display position control to off")
        self.processDisplayPositionControl.terminate()

class qtinterface(QtGui.QWidget):
    def __init__(
        self,
        docopt_args=None
	):
        self.docopt_args=docopt_args
        super(qtinterface, self).__init__()
        self.spinner = spinner()
        if not (docopt_args["--nogui"]):
            # create buttons
            buttonsList = []
            # button: tablet mode
            buttonModeTablet = QtGui.QPushButton('tablet mode', self)
            buttonModeTablet.clicked.connect(self.engageModeTablet)
            buttonsList.append(buttonModeTablet)
            # button: laptop mode
            buttonModeLaptop = QtGui.QPushButton('laptop mode', self)
            buttonModeLaptop.clicked.connect(self.engageModeLaptop)
            buttonsList.append(buttonModeLaptop)
            # button: left
            buttonLeft = QtGui.QPushButton('left', self)
            buttonLeft.clicked.connect(self.engageLeft)
            buttonsList.append(buttonLeft)
            # button: right
            buttonRight = QtGui.QPushButton('right', self)
            buttonRight.clicked.connect(self.engageRight)
            buttonsList.append(buttonRight)
            # button: inverted
            buttonInverted = QtGui.QPushButton('inverted', self)
            buttonInverted.clicked.connect(self.engageInverted)
            buttonsList.append(buttonInverted)
            # button: normal
            buttonNormal = QtGui.QPushButton('normal', self)
            buttonNormal.clicked.connect(self.engageNormal)
            buttonsList.append(buttonNormal)
            # button: touchscreen on
            buttonTouchscreenOn = QtGui.QPushButton('touchscreen on', self)
            buttonTouchscreenOn.clicked.connect(self.engageTouchscreenOn)
            buttonsList.append(buttonTouchscreenOn)
            # button: touchscreen off
            buttonTouchscreenOff = QtGui.QPushButton('touchscreen off', self)
            buttonTouchscreenOff.clicked.connect(self.engageTouchscreenOff)
            buttonsList.append(buttonTouchscreenOff)
            # button: touchpad on
            buttonTouchpadOn = QtGui.QPushButton('touchpad on', self)
            buttonTouchpadOn.clicked.connect(self.engageTouchpadOn)
            buttonsList.append(buttonTouchpadOn)
            # button: touchpad off
            buttonTouchpadOff = QtGui.QPushButton('touchpad off', self)
            buttonTouchpadOff.clicked.connect(self.engageTouchpadOff)
            buttonsList.append(buttonTouchpadOff)
            # button: nipple on
            buttonNippleOn = QtGui.QPushButton('nipple on', self)
            buttonNippleOn.clicked.connect(self.engageNippleOn)
            buttonsList.append(buttonNippleOn)
            # button: nipple off
            buttonNippleOff = QtGui.QPushButton('nipple off', self)
            buttonNippleOff.clicked.connect(self.engageNippleOff)
            buttonsList.append(buttonNippleOff)
            # button: stylus proximity monitoring on
            buttonStylusProximityControlOn = QtGui.QPushButton('stylus proximity monitoring on', self)
            buttonStylusProximityControlOn.clicked.connect(self.engageStylusProximityControlOn)
            buttonsList.append(buttonStylusProximityControlOn)
            # button: stylus proximity monitoring off
            buttonStylusProximityControlOff = QtGui.QPushButton('stylus proximity monitoring off', self)
            buttonStylusProximityControlOff.clicked.connect(self.engageStylusProximityControlOff)
            buttonsList.append(buttonStylusProximityControlOff)
            # button: display position monitoring on
            buttonDisplayPositionControlOn = QtGui.QPushButton('display position monitoring on', self)
            buttonDisplayPositionControlOn.clicked.connect(self.engageDisplayPositionControlOn)
            buttonsList.append(buttonDisplayPositionControlOn)
            # button: display position monitoring off
            buttonDisplayPositionControlOff = QtGui.QPushButton('display position monitoring off', self)
            buttonDisplayPositionControlOff.clicked.connect(self.engageDisplayPositionControlOff)
            buttonsList.append(buttonDisplayPositionControlOff)
            # set button dimensions
            buttonsWidth=250
            buttonsHeight=50
            for button in buttonsList:
                button.setFixedSize(buttonsWidth, buttonsHeight)
            # set layout
            vbox = QtGui.QVBoxLayout()
            vbox.addStretch(1)
            for button in buttonsList:
                vbox.addWidget(button)
                vbox.addStretch(1)	
            self.setLayout(vbox)
            # window
            self.setWindowTitle('spin')
            # set window position
            self.move(0, 0)
            self.show()
        elif docopt_args["--nogui"]:
            logger.info("non-GUI mode")
    def closeEvent(self, event):
        logger.info("stopping spin")
        self.spinner.stylusProximityControlOff()
        self.engageDisplayPositionControlOff()
        self.deleteLater()
    def engageModeTablet(self):
        logger.info("engaging mode tablet")
        self.spinner.displayLeft()
        self.spinner.touchscreenLeft()
        self.spinner.touchpadOff()
        self.spinner.nippleOff()
    def engageModeLaptop(self):
        logger.info("engaging mode laptop")
        self.spinner.displayNormal()
        self.spinner.touchscreenNormal()
        self.spinner.touchscreenOn()
        self.spinner.touchpadOn()
        self.spinner.nippleOn()
    def engageLeft(self):
        logger.info("engaging mode left")
        self.spinner.displayLeft()
        self.spinner.touchscreenLeft()
    def engageRight(self):
        logger.info("engaging mode right")
        self.spinner.displayRight()
        self.spinner.touchscreenRight()
    def engageInverted(self):
        logger.info("engaging mode inverted")
        self.spinner.displayInverted()
        self.spinner.touchscreenInverted()
    def engageNormal(self):
        logger.info("engaging mode normal")
        self.spinner.displayNormal()
        self.spinner.touchscreenNormal()
    def engageTouchscreenOn(self):
        self.spinner.touchscreenOn()
    def engageTouchscreenOff(self):
        self.spinner.touchscreenOff()
    def engageTouchpadOn(self):
        self.spinner.touchpadOn()
    def engageTouchpadOff(self):
        self.spinner.touchpadOff()
    def engageNippleOn(self):
        self.spinner.nippleOn()
    def engageNippleOff(self):
        self.spinner.nippleOff()
    def engageStylusProximityControlOn(self):
        self.spinner.stylusProximityControlOn()
    def engageStylusProximityControlOff(self):
        self.spinner.stylusProximityControlOff()
    def engageDisplayPositionControlOn(self):
        self.spinner.displayPositionControlOn()
    def engageDisplayPositionControlOff(self):
        self.spinner.displayPositionControlOff()
        
class fancyinterface(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title,
                        style=wx.FRAME_SHAPED |
                        wx.STAY_ON_TOP |
                        wx.FRAME_NO_TASKBAR)
        self.fieldbit = wx.Bitmap('field.png', wx.BITMAP_TYPE_PNG)
        self.selbit = wx.Bitmap('selection.png', wx.BITMAP_TYPE_PNG)
        self.delta = ((0, 0))
        self.spinner = spinner()
        w = self.fieldbit.GetWidth()
        h = self.fieldbit.GetHeight()
        self.SetClientSize((w, h))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.fieldbit, 0, 0, True)
        self.sel1_x = 36
        self.sel1_y = 7
        self.sel2_x = 120
        self.sel2_y = 14
        dc.DrawBitmap(self.selbit, self.sel1_x, self.sel1_y, True)
        dc.DrawBitmap(self.selbit, self.sel2_x, self.sel2_y, True)
        self.SetFramePosition()
        self.Show(True)
    def SetFramePosition(self):
        display_x, display_y = wx.GetDisplaySize()
        x, y = self.GetSize()
        self.Move((display_x-x-10, display_y-y-10))
    def IsInRadius(self, pos, checkpos):
        distance = ((pos[0]-checkpos[0])**2+(pos[1]-checkpos[1])**2)**(0.5)
        return distance < 14
    def OnLeftDown(self, event):
        pos = event.GetPosition()
        #Close
        if self.IsInRadius(pos,(185,17)):
			logger.info("stopping spin")
			self.spinner.stylusProximityControlOff()
			self.spinner.displayPositionControlOff()
			self.Close()
        #Up
        if self.IsInRadius(pos,(56,27)):
            self.engageNormal()
            self.spinner.touchscreenNormal()
        #Down
        if self.IsInRadius(pos,(56,88)):
            self.engageInverted()
            self.spinner.touchscreenInverted()
        #Left
        if self.IsInRadius(pos,(26,58)):
            self.engageLeft()
            self.spinner.touchscreenLeft()
        #Right
        if self.IsInRadius(pos,(86,58)):
            self.engageRight()
            self.spinner.touchscreenRight()
        #Set laptop mode
        if self.IsInRadius(pos,(140,34)):
            self.engageModeLaptop()
        #Set tablet mode
        if self.IsInRadius(pos,(140,82)):
            self.engageModeTablet()        
        x, y = self.ClientToScreen(event.GetPosition())
        ox, oy = self.GetPosition()
        dx = x - ox
        dy = y - oy
        self.delta = ((dx, dy))        
    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            x, y = self.ClientToScreen(event.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.Move(fp)
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.fieldbit, 0, 0, True)
        dc.DrawBitmap(self.selbit, self.sel1_x, self.sel1_y, True)
        dc.DrawBitmap(self.selbit, self.sel2_x, self.sel2_y, True)       
    def engageLeft(self):
        self.sel1_x = 6
        self.sel1_y = 38
        self.spinner.displayLeft()
        self.OnPaint(self)
    def engageRight(self):
        self.sel1_x = 66
        self.sel1_y = 38
        self.spinner.displayRight()
        self.OnPaint(self)
    def engageInverted(self):
        self.sel1_x = 36
        self.sel1_y = 68
        self.spinner.displayInverted()
        self.OnPaint(self)
    def engageNormal(self):
        self.sel1_x = 36
        self.sel1_y = 7
        self.spinner.displayNormal()
        self.OnPaint(self)
    def engageModeTablet(self):
        self.sel2_x = 120
        self.sel2_y = 62
        self.engageLeft()
        self.spinner.touchscreenLeft()
        self.spinner.touchpadOff()
        self.spinner.nippleOff()
        self.spinner.stylusProximityControlOn()  
        self.OnPaint(self)
    def engageModeLaptop(self):
        self.sel2_x = 120
        self.sel2_y = 14
        self.engageNormal()
        self.spinner.touchscreenNormal()
        self.spinner.touchscreenOn()
        self.spinner.touchpadOn()
        self.spinner.nippleOn()
        self.spinner.stylusProximityControlOff()
        self.OnPaint(self)
            
def main(docopt_args):
	if not docopt_args["--fancygui"]:
		application = QtGui.QApplication(sys.argv)
		interface1 = qtinterface(docopt_args)
		sys.exit(application.exec_())
	else:
		application = wx.App()
		fancyinterface(None, -1, '')
		application.MainLoop()
		
if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
