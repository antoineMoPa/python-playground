import wave
import math
from os import system

SECOND = 44100
sound = wave.open('sound.wav', 'w')
sound.setparams((1, 1, SECOND, 0, 'NONE', 'not compressed'))
data = bytearray()


for i in range (0,SECOND):
    f = 440
    d = math.sin(2 * math.pi * f * i / SECOND)
    s = int(127*d+127)
    data.append(s)
        
sound.writeframes(data)
sound.close()
system("aplay sound.wav")

