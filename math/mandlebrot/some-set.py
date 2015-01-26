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
        self.clear()
        # mouse
        self.x = 0
        self.y = 0
        
        if not os.path.exists("./images"):
            os.makedirs("./images")

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
        
        self.multR = 3
        self.multI = 3
        self.posR = 2
        self.posI = 1.5
        
        for i in range(0,self.w):
            for j in range(0,self.h):
                self.real[i,j] = self.multR * i / (self.w) - self.posR
                self.im[i,j] = self.multI * j / (self.w) - self.posI
    
    def iterate(self):
        self.step += 1
        c = 2
        self.real[np.abs(self.real) > c**2] = 0
        self.im[np.abs(self.im) > c**2] = 0
        # c = c**2 + c
        a = self.real
        b = self.im

        # square complex number
        aTemp = (a**2 - b**2)
        b = b*a + a*b
        a = aTemp
        # addition
        self.real = a + self.real
        self.im = b + self.im        
        modulus = np.sqrt(self.real**2 + self.im**2)                
        self.set[(self.set == 0) & ((modulus) > c)] = 255-self.step
        #self.saveImage()

            
    def createImage(self, canvas):
        canvas.delete("all")
        self.data[:,:,0] = self.set
        self.data[:,:,1] = self.set
        self.data[:,:,2] = self.set
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

        self.iterate_btn = ttk.Button(self.top_panel)
        self.iterate_btn["text"] = "Iterate"
        self.iterate_btn["command"] = self.iterate
        
        self.redraw_btn = ttk.Button(self.top_panel)
        self.redraw_btn["text"] = "Redraw"
        self.redraw_btn["command"] = self.putSimulationImage

        self.clear_btn = ttk.Button(self.top_panel)
        self.clear_btn["text"] = "Clear"
        self.clear_btn["command"] = self.simulation.clear

        self.play_btn.grid(column = 0, row=0, padx=5, pady=5)
        self.redraw_btn.grid(column = 1, row=0, padx=5, pady=5)
        self.iterate_btn.grid(column = 2, row=0, padx=5, pady=5)
        self.clear_btn.grid(column = 3, row=0, padx=5, pady=5)
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

        def updatePosition(event):
            self.simulation.x = event.x
            self.simulation.y = event.y
            
        def click(e):
            ps = self.simulation.particles
            ps = np.append(ps, [[e.x, e.y, 0, 0]], axis=0)
            self.simulation.particles= ps
            
        #self.canvas.bind("<Motion>", motion)
        self.canvas.bind("<Button-1>", click)

        self.canvas.pack()

    def createSettingsWidgets(self):
        # you can create settings and use them in your simulation
        self.settingsFrame = tk.Frame()
        self.somesetting = tk.StringVar()

        self.somesetting.set(3)

        someSettingLabel = ttk.Label(self.settingsFrame,
                                     text="Some setting")
        someSetting = ttk.Entry(self.settingsFrame,
                                textvariable=self.somesetting,
                                width=5, justify="r")

        someSettingLabel.grid(row=0, column=0)
        someSetting.grid(row=1, column=0)

        self.settingsFrame.pack(pady=10)

master = tk.Tk()
app = Application(500, 500, master)
app.master.title("Simulation")
app.mainloop()
