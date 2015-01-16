# run specifying number of frames to render
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import numpy as np
import math
import os
import sys
from copy import *

class Simulation:
    def __init__(self,w,h):
        self.w, self.h = w,h
        self.time = 0
        self.interval = 0.2
        self.image = 0

        self.clear()

        if not os.path.exists("./images"):
            os.makedirs("./images")

    def clear(self):
        # rgba data container
        self.data = np.ones( (self.w,self.h,4), dtype=np.uint8)
        # array you can play with
        self.heights = np.ones( (self.w,self.h), dtype=np.float32 )
        
    def outputImg(self):
        img = self.getImage()
        img.save('./images/test'+str(self.image).zfill(6)+'.png')
        self.image += 1

    def getImage(self):
        return Image.fromarray(self.data,'RGBA')

    def iterate(self):
        factor = 1/4
        self.time += self.interval
        self.heights /= 2

        #h1 = np.roll(np.copy(heights),1,axis=0)
        #h2 = np.roll(np.copy(heights),-1,axis=0)
        #h3 = np.roll(np.copy(heights),1,axis=1)
        #h4 = np.roll(np.copy(heights),-1,axis=1)
        
    def draw(self):
        self.data[:,:,0] = np.floor(self.heights * 255)
        self.data[:,:,1] = np.floor(self.heights * 255)
        self.data[:,:,2] = np.floor(self.heights * 255)
        self.data[:,:,3] = 255  

class Application(ttk.Frame):
    def __init__(self, master = None):
        ttk.Frame.__init__(self, master)
        self.pack()
        self.w = 500
        self.h = 500
        self.simulation = Simulation(self.w, self.h)
        self.createWidgets()
        self.image = None
        self.master = master
        self.mouseX = self.w/2
        self.mouseY = self.h/2
        self.putSimulationImage()
        self.after(30, self.refresh)
        self.playing = 0

    def refresh(self):
        if(self.playing == 1):
            self.iterate()
        self.after(30, self.refresh)

    def iterate(self):
        self.simulation.iterate()
        
        self.putSimulationImage()
        
    def putSimulationImage(self):
        self.simulation.draw()
        self.image = ImageTk.PhotoImage(self.simulation.getImage())
        self.canvas.create_image(self.w/2, self.h/2, image = self.image)

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
        self.redraw_btn["command"] = self.putSimulationImage
        
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

        def canvasDrawHeights(event):
            self.canvasDraw(event,"heights")

        def canvasDrawTFactors(event):
            self.canvasDraw(event,"tfactors")


        self.canvas.bind("<B1-Motion>",canvasDrawHeights)
        self.canvas.bind("<Button-1>",canvasDrawHeights)

        self.canvas.bind("<B3-Motion>",canvasDrawTFactors)
        self.canvas.bind("<Button-3>",canvasDrawTFactors)

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
app = Application(master)
app.master.title("Simulation")
app.mainloop()
