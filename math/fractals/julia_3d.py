import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import numpy as np
import math
import time
import os
import sys
from copy import *
from os import system

# Ref:
# http://hypertextbook.com/chaos/22.shtml
# http://www.mcgoodwin.net/julia/juliajewels.html
# http://en.wikipedia.org/wiki/Open_set
# http://en.wikipedia.org/wiki/Julia_set

class Simulation:
    def __init__(self,w,h):
        np.errstate(divide='ignore')
        self.w, self.h = w,h
        self.time = 0
        self.interval = 0.2
        self.imagenum = 0
        self.layers_num = 150
        self.limit = 10

        self.cReal = 1
        self.cIm = 0
        self.clear()
        self.iterate()
        if not os.path.exists("./images"):
            os.makedirs("./images")

    def positionZ(self):
        self.zReal = self.zReal / self.w  * self.mult + self.posR
        self.zIm = self.zIm / self.w  * self.mult + self.posI

    def dePositionZ(self):
        self.zReal = (self.zReal - self.posR) * self.w / self.mult
        self.zIm = (self.zIm - self.posI) * self.w  / self.mult

    def zoomZ(self,coords,factor=0.5):
        self.dePositionZ()
        self.mult *= factor
        print("Zoom multiplier: "+str(self.mult))
        x = coords[1]/self.w
        y = coords[0]/self.w
        if factor < 1:
            self.posR += (x * self.mult)
            self.posI += (y * self.mult)

        self.positionZ()
        self.drawn = 0
    def clear(self):
        self.step = 0
        # rgba data container
        self.data = np.ones( (self.w,self.h,4), dtype=np.uint8)

        # the set
        self.set = np.zeros( (self.w,self.h), dtype=np.int32)

        self.mult = 4
        self.posR = -2
        self.posI = -2

        self.drawn = 0
        self.iteration = 0
        self.iterations = 40

        # Initialize the values of z in z -> z**2 + c
        self.zReal = np.indices((self.w,self.h),dtype=np.float64)[0]
        self.zIm = np.indices((self.w,self.h),dtype=np.float64)[1]
        self.positionZ()


    def iterate(self):
        if(self.drawn == 1):
            return
        
        limit = self.limit
        layers_num = self.layers_num
        self.layers = np.zeros((layers_num,self.w,self.h),dtype=np.float64)
        for layer in range(0,layers_num):
            step = 0
            zReal = np.copy(self.zReal)
            zIm = np.copy(self.zIm)
            for iteration in range(0,self.iterations):
                step += 1
                # protect against overflow
                zReal[np.abs(zReal) > limit**2] = 0
                zIm[np.abs(zIm) > limit**2] = 0
                # z = z**2 + c
                a = np.copy(zReal)
                b = np.copy(zIm)
                # square complex number
                aTemp = (a**2 - b**2)
                b = b*a + a*b
                a = aTemp

                # addition
                zReal = a + self.cReal + 0.003 * layer
                zIm = b + self.cIm + 0.003 * layer
                modulus = np.sqrt(zReal**2 + zIm**2)
                self.layers[layer,(self.layers[layer,:] == 0) & ((modulus) > limit)] = step
        
        self.layers[self.layers < 3] = 1
        #self.layers[self.layers == 0] = 1
        
        
        np.save("voxel.npy",self.layers)
        
        
        self.set = np.sum(self.layers,axis=0)
        self.createImageData()
        self.saveImage()
        self.drawn = 1

    def createImageData(self):
        drawSet = np.copy(self.set)
        
        # create colors
        max = self.iterations * self.layers_num
        drawSet[drawSet == 0] = max
        self.data[:,:,0] = (drawSet/max) * 255
        self.data[:,:,1] = (drawSet/max) * 255
        self.data[:,:,2] = (drawSet/max) * 255
        self.data[:,:,3] = 255
        self.image = Image.fromarray(self.data,'RGBA')

    def createImage(self, canvas):
        canvas.delete("all")
        self.tkimage = ImageTk.PhotoImage(self.image)
        canvas.create_image((self.w/2, self.h/2),image=self.tkimage)

    def saveImage(self):
        self.imagenum += 1
        self.image.save("./images/image-"+str(self.imagenum).zfill(6)+".png")

class Application(ttk.Frame):
    def __init__(self, w, h, master = None):
        ttk.Frame.__init__(self, master)
        self.total_time_between_frames = 0
        self.total_frames = 0
        self.pack()
        self.w = w
        self.h = h
        self.simulation = Simulation(self.w, self.h)
        self.createWidgets()
        self.master = master
        self.mouseX = self.w/2
        self.mouseY = self.h/2
        self.putSimulationImage()
        self.after(30, self.refresh)
        self.playing = 0
        
    def refresh(self):
        if(self.playing == 1):
            self.iterate()
        self.after(20, self.refresh)
    
    def iterate(self):
        res = 50

        # time stats
        if(self.total_frames == res):
            # reset
            self.total_frames = 0
            self.total_time_between_frames = 0

        t = time.time()

        # pass settings
        try:
            self.simulation.iterations = int(self.iterations_num.get())
            self.simulation.limit = int(self.limit.get())
            self.simulation.cReal = float(self.cReal.get())
            self.simulation.cIm = float(self.cIm.get())
            print("c: "+str(self.simulation.cReal) +" + " + str(self.simulation.cIm) + "i")

        except:
            pass

        # actual operation
        self.simulation.iterate()
        self.putSimulationImage()

        # time stats
        delta_t = time.time() - t
        self.total_time_between_frames += delta_t
        self.total_frames += 1

        self.showStats()

    def showStats(self):
        a = self.total_time_between_frames
        b  = self.total_frames
        average_time = a / b
        print("Avg. frame time:" + str(int(average_time * (10 ** 3))))

    def putSimulationImage(self):
        self.simulation.createImage(self.canvas)

    def play(self):
        if(self.playing == 1):
            self.playing = 0
            self.play_btn["text"] = "Play"
        else:
            self.playing = 1
            self.play_btn["text"] = "Pause"

    def createWidgets(self):
        self.middle_panel = tk.Frame()

        self.createTopPanelWidgets()
        self.createCanvasWidgets()
        self.createSettingsWidgets()

    def createTopPanelWidgets(self):
        self.top_panel = tk.Frame()
        self.play_btn = ttk.Button(self.top_panel)
        self.play_btn["text"] = "Play"
        self.play_btn["command"] = self.play

        self.redraw_btn = ttk.Button(self.top_panel)
        self.redraw_btn["text"] = "Redraw"
        self.redraw_btn["command"] = self.simulation.clear

        def clear():
            self.simulation.clear()

        self.clear_btn = ttk.Button(self.top_panel)
        self.clear_btn["text"] = "Clear"
        self.clear_btn["command"] = clear

        self.iterations_num = tk.StringVar()
        self.iterations_num.set(40)

        iterations_numLabel = ttk.Label(self.top_panel,
                                        text="max iterations")
        iterations_num = ttk.Entry(self.top_panel,
                                textvariable=self.iterations_num,
                                width=5, justify="r")

        self.limit = tk.StringVar()
        self.limit.set(40)
        limitLabel = ttk.Label(self.top_panel,
                                     text="limit")
        limit = ttk.Entry(self.top_panel,
                                textvariable=self.limit,
                                width=5, justify="r")


        self.cReal = tk.StringVar()
        self.cReal.set("-0.5")
        cRealLabel = ttk.Label(self.top_panel,
                                     text="real part of c")
        cReal_input = ttk.Entry(self.top_panel,
                                textvariable=self.cReal,
                                width=5, justify="r")

        self.cIm = tk.StringVar()
        self.cIm.set("0.563")

        cImLabel = ttk.Label(self.top_panel,
                                     text="imaginary part of c")
        cIm_input = ttk.Entry(self.top_panel,
                                textvariable=self.cIm,
                                width=5, justify="r")



        self.play_btn.grid(column = 0, row=0, padx=5, pady=5)
        self.redraw_btn.grid(column = 1, row=0, padx=5, pady=5)
        self.clear_btn.grid(column = 2, row=0, padx=5, pady=5)
        iterations_numLabel.grid(column=4, row=0,)
        iterations_num.grid(column=4, row=1)
        limitLabel.grid(column=5, row=0,)
        limit.grid(column=5, row=1)
        cRealLabel.grid(column=6, row=0,)
        cReal_input.grid(column=6, row=1)
        cImLabel.grid(column=7, row=0,)
        cIm_input.grid(column=7, row=1)


        self.top_panel.pack()
        self.middle_panel.pack()

    def clipValue(self, val, min, max):
        if(val < min):
            val = min
        elif(val > max):
            val = max
        return val

    def createCanvasWidgets(self):
        self.canvas = tk.Canvas(self.middle_panel,
                                width = self.simulation.w,
                                height = self.simulation.h)

        def left(e=None):
            self.simulation.zIm -= 1/10 * self.simulation.mult
        def right(e=None):
            self.simulation.zIm += 1/10 * self.simulation.mult
        def top(e):
            self.simulation.zReal -= 1/10 * self.simulation.mult
        def bottom(e):
            self.simulation.zReal += 1/10 * self.simulation.mult

        def zoom(e):
            self.simulation.zoomZ((e.x,e.y))

        def unzoom(e):
            self.simulation.zoomZ((e.x,e.y),2)

        self.canvas.bind("<Button-1>",zoom)
        self.canvas.bind("<Button-3>",unzoom)

        self.master.bind("<w>", top)
        self.master.bind("<s>", bottom)
        self.master.bind("<a>", left)
        self.master.bind("<d>", right)


        self.canvas.pack()

    def createSettingsWidgets(self):
        # you can create settings and use them in your simulation
        self.settingsFrame = tk.Frame()
        self.settingsFrame.pack(pady=10)

master = tk.Tk()
app = Application(200, 200, master)
print("use click to zoom and right click to unzoom")
app.master.title("Simulation")
app.mainloop()
