#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# ./wxFORTHide.py
# generated by wxGlade 0.4cvs on Tue May 16 10:20:28 2006

"""
#------------------------------------------------------------------
#  Copyright (C) 2006
#  Author:  gerd franzkowiak <gfranzkowiak@forth-ev.de>
#  Date:    2006-05-16
#  Version: 0.01
#  License: "GPLv2"
#------------------------------------------------------------------

This source is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#------------------------------------------------------------------
"""

import sys, wx
import popen2, threading
import stackWordSet


#----------------------------------------------------------------------
# Create an own event type, so that GUI updates can be delegated
# this is required as on some platforms only the main thread can
# access the GUI without crashing. wxMutexGuiEnter/wxMutexGuiLeave
# could be used too, but an event is more elegant.

FORTHREAD = wx.NewEventType()
# bind to serial data receive events
EVT_FORTHREAD = wx.PyEventBinder(FORTHREAD, 0)

class ForthReadEvent(wx.PyCommandEvent):
    eventType = FORTHREAD
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)

#----------------------------------------------------------------------

NEWLINE_CR      = 0
NEWLINE_LF      = 1
NEWLINE_CRLF    = 2



class FORTHide(wx.Frame):
    def __init__(self, *args, **kwds):
        self.pipeExists=False

        # begin wxGlade: FORTHide.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.horizonSplitter     = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)

        self.infoPane            = wx.Panel(self.horizonSplitter, -1)
        self.topVerticalSplitter = wx.SplitterWindow(self.infoPane, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.rightPane           = wx.Panel(self.topVerticalSplitter, -1)
        self.leftPane            = wx.Panel(self.topVerticalSplitter, -1)

        self.hmiPane             = wx.Panel(self.horizonSplitter, -1)
        self.forthNotebook       = wx.Notebook(self.hmiPane, -1, style=wx.NB_TOP)
        self.forthTerminalPane   = wx.Panel(self.forthNotebook, -1)
        self.forthEditorPane     = wx.Panel(self.forthNotebook, -1)
        
        # Status Bar
        self.FORTHframe_statusbar = wx.StatusBar(parent=self, style=0)
        self.SetStatusBar(self.FORTHframe_statusbar)
        # Menu Bar
        self.FORTHframe_menubar = wx.MenuBar()
        self.SetMenuBar(self.FORTHframe_menubar)
        self.fileMenu     = wx.Menu()
        self.fileMenuNew        = wx.MenuItem(self.fileMenu, 101, "&New", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.fileMenuNew)
        self.fileMenuOpen       = wx.MenuItem(self.fileMenu, 102, "&Open", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.fileMenuOpen)
        self.fileMenu.AppendSeparator()
        self.fileMenuSave       = wx.MenuItem(self.fileMenu, 103, "&Save", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.fileMenuSave)
        self.fileMenuSaveAs     = wx.MenuItem(self.fileMenu, 104, "Save &As", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.fileMenuSaveAs)
        self.fileMenu.AppendSeparator()
        self.fileMenuExit       = wx.MenuItem(self.fileMenu, 109, "E&xit", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.fileMenuExit)
        self.FORTHframe_menubar.Append(self.fileMenu, "&File")
        self.conMenu            = wx.Menu()
        self.conMenuFORTHsystem = wx.MenuItem(self.conMenu, 201, "&FORTH system", "", wx.ITEM_NORMAL)
        self.conMenu.AppendItem(self.conMenuFORTHsystem)
        self.conMenu.AppendSeparator()
        self.conMenuStdIoPipe   = wx.MenuItem(self.conMenu, 202, "Standard-IO-&Pipe", "", wx.ITEM_NORMAL)
        self.conMenu.AppendItem(self.conMenuStdIoPipe)
        serialMenu        = wx.Menu()
        self.conMenuTtyS0       = wx.MenuItem(serialMenu, 221, "ttyS&0", "", wx.ITEM_NORMAL)
        serialMenu.AppendItem(self.conMenuTtyS0)
        self.conMenuTtyS1       = wx.MenuItem(serialMenu, 222, "ttyS&1", "", wx.ITEM_NORMAL)
        serialMenu.AppendItem(self.conMenuTtyS1)
        self.conMenuTtyS2       = wx.MenuItem(serialMenu, 223, "ttyS&2", "", wx.ITEM_NORMAL)
        serialMenu.AppendItem(self.conMenuTtyS2)
        self.conMenuTtyS3       = wx.MenuItem(serialMenu, 224, "ttyS&3", "", wx.ITEM_NORMAL)
        serialMenu.AppendItem(self.conMenuTtyS3)
        self.conMenu.AppendMenu(220, "&Serial", serialMenu, "")
        tcpIpMenu         = wx.Menu()
        self.targetIpMenu       = wx.MenuItem(tcpIpMenu, 231, "target &IP", "", wx.ITEM_NORMAL)
        tcpIpMenu.AppendItem(self.targetIpMenu)
        self.targetPortMenu     = wx.MenuItem(tcpIpMenu, 232, "target &port", "", wx.ITEM_NORMAL)
        tcpIpMenu.AppendItem(self.targetPortMenu)
        self.conMenu.AppendMenu(230, "&TCP/IP", tcpIpMenu, "")
        self.FORTHframe_menubar.Append(self.conMenu, "&Connect")
        # Menu Bar end

        startUpText = '\nF O R T H environment\n\nOpen the pull down menu "Connect" and choose a FORTH system\n\n( Test one and two clicks on a word in the top right list box )\n\n A T T E N T I O N\nbefore you leave this environment you must exit from FORTH !!! '
        self.topLeftHelpCtrl = wx.TextCtrl(self.leftPane,
                                           -1,
                                           startUpText,
                                           style=wx.TE_MULTILINE)
        # ----------------------------------------------
        self.FORTHwordSet = stackWordSet.stackWordSet.keys()
        # ... Unicode-Wandlung f. WxPython notwendig ...
        for i in range(len(self.FORTHwordSet)):
            self.FORTHwordSet[i] = unicode(self.FORTHwordSet[i])
        self.FORTHwordSet.sort()
        # ----------------------------------------------
        self.topRightListBox = wx.ListBox(self.rightPane,
                                          -1,
                                          choices=self.FORTHwordSet,
                                          style=wx.LB_SINGLE)
        
        #self.forthTerminalCtrl = wx.TextCtrl(self.hmiPane,
        self.forthTerminalCtrl = wx.TextCtrl(self.forthTerminalPane,
                                             -1,
                                             value = "Choose the FORTH system with <Connect - FORTH system> ...\n",
                                             style = wx.TE_MULTILINE)
        self.forthEditorCtrl = wx.TextCtrl(self.forthEditorPane,
                                           -1,
                                           value = "( Comment )\n",
                                           style = wx.TE_MULTILINE)

        self.__set_properties()
        self.__do_layout()

        # end wxGlade


        ############################################################################################
        self.echo = True
        self.thread = None
        self.alive  = threading.Event()               
        self.__attach_events()          #register events

        self.newline = NEWLINE_CR
        #self.newline = NEWLINE_LF
        #self.newline = NEWLINE_CRLF


        ############################################################################################



    def __set_properties(self):
        # begin wxGlade: FORTHide.__set_properties
        self.SetTitle("FORTH")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("./res/drache.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((800, 600))
        self.SetPosition((100, 100))

        self.topLeftHelpCtrl.SetBackgroundColour(wx.Colour(63, 255, 243))
        self.topLeftHelpCtrl.SetForegroundColour(wx.Colour(0, 0, 0))

        self.topRightListBox.SetBackgroundColour(wx.Colour(219, 255, 143))
        self.topRightListBox.SetForegroundColour(wx.Colour(0, 0, 0))
        self.topRightListBox.SetSelection(0)

        self.forthTerminalCtrl.SetMinSize((-1,-1))
        self.forthTerminalCtrl.SetBackgroundColour(wx.Colour(255, 218, 185))
        self.forthTerminalCtrl.SetForegroundColour(wx.Colour(0, 0, 0))

        self.forthEditorCtrl.SetMinSize((-1,-1))
        self.forthEditorCtrl.SetBackgroundColour(wx.Colour(219, 219, 112))
        self.forthEditorCtrl.SetForegroundColour(wx.Colour(0, 0, 0))

        self.forthNotebook.SetMinSize((-1, -1))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: FORTHide.__do_layout
        FORTHframeSizer  = wx.BoxSizer(wx.VERTICAL)
        
        topSizer         = wx.BoxSizer(wx.VERTICAL)
        topLeftSizer     = wx.BoxSizer(wx.HORIZONTAL)
        topRightSizer    = wx.BoxSizer(wx.HORIZONTAL)

        bottomSizer      = wx.BoxSizer(wx.VERTICAL)
        forthTermSizer   = wx.BoxSizer(wx.VERTICAL)
        forthEditorSizer = wx.BoxSizer(wx.VERTICAL)
        # ==========================================
        topLeftSizer.Add(self.topLeftHelpCtrl,
                         1,
                         wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE,
                         0)
        self.leftPane.SetAutoLayout(True)
        self.leftPane.SetSizer(topLeftSizer)
        #topLeftSizer.Fit(self.leftPane)
        topLeftSizer.SetSizeHints(self.leftPane)
        # ..........................................
        topRightSizer.Add(self.topRightListBox,
                          1,
                          wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE,
                          0)
        self.rightPane.SetAutoLayout(True)
        self.rightPane.SetSizer(topRightSizer)
        #topRightSizer.Fit(self.rightPane)
        topRightSizer.SetSizeHints(self.rightPane)
        # ..........................................
        self.topVerticalSplitter.SplitVertically(self.leftPane, self.rightPane, -150)
        # ..........................................
        topSizer.Add(self.topVerticalSplitter,
                     1,
                     wx.EXPAND,
                     0)
        self.infoPane.SetAutoLayout(True)
        self.infoPane.SetSizer(topSizer)
        #topSizer.Fit(self.infoPane)
        topSizer.SetSizeHints(self.infoPane)

        # ------------------------------------------

        forthTermSizer.Add(self.forthTerminalCtrl,
                           1,
                           wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE,
                           0)
        self.forthTerminalPane.SetAutoLayout(True)
        self.forthTerminalPane.SetSizer(forthTermSizer)
        #forthTermSizer.Fit(self.forthTerminalPane)
        forthTermSizer.SetSizeHints(self.forthTerminalPane)
        # ..........................................
        forthEditorSizer.Add(self.forthEditorCtrl,
                             1,
                             wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE,
                             0)
        self.forthEditorPane.SetAutoLayout(True)
        self.forthEditorPane.SetSizer(forthEditorSizer)
        #forthEditorSizer.Fit(self.forthEditorPane)
        forthEditorSizer.SetSizeHints(self.forthEditorPane)
        # ..........................................
        self.forthNotebook.AddPage(self.forthTerminalPane,"Terminal")
        self.forthNotebook.AddPage(self.forthEditorPane,  "Editor")
        # ..........................................
        bottomSizer.Add(self.forthNotebook,
                        1,
                        wx.EXPAND,
                        0)
        self.hmiPane.SetAutoLayout(True)
        self.hmiPane.SetSizer(bottomSizer)
        #bottomSizer.Fit(self.hmiPane)
        bottomSizer.SetSizeHints(self.hmiPane)
        # ------------------------------------------
        self.horizonSplitter.SplitHorizontally(self.infoPane, self.hmiPane)
        FORTHframeSizer.Add(self.horizonSplitter,
                            1,
                            wx.EXPAND,
                            0)
        # ==========================================
        self.SetAutoLayout(True)
        self.SetSizer(FORTHframeSizer)
        self.Layout()
        # end wxGlade


    def __attach_events(self):
        #register events at the controls
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Bind(wx.EVT_MENU, self.OnClose,           id=109)
        self.Bind(wx.EVT_MENU, self.OnMenuFORTHsystem, id=201)

        self.forthTerminalCtrl.Bind(wx.EVT_CHAR, self.OnKey)        
        self.Bind(EVT_FORTHREAD, self.OnForthRead)

        self.Bind(wx.EVT_LISTBOX,        self.OnClickTopRightListBox,  self.topRightListBox)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDClickTopRightListBox, self.topRightListBox)


    ############################################################################################



    def FromForthReceiveThread(self):
        """Thread that handles the incomming traffic. Does the basic input
           transformation (newlines) and generates an ForthReadEvent"""

        while self.alive.isSet():               #loop while alive event is true
            #self.text = self.forthStdOut.read(1)     #read one
            self.text = self.forthStdOut.readline()
            #newline transformation
            if self.newline == NEWLINE_CR:
                self.text = self.text.replace('\r', '\n')
            elif self.newline == NEWLINE_LF:
                self.text = self.text.replace('\n', '\n')
            elif self.newline == NEWLINE_CRLF:
                self.text = self.text.replace('\r\n', '\n')
            event = ForthReadEvent(self.GetId(), self.text)
            self.GetEventHandler().AddPendingEvent(event)
            # self.OnSerialRead(self.text)         #output text in window



    def StartFromForthReceiveThread(self):
        """Start the receiver thread"""        
        self.thread = threading.Thread(target=self.FromForthReceiveThread)
        self.thread.setDaemon(1)
        self.alive.set()                #must be set before go to while loop with start !!! gf/23.01.06
        self.thread.start()


    def StopFromForthReceiveThread(self):
        """Stop the receiver thread, wait util it's finished."""
        if self.thread is not None:
            self.alive.clear()          #clear alive event for thread
            self.thread.join()          #wait until thread has finished
            self.thread = None




    def OnMenuFORTHsystem(self, event):
        self.fileDlg = wx.FileDialog(parent=self,
                                     message="Choose your FORTH system",
                                     defaultDir="/usr/bin",
                                     defaultFile="gforth",
                                     wildcard="*.*",
                                     style=wx.OPEN)
        try:
            if self.fileDlg.ShowModal() == wx.ID_OK:
                self.fORTHsystem = self.fileDlg.GetPath()
        finally:
            self.fileDlg.Destroy()

        try:
            #self.forthStdOut, self.forthStdIn, self.forthStdErr = popen2.popen3('/usr/local/bin/bigforth')
            self.forthStdOut, self.forthStdIn, self.forthStdErr = popen2.popen3(self.fORTHsystem)
            """Clear contents of output window."""
            self.forthTerminalCtrl.Clear()
            self.StartFromForthReceiveThread()
            #self.forthStdIn.write('\r')    # CR
            #self.forthStdIn.write('\n')    # LF

            if not self.alive.isSet():
                self.forthStdOut.close()        #cleanup
                self.forthStdIn.close()
                self.forthStdErr.close()
                self.Close()
            self.pipeExists=True

            self.forthTerminalCtrl.SetFocus()
            
        except:
            self.pipeExists=False



    def OnKey(self, event):
        """Key event handler. If the key is in the ASCII range, write it to the FORTH environment.
           Newline handling and local echo is also done here."""
        self.code = event.GetKeyCode()
        if self.code < 256:                          #is it printable?
            try:
                if self.code == 13:                      #is it a newline? (check for CR which is the RETURN key)
                    self.FORTHframe_statusbar.SetStatusText("%s   0x%X (%i)   "
                                                            %('Key:', self.code, self.code))
                    if self.echo:          #do echo if needed
                        self.forthTerminalCtrl.AppendText('\n')
                    #newline transformation
                    if self.newline == NEWLINE_CR:
                        self.forthStdIn.write('\r')     #send CR
                    elif self.newline == NEWLINE_LF:
                        self.forthStdIn.write('\n')     #send LF
                    elif self.newline == NEWLINE_CRLF:
                        self.forthStdIn.write('\r\n')   #send CR+LF
                    self.forthStdIn.flush()
                else:
                    self.FORTHframe_statusbar.SetStatusText("%s   '%c' 0x%X (%i)   "
                                                            %('Key:', self.code, self.code, self.code))
                    self.char = chr(self.code)
                    if self.echo:          #do echo if needed
                        self.forthTerminalCtrl.WriteText(unicode(self.char))
                    self.forthStdIn.write(self.char)         #send the charcater
            except:
                self.forthTerminalCtrl.WriteText('No FORTH system available !\n')
                self.forthTerminalCtrl.WriteText("Choose the FORTH system with\t<Connect - FORTH system> ...\n")
        else:
            self.FORTHframe_statusbar.SetStatusText("%s   0x%X (%i)"
                                                    %('Extra Key:', self.code, self.code))


    def OnForthRead(self, event):
        """Handle input from the FORTH environment."""
        self.text = event.data
        #if self.unprintable:
            #self.text = ''.join([(c >= ' ') and c or '<%d>' % ord(c)  for c in text])
        self.forthTerminalCtrl.AppendText(unicode(self.text))



    def OnClickTopRightListBox(self, event):
        """Called by single click on word set list box"""
        self.FORTHword  = event.GetString()
        self.stackDiagram = stackWordSet.stackWordSet[self.FORTHword]
        self.topLeftHelpCtrl.Clear()
        self.topLeftHelpCtrl.AppendText(self.FORTHword+'\t'+self.stackDiagram)
            


    def OnDClickTopRightListBox(self, event):
        """Called by double click on word set list box"""
        self.FORTHword  = event.GetString()
        self.forthTerminalCtrl.AppendText(' '+event.GetString()+' ')

        self.FORTHframe_statusbar.SetStatusText("Sent:  %s                "
                                                %(self.FORTHword))
        self.forthStdIn.write(self.FORTHword)         #send the FORTH word
        self.forthTerminalCtrl.SetFocus()



    def OnClose(self, event):
        """Called on application shutdown."""
        if self.alive.isSet():
            self.StopFromForthReceiveThread()           #stop reader thread
        if self.pipeExists:
            self.forthStdOut.close()        #cleanup
            self.forthStdIn.close()
            self.forthStdErr.close()
        self.Destroy()                  #close windows, exit app


# end of class FORTHide




class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        forthIDE = FORTHide(None, -1, "")
        self.SetTopWindow(forthIDE)
        forthIDE.Show(1)
        return 1

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
