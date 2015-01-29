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
import wave
from os import system

class Simulation:
    def __init__(self,w,h):
        np.errstate(divide='ignore')
        self.w, self.h = w,h
        self.time = 0
        self.interval = 0.2
        self.imagenum = 0
        
        self.mult = 3
        self.posR = 0
        self.posI = 0
        
        self.clearC()
        self.clear()
        
        if not os.path.exists("./images"):
            os.makedirs("./images")
    
    def clearC(self):
        # Initialize the values of c in z -> z**2 + c
        self.c = 2
                
        self.cReal = np.indices((self.w,self.h),dtype=np.float64)[0]
        self.cIm = np.indices((self.w,self.h),dtype=np.float64)[1]
        
        #for i in range(0,self.w):
        #    for j in range(0,self.h):
        #        self.cReal[i,j] = j
        #        self.cIm[i,j] = i
                
        self.positionC()

    def positionC(self):
        self.cReal = self.cReal / self.w  * self.mult + self.posR - 2
        self.cIm = self.cIm / self.w  * self.mult + self.posI - 1.5
    
    def dePositionC(self):    
        self.cReal = (self.cReal - self.posR + 2) * self.w / self.mult
        self.cIm = (self.cIm - self.posI + 1.5) * self.w  / self.mult
    
    def zoomC(self,coords,factor=0.5):
        self.clearC()
        self.dePositionC()
        self.mult *= factor
        print("Zoom multiplier: "+str(self.mult))
        x = coords[1]/self.w
        y = coords[0]/self.w
        if factor < 1:
            self.posR += (x * self.mult) 
            self.posI += (y * self.mult) 
        
        self.positionC()
        self.clear()
        
    def clear(self):
        self.step = 0
        # rgba data container
        self.data = np.ones( (self.w,self.h,4), dtype=np.uint8)

        # real part
        self.real = np.zeros( (self.w,self.h), dtype=np.float32)
        # imaginary part
        self.im = np.zeros( (self.w,self.h), dtype=np.float32)
        # the set
        self.set = np.zeros( (self.w,self.h), dtype=np.int32)
        
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
            # z = z**2 + c
            a = self.real
            b = self.im
            
            # square complex number
            aTemp = (a**2 - b**2)
            b = b*a + a*b
            a = aTemp
            
            # addition
            self.real = a + self.cReal
            self.im = b + self.cIm
            modulus = np.sqrt(self.real**2 + self.im**2)
            self.set[(self.set == 0) & ((modulus) > limit)] = step
            
        self.saveImage()
        self.drawn = 1
        
    def createImage(self, canvas):
        canvas.delete("all")
        drawSet = np.copy(self.set)
        drawSet[drawSet == 0] = self.iterations
        # create colors
        self.data[:,:,0] = (drawSet/self.iterations) * 255
        self.data[:,:,1] = (drawSet/self.iterations) * 255
        self.data[:,:,2] = (drawSet/self.iterations) * 255
        self.data[:,:,3] = 255
        self.image = Image.fromarray(self.data,'RGBA')
        self.tkimage = ImageTk.PhotoImage(self.image)
        canvas.create_image((self.w/2, self.h/2),image=self.tkimage)

    def saveImage(self):
        self.imagenum += 1
        self.image.save("./images/image-"+str(self.imagenum).zfill(6)+".png")

    def play_audio(self):
        SECOND = 44100
        sound = wave.open('sound.wav', 'w')
        sound.setparams((1, 1, SECOND, 0, 'NONE', 'not compressed'))
        data = bytearray()
        set = self.set
        
        audio = np.sum(set,axis=1)
        max = np.max(audio)
        audio = audio / max
        print(np.min(audio))
        for r in range (0,1):
            for i in range(0,len(audio)):
                s = int(127*audio[i]+127)
                data.append(s)
            
        sound.writeframes(data)
        sound.close()
        system("aplay sound.wav")

        
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
        
        def clear():
            self.simulation.clearC()
            self.simulation.clear()
        
        self.clear_btn = ttk.Button(self.top_panel)
        self.clear_btn["text"] = "Clear"
        self.clear_btn["command"] = clear

        self.play_audio_btn = ttk.Button(self.top_panel)
        self.play_audio_btn["text"] = "Play audio"
        self.play_audio_btn["command"] = self.simulation.play_audio
        
        self.play_btn.grid(column = 0, row=0, padx=5, pady=5)        
        self.redraw_btn.grid(column = 1, row=0, padx=5, pady=5)
        self.clear_btn.grid(column = 2, row=0, padx=5, pady=5)
        self.play_audio_btn.grid(column = 3, row=0, padx=5, pady=5)
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
            self.simulation.cIm -= 1/10 * self.simulation.mult
            self.simulation.clear() 
        def right(e=None):
            self.simulation.cIm += 1/10 * self.simulation.mult
            self.simulation.clear()
        def top(e):
            self.simulation.cReal -= 1/10 * self.simulation.mult
            self.simulation.clear()
        def bottom(e):
            self.simulation.cReal += 1/10 * self.simulation.mult
            self.simulation.clear()
            
        def zoom(e):
            self.simulation.zoomC((e.x,e.y))
            
        def unzoom(e):
            self.simulation.zoomC((e.x,e.y),2)
            
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
        self.iterations_num = tk.StringVar()

        self.iterations_num.set(40)

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
print("use click to zoom and right click to unzoom")
app.master.title("Simulation")
app.mainloop()


