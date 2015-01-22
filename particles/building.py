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
        self.image = Image.new("RGB", (self.w, self.h), (255, 255, 255))
        self.imageDraw = ImageDraw.Draw(self.image,'RGBA')
        self.clear()
        # mouse
        self.x = 0
        self.y = 0

        if not os.path.exists("./images"):
            os.makedirs("./images")

    def clear(self):
        self.particle_num = 0
        # rgba data container
        self.data = np.ones( (self.w,self.h,4), dtype=np.uint8)
        # x,y,speed x, speed y
        self.particles = np.zeros( (self.particle_num, 6), dtype=np.float16 )
        self.fixed = np.zeros( (self.particle_num), dtype=bool )
        # place points
        for i in range(0, int(len(self.particles))):
            column = (i % 5)
            x = 40 + 20 *(column) + i/6
            y = 180 + 3 * (i - column) + i
            self.particles[i] = [x, y, 0, 0, 0, 0]

        self.attached = np.zeros((len(self.particles),len(self.particles)), dtype=bool)

    def dist(self,x1,y1,x2,y2):
        return math.sqrt(math.pow(x2 - x1,2) + math.pow(y2 - y1,2))

    def createImage(self, canvas):
        canvas.delete("all")
        fill = (255, 255, 255, 255)
        self.imageDraw.rectangle((0, 0, self.w, self.h),fill=fill)
        for i in range(0, len(self.particles)):
            part = self.particles[i]
            radius = 4
            x,y = part[0], part[1]
            box = (x - radius, y - radius, x + radius, y + radius)
            red = blue = 0
            if self.fixed[i] == 1:
                red = 255
            if np.any(self.attached[i,:]):
                blue = 255
            self.imageDraw.ellipse(box,
                                   fill=(red,0,blue,15))

        self.tkimage = ImageTk.PhotoImage(self.image)
        canvas.create_image((self.w/2, self.h/2),image=self.tkimage)

    def iterate(self):
        self.time += self.interval
        ps = self.particles
        fixed = self.fixed

        # reset acceleration
        self.particles[:, 4] = 0
        self.particles[:, 5] = 0

        deltaXs = np.zeros((len(ps),len(ps)))
        deltaYs = np.zeros((len(ps),len(ps)))
        zeros = np.zeros((len(ps),len(ps)))

        for i in range(0, len(ps)):
            for j in range(0, len(ps)):
                if(i != j):
                    deltaXs[i, j] = ps[i, 0] - ps[j, 0]
                    deltaYs[i, j] = ps[i, 1] - ps[j, 1]
                else:
                    deltaXs[i, j] = deltaYs[i, j] = 0

        distsSQUARE = np.power(deltaXs,2) + np.power(deltaYs,2)
        dists = np.sqrt(distsSQUARE)

        dists_rep = np.where(dists[:,:] < 12, dists, 0)
        dists_inverses = 1 / dists_rep
        dists_inverses[dists_rep == 0] = 0

        rep = 100

        ps[:,4] += rep * np.sum(np.power(dists_inverses, 3) * deltaXs, axis=1)
        ps[:,5] += rep * np.sum(np.power(dists_inverses, 3) * deltaYs, axis=1)
        
        # connected (attached) points
        
        for i in range(0, len(ps)):
            for j in range(0, len(ps)):
                if(self.attached[i,j] == 1):
                    if(dists[i,j] > 300): 
                        self.attached[i,j] = 0
                    else:
                        ps[i,4] -= 0.002 * (dists[i,j] - 30) * deltaXs[i,j]
                        ps[i,5] -= 0.002 * (dists[i,j] - 30) * deltaYs[i,j]
                    

        # add gravity
        self.particles[fixed == 0,5] += 0.4

        self.particles[:, 2] += ps[:,4]
        self.particles[:, 3] += ps[:,5]
        
        self.particles[fixed == 1,2] *= 0.0
        self.particles[fixed == 1,3] *= 0.0
        
        self.particles[:, 0] += self.particles[:,2]
        self.particles[:, 1] += self.particles[:,3]

        # ambiant friction
        self.particles[:,3] *= 0.8
        self.particles[:,4] *= 0.8

        self.saveImage()

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
        print("Particles: "+str(len(self.simulation.particles))+" | Avg. frame time:" + str(int(average_time * (10 ** 3))))

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

        def clear():
            self.simulation.clear()
            self.putSimulationImage()

        self.clear_btn = ttk.Button(self.top_panel)
        self.clear_btn["text"] = "Clear"
        self.clear_btn["command"] = clear

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

        self.lastX = None
        self.lastY = None
        def click3(e):
            lastX = self.lastX
            lastY = self.lastY
            ps = self.simulation.particles
            if(lastX != None):
                deltaX = e.x - lastX
                deltaY = e.y - lastY
                dist = math.sqrt(deltaX ** 2 + deltaY ** 2)
                number = int(dist/10)
                if(number < 1):
                    number = 1
                for i in range(0, number):
                    x = i / number * deltaX + lastX
                    y = i / number * deltaY + lastY
                    fixed = self.simulation.fixed
                    ps = np.append(ps, [[x, y, 0, 0, 0, 0]], axis=0)
                    self.simulation.fixed = np.append(self.simulation.fixed, 1)
                    growAttached()
                    
                self.lastX = None
                self.lastY = None
            else:
                self.lastX = e.x
                self.lastY = e.y
            self.simulation.particles = ps
            self.putSimulationImage()
        def click1(e):
            x = e.x
            y = e.y
            ps = self.simulation.particles
            fixed = self.simulation.fixed
            ps = np.append(ps, [[x, y, 0, 0, 0, 0]], axis=0)
            self.simulation.fixed = np.append(self.simulation.fixed, 0)
            self.simulation.particles = ps
            
            growAttached()
            att = self.simulation.attached
            
            if(att.shape[0] >= 2):
                i = att.shape[0] - 1
                j = att.shape[0] - 2
                if self.simulation.fixed[i] != 1 and self.simulation.fixed[j] != 1:
                    att[i,j] = 1
                    att[j,i] = 1

            self.simulation.attached = att
            self.putSimulationImage()
            
        def growAttached():
            att = self.simulation.attached
            newAtt = np.zeros((att.shape[0]+1,att.shape[1]+1),dtype=bool)
            newAtt[:-1,:-1] = self.simulation.attached
            self.simulation.attached = newAtt
            
        #self.canvas.bind("<Motion>", motion)
        self.canvas.bind("<Button-3>", click3)
        self.canvas.bind("<Button-1>", click1)

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
