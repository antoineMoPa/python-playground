# run specifying number of frames to render
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
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
        self.imagenum = 0
        self.image = Image.new("RGB", (self.w, self.h), (255, 255, 255))
        self.imageDraw = ImageDraw.Draw(self.image,'RGBA')
        self.clear()
        # mouse
        self.x = 0
        self.y = 0
        self.gravity = 0
        
        if not os.path.exists("./images"):
            os.makedirs("./images")

    def clear(self):
        self.particle_num = 0
        # rgba data container
        self.data = np.ones( (self.w,self.h,4), dtype=np.uint8)
        # x,y,speed x, speed y
        self.particles = np.zeros( (self.particle_num, 4), dtype=np.float16 )
        
        for i in range(0, len(self.particles)):
            column = (i % 8)
            self.particles[i] = [150 + 20 *(column) + i/6, 40 + 1 * (i - column) + i, 0, 0]

    def dist(self,x1,y1,x2,y2):
        return math.sqrt(math.pow(x2 - x1,2) + math.pow(y2 - y1,2))

    def createImage(self, canvas):
        #rec = canvas.create_rectangle(0, 0, self.w, self.h, fill="#ffffff")

        canvas.delete("all")
        self.imageDraw.rectangle((0, 0, self.w, self.h),fill="#ffffff")
        for part in self.particles:
            radius = 5
            x,y = part[0], part[1]
            box = (x - radius, y - radius, x + radius, y + radius)
            self.imageDraw.ellipse(box, fill=(0,0,0,30))

        self.tkimage = ImageTk.PhotoImage(self.image)
        canvas.create_image((self.w/2, self.h/2),image=self.tkimage)

    def iterate(self):
        self.time += self.interval
        ps = self.particles
        
        # add gravity
        #self.particles[:,3] += 0.5
        deltaXs = np.zeros((len(ps),len(ps)))
        deltaYs = np.zeros((len(ps),len(ps)))
        
        for i in range(0, len(ps)):
            for j in range(0, len(ps)):
                deltaXs[i, j] = ps[i, 0] - ps[j, 0]
                deltaYs[i, j] = ps[i, 1] - ps[j, 1]
            
        distsSQUARE = np.power(deltaXs,2) + np.power(deltaYs,2)
        
        dists = np.sqrt(distsSQUARE)
        
        factorsAttraction = 1 / 4 * np.power(1 - (np.clip(dists,0,30)) / 30, 2)
        factorsRepulsion = np.power(1 - (np.clip(dists,0,15)) / 15, 2)
        ps[:,2] -= np.sum(factorsAttraction * deltaXs, axis=1)
        ps[:,3] -= np.sum(factorsAttraction * deltaYs, axis=1)
        ps[:,2] += np.sum(factorsRepulsion * deltaXs, axis=1)
        ps[:,3] += np.sum(factorsRepulsion * deltaYs, axis=1)
        
        #self.particles[:,2] *= 0.9
        #self.particles[:,3] *= 0.9
        
        self.particles[:,0] += self.particles[:,2]
        self.particles[:,1] += self.particles[:,3]
        
        self.manageWalls()
        self.saveImage()

    def saveImage(self):
        self.imagenum += 1
        self.image.save("./images/image-"+str(self.imagenum).zfill(6)+".png")
        
    def manageWalls(self):
        # to optimize
        for i in range(0, len(self.particles)):
            p = self.particles[i]
            
            limitDown = self.h - 10
            if(p[1] >= limitDown):
                p[1] = limitDown
                #p[3] = 0
                
            # friction at bottom
            if(p[1] >= limitDown-20):
                p[2] *= 0.3
            
            limitTop = 10
            if(p[1] <= limitTop):
                p[1] = limitTop
                p[3] = 0
            
            limitRight = self.w - 10
            if(p[0] >= limitRight):
                p[0] = limitRight
                p[2] = 0
                    
            limitLeft = 10
            if(p[0] <= limitLeft):
                p[0] = limitLeft
                p[2] = 0

            
class Application(ttk.Frame):
    def __init__(self, master = None):
        ttk.Frame.__init__(self, master)
        self.pack()
        self.w = 500
        self.h = 500
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
        t = datetime.now()
        self.simulation.iterate()
        self.putSimulationImage()
        print(datetime.now() - t)
        
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
app = Application(master)
app.master.title("Simulation")
app.mainloop()
