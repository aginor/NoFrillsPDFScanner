#!/usr/bin/env python
# coding: utf8

# This is a simple scanning application that only outputs to multi-page PDFs
# Copyright (C) 2012  Andreas Löf <andreas@alternating.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.



import Image
import sane
import wx
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import wx.lib.agw.advancedsplash as AS

class ImagePanel(wx.Panel):
    def __init__(self,*args,**kwargs):
        super(ImagePanel,self).__init__(*args, **kwargs)

        self.image = None  # wxPython image
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnPaint)
        self.Refresh(True)
        


    def display(self, image):
        self.image = image
        self.Refresh(True)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        size = self.GetSize()
        dc.DrawRectangle(0,0,size.GetWidth(),size.GetHeight())

        if self.image:

            w = self.image.GetWidth()
            h = self.image.GetHeight()
            if w > h:
                newWidth = size.GetWidth()
                newHeight = size.GetHeight() * h / w
            else:
                newHeight = size.GetHeight()
                newWidth = size.GetWidth() * w / h
            tempImage = self.image.Scale(newWidth,newHeight,wx.IMAGE_QUALITY_HIGH)
            dc.DrawBitmap(tempImage.ConvertToBitmap(), 0,0)




class ScanWindow(wx.Frame):
    def __init__(self,*args,**kwargs):
        super(ScanWindow,self).__init__(*args, **kwargs)

        self.scannerSettings = {}
        self.images = []
        
        self.sane_version = sane.init()
        self.sane_devices = sane.get_devices()
        self.scanner = sane.open(self.sane_devices[0][0])
        self.initialiseScannerOptions(self.scanner)
        self.countLabel = None
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.InitUI()
        self.Show(True)
        

    def OnClose(self,e):
        if(self.scanner is not None):
            self.scanner.close()
        self.Destroy()

    def InitUI(self):
        
        self.SetTitle('Scan Window')
        self.SetSize(wx.Size(800,600))
        
        basePanel = wx.Panel(self)
        
        vbox = wx.BoxSizer(wx.HORIZONTAL)
        
        buttonPanel = wx.Panel(basePanel)
        buttonLayout = wx.FlexGridSizer(cols=1,rows=10)
        buttonPanel.SetSizer(buttonLayout)

        self.imagePanel = ImagePanel(basePanel,pos=(0,50),style=wx.SUNKEN_BORDER)
        

        vbox.Add(buttonPanel,1,wx.WEST)
        vbox.Add(self.imagePanel,3,wx.ALL| wx.EXPAND)
        basePanel.SetSizer(vbox)


        self.countLabel = wx.StaticText(buttonPanel,wx.ID_ANY)
        self.updatePageCount()
        
        scanButton = wx.Button(buttonPanel,label="Scan")
        scanButton.Bind(wx.EVT_BUTTON,self.performScan)
        
        
        previewButton = wx.Button(buttonPanel,label="Preview")
        previewButton.Bind(wx.EVT_BUTTON,self.performPreview)

        clearButton = wx.Button(buttonPanel,label="Clear")
        clearButton.Bind(wx.EVT_BUTTON,self.performClear)

        saveButton = wx.Button(buttonPanel,label="Save")
        saveButton.Bind(wx.EVT_BUTTON,self.performSave)
        
        self.modeBox = wx.ComboBox(buttonPanel, choices=self.scannerSettings['mode'], style=wx.CB_READONLY)
        self.modeBox.Select(0)
        self.scanner.mode = self.scannerSettings['mode'][0]
        self.modeBox.Bind(wx.EVT_COMBOBOX, self.modeSelect)
        
        self.resolutionBox = wx.ComboBox(buttonPanel, choices=self.scannerSettings['resolution'], style=wx.CB_READONLY)
        self.resolutionBox.Select(0)
        self.scanner.resolution = int(self.scannerSettings['resolution'][0])
        self.resolutionBox.Bind(wx.EVT_COMBOBOX, self.resolutionSelect)
        
        (minVal,maxVal,tick) = self.scannerSettings['contrast']
        self.contrastSlider = wx.Slider(buttonPanel,value=(minVal+maxVal)/2,minValue=minVal,maxValue=maxVal,size=(150,-1),style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS, name="Contrast")
        self.contrastSlider.Bind(wx.EVT_SCROLL, self.contrastChanged)
        
        (minVal,maxVal,tick) = self.scannerSettings['brightness']
        self.brightnessSlider = wx.Slider(buttonPanel,value=(minVal+maxVal)/2,minValue=minVal,maxValue=maxVal,size=(150,-1),style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        #self.brightnessSlider.SetTickFreq(tick)
        self.brightnessSlider.Bind(wx.EVT_SCROLL, self.brightnessChanged)
        
        buttonLayout.Add(wx.StaticText(buttonPanel,wx.ID_ANY,label="Scan and Save a Page"))
        buttonLayout.Add(scanButton)
        buttonLayout.Add(wx.StaticText(buttonPanel,wx.ID_ANY,label="Scan a Preview"))
        buttonLayout.Add(previewButton)
        buttonLayout.Add(wx.StaticText(buttonPanel,wx.ID_ANY,label="Select the Scan Mode"))      
        buttonLayout.Add(self.modeBox)
        buttonLayout.Add(wx.StaticText(buttonPanel,wx.ID_ANY,label="Select the Scan Resolution"))      
        buttonLayout.Add(self.resolutionBox)

        try:
            contrast = self.scanner.contrast
            buttonLayout.Add(wx.StaticText(buttonPanel,wx.ID_ANY,label="Select the Contrast"))      
            buttonLayout.Add(self.contrastSlider)
            
        except AttributeError:
            self.contrastSlider.Hide()
        try:
            brightness = self.scanner.contrast
            buttonLayout.Add(wx.StaticText(buttonPanel,wx.ID_ANY,label="Select the Brightness"))      
            buttonLayout.Add(self.brightnessSlider)
            
        except AttributeError:
            self.brightnessSlider.Hide()

        buttonLayout.Add(wx.StaticText(buttonPanel,wx.ID_ANY,label="Remove all Scanned Pages"))      
        buttonLayout.Add(clearButton)
        buttonLayout.Add(wx.StaticText(buttonPanel,wx.ID_ANY,label="Save all Scanned Pages"))      
        buttonLayout.Add(saveButton)


        buttonLayout.AddSpacer(50)
        buttonLayout.Add(self.countLabel)
        
    def brightnessChanged(self,e):
        obj = e.GetEventObject()
        val = obj.GetValue()
        self.scanner.brightness = int(val)

    def contrastChanged(self,e):
        obj = e.GetEventObject()
        val = obj.GetValue()
        self.scanner.contrast = int(val)
        
        
    def resolutionSelect(self,e):
        self.scanner.resolution = int(e.GetString())
    #    pass
    
    def modeSelect(self,e):
        self.scanner.mode = str(e.GetString())
    #    pass
    
    def performClear(self,e):
        self.images = []
    
    def performSave(self,e):
        if len(self.images) == 0:
            return
        filter = "PDF file (.pdf) |*.pdf"
        dlg = wx.FileDialog(
            self, message="Save file as ...", 
            defaultFile="out.pdf", wildcard=filter, style=wx.SAVE | wx.FD_OVERWRITE_PROMPT
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            pdf = canvas.Canvas(path)
            for img in self.images:
                pdf.drawImage(canvas.ImageReader(img),0,0,width=A4[0],height=A4[1],preserveAspectRatio=True)
                pdf.showPage()
            pdf.save()
        dlg.Destroy()
        self.images = []
        self.updatePageCount()

    def updatePageCount(self):
        self.countLabel.SetLabel("Current pages: " + str(len(self.images)))

    """initialises scanner and probes for options and such"""
    def initialiseScannerOptions(self,scanner):
        self.scannerSettings['mode'] = get_scanner_option(scanner, 'mode')[-1]
        m = get_scanner_option(scanner, 'resolution')[-1]
        strres = []
        for i in m:
            strres.append(str(i))
        self.scannerSettings['resolution'] = strres
        
        self.scannerSettings['brightness'] = get_scanner_option(scanner, 'brightness')[-1]
        self.scannerSettings['contrast'] = get_scanner_option(scanner, 'contrast')[-1]
    
    def performPreview(self,e):
        res = self.scanner.resolution
        m = get_scanner_option(self.scanner, 'resolution')[-1]
        self.scanner.resolution = m[0]
        self.scanner.preview=1
        self.performScan(e)
        self.images.pop()
        self.scanner.preview=0
        self.scanner.resolution = res
        self.updatePageCount()

    def performScan(self,e):
        # geometry
        try:
            self.scanner.tl_x = 0
            self.scanner.tl_y = 0
            option = get_scanner_option (self.scanner, 'br-x')
#            self.scanner.br_x = option[8][1]
            self.scanner.br_x = 210.0
            option = get_scanner_option (self.scanner, 'br-y')
            #self.scanner.br_y = option[8][1]
            self.scanner.br_y = 297.0
        except AttributeError:
            print "WARNING: Can't set scan geometry"
        #scan
        try:
            pil_image = self.scanner.scan()
            self.images.append(pil_image)
            self.display_image(pil_image)
                    
        except sane._sane.error, err:
            print "ERROR: Can't scan"
            print(_("Can't scan preview image,\n%s,\nCheck scanner settings") % err)
        self.updatePageCount()


    def display_image(self,pil_image):
        wximg = pil_to_image(pil_image)
        self.imagePanel.display(wximg)

def pil_to_image(pil, alpha=True):
    """ Method will convert PIL Image to wx.Image """
    if alpha:
        image = apply( wx.EmptyImage, pil.size )
        image.SetData( pil.convert( "RGB").tostring() )
        image.SetAlphaData(pil.convert("RGBA").tostring()[3::4])
    else:
        image = wx.EmptyImage(pil.size[0], pil.size[1])
        new_image = pil.convert('RGB')
        data = new_image.tostring()
        image.SetData(data)
    return image


def image_to_pil(self, image):
    """ Method will convert wx.Image to PIL Image """
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.fromstring(image.GetData())
    return pil


# set global functions
def get_scanner_option (scanner, name):
    options = scanner.get_options()
    
    for option in options:
        if option[1] == name:
            return option
    return False



class ScanApp(wx.App):
    def OnInit(self):
        ScanWindow(None)
        return True

if __name__ == '__main__':
    app = ScanApp()
    app.MainLoop()
