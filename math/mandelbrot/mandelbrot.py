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

class Simulation:
    def __init__(self,w,h):
        np.errstate(divide='ignore')
        self.w, self.h = w,h
        self.time = 0
        self.interval = 0.2
        self.imagenum = 0
                
        self.clearC()
        self.clear()
        
        if not os.path.exists("./images"):
            os.makedirs("./images")
    
    def clearC(self):
        # Initialize the values of c in z -> z**2 + c
        
        multR = 3
        multI = 3
        posR = 2
        posI = 1.5
        
        self.c = 2
        
        self.cReal = np.zeros((self.w,self.h), dtype=np.float32)
        self.cIm = np.zeros((self.w,self.h), dtype=np.float32)
        for i in range(0,self.w):
            for j in range(0,self.h):
                self.cReal[i,j] = multR * j / (self.w) - posR
                self.cIm[i,j] = multI * i / (self.w) - posI

    def clear(self):
        self.step = 0
        # rgba data container
        self.data = np.ones( (self.w,self.h,4), dtype=np.uint8)

        # real part
        self.real = np.zeros( (self.w,self.h), dtype=np.float32)
        # imaginary part
        self.im = np.zeros( (self.w,self.h), dtype=np.float32)
        # the set
        self.set = np.zeros( (self.w,self.h), dtype=np.int8)
        
        self.drawn = 0        
        self.iteration = 0
        self.iterations = 4

    def iterate(self):
        if(self.drawn == 1):
            return
        step = 0
        limit = 2
        for iteration in range(0,self.iterations):
            step += 1
            # protect against overflow
            self.real[np.abs(self.real) > limit**2] = 0
            self.im[np.abs(self.im) > limit**2] = 0
            # c = c**2 + c
            a = self.real
            b = self.im
            
            # square complex number
            aTemp = (a**2 - b**2)
            b = b*a + a*b
            a = aTemp
            
            aTemp = (a**2 - b**2)
            b = b*a + a*b
            a = aTemp
            
            
            # addition
            self.real = a + self.cReal
            self.im = b + self.cIm
            modulus = np.sqrt(self.real**2 + self.im**2)
            self.set[(self.set == 0) & ((modulus) > limit)] = step
            
        #self.saveImage()
        self.drawn = 1

    def createImage(self, canvas):
        canvas.delete("all")
        self.data[:,:,0] = self.set%10/10*255
        self.data[:,:,1] = self.set%20/20*255
        self.data[:,:,2] = self.set%50/50*255
        self.data[:,:,3] = 255
        self.image = Image.fromarray(self.data,'RGBA')
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

        self.clear_btn = ttk.Button(self.top_panel)
        self.clear_btn["text"] = "Clear"
        self.clear_btn["command"] = self.simulation.clear

        self.play_btn.grid(column = 0, row=0, padx=5, pady=5)        
        self.redraw_btn.grid(column = 1, row=0, padx=5, pady=5)
        self.clear_btn.grid(column = 2, row=0, padx=5, pady=5)
        self.top_panel.pack()
        self.middle_panel.pack()

    def canvasDraw(self,event,arr):
        # Safe zone
        x = self.clipValue(event.x,0,self.w)
        y = self.clipValue(event.y,0,self.h)

        if(arr == "tfactors"):
            #size = 3
            #for i in range(y-size, y+size):
            #    for j in range(x-size, x+size):
            #        self.simulation.tfactors[i,j] = 0
            self.simulation.point(y, x, 80, +0.1, arr=arr, shape="point")
            self.simulation.tfactors = np.clip(self.simulation.tfactors,0.1,1)
        else:
            self.simulation.point(y, x, 20, 0.1, arr=arr, shape="pointsine")


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
        
        self.zoom = 10
        
        def left(e=None):
            self.simulation.cReal -= 1/self.zoom
            self.simulation.clear() 
        def right(e=None):
            self.simulation.cReal += 1/self.zoom
            self.simulation.clear()
        def top(e):
            self.simulation.cIm -= 1/self.zoom
            self.simulation.clear()
        def bottom(e):
            self.simulation.cIm += 1/self.zoom
            self.simulation.clear()
        def zoomIn(e):
            self.simulation.cReal *= 0.9
            self.simulation.cIm *= 0.9
            self.simulation.clear()
        def zoomOut(e):
            self.simulation.cReal *= 1.1
            self.simulation.cIm *= 1.1
            self.simulation.clear()

        self.master.bind("<Left>", left)
        self.master.bind("<Right>", right)
        self.master.bind("<Up>", zoomIn)
        self.master.bind("<Down>", zoomOut)
        self.master.bind("<w>", top)
        self.master.bind("<s>", bottom)
        self.master.bind("<a>", left)
        self.master.bind("<d>", right)
        
        
        self.canvas.pack()

    def createSettingsWidgets(self):
        # you can create settings and use them in your simulation
        self.settingsFrame = tk.Frame()
        self.iterations_num = tk.StringVar()

        self.iterations_num.set(10)

        iterations_numLabel = ttk.Label(self.settingsFrame,
                                     text="max iterations")
        iterations_num = ttk.Entry(self.settingsFrame,
                                textvariable=self.iterations_num,
                                width=5, justify="r")

        iterations_numLabel.grid(row=0, column=0)
        iterations_num.grid(row=1, column=0)

        self.settingsFrame.pack(pady=10)

master = tk.Tk()
app = Application(500, 500, master)
app.master.title("Simulation")
app.mainloop()
