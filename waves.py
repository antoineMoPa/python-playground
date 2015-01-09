# run specifying number of frames to render
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import numpy as np
import math
import os
import sys
from copy import *

class Waves:
    def __init__(self,w,h):
        self.w, self.h = w,h
        self.time = 0
        self.interval = 0.2
        self.damping = 1.0
        self.image = 0

        self.clear()

        if not os.path.exists("./images"):
            os.makedirs("./images")

    def clear(self):
        # rgba data container
        self.data = np.ones( (self.w,self.h,4), dtype=np.uint8)
        # 'height' of every 'particle'
        self.heights = np.ones( (self.w,self.h), dtype=np.float32 )
        # their individual vertical speeds
        self.speeds = np.zeros( (self.w,self.h), dtype=np.float32 )
        # transmission factors
        self.tfactors = np.ones( (self.w,self.h), dtype=np.float32 )/3
        # make heights equal to 0.5
        self.heights /= 2
        
    def outputImg(self):
        img = self.getImage()
        img.save('./images/test'+str(self.image).zfill(6)+'.png')
        self.image += 1

    def getImage(self, channels):
        self.draw(channels)
        return Image.fromarray(self.data,'RGBA')

    def point(self,i,j,radius,value, arr="heights", shape="pointsine"):
        i = math.floor(i)
        j = math.floor(j)

        if(arr == "heights"):
            arr = self.heights
        elif(arr == "speeds"):
            arr = self.speeds
        elif(arr == "tfactors"):
            arr = self.tfactors
        else:
            print("error: arr must be either 'heights', 'speeds' or 'tfactors'")
            return
        
        if(shape == "pointsine"):
            shape = lambda d: math.sin(20*(1-d / radius))
        elif(shape == "point"):
            shape = lambda d: (1-d / radius)
            
        for k in range(i - radius,i + radius):
            for l in range(j - radius,j + radius):
                d = self.dist(i,j,k,l)
                if(d < radius):
                    arr[k][l] += value * shape(d)

    def dist(self,x1,y1,x2,y2):
        return math.sqrt(math.pow(x2 - x1,2) + math.pow(y2 - y1,2))

    def iterate(self):
        # we equilibrate with 4 cells so we divide effect of each cell by 4
        factor = 1/4
        self.time += self.interval
        speeds = self.speeds
        heights = self.heights
        damping = self.damping

        # When I wrote that code, only god and I knew what it meant
        # now only god knows

        # find difference
        # multiply difference by factor
        # add it to speed
        # substract speed to neighbours

        h1 = np.roll(np.copy(heights),1,axis=0)
        h2 = np.roll(np.copy(heights),-1,axis=0)
        h3 = np.roll(np.copy(heights),1,axis=1)
        h4 = np.roll(np.copy(heights),-1,axis=1)
        
        d1 = self.tfactors * factor * (heights - h1)
        d2 = self.tfactors * factor * (heights - h2)
        d3 = self.tfactors * factor * (heights - h3)
        d4 = self.tfactors * factor * (heights - h4)

        speeds -= d1
        speeds -= d2
        speeds -= d3
        speeds -= d4

        speeds += np.roll(d1,-1,axis=0)
        speeds += np.roll(d2,1,axis=0)
        speeds += np.roll(d3,-1,axis=1)
        speeds += np.roll(d4,1,axis=1)

        speeds *= damping
        heights += speeds

    def draw(self, channels):
        red = green = blue = alpha = None

        for channel in ["red","green","blue","alpha"]:
            i = None
            if (channel == 'red'):
                i = 0
            elif (channel == 'green'):
                i = 1
            elif (channel == 'blue'):
                i = 2
            elif (channel == 'alpha'):
                i = 3
            else:
                print("error: channel does not exist")

            ch = channels[channel].get()
            val = None

            try:
                mult = float(channels[channel+"Multiplier"].get())
            except:
                print("invalid channel multiplier for "+channel)
                mult = 1

            if (ch == "height"):
                val = mult * self.heights
            elif (ch == "speed"):
                val = mult * self.speeds + 0.5
            elif (ch == "tfactor"):
                val = mult * self.tfactors
            elif (ch == "1"):
                val = mult * 1
            elif (ch == "0"):
                val = 0
            else:
                print("error: channel value is not handled")

            self.data[:,:,i] = np.floor(val * 255)

class Application(ttk.Frame):
    def __init__(self, master = None):
        ttk.Frame.__init__(self, master)
        self.pack()
        self.w = 500
        self.h = 500
        self.waves = Waves(self.w, self.h)
        self.initChanels()
        self.createWidgets()
        self.image = None
        self.master = master
        self.mouseX = self.w/2
        self.mouseY = self.h/2
        self.putWavesImage()
        self.after(30, self.refresh)
        self.playing = 0

    def refresh(self):
        if(self.playing == 1):
            self.iterate()
        self.after(30, self.refresh)

    def initChanels(self):
        self.channelsOptions = [
            "height",
            "speed",
            "tfactor",
            "1",
            "0"]

        self.redCO = copy(self.channelsOptions)
        self.greenCO = copy(self.channelsOptions)
        self.blueCO = copy(self.channelsOptions)
        self.alphaCO = copy(self.channelsOptions)

        self.redCO.insert(0,"height")
        self.greenCO.insert(0,"height")
        self.blueCO.insert(0,"height")
        self.alphaCO.insert(0,"1")

        self.channels = {}
        self.channels["red"] = tk.StringVar(master)
        self.channels["green"] = tk.StringVar(master)
        self.channels["blue"] = tk.StringVar(master)
        self.channels["alpha"] = tk.StringVar(master)

        self.channels["redMultiplier"] = tk.StringVar(master)
        self.channels["greenMultiplier"] = tk.StringVar(master)
        self.channels["blueMultiplier"] = tk.StringVar(master)
        self.channels["alphaMultiplier"] = tk.StringVar(master)

        self.channels['red'].set("height")
        self.channels['green'].set("height")
        self.channels['blue'].set("height")
        self.channels['alpha'].set("1")

        self.channels["redMultiplier"].set("1")
        self.channels["greenMultiplier"].set("1")
        self.channels["blueMultiplier"].set("1")
        self.channels["alphaMultiplier"].set("1")

    def iterate(self):
        self.waves.iterate()
        self.putWavesImage()

    def putWavesImage(self):
        self.image = ImageTk.PhotoImage(self.waves.getImage(self.channels))
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
        self.createColorSettingsWidgets()

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
        self.redraw_btn["command"] = self.putWavesImage

        self.clear_btn = ttk.Button(self.top_panel)
        self.clear_btn["text"] = "Clear"
        self.clear_btn["command"] = self.waves.clear

        self.play_btn.grid(column = 0, row=0, padx=5, pady=5)

        self.iterate_btn.grid(column = 1, row=0, padx=5, pady=5)
        self.redraw_btn.grid(column = 2, row=0, padx=5, pady=5)
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
            #        self.waves.tfactors[i,j] = 0
            self.waves.point(y, x, 80, +0.1, arr=arr, shape="point")
            self.waves.tfactors = np.clip(self.waves.tfactors,0.1,1)
        else:
            self.waves.point(y, x, 20, 0.1, arr=arr, shape="pointsine")


    def clipValue(self, val, min, max):
        if(val < min):
            val = min
        elif(val > max):
            val = max
        return val

    def createCanvasWidgets(self):
        self.canvas = tk.Canvas(self.middle_panel,
                                width = self.waves.w,
                                height = self.waves.h)

        def canvasDrawHeights(event):
            self.canvasDraw(event,"heights")

        def canvasDrawTFactors(event):
            self.canvasDraw(event,"tfactors")


        self.canvas.bind("<B1-Motion>",canvasDrawHeights)
        self.canvas.bind("<Button-1>",canvasDrawHeights)

        self.canvas.bind("<B3-Motion>",canvasDrawTFactors)
        self.canvas.bind("<Button-3>",canvasDrawTFactors)

        self.canvas.pack()

    def createColorSettingsWidgets(self):
        self.colorFrame = ttk.Frame()
        cF = self.colorFrame
        chs = self.channels

        rL = ttk.Label(cF,text="Red channel")
        gL = ttk.Label(cF,text="Green channel")
        bL = ttk.Label(cF,text="Blue channel")
        aL = ttk.Label(cF,text="Alpha channel")

        rO = ttk.OptionMenu(cF,
                            chs['red'],
                            *self.redCO
                            )
        gO = ttk.OptionMenu(cF,
                            chs['green'],
                            *self.greenCO
                            )
        bO = ttk.OptionMenu(cF,
                            chs['blue'],
                            *self.blueCO
                            )
        aO = ttk.OptionMenu(cF,
                            chs['alpha'],
                            *self.alphaCO
                            )

        # M for multiplier
        # rgba for channel

        rM = ttk.Entry(cF, textvariable=chs['redMultiplier'], width=5, justify="r")
        gM = ttk.Entry(cF, textvariable=chs['greenMultiplier'], width=5, justify="r")
        bM = ttk.Entry(cF, textvariable=chs['blueMultiplier'], width=5, justify="r")
        aM = ttk.Entry(cF, textvariable=chs['alphaMultiplier'], width=5, justify="r")

        # grid label

        rL.grid(row=0, column=0)
        gL.grid(row=0, column=1)
        bL.grid(row=0, column=2)
        aL.grid(row=0, column=3)

        # grid combobox

        rO.grid(row=1, column=0, padx=5, pady=5)
        gO.grid(row=1, column=1, padx=5, pady=5)
        bO.grid(row=1, column=2, padx=5, pady=5)
        aO.grid(row=1, column=3, padx=5, pady=5)

        # multipliers

        rM.grid(row=2, column=0, sticky='e', padx=5)
        gM.grid(row=2, column=1, sticky='e', padx=5)
        bM.grid(row=2, column=2, sticky='e', padx=5)
        aM.grid(row=2, column=3, sticky='e', padx=5)

        self.colorFrame.pack(pady=10)


master = tk.Tk()
app = Application(master)
app.master.title("Waves")
app.mainloop()


# get number of frames in argument
#num = 100
#w = Waves(100,100,num)
#print ("to generate gif:")
#print ("convert -delay 2 -loop 0 -layers optimize-frame -fuzz 50% images/*.png animat#ion.gif")
